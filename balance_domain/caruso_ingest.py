"""Fail-closed local ingest for the Caruso et al. 2019 non-duplicated Dryad workbook.

The public source-of-truth workbook is a legacy BIFF .xls file. This module keeps
acquisition separate from analysis: once the exact workbook bytes are available locally,
it freezes file identity, detects the 755-record data sheet without outcome-driven
screening, and writes a loss-minimized text inventory plus the companion column dictionary.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Iterable


DATASET_DOI = "10.5061/dryad.2v8c5g0"
PUBLIC_LANDING_PAGE = "https://datadryad.org/dataset/doi:10.5061/dryad.2v8c5g0"
EXPECTED_FILENAME = "Exp_stud_NOTdup_Dryad.xls"
DRYAD_FILE_STREAM_ID = 21862
EXPECTED_RECORD_COUNT = 755
EXPECTED_WORKSHEET_COUNT = 2

RECEIPT_BASENAME = "BALANCE_CARUSO_NONDUP_SOURCE_RECEIPT_V1.json"
INVENTORY_BASENAME = "BALANCE_CARUSO_NONDUP_ROW_INVENTORY_V1.csv"
DICTIONARY_BASENAME = "BALANCE_CARUSO_NONDUP_COLUMN_DICTIONARY_V1.csv"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _plain_text(value: object) -> str:
    """Normalize already-decoded workbook values without changing sign information."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Caruso workbook contains a non-finite numeric cell")
        if value.is_integer():
            return str(int(value))
        return format(value, ".15g")
    return str(value).strip()


def _trim_matrix(rows: Iterable[Iterable[object]]) -> list[list[str]]:
    out = [[_plain_text(value) for value in row] for row in rows]
    while out and not any(cell for cell in out[-1]):
        out.pop()
    width = max((len(row) for row in out), default=0)
    normalized = [row + [""] * (width - len(row)) for row in out]
    while width and normalized and all(row[width - 1] == "" for row in normalized):
        width -= 1
    return [row[:width] for row in normalized]


def _header_is_usable(row: list[str]) -> bool:
    names = [cell.strip() for cell in row if cell.strip()]
    return (
        len(names) >= 5
        and len(names) == len(set(names))
        and all("\n" not in name and "\r" not in name for name in names)
    )


def _nonempty_rows(rows: list[list[str]], start: int) -> list[tuple[int, list[str]]]:
    return [
        (i, row)
        for i, row in enumerate(rows[start:], start=start)
        if any(cell != "" for cell in row)
    ]


def detect_data_sheet(
    sheets: dict[str, list[list[str]]],
    *,
    expected_records: int = EXPECTED_RECORD_COUNT,
) -> dict:
    """Identify the unique data sheet/header using only frozen row-count structure."""
    candidates = []
    for sheet_name, raw_rows in sheets.items():
        rows = _trim_matrix(raw_rows)
        for header_index in range(min(10, len(rows))):
            header = rows[header_index]
            if not _header_is_usable(header):
                continue
            records = _nonempty_rows(rows, header_index + 1)
            if len(records) == expected_records:
                candidates.append({
                    "sheet_name": sheet_name,
                    "rows": rows,
                    "header_index": header_index,
                    "header": header,
                    "records": records,
                })
    if len(candidates) != 1:
        summary = [
            (name, len(_trim_matrix(rows)))
            for name, rows in sheets.items()
        ]
        raise ValueError(
            "Caruso non-duplicated workbook must contain exactly one sheet/header "
            f"yielding {expected_records} non-empty records; candidates={len(candidates)} "
            f"sheets={summary}"
        )
    return candidates[0]


def build_inventory(
    sheets: dict[str, list[list[str]]],
    *,
    expected_records: int = EXPECTED_RECORD_COUNT,
) -> tuple[list[str], list[dict[str, str]], dict]:
    detected = detect_data_sheet(sheets, expected_records=expected_records)
    header = list(detected["header"])
    if any(not field for field in header):
        raise ValueError(
            "Caruso data header contains blank internal columns; preserve workbook "
            "and update the ingest contract explicitly before proceeding"
        )

    inventory: list[dict[str, str]] = []
    for zero_index, row in detected["records"]:
        padded = row + [""] * (len(header) - len(row))
        if len(padded) != len(header):
            raise ValueError("Caruso data row exceeds the detected header width")
        record = {
            "source_row_number": str(zero_index + 1),
            **dict(zip(header, padded)),
        }
        inventory.append(record)

    return ["source_row_number", *header], inventory, detected


def build_dictionary_inventory(
    sheets: dict[str, list[list[str]]],
    *,
    data_sheet_name: str,
) -> tuple[list[str], list[dict[str, str]], str]:
    others = [name for name in sheets if name != data_sheet_name]
    if len(others) != 1:
        raise ValueError(
            "Caruso source contract requires exactly one companion column-dictionary "
            f"sheet; found {others}"
        )
    name = others[0]
    rows = _trim_matrix(sheets[name])
    width = max((len(row) for row in rows), default=0)
    fields = ["source_row_number", *[f"column_{i}" for i in range(1, width + 1)]]
    out = []
    for i, row in enumerate(rows, start=1):
        if not any(row):
            continue
        padded = row + [""] * (width - len(row))
        out.append({
            "source_row_number": str(i),
            **{f"column_{j + 1}": padded[j] for j in range(width)},
        })
    return fields, out, name


def _xlrd_cell_text(cell, *, datemode: int, xlrd_module) -> str:
    ctype = cell.ctype
    if ctype in (xlrd_module.XL_CELL_EMPTY, xlrd_module.XL_CELL_BLANK):
        return ""
    if ctype == xlrd_module.XL_CELL_TEXT:
        return str(cell.value).strip()
    if ctype == xlrd_module.XL_CELL_NUMBER:
        return _plain_text(float(cell.value))
    if ctype == xlrd_module.XL_CELL_DATE:
        dt = xlrd_module.xldate_as_datetime(cell.value, datemode)
        if dt.time().isoformat() == "00:00:00":
            return dt.date().isoformat()
        return dt.isoformat()
    if ctype == xlrd_module.XL_CELL_BOOLEAN:
        return "TRUE" if bool(cell.value) else "FALSE"
    if ctype == xlrd_module.XL_CELL_ERROR:
        return f"#XL_ERROR_{int(cell.value)}"
    return _plain_text(cell.value)


def read_legacy_xls(path: Path) -> tuple[bytes, dict[str, list[list[str]]]]:
    """Read the exact legacy .xls source using xlrd, imported only for this optional path."""
    if path.name != EXPECTED_FILENAME:
        raise ValueError(
            f"expected source basename {EXPECTED_FILENAME!r}, got {path.name!r}"
        )
    if path.suffix.lower() != ".xls":
        raise ValueError("Caruso source-of-truth ingest requires the legacy .xls workbook")
    try:
        import xlrd  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "legacy Caruso .xls ingest requires xlrd; install with "
            "python -m pip install 'xlrd>=2.0.1,<3'"
        ) from exc

    raw = path.read_bytes()
    book = xlrd.open_workbook(file_contents=raw, on_demand=True)
    sheets: dict[str, list[list[str]]] = {}
    try:
        for name in book.sheet_names():
            sheet = book.sheet_by_name(name)
            rows = []
            for r in range(sheet.nrows):
                rows.append([
                    _xlrd_cell_text(
                        sheet.cell(r, c),
                        datemode=book.datemode,
                        xlrd_module=xlrd,
                    )
                    for c in range(sheet.ncols)
                ])
            sheets[name] = rows
    finally:
        book.release_resources()

    if len(sheets) != EXPECTED_WORKSHEET_COUNT:
        raise ValueError(
            f"Caruso source contract expects {EXPECTED_WORKSHEET_COUNT} worksheets, "
            f"found {len(sheets)}: {list(sheets)}"
        )
    return raw, sheets


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ingest_caruso_nondedup(source_path: Path, out_dir: Path) -> dict:
    """Freeze Stage-A source identity and row inventory without biological screening."""
    if out_dir.exists():
        raise ValueError("Caruso ingest output directory already exists; choose a new path")

    raw, sheets = read_legacy_xls(source_path)
    fields, inventory, detected = build_inventory(sheets)
    dictionary_fields, dictionary, dictionary_sheet = build_dictionary_inventory(
        sheets,
        data_sheet_name=detected["sheet_name"],
    )

    receipt = {
        "schema_version": "BALANCE_CARUSO_NONDUP_SOURCE_RECEIPT_V1",
        "status": "SOURCE_INGESTED_SCREENING_NOT_STARTED",
        "dataset_doi": DATASET_DOI,
        "public_landing_page": PUBLIC_LANDING_PAGE,
        "dryad_file_stream_id": DRYAD_FILE_STREAM_ID,
        "source_filename": EXPECTED_FILENAME,
        "source_bytes": len(raw),
        "source_sha256": _sha256_bytes(raw),
        "workbook_sheet_names": list(sheets),
        "workbook_sheet_count": len(sheets),
        "data_sheet": detected["sheet_name"],
        "data_header_row_number": detected["header_index"] + 1,
        "data_columns": detected["header"],
        "record_count": len(inventory),
        "expected_record_count": EXPECTED_RECORD_COUNT,
        "column_dictionary_sheet": dictionary_sheet,
        "row_inventory": INVENTORY_BASENAME,
        "column_dictionary_inventory": DICTIONARY_BASENAME,
        "duplicated_workbook_role": "DEPENDENCE_AUDIT_ONLY_NOT_SOURCE_INVENTORY",
        "next_gate": (
            "freeze source-level experiment/population/trait grouping before "
            "directional agent-pair screening"
        ),
        "claim_ceiling": "immutable_source_inventory_only_no_BALANCE_conflict_result",
    }
    if receipt["record_count"] != EXPECTED_RECORD_COUNT:
        raise ValueError("Caruso source row-count contract drifted")

    out_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.tmp-", dir=out_dir.parent))
    try:
        _write_csv(tmp / INVENTORY_BASENAME, fields, inventory)
        _write_csv(tmp / DICTIONARY_BASENAME, dictionary_fields, dictionary)
        (tmp / RECEIPT_BASENAME).write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp, out_dir)
    except Exception:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
        raise

    return receipt

"""Fail-closed source inventory and semantic mapping for Peucedanum raw data.

This layer deliberately separates byte/file inspection from biological semantics.
It never guesses source columns from their names. Normalized rows are emitted only
from an explicitly source-verified mapping contract.
"""
from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
import math
import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterable, Mapping

from .peucedanum_raw import REQUIRED_NORMALIZED_FIELDS, validate_normalized_rows


MAPPING_SCHEMA = "BALANCE_PEUCEDANUM_RAW_SEMANTIC_MAPPING_V1"
MAPPING_READY_STATUS = "SOURCE_VERIFIED_MAPPING"

INVENTORY_RECEIPT_BASENAME = "BALANCE_PEUCEDANUM_RAW_SOURCE_INVENTORY_V1.json"
NORMALIZED_ROWS_BASENAME = "BALANCE_PEUCEDANUM_NORMALIZED_ROWS_V1.csv"
NORMALIZATION_RECEIPT_BASENAME = "BALANCE_PEUCEDANUM_NORMALIZATION_RECEIPT_V1.json"

NORMALIZED_FIELDS = (
    "dataset_id",
    "source_doi",
    "source_file",
    "source_sheet",
    "source_row_number",
    "year",
    "population_id",
    "plant_id",
    "flowering_day",
    "perfect_flower_count",
    "male_flower_count",
    "initial_fruit_count",
    "intact_fruit_count",
    "predator_egg_count",
    "seed_predation_rate",
    "flower_stem_height",
    "male_fitness",
    "pollen_or_siring_measure",
    "total_flower_count",
    "male_fraction",
    "final_fruit_set_rate",
)

DERIVED_FIELDS = {
    "total_flower_count",
    "male_fraction",
    "final_fruit_set_rate",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _plain_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Peucedanum source contains a non-finite numeric cell")
        if value.is_integer():
            return str(int(value))
        return format(value, ".15g")
    return str(value).strip()


def _trim_matrix(rows: Iterable[Iterable[object]]) -> list[list[str]]:
    matrix = [[_plain_text(value) for value in row] for row in rows]
    while matrix and not any(matrix[-1]):
        matrix.pop()
    width = max((len(row) for row in matrix), default=0)
    matrix = [row + [""] * (width - len(row)) for row in matrix]
    while width and matrix and all(row[width - 1] == "" for row in matrix):
        width -= 1
    return [row[:width] for row in matrix]


def _table_inventory(
    *,
    source_file: str,
    source_sheet: str,
    rows: Iterable[Iterable[object]],
) -> dict:
    matrix = _trim_matrix(rows)
    width = max((len(row) for row in matrix), default=0)
    return {
        "source_file": source_file,
        "source_sheet": source_sheet,
        "row_count": len(matrix),
        "column_count": width,
        "nonempty_row_count": sum(any(cell != "" for cell in row) for row in matrix),
    }


def inventory_tables(
    tables: Mapping[tuple[str, str], Iterable[Iterable[object]]],
) -> list[dict]:
    """Inventory decoded tables without interpreting any biological column."""
    if not tables:
        raise ValueError("at least one source table is required")
    out = []
    for (source_file, source_sheet), rows in sorted(tables.items()):
        if not source_file or not source_sheet:
            raise ValueError("source file and sheet names must be non-empty")
        out.append(
            _table_inventory(
                source_file=source_file,
                source_sheet=source_sheet,
                rows=rows,
            )
        )
    return out


def _read_delimited(raw: bytes, *, delimiter: str) -> list[list[str]]:
    text = raw.decode("utf-8-sig")
    return [list(row) for row in csv.reader(io.StringIO(text), delimiter=delimiter)]


def _read_xlsx(raw: bytes) -> dict[str, list[list[object]]]:
    try:
        import openpyxl  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Peucedanum .xlsx ingest requires openpyxl; install with "
            "python -m pip install -e '.[peucedanum]'"
        ) from exc

    book = openpyxl.load_workbook(
        filename=io.BytesIO(raw),
        read_only=True,
        data_only=False,
    )
    try:
        return {
            sheet.title: [list(row) for row in sheet.iter_rows(values_only=True)]
            for sheet in book.worksheets
        }
    finally:
        book.close()


def _read_xls(raw: bytes) -> dict[str, list[list[object]]]:
    try:
        import xlrd  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Peucedanum .xls ingest requires xlrd; install with "
            "python -m pip install -e '.[peucedanum]'"
        ) from exc

    book = xlrd.open_workbook(file_contents=raw, on_demand=True)
    sheets: dict[str, list[list[object]]] = {}
    try:
        for name in book.sheet_names():
            sheet = book.sheet_by_name(name)
            rows = []
            for r in range(sheet.nrows):
                row = []
                for c in range(sheet.ncols):
                    cell = sheet.cell(r, c)
                    if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                        value: object = ""
                    elif cell.ctype == xlrd.XL_CELL_TEXT:
                        value = str(cell.value).strip()
                    elif cell.ctype == xlrd.XL_CELL_NUMBER:
                        value = float(cell.value)
                    elif cell.ctype == xlrd.XL_CELL_DATE:
                        dt = xlrd.xldate_as_datetime(cell.value, book.datemode)
                        value = (
                            dt.date().isoformat()
                            if dt.time().isoformat() == "00:00:00"
                            else dt.isoformat()
                        )
                    elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
                        value = bool(cell.value)
                    elif cell.ctype == xlrd.XL_CELL_ERROR:
                        value = f"#XL_ERROR_{int(cell.value)}"
                    else:
                        value = cell.value
                    row.append(value)
                rows.append(row)
            sheets[name] = rows
    finally:
        book.release_resources()
    return sheets


def read_tabular_source(
    path: Path,
) -> tuple[bytes, dict[str, list[list[object]]]]:
    """Read one source file without assigning biological semantics."""
    raw = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return raw, {"__CSV__": _read_delimited(raw, delimiter=",")}
    if suffix == ".tsv":
        return raw, {"__TSV__": _read_delimited(raw, delimiter="\t")}
    if suffix == ".xlsx":
        return raw, _read_xlsx(raw)
    if suffix == ".xls":
        return raw, _read_xls(raw)
    raise ValueError(
        "Peucedanum source ingest accepts only .csv, .tsv, .xlsx or .xls files"
    )


def load_sources(
    source_paths: Iterable[Path],
) -> tuple[dict[str, dict], dict[tuple[str, str], list[list[object]]]]:
    """Load exact source bytes and return provenance plus decoded tables."""
    paths = list(source_paths)
    if not paths:
        raise ValueError("at least one Peucedanum source file is required")
    names = [path.name for path in paths]
    if len(names) != len(set(names)):
        raise ValueError("Peucedanum source basenames must be unique")

    files: dict[str, dict] = {}
    tables: dict[tuple[str, str], list[list[object]]] = {}
    for path in paths:
        raw, decoded = read_tabular_source(path)
        files[path.name] = {
            "source_bytes": len(raw),
            "source_sha256": _sha256_bytes(raw),
            "format": path.suffix.lower().lstrip("."),
            "sheet_names": list(decoded),
        }
        for sheet, rows in decoded.items():
            tables[(path.name, sheet)] = rows
    return files, tables


def build_source_inventory_receipt(
    source_paths: Iterable[Path],
) -> dict:
    files, tables = load_sources(source_paths)
    return {
        "schema_version": "BALANCE_PEUCEDANUM_RAW_SOURCE_INVENTORY_V1",
        "status": "SOURCE_BYTES_INVENTORIED_SEMANTIC_MAPPING_NOT_APPLIED",
        "files": files,
        "tables": inventory_tables(tables),
        "semantic_mapping_applied": False,
        "claim_ceiling": "source_inventory_only_no_biological_result",
    }


def _source_registry(mapping: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    if mapping.get("schema_version") != MAPPING_SCHEMA:
        raise ValueError("Peucedanum semantic mapping schema mismatch")
    if mapping.get("status") != MAPPING_READY_STATUS:
        raise ValueError(
            "Peucedanum semantic mapping must be SOURCE_VERIFIED_MAPPING before normalization"
        )
    sources = mapping.get("registered_sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Peucedanum mapping requires registered_sources")

    out: dict[str, Mapping[str, object]] = {}
    for source in sources:
        if not isinstance(source, Mapping):
            raise ValueError("registered source must be an object")
        doi = str(source.get("source_doi") or "").strip()
        if not doi or doi in out:
            raise ValueError("registered source DOI must be non-empty and unique")
        out[doi] = source
    return out


def _mapping_entries(mapping: Mapping[str, object]) -> list[dict]:
    sources = _source_registry(mapping)
    entries = []
    for doi, source in sources.items():
        raw_entries = source.get("sheet_mappings")
        if not isinstance(raw_entries, list) or not raw_entries:
            raise ValueError(
                f"registered source {doi!r} has no source-verified sheet_mappings"
            )
        for raw_entry in raw_entries:
            if not isinstance(raw_entry, Mapping):
                raise ValueError("sheet mapping must be an object")
            entry = dict(raw_entry)
            entry["source_doi"] = doi
            entries.append(entry)
    if not entries:
        raise ValueError("Peucedanum mapping contains no sheet mappings")
    return entries


def _header_index(header: list[str]) -> dict[str, int]:
    names = [name.strip() for name in header]
    if not names or any(not name for name in names):
        raise ValueError("mapped source header must not contain blank columns")
    if len(names) != len(set(names)):
        raise ValueError("mapped source header columns must be unique")
    return {name: i for i, name in enumerate(names)}


def _derive_registered_fields(row: dict[str, str]) -> None:
    def number(field: str) -> Decimal | None:
        value = row.get(field, "")
        if value == "":
            return None
        try:
            out = Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"mapped {field} is not numeric") from exc
        if not out.is_finite():
            raise ValueError(f"mapped {field} is not finite")
        return out

    perfect = number("perfect_flower_count")
    male = number("male_flower_count")
    if perfect is not None and male is not None:
        total = perfect + male
        if not total.is_finite() or total <= 0:
            raise ValueError("mapped flower counts produce invalid total")
        row["total_flower_count"] = str(total.normalize())
        row["male_fraction"] = format(male / total, ".15g")

    intact = number("intact_fruit_count")
    if intact is not None and perfect is not None and perfect > 0:
        row["final_fruit_set_rate"] = format(intact / perfect, ".15g")


def normalize_from_mapping(
    tables: Mapping[tuple[str, str], Iterable[Iterable[object]]],
    mapping: Mapping[str, object],
) -> list[dict[str, str]]:
    """Apply only explicit source-verified mappings, then validate normalized rows."""
    entries = _mapping_entries(mapping)
    normalized: list[dict[str, str]] = []

    for entry in entries:
        dataset_id = str(entry.get("dataset_id") or "").strip()
        source_doi = str(entry["source_doi"]).strip()
        source_file = str(entry.get("source_file") or "").strip()
        source_sheet = str(entry.get("source_sheet") or "").strip()
        header_row = entry.get("header_row")
        columns = entry.get("columns")
        constants = entry.get("constants", {})

        if not dataset_id:
            raise ValueError("sheet mapping requires dataset_id")
        if not source_file or not source_sheet:
            raise ValueError("sheet mapping requires source_file and source_sheet")
        if isinstance(header_row, bool) or not isinstance(header_row, int) or header_row < 1:
            raise ValueError("sheet mapping header_row must be a positive integer")
        if not isinstance(columns, Mapping) or not columns:
            raise ValueError("sheet mapping requires explicit columns")
        if not isinstance(constants, Mapping):
            raise ValueError("sheet mapping constants must be an object")

        key = (source_file, source_sheet)
        if key not in tables:
            raise ValueError(f"mapped source table not loaded: {key!r}")
        matrix = _trim_matrix(tables[key])
        if header_row > len(matrix):
            raise ValueError(f"mapped header row exceeds source table: {key!r}")

        header = matrix[header_row - 1]
        index = _header_index(header)

        field_sources: dict[str, int] = {}
        for normalized_field, source_column in columns.items():
            normalized_field = str(normalized_field)
            source_column = str(source_column)
            if normalized_field not in NORMALIZED_FIELDS:
                raise ValueError(
                    f"unsupported normalized field {normalized_field!r}"
                )
            if normalized_field in {
                "dataset_id",
                "source_doi",
                "source_file",
                "source_sheet",
                "source_row_number",
            } | DERIVED_FIELDS:
                raise ValueError(
                    f"field {normalized_field!r} is provenance/derived and cannot be mapped"
                )
            if source_column not in index:
                raise ValueError(
                    f"mapped source column {source_column!r} not found in {key!r}"
                )
            field_sources[normalized_field] = index[source_column]

        constant_values = {
            str(field): _plain_text(value)
            for field, value in constants.items()
        }
        if any(field not in NORMALIZED_FIELDS for field in constant_values):
            raise ValueError("sheet mapping contains unsupported constant field")
        if any(field in DERIVED_FIELDS for field in constant_values):
            raise ValueError("derived normalized fields cannot be supplied as constants")
        overlap = set(field_sources) & set(constant_values)
        if overlap:
            raise ValueError(
                "normalized fields cannot be supplied by both column and constant: "
                + ", ".join(sorted(overlap))
            )

        provided = set(field_sources) | set(constant_values) | {
            "dataset_id",
            "source_doi",
        }
        missing_required = [
            field for field in REQUIRED_NORMALIZED_FIELDS if field not in provided
        ]
        if missing_required:
            raise ValueError(
                f"mapping {dataset_id!r} lacks required normalized fields: "
                + ", ".join(missing_required)
            )

        for row_index, raw_row in enumerate(matrix[header_row:], start=header_row + 1):
            if not any(cell != "" for cell in raw_row):
                continue
            padded = raw_row + [""] * (len(header) - len(raw_row))
            if len(padded) > len(header):
                raise ValueError(f"source row {row_index} exceeds mapped header width")

            row = {field: "" for field in NORMALIZED_FIELDS}
            row.update({
                "dataset_id": dataset_id,
                "source_doi": source_doi,
                "source_file": source_file,
                "source_sheet": source_sheet,
                "source_row_number": str(row_index),
            })
            row.update(constant_values)
            for field, col_index in field_sources.items():
                row[field] = padded[col_index]
            _derive_registered_fields(row)
            normalized.append(row)

    if not normalized:
        raise ValueError("source-verified mapping produced no normalized rows")
    validate_normalized_rows(normalized)
    return normalized


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def inventory_peucedanum_sources(
    source_paths: Iterable[Path],
    out_dir: Path,
) -> dict:
    """Write an immutable R0 byte/table inventory without semantic mapping."""
    if out_dir.exists():
        raise ValueError("Peucedanum inventory output directory already exists")
    receipt = build_source_inventory_receipt(source_paths)
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.tmp-", dir=out_dir.parent))
    try:
        (tmp / INVENTORY_RECEIPT_BASENAME).write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp, out_dir)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return receipt


def normalize_peucedanum_sources(
    source_paths: Iterable[Path],
    mapping_path: Path,
    out_dir: Path,
) -> dict:
    """Normalize source rows only from a reviewed mapping contract."""
    if out_dir.exists():
        raise ValueError("Peucedanum normalization output directory already exists")
    source_paths = list(source_paths)
    files, tables = load_sources(source_paths)
    mapping_raw = mapping_path.read_bytes()
    mapping = json.loads(mapping_raw.decode("utf-8"))
    rows = normalize_from_mapping(tables, mapping)
    inventory = inventory_tables(tables)

    receipt = {
        "schema_version": "BALANCE_PEUCEDANUM_NORMALIZATION_RECEIPT_V1",
        "status": "SOURCE_VERIFIED_MAPPING_APPLIED",
        "mapping_file": mapping_path.name,
        "mapping_sha256": _sha256_bytes(mapping_raw),
        "source_files": files,
        "source_tables": inventory,
        "normalized_rows": len(rows),
        "normalized_output": NORMALIZED_ROWS_BASENAME,
        "next_gate": "reproduce_published_2025_source_models_before_new_criticality",
        "claim_ceiling": "normalized_raw_rows_only_no_criticality_result",
    }

    out_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.tmp-", dir=out_dir.parent))
    try:
        _write_csv(tmp / NORMALIZED_ROWS_BASENAME, rows)
        (tmp / NORMALIZATION_RECEIPT_BASENAME).write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp, out_dir)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return receipt

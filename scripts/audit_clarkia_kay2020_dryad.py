"""Dryad Kay-2020 source-file retrieval and *accessibility* audit.

This never estimates a Clarkia effect. It verifies archive provenance and the
presence/absence of raw inputs. Raw bytes, if retrievable, stay in the CI temp
directory; the output contains only SHA256, row counts and column names.

No credentials are requested or invented. Public Dryad API requests can return
401/403, which are explicit HOLD results, not fabricated successful retrieval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "BALANCE_CLARKIA_KAY2020_DRYAD_RECEIPT_V1.json"
API = "https://datadryad.org/api/v2/files/"
MAX_FILE_BYTES = 500_000
CROSS_EXPERIMENT_LINK_FORBIDDEN = True


def read_receipt(path: Path = SOURCE) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "BALANCE_CLARKIA_KAY2020_DRYAD_RECEIPT_V1":
        raise ValueError("Unexpected original-archive evidence contract")
    dryad = data["dryad"]
    if dryad["doi"] != "10.5061/dryad.8cz8w9gmp":
        raise ValueError("Wrong source study DOI")
    files = dryad["files"]
    if len(files) != 10 or len({f["filename"] for f in files}) != len(files):
        raise ValueError("Source file roster not complete or contains duplicates")
    missing = [f for f in files if not f["listed"]]
    if [(f["filename"], f["file_id"]) for f in missing] != [
        ("BombusTrials2018.csv", None)
    ]:
        raise ValueError("Missing-input gate was silently changed")
    for item in files:
        if item["listed"] and (not isinstance(item["file_id"], int) or item["file_id"] <= 0):
            raise ValueError("Every listed source file needs verified file ID")
    return data


def verify_file_bytes(filename: str, raw: bytes) -> dict:
    if not isinstance(raw, bytes) or len(raw) < 4 or len(raw) > MAX_FILE_BYTES:
        raise ValueError("Empty, invalid or excessively large Dryad file")
    start = raw[:1024].lstrip().lower()
    if b"<html" in start or b"<!doctype html" in start or start.startswith(b"{\"error\""):
        raise ValueError("Refusing HTML/JSON error content as raw published data")
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError as err:
        raise ValueError("Expected UTF-8 source text") from err
    descriptor = {
        "name": filename,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "columns": [],
        "rows": None,
        "status": "DOWNLOADED_METADATA_VERIFIED_ONLY",
    }
    if filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(decoded))
        cols = reader.fieldnames
        if not cols or len(cols) != len(set(cols)) or any(not x.strip() for x in cols):
            raise ValueError("CSV lacks unique, nonblank columns")
        count = 0
        for row in reader:
            if None in row or None in row.values():
                raise ValueError("Source CSV has malformed ragged rows")
            count += 1
        if count == 0:
            raise ValueError("No data rows in published CSV")
        descriptor["columns"] = cols
        descriptor["rows"] = count
    elif filename.endswith((".R", ".txt")):
        descriptor["lines"] = len(decoded.splitlines())
    else:
        raise ValueError("Unsupported download file type")
    return descriptor


def default_downloader(file_id: int) -> bytes:
    """Attempt the two public Dryad URL forms, without credential escalation.

    The API URL may require OAuth on public files. The public website's
    file_stream URL is an alternative user-facing download route, but may
    independently return HTTP 403. Both fail closed if access is denied.
    """
    urls = [
        f"{API}{file_id}/download",
        f"https://datadryad.org/downloads/file_stream/{file_id}",
    ]
    errors = []
    for url in urls:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "BALANCE-Kay2020-open-data-audit/1.0", "Accept": "*/*"},
        )
        try:
            with urllib.request.urlopen(request, timeout=18) as result:
                return result.read(MAX_FILE_BYTES + 1)
        except urllib.error.HTTPError as err:
            errors.append(f"HTTP_{err.code}")
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            errors.append(type(err).__name__)
    raise ValueError("TWO_PUBLIC_DRYAD_ENDPOINTS_FAILED: " + "/".join(errors))


def audit_source_retrieval(
    receipt: dict,
    *,
    download: bool = False,
    fetcher=None,
) -> dict:
    items = []
    retrieved = {}
    if fetcher is None:
        fetcher = default_downloader
    for item in receipt["dryad"]["files"]:
        name = item["filename"]
        if not item["listed"]:
            items.append({"filename": name, "status": "MISSING_FROM_PUBLISHED_FILE_LIST"})
            continue
        if not download:
            items.append({"filename": name, "status": "NOT_ATTEMPTED_OFFLINE"})
            continue
        try:
            raw = fetcher(item["file_id"])
            item_info = verify_file_bytes(name, raw)
            if item_info["status"] != "DOWNLOADED_METADATA_VERIFIED_ONLY":
                raise ValueError("Internal source byte status mismatch")
            retrieved[name] = item_info
            items.append({"filename": name, "status": "DOWNLOADED_METADATA_VERIFIED_ONLY",
                          "sha256": item_info["sha256"], "rows": item_info["rows"],
                          "columns": item_info["columns"], "bytes": item_info["bytes"]})
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as err:
            status = "DOWNLOAD_FAILED_HOLD"
            if isinstance(err, urllib.error.HTTPError):
                status = f"HTTP_{err.code}_DOWNLOAD_HOLD"
            items.append({"filename": name, "status": status,
                          "error_type": type(err).__name__})
    present = set(retrieved)
    field_pair = {"CungManipulative.csv", "CungSeeds.csv"}
    greenhouse_pair = {"BombusTrials2018.R", "BombusTrials2018.csv"}
    return {
        "analysis": "BALANCE_CLARKIA_KAY2020_PUBLIC_SOURCE_ACCESSIBILITY_AUDIT",
        "dryad_doi": receipt["dryad"]["doi"],
        "independent_original_programmes": 1,
        "files": items,
        "datafiles_accessed": sorted(present),
        "field_visit_and_seed_files_retrievable": field_pair.issubset(present),
        "field_visit_to_seed_focal_flower_join_identified": False,
        "field_join_rule": "Requires inspection of actual FieldManipulationsCung.R and validated flower or patch keys; never join on treatment alone",
        "greenhouse_export_original_raw_csv_retrievable": greenhouse_pair.issubset(present),
        "greenhouse_export_status": (
            "HOLD_CRITICAL_ORIGINAL_CSV_NOT_LISTED_BY_DRYAD_VERSION"
            if "BombusTrials2018.csv" not in present
            else "SOURCE_BYTES_PRESENT_NOT_YET_REANALYSED"
        ),
        "experiment_year_cross_join": "PROHIBITED",
        "raw_observation_effect_refits_performed": 0,
        "direct_paternity_outcomes_verified": 0,
        "v4_architecture_or_phylogenetic_effects_inferred": False,
        "claim_ceiling": "source_access_and_schema_only_not_effect_or_male_fitness",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = audit_source_retrieval(read_receipt(), download=args.download)
    output = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
    print(output)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Retrieve and verify the exact small public 2013 Dryad dataset ZIP.

Only allow the registered Dryad version and single source workbook already
verified in the API receipt. Do not interpret workbook variables or model
ecological outcomes here. Fail closed on oversized, altered or unsafe ZIPs.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import urllib.error
import urllib.request
import zipfile

EXPECTED_DOI = "10.5061/dryad.6cv06"
EXPECTED_VERSION_ID = 11193
EXPECTED_FILE = "raw data.xlsx"
EXPECTED_SIZE = 89597
EXPECTED_MD5 = "10a98383677bbd2a01e19a86c350fdd3"
MAX_ZIP_BYTES = 4_000_000
MAX_EXPANDED_BYTES = 2_000_000
VERSION_ZIP_URL = f"https://datadryad.org/api/v2/versions/{EXPECTED_VERSION_ID}/download"


def verify_zip(content: bytes) -> dict:
    if not isinstance(content, bytes) or len(content) > MAX_ZIP_BYTES:
        raise ValueError("source ZIP invalid size or datatype")
    try:
        with zipfile.ZipFile(io.BytesIO(content), "r") as archive:
            files = [f for f in archive.infolist() if not f.is_dir()]
            if len(files) != 1:
                raise ValueError("expected exactly one public Dryad source workbook")
            f = files[0]
            if (f.filename != EXPECTED_FILE or f.file_size != EXPECTED_SIZE
                    or f.flag_bits & 0x1 or f.file_size > MAX_EXPANDED_BYTES):
                raise ValueError("source ZIP path, size or encryption changed")
            if f.filename.startswith("/") or ".." in Path(f.filename).parts:
                raise ValueError("unsafe ZIP member path")
            data = archive.read(f, pwd=None)
    except (zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError("source ZIP unreadable") from exc
    md5 = hashlib.md5(data).hexdigest()
    if md5 != EXPECTED_MD5:
        raise ValueError("source workbook digest mismatches Dryad manifest")
    if not data.startswith(b"PK\x03\x04"):
        raise ValueError("source workbook lacks XLSX zip signature")
    return {
        "schema_version": "PEDICULARIS_2013_DRYAD_RAW_BYTE_RECEIPT_V1",
        "status": "EXACT_RAW_WORKBOOK_BYTES_VERIFIED_NOT_ANALYSED",
        "archive_doi": EXPECTED_DOI,
        "version_id": EXPECTED_VERSION_ID,
        "version_url": VERSION_ZIP_URL,
        "source_filename": EXPECTED_FILE,
        "source_size_bytes": len(data),
        "source_md5": md5,
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "version_zip_sha256": hashlib.sha256(content).hexdigest(),
        "version_zip_bytes": len(content),
        "raw_workbook_downloaded": True,
        "raw_rows_interpreted": False,
        "independent_density_result": False,
        "claim_ceiling": "source_bytes_only_no_semantic_variables_or_Allee_effect",
    }


def retrieve(receipt_path: Path, out_zip: Path, out_json: Path):
    if out_zip.exists() or out_json.exists():
        raise ValueError("refusing to overwrite source bytes or raw receipt")
    metadata = json.loads(receipt_path.read_text(encoding="utf-8"))
    if (metadata.get("status") != "DRYAD_METADATA_AND_FILE_MANIFEST_VERIFIED"
            or metadata.get("declared_repository_doi") != EXPECTED_DOI
            or metadata.get("version_id") != EXPECTED_VERSION_ID):
        raise ValueError("Dryad metadata and version not verified")
    files = metadata.get("source_file_manifest")
    if not isinstance(files, list) or len(files) != 1:
        raise ValueError("unexpected Dryad source manifest")
    if (files[0].get("path") != EXPECTED_FILE
            or files[0].get("size_bytes") != EXPECTED_SIZE
            or files[0].get("digest") != EXPECTED_MD5
            or files[0].get("digest_type") != "md5"):
        raise ValueError("source manifest changed")
    request = urllib.request.Request(
        VERSION_ZIP_URL, headers={"User-Agent":"balance-dryad-source-audit/1.0"}
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        advertised = response.headers.get("Content-Length")
        if advertised is not None and int(advertised) > MAX_ZIP_BYTES:
            raise ValueError("Dryad version archive exceeds registered limit")
        source_zip = response.read(MAX_ZIP_BYTES+1)
        if len(source_zip) > MAX_ZIP_BYTES:
            raise ValueError("Dryad version download exceeds safety size")
    result = verify_zip(source_zip)
    result["metadata_receipt_sha256"] = hashlib.sha256(
        receipt_path.read_bytes()).hexdigest()
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    # Output paths have already been checked for existence.
    out_zip.write_bytes(source_zip)
    out_json.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",
                        encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out-zip", required=True, type=Path)
    parser.add_argument("--out-receipt", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = retrieve(args.metadata,args.out_zip,args.out_receipt)
        print(json.dumps({
            "status": report["status"], "source_sha256": report["source_sha256"],
            "version_zip_sha256": report["version_zip_sha256"],
            "source_size_bytes": report["source_size_bytes"],
            "raw_rows_interpreted": report["raw_rows_interpreted"],
        },sort_keys=True))
    except (ValueError, urllib.error.HTTPError, urllib.error.URLError,
            TimeoutError) as exc:
        # A source download failure is not a scientific NO_RESULT.
        hold = {"schema_version":"PEDICULARIS_2013_DRYAD_RAW_BYTE_RECEIPT_V1",
                "status":"SOURCE_BYTES_DOWNLOAD_HOLD",
                "source_expected": EXPECTED_FILE,
                "error_type": type(exc).__name__, "error":str(exc)[:240],
                "raw_workbook_downloaded":False,"raw_rows_interpreted":False}
        args.out_receipt.parent.mkdir(parents=True,exist_ok=True)
        args.out_receipt.write_text(json.dumps(hold,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(hold,sort_keys=True))


if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Recover immutable original Pélabon 2015 Dryad text files, fail closed.

All remote requests use the official archived Dryad version or original file
IDs, with fixed digest/size checks before any biological rows are inspected.
Network/access failures emit a non-biological DOWNLOAD_HOLD receipt. Authenticated
bytes are never repaired or replaced with synthetic test fixtures.

The resulting source-support receipt is NOT a fitted mixed-effect model or a
bract-carbon causal mechanism claim.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import csv
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
import urllib.error
import urllib.request
import zipfile

from balance_domain.dalechampia_method_scope import (
    FILE_IDENTITIES, audit_dalechampia_method_scope, verify_exact_dryad_bytes,
)

SCHEMA = "DALECHAMPIA_2015_ORIGINAL_DRYAD_RECOVERY_V1"
SOURCE_ZIP_URL = "https://datadryad.org/api/v2/versions/11209/download"
PER_FILE_URLS = (
    "https://datadryad.org/downloads/file_stream/{file_id}",
    "https://datadryad.org/api/v2/files/{file_id}/download",
)
MAX_RESPONSE_BYTES = 4_000_000
MAX_MEMBER_BYTES = 200_000


def _digest_ok(name: str, data: bytes) -> bool:
    for expected_name, size, md5 in FILE_IDENTITIES.values():
        if expected_name == name:
            return len(data) == size and hashlib.md5(data).hexdigest() == md5
    return False


def _read_limited(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "balance-dalechampia-original-dryad/1.0",
            "Accept": "application/zip,application/octet-stream,text/plain",
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        claimed_length = response.headers.get("Content-Length")
        if claimed_length is not None and int(claimed_length) > MAX_RESPONSE_BYTES:
            raise ValueError("original Dryad response exceeds upper size bound")
        content = response.read(MAX_RESPONSE_BYTES + 1)
    if len(content) > MAX_RESPONSE_BYTES:
        raise ValueError("original Dryad response exceeded safe byte bound")
    return content


def _verify_version_zip(content: bytes) -> dict[str, bytes]:
    """Accept only the two published files in an ordinary safe ZIP archive."""
    if not isinstance(content, bytes) or len(content) > MAX_RESPONSE_BYTES:
        raise ValueError("version ZIP is not a bounded byte buffer")
    files: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(io.BytesIO(content), "r") as archive:
            members = [x for x in archive.infolist() if not x.is_dir()]
            if len(members) != 2:
                raise ValueError("Dryad source ZIP must contain exactly two files")
            for member in members:
                parts = PurePosixPath(member.filename).parts
                if (member.filename.startswith("/") or "\\" in member.filename
                        or not parts or any(x in {".", ".."} for x in parts)
                        or member.flag_bits & 1 or member.file_size > MAX_MEMBER_BYTES):
                    raise ValueError("unsafe Dryad source ZIP member")
                name = parts[-1]
                if name in files or name not in {
                    x[0] for x in FILE_IDENTITIES.values()
                }:
                    raise ValueError("unexpected or duplicate original Dryad file")
                expected = next(x for x in FILE_IDENTITIES.values() if x[0] == name)
                if member.file_size != expected[1]:
                    raise ValueError("original Dryad member size changed")
                raw = archive.read(member)
                if not _digest_ok(name, raw):
                    raise ValueError("original Dryad member MD5 changed")
                files[name] = raw
    except (zipfile.BadZipFile, OSError, EOFError, RuntimeError) as exc:
        raise ValueError("Dryad version ZIP unreadable") from exc
    if set(files) != {x[0] for x in FILE_IDENTITIES.values()}:
        raise ValueError("Dryad version ZIP missing registered source files")
    return files


def _verified_individual(download) -> dict[str, bytes]:
    """Only accept an all-files match for one official endpoint family."""
    failure = None
    for template in PER_FILE_URLS:
        payloads = {}
        try:
            for file_id, (name, _, _) in FILE_IDENTITIES.items():
                payload = download(template.format(file_id=file_id))
                if not _digest_ok(name, payload):
                    raise ValueError("individual Dryad original file size/MD5 mismatch")
                payloads[name] = payload
            return payloads
        except (ValueError, urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, OSError) as exc:
            failure = type(exc).__name__
    raise ValueError(f"original individual-file recovery unavailable: {failure}")


def recover_original_pair(download=_read_limited) -> tuple[dict[str, bytes], str]:
    """Attempt the version archive first, then only official individual URLs."""
    try:
        zip_bytes = download(SOURCE_ZIP_URL)
        return _verify_version_zip(zip_bytes), "ARCHIVED_VERSION_ZIP"
    except (ValueError, urllib.error.HTTPError, urllib.error.URLError,
            TimeoutError, OSError, zipfile.BadZipFile):
        pass
    return _verified_individual(download), "OFFICIAL_FILE_DOWNLOADS"


def _atomic_json(path: Path, document: dict) -> None:
    if path.exists():
        raise ValueError("refusing to overwrite existing source recovery receipt")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False,
        prefix=".dalechampia-recovery-", suffix=".tmp",
    ) as writer:
        tmp = Path(writer.name)
        json.dump(document, writer, indent=2, sort_keys=True)
        writer.write("\n")
    try:
        # Caller has already checked output path; avoid clobbering if it moved.
        with tmp.open("rb") as read, path.open("xb") as out:
            out.write(read.read())
    finally:
        tmp.unlink(missing_ok=True)


def retrieve(
    contract_path: Path, source_dir: Path, out_receipt: Path,
    *, download=_read_limited,
) -> dict:
    """Write source files only once fully MD5-verified, no artificial success."""
    if out_receipt.exists():
        raise ValueError("source recovery receipt already exists")
    names = [x[0] for x in FILE_IDENTITIES.values()]
    if any((source_dir / name).exists() for name in names):
        raise ValueError("refusing to overwrite original downloaded Dryad files")
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    audit_dalechampia_method_scope(contract)
    base = {
        "schema_version": SCHEMA,
        "dataset_doi": "10.5061/dryad.nb675",
        "archived_version_id": 11209,
        "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "is_original_mixed_model_replay": False,
        "bract_local_carbon_causally_identified": False,
        "structural_BALANCE_identified": False,
    }
    try:
        files, method = recover_original_pair(download)
    except (ValueError, urllib.error.HTTPError, urllib.error.URLError,
            TimeoutError, OSError) as exc:
        hold = {
            **base,
            "status": "ORIGINAL_SOURCE_DOWNLOAD_HOLD",
            "raw_file_bytes_verified": False,
            "raw_reanalysis_executed": False,
            "failure_type": type(exc).__name__,
            "error_summary": str(exc)[:160],
        }
        _atomic_json(out_receipt, hold)
        return hold

    if set(files) != set(names) or any(not _digest_ok(k, v) for k, v in files.items()):
        raise ValueError("download result did not meet two-file source identity contract")
    # Even when parser fails, preserve authenticated bytes for later independent
    # source-row review. This does not imply any fitted ecological result.
    try:
        parsed = verify_exact_dryad_bytes(contract, files)
        status = "ORIGINAL_DRYAD_BYTES_AND_ROW_SUPPORT_VERIFIED_NO_MODEL"
        issue = None
    except (ValueError, UnicodeError, csv.Error) as exc:
        parsed = None
        status = "ORIGINAL_DRYAD_BYTES_VERIFIED_PARSER_HOLD"
        issue = {"type": type(exc).__name__, "detail": str(exc)[:160]}
    source_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        with (source_dir / name).open("xb") as sink:
            sink.write(files[name])
    receipt = {
        **base,
        "status": status,
        "source_route": method,
        "raw_file_bytes_verified": True,
        "source_file_sha256": {
            name: hashlib.sha256(files[name]).hexdigest() for name in names
        },
        "row_support": parsed,
        "parser_hold": issue,
        "raw_reanalysis_executed": False,
    }
    _atomic_json(out_receipt, receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path,
        default=Path(__file__).resolve().parents[1] /
        "data/DALECHAMPIA_POSTANTHESIS_METHOD_AND_DRYAD_V2.json")
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = retrieve(args.contract, args.source_dir, args.out)
    print(json.dumps({
        "status": result["status"],
        "raw_file_bytes_verified": result["raw_file_bytes_verified"],
        "raw_reanalysis_executed": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

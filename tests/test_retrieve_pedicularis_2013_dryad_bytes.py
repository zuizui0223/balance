"""Synthetic ZIP-only tests; not evidence of obtaining Dryad raw data."""
import hashlib
import io
import zipfile

import pytest

import scripts.retrieve_pedicularis_2013_dryad_bytes as download


def make_archive(path=download.EXPECTED_FILE, payload=b"PK\x03\x04fake-xlsx-bytes"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as handle:
        handle.writestr(path, payload)
    return buffer.getvalue(), payload


def test_exact_manifest_check_pass_never_promotes_raw_rows(monkeypatch):
    data, payload = make_archive()
    monkeypatch.setattr(download, "EXPECTED_SIZE", len(payload))
    monkeypatch.setattr(download, "EXPECTED_MD5", hashlib.md5(payload).hexdigest())
    report = download.verify_zip(data)
    assert report["status"] == "EXACT_RAW_WORKBOOK_BYTES_VERIFIED_NOT_ANALYSED"
    assert report["source_sha256"] == hashlib.sha256(payload).hexdigest()
    assert report["raw_rows_interpreted"] is False
    assert report["independent_density_result"] is False


def test_corrupt_member_digest_rejected():
    data, payload = make_archive()
    with pytest.raises(ValueError, match="path, size"):
        download.verify_zip(data)


def test_traversal_and_multiple_members_rejected(monkeypatch):
    payload = b"PK\x03\x04small"
    monkeypatch.setattr(download, "EXPECTED_SIZE", len(payload))
    monkeypatch.setattr(download, "EXPECTED_MD5", hashlib.md5(payload).hexdigest())
    data, _ = make_archive("../" + download.EXPECTED_FILE, payload)
    with pytest.raises(ValueError, match="path"):
        download.verify_zip(data)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr(download.EXPECTED_FILE, payload)
        z.writestr("extraneous.txt", "unknown")
    with pytest.raises(ValueError, match="exactly one"):
        download.verify_zip(buffer.getvalue())


def test_non_excel_inner_bytes_rejected(monkeypatch):
    payload = b"not-an-excel-archive"
    monkeypatch.setattr(download, "EXPECTED_SIZE", len(payload))
    monkeypatch.setattr(download, "EXPECTED_MD5", hashlib.md5(payload).hexdigest())
    data, _ = make_archive(download.EXPECTED_FILE, payload)
    with pytest.raises(ValueError, match="XLSX zip signature"):
        download.verify_zip(data)

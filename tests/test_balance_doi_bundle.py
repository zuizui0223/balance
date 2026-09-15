from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from scripts.build_balance_doi_bundle import (
    MANIFEST_PATH,
    build_bundle,
    bundle_files,
    validate_release_contract,
)


def test_doi_release_contract_keeps_claim_ceiling_closed() -> None:
    receipt = validate_release_contract()
    assert receipt["all_contract_checks_pass"] is True
    assert receipt["publication_status"] == "DOI_TECHNICAL_MODULE_SUPPORTING_SLK"
    assert receipt["active_publication_queue"] is False
    assert receipt["pattern_independent_clusters"] == 17
    assert receipt["middle_regime_signature_clusters"] == 9
    assert receipt["direct_matched_worldline_receipts"] == 0
    assert "no direct matched BALANCE worldline occupancy" in receipt["claim_ceiling"]


def test_doi_bundle_inventory_is_explicit_and_excludes_generated_outputs() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = bundle_files()
    names = {path.as_posix() for path in files}
    assert "release/BALANCE_DOI_MODULE_MANIFEST_V1.json" in names
    assert "docs/BALANCE_TECHNICAL_MODULE_V1.md" in names
    assert "docs/ZENODO_RELEASE_CHECKLIST_V1.md" in names
    for rel in manifest["primary_theory_anchors"]:
        assert rel in names
    for rel in manifest["primary_empirical_anchors"]:
        assert rel in names
    for rel in manifest["primary_figures"]:
        assert rel in names
    assert all(not name.startswith("release/generated/") for name in names)
    assert all("/__pycache__/" not in f"/{name}" for name in names)
    assert all(not name.endswith(".pyc") for name in names)


def test_doi_bundle_is_self_verifying(tmp_path: Path) -> None:
    zip_path, receipt_path, sha_path = build_bundle(tmp_path)
    assert zip_path.exists()
    assert receipt_path.exists()
    assert sha_path.exists()

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["all_contract_checks_pass"] is True
    assert receipt["bundle_file_count"] == len(receipt["bundle_inventory"])
    assert receipt["bundle_file_count"] > 0

    expected_zip_hash = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert sha_path.read_text(encoding="utf-8") == (
        f"{expected_zip_hash}  {zip_path.name}\n"
    )

    with zipfile.ZipFile(zip_path) as archive:
        archive.testzip() is None
        names = set(archive.namelist())
        assert "RELEASE_RECEIPT.json" in names
        embedded = json.loads(archive.read("RELEASE_RECEIPT.json"))
        assert embedded == receipt
        for item in receipt["bundle_inventory"]:
            data = archive.read(item["path"])
            assert len(data) == item["bytes"]
            assert hashlib.sha256(data).hexdigest() == item["sha256"]

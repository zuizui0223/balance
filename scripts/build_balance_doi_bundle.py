#!/usr/bin/env python3
"""Build a self-verifying BALANCE DOI-module candidate bundle."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from balance_domain.pattern_ledger import build_pattern_readout, load_pattern_ledger  # noqa: E402
from assemble_balance_manuscript import build_manuscript  # noqa: E402

MANIFEST_PATH = ROOT / "release" / "BALANCE_DOI_MODULE_MANIFEST_V1.json"
STATUS_PATH = ROOT / "docs" / "PUBLICATION_STATUS.md"
CANONICAL_MANIFEST_PATH = ROOT / "manuscript" / "BALANCE_CANONICAL_MANUSCRIPT_MANIFEST_V1.json"
CANONICAL_MANUSCRIPT_PATH = ROOT / "manuscript" / "BALANCE_MANUSCRIPT_V1.md"
PATTERN_LEDGER = ROOT / "data" / "BALANCE_PATTERN_LEDGER_V1.csv"
PATTERN_READOUT = ROOT / "data" / "BALANCE_PATTERN_READOUT_V1.json"
DEFAULT_OUT_DIR = ROOT / "release" / "generated"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_head() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNAVAILABLE"


def load_release_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def validate_release_contract() -> dict[str, object]:
    release_manifest = load_release_manifest()
    status = STATUS_PATH.read_text(encoding="utf-8")
    if "STATUS = DOI_MODULE / DORMANT_PAPER_BRANCH" not in status:
        raise ValueError("publication status no longer freezes BALANCE as DOI module")
    if "ACTIVE_PUBLICATION_QUEUE = false" not in status:
        raise ValueError("publication status unexpectedly reactivated BALANCE")

    if release_manifest["publication_status"] != "DOI_TECHNICAL_MODULE_SUPPORTING_SLK":
        raise ValueError("release manifest has wrong programme role")
    if release_manifest["active_publication_queue"] is not False:
        raise ValueError("release manifest must keep active publication queue closed")

    canonical = json.loads(CANONICAL_MANIFEST_PATH.read_text(encoding="utf-8"))
    required_canonical = {
        "publication_status": "DORMANT_PAPER_BRANCH",
        "current_programme_role": "DOI_TECHNICAL_MODULE_SUPPORTING_SLK",
        "active_publication_queue": False,
        "direct_worldline_status": "0_direct_matched_receipts",
    }
    for key, expected in required_canonical.items():
        if canonical.get(key) != expected:
            raise ValueError(f"canonical manifest drift for {key}: {canonical.get(key)!r}")
    if "not_direct_BALANCE_worldline_occupancy" not in canonical.get("claim_ceiling", ""):
        raise ValueError("canonical claim ceiling no longer excludes direct BALANCE occupancy")

    assembled = build_manuscript()
    expected_assembled = {
        "sha256": canonical["expected_sha256"],
        "word_count": canonical["expected_word_count"],
        "line_count": canonical["expected_line_count"],
    }
    actual_assembled = {
        "sha256": _sha256_bytes(assembled.encode("utf-8")),
        "word_count": len(assembled.split()),
        "line_count": len(assembled.splitlines()),
    }
    if actual_assembled != expected_assembled:
        raise ValueError(
            f"canonical manuscript assembly drift: expected {expected_assembled}, got {actual_assembled}"
        )
    if CANONICAL_MANUSCRIPT_PATH.read_text(encoding="utf-8") != assembled:
        raise ValueError("saved canonical manuscript differs from deterministic assembly")

    rows = load_pattern_ledger(PATTERN_LEDGER)
    computed_readout = build_pattern_readout(PATTERN_LEDGER)
    frozen_readout = json.loads(PATTERN_READOUT.read_text(encoding="utf-8"))
    if computed_readout != frozen_readout:
        raise ValueError("pattern ledger/readout drift blocks DOI release")

    frozen = release_manifest["frozen_empirical_receipts"]
    if frozen_readout["n_independent_clusters"] != frozen["pattern_independent_clusters"]:
        raise ValueError("independent-cluster count drift")
    if frozen_readout["n_middle_regime_signature_clusters"] != frozen["middle_regime_signature_clusters"]:
        raise ValueError("middle-regime signature count drift")
    if frozen["direct_matched_worldline_receipts"] != 0:
        raise ValueError("release manifest incorrectly claims a direct worldline receipt")

    required_paths = (
        release_manifest["primary_theory_anchors"]
        + release_manifest["primary_empirical_anchors"]
        + release_manifest["primary_figures"]
        + [
            release_manifest["canonical_context"]["manuscript"],
            release_manifest["canonical_context"]["manifest"],
            "docs/BALANCE_TECHNICAL_MODULE_V1.md",
            "docs/PUBLICATION_STATUS.md",
        ]
    )
    missing = [rel for rel in required_paths if not (ROOT / rel).exists()]
    if missing:
        raise FileNotFoundError("missing release anchors: " + ", ".join(missing))

    return {
        "module_id": release_manifest["module_id"],
        "publication_status": release_manifest["publication_status"],
        "active_publication_queue": False,
        "claim_ceiling": release_manifest["claim_ceiling"],
        "git_head": _git_head(),
        "canonical_manuscript": actual_assembled,
        "pattern_records": len(rows),
        "pattern_independent_clusters": frozen_readout["n_independent_clusters"],
        "middle_regime_signature_clusters": frozen_readout[
            "n_middle_regime_signature_clusters"
        ],
        "direct_matched_worldline_receipts": 0,
        "external_deposition_metadata_required": release_manifest[
            "external_deposition_metadata_required"
        ],
        "all_contract_checks_pass": True,
    }


def _excluded(rel: Path) -> bool:
    posix = rel.as_posix()
    parts = rel.parts
    return (
        ".git" in parts
        or "__pycache__" in parts
        or ".pytest_cache" in parts
        or posix.startswith("release/generated/")
        or rel.suffix == ".pyc"
        or rel.name == ".DS_Store"
    )


def bundle_files() -> list[Path]:
    manifest = load_release_manifest()
    files: set[Path] = set()
    for entry in manifest["bundle_roots"]:
        path = ROOT / entry
        if not path.exists():
            raise FileNotFoundError(path)
        if path.is_file():
            rel = path.relative_to(ROOT)
            if not _excluded(rel):
                files.add(rel)
            continue
        for child in path.rglob("*"):
            if child.is_file():
                rel = child.relative_to(ROOT)
                if not _excluded(rel):
                    files.add(rel)
    return sorted(files, key=lambda p: p.as_posix())


def _zip_write_bytes(zf: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, data)


def build_bundle(out_dir: Path = DEFAULT_OUT_DIR) -> tuple[Path, Path, Path]:
    receipt = validate_release_contract()
    files = bundle_files()
    inventory = []
    for rel in files:
        data = (ROOT / rel).read_bytes()
        inventory.append(
            {
                "path": rel.as_posix(),
                "bytes": len(data),
                "sha256": _sha256_bytes(data),
            }
        )
    receipt["bundle_file_count"] = len(inventory)
    receipt["bundle_inventory"] = inventory

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "BALANCE_DOI_MODULE_V1.zip"
    receipt_path = out_dir / "BALANCE_DOI_MODULE_V1_RELEASE_RECEIPT.json"
    sha_path = out_dir / "BALANCE_DOI_MODULE_V1.sha256"

    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for item in inventory:
            rel = Path(item["path"])
            _zip_write_bytes(zf, rel.as_posix(), (ROOT / rel).read_bytes())
        _zip_write_bytes(zf, "RELEASE_RECEIPT.json", receipt_bytes)

    receipt_path.write_bytes(receipt_bytes)
    bundle_hash = _sha256_bytes(zip_path.read_bytes())
    sha_path.write_text(f"{bundle_hash}  {zip_path.name}\n", encoding="utf-8")
    print(zip_path)
    print(receipt_path)
    print(sha_path)
    return zip_path, receipt_path, sha_path


def main() -> None:
    build_bundle()


if __name__ == "__main__":
    main()

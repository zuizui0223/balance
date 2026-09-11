import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manuscript" / "BALANCE_CANONICAL_MANUSCRIPT_MANIFEST_V1.json"

sys.path.insert(0, str(ROOT / "scripts"))
assemble = importlib.import_module("assemble_balance_manuscript")


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def test_canonical_manifest_matches_assembled_manuscript():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    text = assemble.build_manuscript()
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == manifest["expected_sha256"]
    assert len(text.split()) == manifest["expected_word_count"]
    assert len(text.splitlines()) == manifest["expected_line_count"]


def test_section_blob_shas_are_frozen():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for section, meta in manifest["section_sources"].items():
        path = ROOT / meta["path"]
        assert path.exists(), section
        assert _git_blob_sha(path) == meta["blob_sha"], section


def test_canonical_figure_set_and_claim_ceiling_are_present():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["direct_worldline_status"] == "0_direct_matched_receipts"
    assert "not_direct_BALANCE_worldline_occupancy" in manifest["claim_ceiling"]
    for rel in manifest["figure_set"]:
        assert (ROOT / rel).exists(), rel

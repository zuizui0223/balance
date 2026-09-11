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
    assert "## Figure captions" in text
    assert "data/BALANCE_MANUSCRIPT_CITATION_LEDGER_V1.csv" in text
    assert "data/BALANCE_PATTERN_CLUSTER_CITATION_MAP_V1.csv" in text


def _assert_frozen_sources(group):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for label, meta in manifest[group].items():
        path = ROOT / meta["path"]
        assert path.exists(), label
        assert _git_blob_sha(path) == meta["blob_sha"], label


def test_section_blob_shas_are_frozen():
    _assert_frozen_sources("section_sources")


def test_caption_blob_shas_are_frozen():
    _assert_frozen_sources("caption_sources")


def test_canonical_figure_set_citation_provenance_and_claim_ceiling_are_present():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["direct_worldline_status"] == "0_direct_matched_receipts"
    assert "not_direct_BALANCE_worldline_occupancy" in manifest["claim_ceiling"]
    assert manifest["citation_provenance"]["pattern_cluster_coverage"] == "17_of_17"
    for key in ("study_ledger", "pattern_cluster_map"):
        assert (ROOT / manifest["citation_provenance"][key]).exists()
    for rel in manifest["figure_set"]:
        assert (ROOT / rel).exists(), rel

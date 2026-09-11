import importlib.util
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_balance_pattern_map_figure3.py"


def _module():
    spec = importlib.util.spec_from_file_location("balance_fig3", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_figure3_counts_match_frozen_pattern_readout():
    mod = _module()
    rows, clusters, counts = mod._load()
    assert len({c for c, _, _ in clusters}) == 17
    assert sum(1 for c, _, p in clusters if p in mod.MIDDLE) == 9
    assert sum(1 for c, _, p in clusters if p == "BOUNDARY_CROSSING") == 2
    assert sum(1 for c, _, p in clusters if p == "UNRESOLVED") == 5


def test_figure3_preserves_expected_domain_pattern_matrix():
    mod = _module()
    _, _, counts = mod._load()
    assert counts[("plant", "CONFLICT_WITHOUT_SPLITTING")] == 7
    assert counts[("plant", "SANDWICHED_TRANSITION_MOSAIC")] == 1
    assert counts[("plant", "BOUNDARY_CROSSING")] == 1
    assert counts[("plant", "UNRESOLVED")] == 3
    assert counts[("protein_function", "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE")] == 1
    assert counts[("protein_function", "UNRESOLVED")] == 1
    assert counts[("gene_regulatory_architecture", "DIRECT_DIFFERENTIATION")] == 1
    assert counts[("genome_architecture_ecological_strategy", "BOUNDARY_CROSSING")] == 1
    assert counts[("vertebrate_morphology", "UNRESOLVED")] == 1


def test_figure3_explicitly_prohibits_prevalence_interpretation():
    svg = _module().build_svg()
    assert "recurrence map, not an estimate of natural prevalence" in svg
    assert "17 independent clusters; 9 middle-regime signatures" in svg
    assert "do not estimate natural prevalence or direct BALANCE occupancy" in svg

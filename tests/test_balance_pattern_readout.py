import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_balance_pattern_readout.py"
LEDGER = ROOT / "data" / "BALANCE_PATTERN_LEDGER_V1.csv"
READOUT = ROOT / "data" / "BALANCE_PATTERN_READOUT_V1.json"


def _load_builder():
    spec = importlib.util.spec_from_file_location("balance_pattern_readout", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_registered_readout_matches_builder():
    builder = _load_builder()
    expected = json.loads(READOUT.read_text(encoding="utf-8"))
    assert builder.build(LEDGER) == expected


def test_pattern_expansion_does_not_promote_unresolved_clusters():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["n_independent_clusters"] == 9
    assert result["n_middle_regime_signature_clusters"] == 3
    assert result["n_conflict_without_splitting_clusters"] == 2
    assert result["n_sandwiched_transition_mosaic_clusters"] == 1
    assert result["n_unresolved_clusters"] == 6
    assert result["n_persistent_integration_with_alternative_clusters"] == 0
    assert result["n_boundary_crossing_clusters"] == 0
    assert result["n_hysteresis_clusters"] == 0
    assert result["n_direct_differentiation_boundary_clusters"] == 0
    assert result["n_quantitative_pool_eligible_clusters"] == 0


def test_cross_domain_rows_are_visible_but_not_counted_as_positive_middle_receipts():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["domain_counts"] == {
        "plant": 7,
        "protein_function": 1,
        "vertebrate_morphology": 1,
    }
    assert result["pattern_class_counts"]["UNRESOLVED"] == 6

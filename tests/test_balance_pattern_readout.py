import csv
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


def test_ledger_rows_have_exact_registered_schema():
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    assert reader.fieldnames is not None
    assert len(reader.fieldnames) == 15
    assert all(None not in row for row in rows)
    assert all(set(row) == set(reader.fieldnames) for row in rows)


def test_targeted_recovery_closes_two_empty_classes_without_overpromotion():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["n_independent_clusters"] == 11
    assert result["n_middle_regime_signature_clusters"] == 4
    assert result["n_conflict_without_splitting_clusters"] == 2
    assert result["n_sandwiched_transition_mosaic_clusters"] == 1
    assert result["n_persistent_integration_with_alternative_clusters"] == 1
    assert result["n_direct_differentiation_boundary_clusters"] == 1
    assert result["n_unresolved_clusters"] == 6
    assert result["n_boundary_crossing_clusters"] == 0
    assert result["n_hysteresis_clusters"] == 0
    assert result["n_quantitative_pool_eligible_clusters"] == 0


def test_cross_domain_counts_are_explicit():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["domain_counts"] == {
        "gene_regulatory_architecture": 1,
        "plant": 7,
        "protein_function": 2,
        "vertebrate_morphology": 1,
    }


def test_no_population_split_is_relabelled_as_within_architecture_boundary():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert "BOUNDARY_CROSSING" not in result["pattern_class_counts"]
    assert result["n_boundary_crossing_clusters"] == 0


def test_no_source_adjudication_is_mistaken_for_hysteresis_or_pooling():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["n_hysteresis_clusters"] == 0
    assert result["n_quantitative_pool_eligible_clusters"] == 0
    assert result["pattern_class_counts"]["UNRESOLVED"] == 6

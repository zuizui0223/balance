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


def _ledger_rows():
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def test_pattern_recovery_counts_include_new_adjudicated_boundaries():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["n_independent_clusters"] == 18
    assert result["n_records"] == 19
    assert result["n_middle_regime_signature_clusters"] == 9
    assert result["n_conflict_without_splitting_clusters"] == 7
    assert result["n_sandwiched_transition_mosaic_clusters"] == 1
    assert result["n_persistent_integration_with_alternative_clusters"] == 1
    assert result["n_boundary_crossing_clusters"] == 3
    assert result["n_direct_differentiation_boundary_clusters"] == 1
    assert result["n_unresolved_clusters"] == 5
    assert result["n_hysteresis_clusters"] == 1
    assert result["n_quantitative_pool_eligible_clusters"] == 0


def test_cross_domain_counts_are_explicit():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["domain_counts"] == {
        "gene_regulatory_architecture": 1,
        "genome_architecture_ecological_strategy": 1,
        "microbial_population": 1,
        "plant": 13,
        "protein_function": 2,
        "vertebrate_morphology": 1,
    }


def test_pedicularis_geographic_study_is_one_cluster_and_not_direct_balance():
    rows = _ledger_rows()
    ped = [row for row in rows if row["cluster_id"] == "Pedicularis_rex_geographic_conflict"]
    assert len(ped) == 1
    row = ped[0]
    assert row["pattern_class"] == "CONFLICT_WITHOUT_SPLITTING"
    assert row["confidence"] == "high"
    assert row["quantitative_pool_eligible"] == "false"
    assert "not_direct_BALANCE_occupancy" in row["claim_ceiling"]


def test_polemonium_is_upgraded_once_not_duplicated():
    rows = _ledger_rows()
    pole = [row for row in rows if row["system_taxon"] == "Polemonium viscosum"]
    assert len(pole) == 1
    row = pole[0]
    assert row["cluster_id"] == "Polemonium_viscosum_pollinator_ant_conflict"
    assert row["pattern_class"] == "CONFLICT_WITHOUT_SPLITTING"
    assert row["confidence"] == "high"
    assert row["quantitative_pool_eligible"] == "false"
    assert "not_direct_BALANCE_occupancy" in row["claim_ceiling"]


def test_primula_species_are_kept_as_distinct_evidence_objects():
    rows = {row["cluster_id"]: row for row in _ledger_rows()}
    farinosa = rows["Primula_farinosa_polymorphism"]
    veris = rows["Primula_veris_component_conflict"]
    assert farinosa["system_taxon"] == "Primula farinosa"
    assert farinosa["pattern_class"] == "UNRESOLVED"
    assert veris["system_taxon"] == "Primula veris"
    assert veris["pattern_class"] == "CONFLICT_WITHOUT_SPLITTING"
    assert veris["quantitative_pool_eligible"] == "false"
    assert "not_direct_pollinator_beta" in veris["claim_ceiling"]


def test_gymnadenia_and_fragaria_are_independent_factorial_patterns():
    rows = {row["cluster_id"]: row for row in _ledger_rows()}
    gym = rows["Gymnadenia_conopsea_pollinator_herbivore_conflict"]
    frag = rows["Fragaria_vesca_pollinator_herbivore_conflict"]
    assert gym["system_taxon"] == "Gymnadenia conopsea"
    assert frag["system_taxon"] == "Fragaria vesca"
    assert gym["pattern_class"] == "CONFLICT_WITHOUT_SPLITTING"
    assert frag["pattern_class"] == "CONFLICT_WITHOUT_SPLITTING"
    assert gym["quantitative_pool_eligible"] == "false"
    assert frag["quantitative_pool_eligible"] == "false"
    assert "diffuse_opposing_agent_selection" in frag["claim_ceiling"]


def test_boundary_classes_keep_architecture_and_selection_crossings_distinct():
    rows = _ledger_rows()
    cluster_ids = {row["cluster_id"] for row in rows}
    assert "Ecoli_alternating_carbon_strategy" not in cluster_ids
    boundary_ids = {
        row["cluster_id"] for row in rows if row["pattern_class"] == "BOUNDARY_CROSSING"
    }
    assert boundary_ids == {
        "Peucedanum_longitudinal_mosaic",
        "Solanum_heteranthery_repeated_origins",
        "Yeast_GAP1_PUT4_CNV_context",
    }
    peucedanum_boundary = [
        row
        for row in rows
        if row["cluster_id"] == "Peucedanum_longitudinal_mosaic"
        and row["pattern_class"] == "BOUNDARY_CROSSING"
    ]
    assert len(peucedanum_boundary) == 1
    assert "not_direct" in peucedanum_boundary[0]["claim_ceiling"]


def test_preprint_boundary_is_bounded_and_not_hysteresis():
    rows = {row["cluster_id"]: row for row in _ledger_rows()}
    yeast = rows["Yeast_GAP1_PUT4_CNV_context"]
    assert yeast["confidence"] == "moderate"
    assert yeast["quantitative_pool_eligible"] == "false"
    assert "preprint" in yeast["claim_ceiling"]
    assert yeast["pattern_class"] == "BOUNDARY_CROSSING"


def test_hysteresis_anchor_is_explicitly_cross_domain_not_balance_occupancy():
    rows = [row for row in _ledger_rows() if row["pattern_class"] == "HYSTERESIS_OR_PATH_DEPENDENCE"]
    assert len(rows) == 1
    row = rows[0]
    assert row["domain"] == "microbial_population"
    assert row["quantitative_pool_eligible"] == "false"
    assert "not_trait_architecture" in row["claim_ceiling"] or "not_BALANCE" in row["claim_ceiling"]


def test_no_quantitative_pooling_is_created_by_pattern_adjudication():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["n_quantitative_pool_eligible_clusters"] == 0
    assert result["pattern_class_counts"]["UNRESOLVED"] == 5

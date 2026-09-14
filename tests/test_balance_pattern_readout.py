import csv
import importlib.util
import json
from pathlib import Path

import pytest


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


def _write_ledger(path: Path, rows: list[dict[str, str]], *, drop: str | None = None):
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        fieldnames = list(csv.DictReader(handle).fieldnames or ())
    if drop is not None:
        fieldnames.remove(drop)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


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
    cluster_ids = [row["cluster_id"] for row in rows]
    assert len(cluster_ids) == len(set(cluster_ids))
    assert all(cluster_ids)


def test_builder_rejects_duplicate_or_missing_cluster_identity(tmp_path):
    builder = _load_builder()
    rows = _ledger_rows()

    duplicate = [dict(rows[0]), dict(rows[1])]
    duplicate[1]["cluster_id"] = duplicate[0]["cluster_id"]
    path = tmp_path / "duplicate.csv"
    _write_ledger(path, duplicate)
    with pytest.raises(ValueError, match="duplicate cluster_id"):
        builder.build(path)

    for bad in ("", "None", "null", "nan", "REQUIRED_BEFORE_USE"):
        malformed = [dict(rows[0])]
        malformed[0]["cluster_id"] = bad
        path = tmp_path / f"bad-{bad or 'empty'}.csv"
        _write_ledger(path, malformed)
        with pytest.raises(ValueError, match="cluster_id.*frozen"):
            builder.build(path)


def test_builder_requires_source_adjudication_columns_and_valid_pool_flag(tmp_path):
    builder = _load_builder()
    rows = _ledger_rows()

    missing_source = tmp_path / "missing-source.csv"
    _write_ledger(missing_source, [dict(rows[0])], drop="source_basis")
    with pytest.raises(ValueError, match="missing required columns: source_basis"):
        builder.build(missing_source)

    malformed = [dict(rows[0])]
    malformed[0]["quantitative_pool_eligible"] = "yes"
    bad_flag = tmp_path / "bad-flag.csv"
    _write_ledger(bad_flag, malformed)
    with pytest.raises(ValueError, match="literal true or false"):
        builder.build(bad_flag)


def test_builder_rejects_placeholder_source_or_claim_provenance(tmp_path):
    builder = _load_builder()
    rows = _ledger_rows()
    for field in ("source_id", "source_basis", "claim_ceiling"):
        malformed = [dict(rows[0])]
        malformed[0][field] = "REQUIRED_BEFORE_USE"
        path = tmp_path / f"bad-{field}.csv"
        _write_ledger(path, malformed)
        with pytest.raises(ValueError, match=f"{field}.*frozen"):
            builder.build(path)


def test_pattern_recovery_adds_fragaria_diffuse_conflict_without_false_pooling():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["n_independent_clusters"] == 17
    assert result["n_middle_regime_signature_clusters"] == 9
    assert result["n_conflict_without_splitting_clusters"] == 7
    assert result["n_sandwiched_transition_mosaic_clusters"] == 1
    assert result["n_persistent_integration_with_alternative_clusters"] == 1
    assert result["n_boundary_crossing_clusters"] == 2
    assert result["n_direct_differentiation_boundary_clusters"] == 1
    assert result["n_unresolved_clusters"] == 5
    assert result["n_hysteresis_clusters"] == 0
    assert result["n_quantitative_pool_eligible_clusters"] == 0


def test_cross_domain_counts_are_explicit():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["domain_counts"] == {
        "gene_regulatory_architecture": 1,
        "genome_architecture_ecological_strategy": 1,
        "plant": 12,
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


def test_population_split_is_not_relabelled_as_within_architecture_boundary():
    rows = _ledger_rows()
    cluster_ids = {row["cluster_id"] for row in rows}
    assert "Ecoli_alternating_carbon_strategy" not in cluster_ids
    boundary_ids = {
        row["cluster_id"] for row in rows if row["pattern_class"] == "BOUNDARY_CROSSING"
    }
    assert boundary_ids == {
        "Solanum_heteranthery_repeated_origins",
        "Yeast_GAP1_PUT4_CNV_context",
    }


def test_preprint_boundary_is_bounded_and_not_hysteresis():
    rows = {row["cluster_id"]: row for row in _ledger_rows()}
    yeast = rows["Yeast_GAP1_PUT4_CNV_context"]
    assert yeast["confidence"] == "moderate"
    assert yeast["quantitative_pool_eligible"] == "false"
    assert "preprint" in yeast["claim_ceiling"]
    assert yeast["pattern_class"] == "BOUNDARY_CROSSING"


def test_no_source_adjudication_is_mistaken_for_hysteresis_or_pooling():
    builder = _load_builder()
    result = builder.build(LEDGER)
    assert result["n_hysteresis_clusters"] == 0
    assert result["n_quantitative_pool_eligible_clusters"] == 0
    assert result["pattern_class_counts"]["UNRESOLVED"] == 5

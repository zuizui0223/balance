import csv

import pytest

from balance_domain.plant_macro import FIELDS, build_plant_macro_readout, load_plant_macro_ledger


def _row(**updates):
    row = {
        "cluster_id": "plant_a",
        "dependency_group": "species_a",
        "sampling_frame_id": "plant_pilot_v1",
        "unit_type": "SPECIES",
        "source_id": "source_a",
        "publication_year": "2020",
        "system_taxon": "Example plant",
        "conflict_family": "POLLEN_REWARD_GAMETE",
        "shared_structure": "stamen system",
        "function_a": "pollen reward",
        "function_b": "pollen export",
        "conflict_status": "POSITIVE",
        "architecture_mode": "WITHIN_FLOWER_DIVISION_OF_LABOUR",
        "structural_module_division": "true",
        "module_substrate": "SERIAL_WITHIN_FLOWER",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
        "self_compatibility": "UNRESOLVED",
        "autonomous_selfing": "UNRESOLVED",
        "pollinator_dependence": "HIGH",
        "life_history": "PERENNIAL",
        "study_design": "field experiment",
        "evidence_quality": "HIGH",
        "adjudication_status": "ADJUDICATED",
        "primary_model_eligible": "true",
        "exclusion_reason": "",
        "source_basis": "TEST",
        "claim_ceiling": "comparative_only",
        "notes": "",
    }
    row.update(updates)
    return row


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_species_level_positive_row_can_pass_primary_gate(tmp_path):
    path = tmp_path / "plants.csv"
    _write(path, [_row()])
    rows = load_plant_macro_ledger(path)
    assert rows[0]["primary_model_eligible"] == "true"


def test_comparative_clade_cannot_be_primary_pseudoreplication(tmp_path):
    path = tmp_path / "plants.csv"
    _write(path, [_row(unit_type="COMPARATIVE_CLADE")])
    with pytest.raises(ValueError, match="species-level grain"):
        load_plant_macro_ledger(path)


def test_resolution_binary_consistency_is_fail_closed(tmp_path):
    path = tmp_path / "plants.csv"
    _write(
        path,
        [_row(architecture_mode="SHARED_INTEGRATED", structural_module_division="true")],
    )
    with pytest.raises(ValueError, match="must be false"):
        load_plant_macro_ledger(path)


def test_polymorphic_or_mosaic_is_not_forced_into_binary(tmp_path):
    path = tmp_path / "plants.csv"
    _write(
        path,
        [
            _row(
                architecture_mode="POLYMORPHIC_OR_MOSAIC",
                structural_module_division="unresolved",
                primary_model_eligible="false",
            )
        ],
    )
    rows = load_plant_macro_ledger(path)
    assert rows[0]["structural_module_division"] == "unresolved"


def test_primary_gate_requires_outcome_independent_geometry_predictors(tmp_path):
    path = tmp_path / "plants.csv"
    _write(path, [_row(module_substrate="UNRESOLVED")])
    with pytest.raises(ValueError, match="resolved module substrate"):
        load_plant_macro_ledger(path)


def test_dependency_groups_are_reported_separately_from_record_count(tmp_path):
    path = tmp_path / "plants.csv"
    _write(
        path,
        [
            _row(cluster_id="context_a", dependency_group="species_a"),
            _row(
                cluster_id="context_b",
                dependency_group="species_a",
                primary_model_eligible="false",
            ),
        ],
    )
    readout = build_plant_macro_readout(path)
    assert readout["n_records"] == 2
    assert readout["n_dependency_groups"] == 1


def test_combined_temporal_spatial_separation_is_nonstructural(tmp_path):
    path = tmp_path / "plants.csv"
    _write(
        path,
        [
            _row(
                architecture_mode="TEMPORAL_AND_SPATIAL_SEPARATION",
                structural_module_division="false",
            )
        ],
    )
    rows = load_plant_macro_ledger(path)
    assert rows[0]["architecture_mode"] == "TEMPORAL_AND_SPATIAL_SEPARATION"
    assert rows[0]["structural_module_division"] == "false"


def test_signal_separation_is_a_nonstructural_architecture_mode(tmp_path):
    path = tmp_path / "plants.csv"
    _write(
        path,
        [
            _row(
                architecture_mode="SIGNAL_SEPARATION",
                structural_module_division="false",
            )
        ],
    )
    rows = load_plant_macro_ledger(path)
    assert rows[0]["architecture_mode"] == "SIGNAL_SEPARATION"
    assert rows[0]["structural_module_division"] == "false"

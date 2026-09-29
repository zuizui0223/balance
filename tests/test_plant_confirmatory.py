import csv

import pytest

from balance_domain.plant_confirmatory import (
    FIELDS as RECEIPT_FIELDS,
    adjudicated_independent_plant_values,
    build_confirmatory_gate_report,
    licensed_primary_clusters,
    load_plant_predictor_receipts,
)
from balance_domain.plant_macro import FIELDS as MACRO_FIELDS, load_plant_macro_ledger


def _macro_row(**updates):
    row = {
        "cluster_id": "plant_a",
        "dependency_group": "species_a",
        "sampling_frame_id": "confirmatory_v1",
        "unit_type": "SPECIES",
        "source_id": "source_outcome",
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


def _receipt(receipt_id, predictor, value, **updates):
    row = {
        "receipt_id": receipt_id,
        "cluster_id": "plant_a",
        "predictor": predictor,
        "reported_value": value,
        "source_id": "source_predictor",
        "evidence_type": "PRE_OUTCOME_MEASUREMENT",
        "outcome_independence": "TRUE",
        "adjudication_status": "ADJUDICATED",
        "notes": "",
    }
    row.update(updates)
    return row


def _receipts():
    return [
        _receipt("r1", "module_substrate", "SERIAL_WITHIN_FLOWER"),
        _receipt("r2", "conflict_timing_geometry", "SIMULTANEOUS"),
        _receipt("r3", "conflict_spatial_geometry", "SAME_UNIT"),
    ]


def _write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _validated_macro(tmp_path, **updates):
    path = tmp_path / "macro.csv"
    _write(path, MACRO_FIELDS, [_macro_row(**updates)])
    return load_plant_macro_ledger(path)


def test_three_independent_predictor_receipts_license_primary_row(tmp_path):
    rows = _validated_macro(tmp_path)
    assert licensed_primary_clusters(rows, _receipts()) == ["plant_a"]


def test_primary_row_fails_closed_when_one_predictor_receipt_is_missing(tmp_path):
    rows = _validated_macro(tmp_path)
    with pytest.raises(ValueError, match="lacks an independent adjudicated receipt"):
        licensed_primary_clusters(rows, _receipts()[:-1])


def test_macro_and_predictor_receipt_must_match(tmp_path):
    rows = _validated_macro(tmp_path)
    receipts = _receipts()
    receipts[0] = _receipt("r1", "module_substrate", "SINGLE_OR_CONTINUOUS")
    with pytest.raises(ValueError, match="ledger and independent receipt disagree"):
        licensed_primary_clusters(rows, receipts)


def test_outcome_derived_predictor_cannot_claim_independence(tmp_path):
    path = tmp_path / "receipts.csv"
    _write(
        path,
        RECEIPT_FIELDS,
        [
            _receipt(
                "r1",
                "module_substrate",
                "SERIAL_WITHIN_FLOWER",
                evidence_type="OUTCOME_DERIVED",
                outcome_independence="TRUE",
            )
        ],
    )
    with pytest.raises(ValueError, match="outcome_independence=FALSE"):
        load_plant_predictor_receipts(path)


def test_conflicting_independent_receipts_fail_closed():
    receipts = [
        _receipt("r1", "module_substrate", "SERIAL_WITHIN_FLOWER"),
        _receipt("r2", "module_substrate", "SINGLE_OR_CONTINUOUS"),
    ]
    with pytest.raises(ValueError, match="conflicting independent adjudicated"):
        adjudicated_independent_plant_values(receipts)


def test_unresolved_receipt_does_not_license_primary_row(tmp_path):
    rows = _validated_macro(tmp_path)
    receipts = _receipts()
    receipts[2] = _receipt("r3", "conflict_spatial_geometry", "UNRESOLVED")
    with pytest.raises(ValueError, match="lacks an independent adjudicated receipt"):
        licensed_primary_clusters(rows, receipts)


def test_mosaic_primary_row_is_licensed_without_binary_structural_call(tmp_path):
    rows = _validated_macro(
        tmp_path,
        architecture_mode="POLYMORPHIC_OR_MOSAIC",
        structural_module_division="unresolved",
        conflict_timing_geometry="CONTEXT_DEPENDENT",
        conflict_spatial_geometry="ENVIRONMENTAL_MOSAIC",
    )
    receipts = [
        _receipt("r1", "module_substrate", "SERIAL_WITHIN_FLOWER"),
        _receipt("r2", "conflict_timing_geometry", "CONTEXT_DEPENDENT"),
        _receipt("r3", "conflict_spatial_geometry", "ENVIRONMENTAL_MOSAIC"),
    ]
    assert licensed_primary_clusters(rows, receipts) == ["plant_a"]


def test_gate_report_freezes_primary_response_classes(tmp_path):
    rows = _validated_macro(tmp_path)
    report = build_confirmatory_gate_report(rows, _receipts())
    assert report["primary_response"] == "architecture_class4"
    assert report["primary_classes"] == [
        "SHARED",
        "NONSTRUCTURAL_SEPARATION",
        "STRUCTURAL_MODULE_DIVISION",
        "MOSAIC",
    ]
    assert report["n_licensed_primary_clusters"] == 1

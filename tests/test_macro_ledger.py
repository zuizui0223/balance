import csv
from pathlib import Path

import pytest

from balance_domain.macro_ledger import (
    FIELDS,
    build_macro_readout,
    derive_resolution_level,
    load_macro_ledger,
)


def _row(**updates):
    row = {
        "cluster_id": "seed_a",
        "sampling_frame_id": "pilot_v1",
        "source_id": "source_a",
        "publication_year": "2020",
        "system_taxon": "Example taxon",
        "domain": "plant",
        "shared_structure": "shared floral structure",
        "function_a": "pollination",
        "function_b": "antagonist avoidance",
        "multifunctionality_status": "YES",
        "conflict_status": "POSITIVE",
        "conflict_strength_proxy": "MEDIUM",
        "architecture_state": "SHARED_INTEGRATED",
        "structural_differentiation": "false",
        "alternative_accessibility": "MEDIUM",
        "functional_coupling": "HIGH",
        "temporal_heterogeneity": "LOW",
        "spatial_heterogeneity": "MEDIUM",
        "alternative_repertoire": "ONE",
        "context_axis": "pollination_x_antagonism",
        "study_design": "field_experiment",
        "evidence_quality": "HIGH",
        "source_count": "1",
        "adjudication_status": "ADJUDICATED",
        "primary_model_eligible": "true",
        "exclusion_reason": "",
        "source_basis": "TEST_RECEIPT",
        "claim_ceiling": "macro_comparative_only",
        "notes": "",
    }
    row.update(updates)
    return row


def _write(path: Path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_macro_ledger_accepts_adjudicated_positive_resolved_row(tmp_path):
    path = tmp_path / "macro.csv"
    _write(path, [_row()])
    rows = load_macro_ledger(path)
    assert rows[0]["cluster_id"] == "seed_a"
    assert rows[0]["primary_model_eligible"] == "true"


def test_primary_model_gate_rejects_nonpositive_conflict(tmp_path):
    path = tmp_path / "macro.csv"
    _write(
        path,
        [
            _row(
                conflict_status="ALIGNED_NO_CONFLICT",
                conflict_strength_proxy="NA",
            )
        ],
    )
    with pytest.raises(ValueError, match="requires POSITIVE conflict"):
        load_macro_ledger(path)


def test_structural_outcome_must_match_architecture_state(tmp_path):
    path = tmp_path / "macro.csv"
    _write(
        path,
        [
            _row(
                architecture_state="SEPARATE_MODULES",
                structural_differentiation="false",
            )
        ],
    )
    with pytest.raises(ValueError, match="must be true"):
        load_macro_ledger(path)


def test_duplicate_cluster_is_rejected(tmp_path):
    path = tmp_path / "macro.csv"
    _write(path, [_row(), _row(source_id="source_b")])
    with pytest.raises(ValueError, match="duplicate cluster_id"):
        load_macro_ledger(path)


def test_unresolved_rows_can_remain_in_screening_universe(tmp_path):
    path = tmp_path / "macro.csv"
    _write(
        path,
        [
            _row(
                conflict_status="UNRESOLVED",
                conflict_strength_proxy="UNRESOLVED",
                architecture_state="UNRESOLVED",
                structural_differentiation="unresolved",
                adjudication_status="SCREENED",
                primary_model_eligible="false",
            )
        ],
    )
    rows = load_macro_ledger(path)
    assert rows[0]["primary_model_eligible"] == "false"


def test_resolution_level_is_derived_not_manually_stored():
    assert derive_resolution_level("SHARED_INTEGRATED") == 0
    assert derive_resolution_level("SEPARATE_MODULES") == 4
    assert derive_resolution_level("POLYMORPHIC") is None


def test_macro_readout_is_descriptive_only(tmp_path):
    path = tmp_path / "macro.csv"
    _write(
        path,
        [
            _row(),
            _row(
                cluster_id="seed_b",
                source_id="source_b",
                architecture_state="PARTIAL_STRUCTURAL_DIFFERENTIATION",
                structural_differentiation="true",
            ),
            _row(
                cluster_id="seed_c",
                source_id="source_c",
                conflict_status="ALIGNED_NO_CONFLICT",
                conflict_strength_proxy="NA",
                architecture_state="SHARED_INTEGRATED",
                structural_differentiation="false",
                primary_model_eligible="false",
            ),
        ],
    )
    readout = build_macro_readout(path)
    assert readout["n_independent_clusters"] == 3
    assert readout["n_primary_model_eligible"] == 2
    assert readout["primary_structural_outcome_counts"] == {
        "false": 1,
        "true": 1,
    }
    assert "not_natural_prevalence" in readout["claim_ceiling"]

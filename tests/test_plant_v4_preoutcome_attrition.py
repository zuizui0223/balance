"""Regression guards for the outcome-blind V4 source-screen attrition audit."""
from pathlib import Path

import pytest

from balance_domain.plant_v4_preoutcome_attrition import (
    build_v4_preoutcome_attrition_audit,
)

ROOT = Path(__file__).resolve().parents[1]
U2_CONFLICT = ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
U2_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U6_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"


def audit(*, u6=U6_RECEIPTS, max_deleted=3):
    return build_v4_preoutcome_attrition_audit(
        U2_CONFLICT, U2_RECEIPTS, u6, max_deleted=max_deleted
    )


def test_all_group_deletions_up_to_three_are_exactly_enumerated():
    out = audit()
    assert out["n_screened_groups"] == 29
    assert out["source_universes"] == {"U2": 8, "U6": 21}
    assert out["full_v4_design_rank"] == 5
    rows = out["attrition_enumeration"]
    assert [r["subsets_checked"] for r in rows] == [1, 29, 406, 3654]
    assert [r["rank_deficient_subsets"] for r in rows] == [0, 0, 0, 2]
    assert [r["primary_level_support_failure_subsets"] for r in rows] == [
        0, 0, 6, 154
    ]
    assert [r["module_level_support_failure_subsets"] for r in rows] == [
        0, 0, 3, 79
    ]
    assert [r["timing_level_support_failure_subsets"] for r in rows] == [
        0, 0, 3, 79
    ]
    assert rows[3]["both_level_support_failure_subsets"] == 4


def test_rank_failure_witnesses_are_the_two_complete_sparse_cells():
    witnesses = audit()["attrition_enumeration"][3]["rank_deficiency_witnesses"]
    assert {frozenset(x) for x in witnesses} == {
        frozenset({
            "Asclepias_exaltata",
            "Mimulus_aurantiacus",
            "Eichhornia_paniculata",
        }),
        frozenset({
            "Campsis_radicans",
            "Asclepias_exaltata",
            "Epilobium_obcordatum",
        }),
    }


def test_g1_not_available_and_no_architecture_outcomes_accessed():
    out = audit(max_deleted=1)
    assert out["strict_cross_universe_g1_ready_under_frozen_v1"] is False
    assert out["shared_single_module_timing_counts"] == {
        "U2": {"SIMULTANEOUS": 1, "ORDERED_OR_ALTERNATING": 2},
        "U6": {"SIMULTANEOUS": 18, "ORDERED_OR_ALTERNATING": 3},
    }
    assert out["architecture_outcomes_used"] is False
    assert out["independent_adjudication_complete"] is False
    assert out["model_fit_performed"] is False


def test_loss_of_one_u6_predictor_value_fails_closed(tmp_path):
    source = U6_RECEIPTS.read_text(encoding="utf-8")
    old = (
        "U6_ACTINIDIA_DELICIOSA_CONFLICT_TIMING_GEOMETRY,"
        "Actinidia_deliciosa,conflict_timing_geometry,SIMULTANEOUS,"
    )
    assert old in source
    altered = source.replace(
        old,
        old.replace(",SIMULTANEOUS,", ",UNRESOLVED,"),
        1,
    )
    path = tmp_path / "u6_corrupted.csv"
    path.write_text(altered, encoding="utf-8")
    with pytest.raises(ValueError, match="all 21 complete"):
        audit(u6=path, max_deleted=0)


def test_adjudication_cannot_be_simulated_in_the_v1_source_screen(tmp_path):
    source = U6_RECEIPTS.read_text(encoding="utf-8")
    assert ",SCREENED," in source
    path = tmp_path / "u6_fake_adjudication.csv"
    path.write_text(
        source.replace(",SCREENED,", ",ADJUDICATED,", 1),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="SCREENED receipts only"):
        audit(u6=path, max_deleted=0)


def test_invalid_deletion_horizon_is_not_silently_truncated():
    with pytest.raises(ValueError, match="from 0 to 3"):
        audit(max_deleted=4)

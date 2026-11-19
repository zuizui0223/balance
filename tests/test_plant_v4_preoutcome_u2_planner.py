"""Outcome-blind prospective-design *scenarios*, never new biological observations."""
from pathlib import Path

import pytest

from balance_domain.plant_v4_preoutcome_u2_planner import (
    _hypothetical_row,
    build_v4_preoutcome_u2_scenario_planner,
)

ROOT = Path(__file__).resolve().parents[1]


def run():
    return build_v4_preoutcome_u2_scenario_planner(
        ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    )


def test_all_six_u2_predictor_cells_preserved_not_just_positive_scenario():
    report = run()
    rows = report["single_qualifying_u2_group_scenarios"]
    assert len(rows) == 6
    assert len({(x["candidate_module"], x["candidate_timing"]) for x in rows}) == 6
    assert all(x["is_observed_addition"] is False for x in rows)
    assert report["architecture_outcomes_used"] is False
    assert report["source_admissions_changed"] is False


def test_information_best_one_group_scenario_does_not_by_itself_open_g1():
    report = run()
    first = report["single_qualifying_u2_group_scenarios"][0]
    assert (first["candidate_module"], first["candidate_timing"]) == (
        "MODULAR", "ORDERED_OR_ALTERNATING"
    )
    assert first["relative_improvement_temporal_ordered"] == pytest.approx(
        0.0690506637487372
    )
    assert first[
        "g1_predictor_common_support_only_if_future_group_independently_qualifies"
    ] is False


def test_single_plus_simultaneous_repairs_predictor_support_only_not_g1_outcomes():
    report = run()
    ss = next(x for x in report["single_qualifying_u2_group_scenarios"]
              if x["candidate_module"] == "SINGLE"
              and x["candidate_timing"] == "SIMULTANEOUS")
    assert ss[
        "g1_predictor_common_support_only_if_future_group_independently_qualifies"
    ] is True
    assert ss["relative_improvement_temporal_ordered"] == pytest.approx(
        0.03509871864598443
    )
    assert "G1 additionally requires independent outcome support" in report["constraints"][
        4
    ]


def test_two_three_addition_scenarios_not_misrepresented_as_observations():
    report = run()
    two = report["specific_two_group_illustration"]
    assert two["g1_predictor_common_support_only"] is True
    assert two["optimistic_binary_se_floors"]["temporal_ordered"] == pytest.approx(
        0.9699794920789633
    )
    three = report["specific_three_group_one_deletion_robust_g1_illustration"]
    assert three["nominal_g1_predictor_common_support_only"] is True
    assert three["one_deletion_robust_single_stratum"] is True
    assert report["status"] == "HYPOTHETICAL_PREDICTOR_PROFILES_NOT_REAL_SPECIES"


def test_invalid_hypothetical_design_profile_is_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        _hypothetical_row("MODULAR", "UNKNOWN")

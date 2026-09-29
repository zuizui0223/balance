import json
import math
from pathlib import Path

from balance_domain.plant_v4_estimands import (
    build_v4_estimand_standardization,
    contrast_draws,
    gamma_negative_margin_probability,
    posterior_contrast_summary,
)


def _row(row_id, universe, mode, module, timing, spatial="SAME_UNIT"):
    return {
        "analysis_row_id": row_id,
        "universe_id": universe,
        "dependency_group": row_id,
        "dependence_block": f"block::{row_id}",
        "system_taxon": row_id,
        "conflict_family": (
            "SEXUAL_INTERFERENCE"
            if universe == "U2_BARRETT_2002"
            else "POLLEN_REWARD_GAMETE"
        ),
        "conflict_receipt_status": "ADJUDICATED_POSITIVE",
        "architecture_mode": mode,
        "module_substrate": module,
        "conflict_timing_geometry": timing,
        "conflict_spatial_geometry": spatial,
        "architecture_adjudication_status": "ADJUDICATED",
        "predictor_receipt_status": "THREE_ADJUDICATED_OUTCOME_INDEPENDENT",
        "source_basis": "synthetic",
        "claim_ceiling": "comparative_only",
    }


def _rows():
    u2 = "U2_BARRETT_2002"
    u6 = "U6_POLLEN_THEFT_HARGREAVES_2009"
    return [
        _row("u2_s1", u2, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u2_s2", u2, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row("u2_n1", u2, "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEASONALLY_ALTERNATING"),
        _row("u2_n2", u2, "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u2_n3", u2, "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row("u2_d1", u2, "WITHIN_FLOWER_DIVISION_OF_LABOUR", "REPEATED_FLOWERS", "CONTEXT_DEPENDENT"),
        _row("u2_m1", u2, "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "MIXED", "BETWEEN_MODULES"),
        _row("u6_s1", u6, "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u6_n1", u6, "TEMPORAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT"),
        _row("u6_n2", u6, "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u6_d1", u6, "AMONG_FLOWER_MODULE_DIVISION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS"),
        _row("u6_m1", u6, "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING"),
    ]


def test_standardization_uses_equal_supported_cells_not_raw_row_weights():
    out = build_v4_estimand_standardization(_rows())

    temporal = out["H_T_primary"]
    cells = {
        (row["universe_id"], row["module_opportunity2"])
        for row in temporal
    }
    assert cells == {
        ("U2_BARRETT_2002", "SINGLE"),
        ("U2_BARRETT_2002", "MODULAR"),
        ("U6_POLLEN_THEFT_HARGREAVES_2009", "SINGLE"),
    }
    assert len(temporal) == 6
    assert all(math.isclose(row["weight"], 1.0 / 3.0) for row in temporal)

    h_m = out["H_M_U2"]
    timings = {row["temporal_exposure3"] for row in h_m}
    assert timings == {
        "SIMULTANEOUS",
        "ORDERED_OR_ALTERNATING",
        "VARIABLE_CONTEXT",
    }
    assert len(h_m) == 6
    assert all(math.isclose(row["weight"], 1.0 / 3.0) for row in h_m)


def test_cross_universe_standardization_uses_only_frozen_common_support():
    out = build_v4_estimand_standardization(_rows())
    assert out["temporal_common_support_module_strata"] == ["SINGLE"]
    assert out["temporal_generality_ready"] is True

    grid = out["H_T_cross_universe"]
    assert len(grid) == 4
    assert {row["module_opportunity2"] for row in grid} == {"SINGLE"}
    assert {row["universe_id"] for row in grid} == {
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    }
    assert all(row["weight"] == 1.0 for row in grid)


def _draw(*, ordered_nonstructural=0.0, module_structural=0.0, gamma_nonstructural=0.0):
    # Response columns are NONSTRUCTURAL, STRUCTURAL, MOSAIC versus SHARED.
    return {
        "alpha": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        "beta": [
            [0.0, module_structural, 0.0],
            [ordered_nonstructural, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ],
        "gamma_u6_ordered": [gamma_nonstructural, 0.0, 0.0],
    }


def test_registered_probability_contrasts_are_computed_from_counterfactual_cells():
    grid = build_v4_estimand_standardization(_rows())

    timing_draws = contrast_draws(
        [_draw(ordered_nonstructural=1.0)] * 5,
        grid["H_T_primary"],
        target_response="NONSTRUCTURAL_SEPARATION",
        arm_field="temporal_exposure3",
        positive_arm="ORDERED_OR_ALTERNATING",
        negative_arm="SIMULTANEOUS",
    )
    assert all(value > 0 for value in timing_draws)
    summary = posterior_contrast_summary(timing_draws)
    assert summary["p_positive"] == 1.0
    assert summary["p_negative"] == 0.0

    module_draws = contrast_draws(
        [_draw(module_structural=1.0)] * 5,
        grid["H_M_U2"],
        target_response="STRUCTURAL_MODULE_DIVISION",
        arm_field="module_opportunity2",
        positive_arm="MODULAR",
        negative_arm="SINGLE",
        universe_id="U2_BARRETT_2002",
    )
    assert all(value > 0 for value in module_draws)


def test_generality_contrast_and_interaction_tail_use_registered_parameters():
    grid = build_v4_estimand_standardization(_rows())["H_T_cross_universe"]
    draws = [_draw(ordered_nonstructural=1.0, gamma_nonstructural=-2.0)] * 4

    u2 = contrast_draws(
        draws,
        grid,
        target_response="NONSTRUCTURAL_SEPARATION",
        arm_field="temporal_exposure3",
        positive_arm="ORDERED_OR_ALTERNATING",
        negative_arm="SIMULTANEOUS",
        universe_id="U2_BARRETT_2002",
        generality=True,
    )
    u6 = contrast_draws(
        draws,
        grid,
        target_response="NONSTRUCTURAL_SEPARATION",
        arm_field="temporal_exposure3",
        positive_arm="ORDERED_OR_ALTERNATING",
        negative_arm="SIMULTANEOUS",
        universe_id="U6_POLLEN_THEFT_HARGREAVES_2009",
        generality=True,
    )

    assert all(value > 0 for value in u2)
    assert all(value < 0 for value in u6)
    assert gamma_negative_margin_probability(draws) == 1.0



ROOT = Path(__file__).resolve().parents[1]
STANDARDIZATION = ROOT / "data" / "BALANCE_PLANT_V4_ESTIMAND_STANDARDIZATION_V1.json"
HYPOTHESES = ROOT / "data" / "BALANCE_PLANT_V4_DIRECTIONAL_HYPOTHESES_V1.json"
MODEL_SPEC = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4.json"
DECISION_RULES = ROOT / "data" / "BALANCE_PLANT_V4_POSTERIOR_DECISION_RULES_V1.json"


def test_v4_registries_share_one_frozen_estimand_standardization_contract():
    target = "data/BALANCE_PLANT_V4_ESTIMAND_STANDARDIZATION_V1.json"
    registry = json.loads(STANDARDIZATION.read_text(encoding="utf-8"))
    assert registry["status"] == "FROZEN_PRE_OUTCOME_CLARIFICATION_OF_EXISTING_V4_ESTIMANDS"
    assert registry["principle"] == (
        "standardize over supported predictor cells rather than weighting by the "
        "number of rows contributed by a sampling universe"
    )
    assert registry["H_T_primary"]["weighting"] == (
        "equal weight per supported universe x module cell"
    )
    assert registry["H_M_U2"]["weighting"] == (
        "equal weight per supported U2 temporal level"
    )
    assert registry["H_T_cross_universe"]["weighting"] == (
        "equal weight per retained common-support module stratum within each universe"
    )

    for path in (HYPOTHESES, MODEL_SPEC, DECISION_RULES):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["estimand_standardization_registry"] == target

import pytest

from balance_domain.plant_model_v4_fit import (
    build_v4_prior_sensitivity_input,
    build_v4_stan_input,
)


def _row(row_id, universe, group, block, mode, module, timing, spatial):
    return {
        "analysis_row_id": row_id,
        "universe_id": universe,
        "dependency_group": group,
        "dependence_block": block,
        "system_taxon": group.replace("_", " "),
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
        "source_basis": "synthetic_test",
        "claim_ceiling": "comparative_only",
    }


def _ready_rows():
    u2 = "U2_BARRETT_2002"
    u6 = "U6_POLLEN_THEFT_HARGREAVES_2009"
    return [
        _row("r1", u2, "u2_s1", "b1", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("r2", u2, "u2_s2", "b2", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "MIXED", "SAME_UNIT"),
        _row("r3", u2, "u2_n1", "b3", "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("r4", u2, "u2_d1", "b4", "WITHIN_FLOWER_DIVISION_OF_LABOUR", "REPEATED_FLOWERS", "SIMULTANEOUS", "BETWEEN_MODULES"),
        _row("r5", u2, "u2_m1", "b5", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "CONTEXT_DEPENDENT", "SAME_UNIT"),
        _row("r6", u6, "u6_s1", "b6", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("r7", u6, "u6_n1", "b7", "SPATIAL_SEPARATION", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("r8", u6, "u6_d1", "b8", "AMONG_FLOWER_MODULE_DIVISION", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("r9", u6, "u6_m1", "b9", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING", "SAME_UNIT"),
    ]


def test_v4_stan_input_has_two_universe_intercepts_and_three_common_slopes():
    out = build_v4_stan_input(_ready_rows())
    data = out["stan_data"]
    meta = out["metadata"]

    assert data["N"] == 9
    assert data["K"] == 4
    assert data["U"] == 2
    assert data["P"] == 3
    assert data["slope_prior_sd"] == 0.75
    assert data["intercept_prior_sd"] == 1.5
    assert meta["universe_order"] == [
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    ]
    assert meta["slope_columns"] == [
        "module_MODULAR",
        "temporal_ORDERED_OR_ALTERNATING",
        "temporal_VARIABLE_CONTEXT",
    ]
    assert meta["U1_role"] == "external_specificity_validation_not_primary_fit"
    assert meta["estimability"]["ready_for_primary_fit"] is True


def test_v4_universe_index_is_frozen_and_design_has_no_global_intercept_column():
    out = build_v4_stan_input(_ready_rows())
    data = out["stan_data"]

    assert data["universe"][:5] == [1, 1, 1, 1, 1]
    assert data["universe"][5:] == [2, 2, 2, 2]
    assert all(len(row) == 3 for row in data["X"])
    assert data["X"][0] == [0, 0, 0]
    assert data["X"][1] == [0, 0, 1]
    assert data["X"][2] == [1, 1, 0]


def test_v4_prior_sensitivity_changes_only_common_slope_prior():
    base = build_v4_stan_input(_ready_rows())
    wide = build_v4_prior_sensitivity_input(_ready_rows())
    assert wide["stan_data"]["slope_prior_sd"] == 1.5
    assert wide["stan_data"]["intercept_prior_sd"] == base["stan_data"]["intercept_prior_sd"]
    assert wide["stan_data"]["X"] == base["stan_data"]["X"]
    assert wide["stan_data"]["universe"] == base["stan_data"]["universe"]
    assert wide["stan_data"]["y"] == base["stan_data"]["y"]


def test_v4_fit_rejects_u1_primary_row_before_stan():
    rows = _ready_rows()
    rows[0]["universe_id"] = "U1_HAAS_LORTIE_2020"
    with pytest.raises(ValueError, match="not licensed for the primary confirmatory denominator"):
        build_v4_stan_input(rows)


def test_v4_fit_rejects_repeated_dependence_block():
    rows = _ready_rows()
    rows[1]["dependence_block"] = rows[0]["dependence_block"]
    with pytest.raises(ValueError, match="one analysis row per dependence block"):
        build_v4_stan_input(rows)

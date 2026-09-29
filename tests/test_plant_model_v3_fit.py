from pathlib import Path

import pytest

from balance_domain.plant_model_v3_fit import (
    build_v3_prior_sensitivity_input,
    build_v3_stan_input,
)


ROOT = Path(__file__).resolve().parents[1]
STAN = ROOT / "comparative" / "models" / "BALANCE_PLANT_V3_MULTINOMIAL.stan"


def _row(row_id, universe, group, block, mode, module, timing, spatial):
    return {
        "analysis_row_id": row_id,
        "universe_id": universe,
        "dependency_group": group,
        "dependence_block": block,
        "system_taxon": group.replace("_", " "),
        "conflict_family": "POLLEN_REWARD_GAMETE",
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
    return [
        _row("r1", "U2_BARRETT_2002", "s1", "b1", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "SIMULTANEOUS", "SAME_UNIT"),
        _row("r2", "U6_POLLEN_THEFT_HARGREAVES_2009", "s2", "b2", "SHARED_INTEGRATED", "SINGLE_OR_CONTINUOUS", "MIXED", "SAME_UNIT"),
        _row("r3", "U2_BARRETT_2002", "n1", "b3", "TEMPORAL_SEPARATION", "SERIAL_WITHIN_FLOWER", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("r4", "U6_POLLEN_THEFT_HARGREAVES_2009", "n2", "b4", "SPATIAL_SEPARATION", "REPEATED_FLOWERS", "SEASONALLY_ALTERNATING", "SAME_UNIT"),
        _row("r5", "U6_POLLEN_THEFT_HARGREAVES_2009", "d1", "b5", "WITHIN_FLOWER_DIVISION_OF_LABOUR", "SERIAL_WITHIN_FLOWER", "SIMULTANEOUS", "SAME_UNIT"),
        _row("r6", "U6_POLLEN_THEFT_HARGREAVES_2009", "d2", "b6", "AMONG_FLOWER_MODULE_DIVISION", "REPEATED_FLOWERS", "CONTEXT_DEPENDENT", "SAME_UNIT"),
        _row("r7", "U2_BARRETT_2002", "m1", "b7", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEQUENTIAL_WITHIN_UNIT", "SAME_UNIT"),
        _row("r8", "U6_POLLEN_THEFT_HARGREAVES_2009", "m2", "b8", "POLYMORPHIC_OR_MOSAIC", "SINGLE_OR_CONTINUOUS", "SEASONALLY_ALTERNATING", "BETWEEN_MODULES"),
    ]


def test_v3_fit_input_uses_frozen_response_and_design_order():
    out = build_v3_stan_input(_ready_rows())
    data = out["stan_data"]
    meta = out["metadata"]

    assert data["N"] == 8
    assert data["K"] == 4
    assert data["P"] == 4
    assert data["slope_prior_sd"] == 0.75
    assert data["intercept_prior_sd"] == 1.5
    assert meta["response_order"] == [
        "SHARED",
        "NONSTRUCTURAL_SEPARATION",
        "STRUCTURAL_MODULE_DIVISION",
        "MOSAIC",
    ]
    assert meta["reference_response"] == "SHARED"
    assert meta["design_columns"] == [
        "intercept",
        "module_MODULAR",
        "temporal_ORDERED_OR_ALTERNATING",
        "temporal_VARIABLE_CONTEXT",
    ]
    assert meta["spatial_axis_role"] == "secondary_not_in_primary_design_matrix"
    assert meta["estimability"]["ready_for_primary_fit"] is True


def test_v3_fit_input_has_expected_dummy_coding():
    out = build_v3_stan_input(_ready_rows())
    x = out["stan_data"]["X"]
    y = out["stan_data"]["y"]

    assert x[0] == [1, 0, 0, 0]  # SINGLE + SIMULTANEOUS
    assert x[1] == [1, 0, 0, 1]  # SINGLE + VARIABLE_CONTEXT
    assert x[2] == [1, 1, 1, 0]  # MODULAR + ORDERED
    assert y[:2] == [1, 1]
    assert y[2:4] == [2, 2]
    assert y[4:6] == [3, 3]
    assert y[6:8] == [4, 4]


def test_v3_prior_sensitivity_changes_only_slope_prior():
    base = build_v3_stan_input(_ready_rows())
    wide = build_v3_prior_sensitivity_input(_ready_rows())
    assert wide["stan_data"]["slope_prior_sd"] == 1.5
    assert wide["stan_data"]["intercept_prior_sd"] == base["stan_data"]["intercept_prior_sd"]
    assert wide["stan_data"]["X"] == base["stan_data"]["X"]
    assert wide["stan_data"]["y"] == base["stan_data"]["y"]


def test_v3_fit_rejects_repeated_dependence_block_before_stan():
    rows = _ready_rows()
    rows[1]["dependence_block"] = rows[0]["dependence_block"]
    with pytest.raises(ValueError, match="one analysis row per dependence block"):
        build_v3_stan_input(rows)


def test_v3_fit_rejects_nonestimable_primary_support_before_stan():
    rows = _ready_rows()
    for row in rows:
        if row["conflict_timing_geometry"] in {"MIXED", "CONTEXT_DEPENDENT"}:
            row["conflict_timing_geometry"] = "SIMULTANEOUS"
    with pytest.raises(ValueError, match="not estimable"):
        build_v3_stan_input(rows)


def test_stan_model_freezes_shared_reference_and_registered_priors():
    source = STAN.read_text(encoding="utf-8")
    assert "eta[1] = 0;" in source
    assert "beta[1, k] ~ normal(0, intercept_prior_sd);" in source
    assert "beta[p, k] ~ normal(0, slope_prior_sd);" in source
    assert "categorical_logit" in source
    assert "log_lik" in source
    assert "category_probability" in source

import pytest

from balance_domain.plant_analysis_pipeline import build_v4_analysis_inputs


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


def _generality_ready_rows():
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


def test_v4_pipeline_builds_main_prior_and_generality_inputs_when_all_gates_pass():
    out = build_v4_analysis_inputs(_generality_ready_rows())
    assert out["main_fit_ready"] is True
    assert out["assembly_readout"]["ready_for_primary_fit"] is True
    assert out["main_stan_input"]["stan_data"]["N"] == 12
    assert out["prior_sensitivity_stan_input"]["stan_data"]["slope_prior_sd"] == 1.5
    assert out["temporal_generality_status"] == "READY"
    assert out["temporal_generality_blockers"] == []
    assert out["temporal_generality_stan_input"] is not None
    assert "u6_ordered" in out["temporal_generality_stan_input"]["stan_data"]
    assert out["temporal_generality_prior_sensitivity_stan_input"] is not None
    assert (
        out["temporal_generality_prior_sensitivity_stan_input"]["stan_data"][
            "slope_prior_sd"
        ]
        == 1.5
    )
    assert (
        out["temporal_generality_prior_sensitivity_stan_input"]["stan_data"][
            "interaction_prior_sd"
        ]
        == 0.75
    )
    assert out["standalone_reactivation_decision"] == "NOT_EVALUATED_BY_PREFIT_PIPELINE"


def test_v4_pipeline_can_build_main_fit_while_generality_stays_blocked():
    rows = _generality_ready_rows()
    row = next(row for row in rows if row["analysis_row_id"] == "u6_m1")
    row["conflict_timing_geometry"] = "SIMULTANEOUS"

    out = build_v4_analysis_inputs(rows)
    assert out["main_fit_ready"] is True
    assert out["assembly_readout"]["ready_for_primary_fit"] is True
    assert out["temporal_generality_status"] == "NOT_READY"
    assert out["temporal_generality_stan_input"] is None
    assert out["temporal_generality_prior_sensitivity_stan_input"] is None
    assert "marginal_timing_replication" in out["temporal_generality_blockers"]
    assert "shared_module_timing_common_support" in out["temporal_generality_blockers"]


def test_v4_pipeline_refuses_nonestimable_licensed_assembly():
    rows = _generality_ready_rows()
    for row in rows:
        row["architecture_mode"] = "SHARED_INTEGRATED"

    with pytest.raises(ValueError, match="not ready for the primary fit"):
        build_v4_analysis_inputs(rows)

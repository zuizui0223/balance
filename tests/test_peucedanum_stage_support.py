import pytest
from balance_domain.peucedanum_stage_support import audit_stage_support


def row(n, *, h="4", initial="3", final="2", eggs="1", year="2022", plot="HA"):
    return {
        "dataset_id": "source_2025", "source_file": "archive::All_Plots_Data.csv",
        "source_sheet": "__CSV__", "source_row_number": str(n),
        "year": year, "population_id": plot,
        "perfect_flower_count": h, "initial_fruit_count": initial,
        "intact_fruit_count": final, "predator_egg_count": eggs,
    }


def test_stage_support_counts_and_missingness():
    r = audit_stage_support([
        row(2), row(3, final="", eggs=""),
        row(4, year="2021", initial="", final="", eggs=""),
    ])
    assert r["source_rows"] == 3
    assert r["observed_plot_year_cells"] == 2
    assert r["totals"]["initial_rate_rows"] == 2
    assert r["totals"]["final_rate_rows"] == 1
    assert r["totals"]["conditional_survival_rows"] == 1
    assert r["totals"]["egg_survival_joint_rows"] == 1
    assert r["status"] == "STAGE_SUPPORT_AUDITED"


def test_inconsistent_counts_reported_without_clipping():
    r = audit_stage_support([row(2, h="3", initial="4", final="5")])
    assert r["status"] == "COUNT_INCONSISTENCY_HOLD"
    assert set(r["count_inconsistencies"][0]["reasons"]) == {
        "initial_exceeds_perfect_flowers", "final_exceeds_initial",
        "final_exceeds_perfect_flowers",
    }


def test_no_imputed_outcome_and_zero_initial_not_conditional_survival():
    r = audit_stage_support([row(2, initial="0", final="0")])
    assert r["totals"].get("conditional_survival_rows", 0) == 0
    assert r["totals"]["final_rate_rows"] == 1


def test_reject_negative_fractional_duplicate_and_empty():
    with pytest.raises(ValueError, match="nonnegative integer"):
        audit_stage_support([row(2, initial="-1")])
    with pytest.raises(ValueError, match="nonnegative integer"):
        audit_stage_support([row(2, initial="1.5")])
    with pytest.raises(ValueError, match="duplicated"):
        audit_stage_support([row(2), row(2)])
    with pytest.raises(ValueError, match="no source rows"):
        audit_stage_support([])

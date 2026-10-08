"""Synthetic checks of the paired adjusted exploratory model (not empirical fit)."""
import pytest

from balance_domain.peucedanum_stage_adjusted import _invert, analyze_adjusted


def _rows():
    out = []
    for i in range(32):
        h = 20 + (7*i)%29
        m = 1 + (11*i)%31
        height = 10 + (13*i)%21
        initial = round(h*(0.42+0.12*m/(m+h)))
        final = round(h*(0.16+0.045*m/(m+h)))
        out.append({
            "year": "2022", "population_id": "HA",
            "perfect_flower_count": str(h), "male_flower_count": str(m),
            "flower_stem_height": str(height),
            "initial_fruit_count": str(initial),
            "intact_fruit_count": str(final),
        })
    return out


def test_adjusted_wls_hc3_numeric_reference():
    result = analyze_adjusted(_rows())
    fit = result["variants"]["log_male_count_all_pairs"]["cells"][0]
    assert fit["n"] == 32
    assert fit["status"] == "EXPLORATORY_FIT"
    assert fit["coefficient_per_sd"] == pytest.approx(-0.00654168727458123, abs=1e-11)
    assert fit["se_hc3"] == pytest.approx(0.0022535234588774845, abs=1e-11)
    assert fit["p_normal_hc3"] == pytest.approx(0.0036975923582706445, abs=1e-10)
    assert fit["q_bh_within_variant"] == pytest.approx(fit["p_normal_hc3"])
    assert "no_causal" in result["claim_ceiling"]


def test_complete_case_nonnested_sensitivity_does_not_clip_counts():
    rows = _rows()
    rows[0]["intact_fruit_count"] = str(int(rows[0]["initial_fruit_count"])+1)
    result = analyze_adjusted(rows)
    all_rows = result["variants"]["log_male_count_all_pairs"]["cells"][0]
    nested_rows = result["variants"]["log_male_count_excluding_nonnested"]["cells"][0]
    assert all_rows["n"] == 32
    assert nested_rows["n"] == 31


def test_missing_height_reduces_fit_support():
    rows = _rows()
    rows[0]["flower_stem_height"] = ""
    result = analyze_adjusted(rows)
    assert result["variants"]["log_male_count_all_pairs"]["cells"][0]["n"] == 31


def test_degenerate_outcome_is_not_a_significance_test():
    rows = _rows()
    for r in rows:
        r["intact_fruit_count"] = r["initial_fruit_count"]
    result = analyze_adjusted(rows)
    fit = result["variants"]["log_male_count_all_pairs"]["cells"][0]
    assert fit["status"] == "DEGENERATE_OUTCOME"
    assert fit["p_normal_hc3"] is None
    assert result["variants"]["log_male_count_all_pairs"]["n_nonnull_tests"] == 0


def test_rank_deficiency_and_bad_input_fail_closed():
    rows = _rows()
    for r in rows:
        r["flower_stem_height"] = "10"
    result = analyze_adjusted(rows)
    assert result["variants"]["log_male_count_all_pairs"]["cells"][0]["status"] == (
        "INSUFFICIENT_PREDICTOR_VARIATION"
    )
    rows = _rows()
    rows[1]["intact_fruit_count"] = "9999"
    with pytest.raises(ValueError, match="exceeds perfect flower"):
        analyze_adjusted(rows)
    rows = _rows()
    rows[1]["male_flower_count"] = "nan"
    with pytest.raises(ValueError, match="nonfinite"):
        analyze_adjusted(rows)


def test_exact_matrix_inverse():
    result = _invert([[4, 1], [1, 3]])
    assert result[0] == pytest.approx([3/11, -1/11])
    assert result[1] == pytest.approx([-1/11, 4/11])

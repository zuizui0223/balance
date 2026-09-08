import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRATA = ROOT / "data" / "BALANCE_QUANTITATIVE_STRATA_V1.csv"


def _rows():
    with STRATA.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_all_quantitative_strata_remain_below_pooling_gate():
    rows = _rows()
    assert len(rows) == 5
    assert all(row["pooling_status"].startswith("NOT_READY") for row in rows)
    assert all(
        int(row["effect_size_ready_clusters"]) < int(row["min_independent_clusters"])
        for row in rows
    )


def test_simple_opposing_floral_selection_keeps_four_candidates_and_zero_ready_effects():
    rows = {row["stratum_id"]: row for row in _rows()}
    floral = rows["OPPOSING_FLORAL_SELECTION"]
    assert floral["registered_pattern_candidates"] == "4"
    assert floral["reanalysis_candidates"] == "1"
    assert floral["min_independent_clusters"] == "3"
    assert floral["effect_size_ready_clusters"] == "0"
    assert "variance_covariance" in floral["variance_requirement"]
    assert "assume_covariance_zero" in floral["prohibited_pooling"]
    assert "mix_path_coefficients" in floral["prohibited_pooling"]
    assert "count_populations_as_independent_studies" in floral["prohibited_pooling"]
    assert "Gymnadenia_factorial_contrast_covariance" in floral["next_gate"]


def test_diffuse_factorial_stratum_has_one_ready_positive_but_is_not_pool_ready():
    rows = {row["stratum_id"]: row for row in _rows()}
    diffuse = rows["DIFFUSE_FACTORIAL_AGENT_SELECTION"]
    assert diffuse["registered_pattern_candidates"] == "1"
    assert diffuse["reanalysis_candidates"] == "1"
    assert diffuse["effect_size_ready_clusters"] == "1"
    assert diffuse["min_independent_clusters"] == "3"
    assert diffuse["pooling_status"] == "NOT_READY_ONLY_ONE_EFFECT_READY_POSITIVE_CLUSTER"
    assert "context_specific_agent_contrast_vector" in diffuse["estimand"]
    assert "reported_factorial_sufficient_statistics" in diffuse["variance_requirement"]
    assert "cherry_pick_one_context_pair" in diffuse["prohibited_pooling"]
    assert "treat_context_specific_contrasts_as_independent" in diffuse["prohibited_pooling"]
    assert "assume_zero_covariance" in diffuse["prohibited_pooling"]
    assert "Fragaria_reported_covariance_receipt" in diffuse["next_gate"]
    assert "two_independent_positive_factorial_replications" in diffuse["next_gate"]


def test_negative_control_is_separate_from_fragaria_ready_numerator():
    rows = {row["stratum_id"]: row for row in _rows()}
    diffuse = rows["DIFFUSE_FACTORIAL_AGENT_SELECTION"]
    assert int(diffuse["registered_pattern_candidates"]) == 1
    assert int(diffuse["reanalysis_candidates"]) == 1
    assert int(diffuse["effect_size_ready_clusters"]) == 1
    assert int(diffuse["effect_size_ready_clusters"]) < int(diffuse["min_independent_clusters"])


def test_direct_balance_parameters_are_not_backfilled_from_pattern_studies():
    rows = {row["stratum_id"]: row for row in _rows()}
    direct = rows["DIRECT_WORLDLINE_RESERVE"]
    assert direct["registered_pattern_candidates"] == "0"
    assert direct["effect_size_ready_clusters"] == "0"
    assert "pooled_s_K_Phi_rho_xi_dB" in direct["prohibited_pooling"]


def test_pattern_boundaries_are_not_numeric_thresholds_yet():
    rows = {row["stratum_id"]: row for row in _rows()}
    boundary = rows["BOUNDARY_THRESHOLD"]
    assert boundary["registered_pattern_candidates"] == "2"
    assert boundary["effect_size_ready_clusters"] == "0"
    assert "PATTERN_BOUNDARIES_NOT_DIRECT_THRESHOLDS" in boundary["pooling_status"]
    assert "categories_to_continuous_e_star" in boundary["prohibited_pooling"]


def test_hysteresis_stratum_stays_empty_until_issue_24_contract_is_met():
    rows = {row["stratum_id"]: row for row in _rows()}
    hysteresis = rows["HYSTERESIS_WIDTH"]
    assert hysteresis["registered_pattern_candidates"] == "0"
    assert hysteresis["effect_size_ready_clusters"] == "0"
    assert hysteresis["next_gate"] == "follow_issue_24_promotion_contract"
    assert "generic_expression_memory" in hysteresis["prohibited_pooling"]

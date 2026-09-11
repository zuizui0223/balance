import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRATA = ROOT / "data" / "BALANCE_QUANTITATIVE_STRATA_V1.csv"


def _rows():
    with STRATA.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_exactly_q1b_has_opened_the_pooling_gate():
    rows = _rows()
    assert len(rows) == 6
    open_rows = [row for row in rows if row["pooling_status"].startswith("POOLING_OPEN")]
    assert [row["stratum_id"] for row in open_rows] == ["DIFFUSE_FACTORIAL_AGENT_SELECTION"]
    for row in rows:
        ready = int(row["effect_size_ready_clusters"])
        minimum = int(row["min_independent_clusters"])
        if row["stratum_id"] == "DIFFUSE_FACTORIAL_AGENT_SELECTION":
            assert ready == minimum == 3
        else:
            assert ready < minimum


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
    assert "Dalechampia_Castilleja_Pedicularis" in floral["next_gate"]


def test_diffuse_factorial_stratum_has_three_ready_positives_and_pool_is_open():
    rows = {row["stratum_id"]: row for row in _rows()}
    diffuse = rows["DIFFUSE_FACTORIAL_AGENT_SELECTION"]
    assert diffuse["registered_pattern_candidates"] == "3"
    assert diffuse["reanalysis_candidates"] == "3"
    assert diffuse["effect_size_ready_clusters"] == "3"
    assert diffuse["min_independent_clusters"] == "3"
    assert diffuse["pooling_status"] == "POOLING_OPEN_FIRST_THREE_CLUSTER_POOL_FROZEN"
    assert "context_specific_agent_contrast_vector" in diffuse["estimand"]
    assert "reported_factorial_sufficient_statistics" in diffuse["variance_requirement"]
    assert "cherry_pick_one_context_pair" in diffuse["prohibited_pooling"]
    assert "treat_context_specific_contrasts_as_independent" in diffuse["prohibited_pooling"]
    assert "assume_zero_covariance" in diffuse["prohibited_pooling"]
    assert "count_multiple_traits_within_one_cluster_as_independent" in diffuse["prohibited_pooling"]
    assert "Fragaria_Impatiens_Gymnadenia" in diffuse["next_gate"]
    assert "expand_independent_replication" in diffuse["next_gate"]


def test_negative_controls_and_within_cluster_traits_do_not_inflate_numerator():
    rows = {row["stratum_id"]: row for row in _rows()}
    diffuse = rows["DIFFUSE_FACTORIAL_AGENT_SELECTION"]
    assert int(diffuse["registered_pattern_candidates"]) == 3
    assert int(diffuse["effect_size_ready_clusters"]) == 3
    assert int(diffuse["effect_size_ready_clusters"]) == int(diffuse["min_independent_clusters"])
    assert "count_multiple_traits_within_one_cluster_as_independent" in diffuse["prohibited_pooling"]


def test_discrete_morph_stratum_keeps_primula_out_of_continuous_beta_pooling():
    rows = {row["stratum_id"]: row for row in _rows()}
    morph = rows["DISCRETE_MORPH_AGENT_SELECTION"]
    assert morph["target_pattern"] == "SELECTION_MOSAIC_BOUNDARY"
    assert morph["registered_pattern_candidates"] == "1"
    assert morph["reanalysis_candidates"] == "0"
    assert morph["effect_size_ready_clusters"] == "0"
    assert morph["min_independent_clusters"] == "3"
    assert morph["pooling_status"] == "NOT_READY_SEPARATE_MORPH_ESTIMAND_ONLY"
    assert "relative_fitness_contrast_long_vs_short_genetic_morph" in morph["estimand"]
    assert "convert_discrete_morph_relative_fitness_to_continuous_beta" in morph["prohibited_pooling"]
    assert "count_sites_years_as_independent_studies" in morph["prohibited_pooling"]
    assert "Primula_site_level_relative_fitness_contrasts" in morph["next_gate"]


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

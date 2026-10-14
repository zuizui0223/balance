"""Source-reported Dalechampia stage-reuse effects; NOT raw-data reanalysis."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from balance_domain.dalechampia_temporal import audit_dalechampia_temporal_bracts


PATH = Path(__file__).resolve().parents[1] / "data/DALECHAMPIA_TEMPORAL_BRACT_SOURCE_V1.json"


def source() -> dict:
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_postanthesis_seed_mass_benefits_recovered_with_qualified_95_reference():
    v = audit_dalechampia_temporal_bracts(source())
    assert v["status"] == "SOURCE_REPORTED_FUNCTIONAL_RETENTION_BENEFIT_NOT_BALANCE"
    assert v["reference_interval_rule"].startswith("point +/- 1.96")
    a = {x["contrast"]: x for x in v["postanthesis_2015"]["contrasts"]}
    removed = a["POSTANTHESIS_BRACTS_REMOVED_MINUS_CONTROL"]
    shade = a["POSTANTHESIS_BRACTS_SHADED_MINUS_CONTROL"]
    cut = a["BRAC_EDGE_CUT_CONTROL_MINUS_CONTROL"]
    assert removed["source_treatment_minus_control_seed_mass_mg"] == -1.34
    assert removed["normal_reference_95_interval_mg"] == [-1.9672, -0.7128]
    assert removed["control_minus_treatment_benefit_mg"] == 1.34
    assert removed["point_difference_percent_of_reported_control_mean"] == -3.87
    assert removed["evidence_of_negative_treatment_effect_under_normal_reference"] is True
    assert shade["normal_reference_95_interval_mg"] == [-2.6572, -1.4028]
    assert shade["point_difference_percent_of_reported_control_mean"] == -5.86
    assert shade["evidence_of_negative_treatment_effect_under_normal_reference"] is True
    assert cut["normal_reference_95_interval_mg"] == [-0.3372, 0.9172]
    assert cut["evidence_of_negative_treatment_effect_under_normal_reference"] is False
    assert all(not x["exact_mixed_model_95_interval_reproduced"] for x in a.values())


def test_source_metadata_and_carbon_ratio_are_bounded_as_descriptive():
    v = audit_dalechampia_temporal_bracts(source())
    x = v["postanthesis_2015"]
    assert x["n_maternal_plants"] == 39
    assert x["n_complete_four_treatments"] == 33
    assert x["reported_control_seed_mass_mg"] == 34.67
    assert x["green_to_white_bract_gross_photosynthesis_mean_ratio"] == 3.5
    assert x["ratio_has_valid_statistical_interval"] is False
    assert x["carbon_translocation_to_seeds_independently_traced"] is False
    assert x["causal_mechanism_isolation_to_photosynthesis_only"] is False
    assert "before full maturity" in x["response"]


def test_independent_2012_resin_contrast_is_not_mislabeled_zero_architecture_cost():
    v = audit_dalechampia_temporal_bracts(source())
    resin = v["resin_cost_2012"]
    assert resin["point_mg"] == -0.66
    assert resin["normal_reference_95_interval_mg"] == [-1.7184, 0.3984]
    assert resin["cost_equivalence_established"] is False
    assert resin["cost_of_structure_or_prior_development_identified"] is False


def test_observational_2013_bract_selection_remains_not_sch_causal_L():
    v = audit_dalechampia_temporal_bracts(source())
    assert v["observational_conflict_2013"]["pollinator_seed_predator_bract_size_opposition_reported"]
    assert v["observational_conflict_2013"]["quantified_sch_L_from_same_experiment"] is False
    assert v["cross_study_joint_fitness_estimated"] is False
    assert v["structural_S_D_worldlines_identified"] is False
    assert v["architecture_cost_K_identified"] is False
    assert v["direct_BALANCE_occupancy_identified"] is False
    assert v["extra_independent_biological_clusters"] == 0


def test_source_numeric_changes_require_new_version_not_silent_reanalysis():
    d = source()
    d["sources"]["postanthesis_2015"]["reported_treatment_minus_unmanipulated_seed_mass"][0]["point_mg"] = -2.0
    with pytest.raises(ValueError, match="numeric anchor changed"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["sources"]["postanthesis_2015"]["control_mean_seed_mass_mg"] = 100
    with pytest.raises(ValueError, match="control mean"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["sources"]["postanthesis_2015"]["area_gross_photosynthesis_umol_m2_s"]["green_bracts_mean"] = 5.0
    with pytest.raises(ValueError, match="published numeric anchor"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["sources"]["resin_cost_2012"]["contrast_seed_mass_mg"] = 0.0
    with pytest.raises(ValueError, match="numeric anchor changed"):
        audit_dalechampia_temporal_bracts(d)


def test_mixing_source_contexts_and_promoting_false_cost_rejected():
    d = source()
    d["cross_source_rule"] = "SAME_CONTEXT_ALGEBRAIC_BRIDGE"
    with pytest.raises(ValueError, match="unrelated"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["inference_limits"]["structural_architecture_cost_identified"] = True
    with pytest.raises(ValueError, match="does not identify"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["inference_limits"]["new_independent_cluster_count"] = 3
    with pytest.raises(ValueError, match="inflate"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["sources"]["resin_cost_2012"]["cost_zero_established"] = True
    with pytest.raises(ValueError, match="not cost equivalence"):
        audit_dalechampia_temporal_bracts(d)


def test_false_2015_outcome_precision_and_source_context_fail_closed():
    d = source()
    d["sources"]["postanthesis_2015"]["sampling_phase"] = "mature lifetime organismal fitness"
    with pytest.raises(ValueError, match="early-harvest"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["sources"]["postanthesis_2015"]["reported_treatment_minus_unmanipulated_seed_mass"][0]["se_mg"] = False
    with pytest.raises(ValueError, match="finite"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["sources"]["postanthesis_2015"]["treatments_are_distinct_independent_maternal_seed_mass_contrasts"] = True
    with pytest.raises(ValueError, match="share maternal"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["sources"]["postanthesis_2015"]["experimental_manipulation_beyond_photosynthesis_possible"] = False
    with pytest.raises(ValueError, match="microclimate"):
        audit_dalechampia_temporal_bracts(d)


def test_missing_gas_covariance_prevents_inferred_ratio_uncertainty():
    d = source()
    d["sources"]["postanthesis_2015"]["area_gross_photosynthesis_umol_m2_s"]["source_does_not_supply_cross_stage_covariance"] = False
    with pytest.raises(ValueError, match="paired uncertainty"):
        audit_dalechampia_temporal_bracts(d)


def test_duplicate_or_missing_treatment_contrast_rejected():
    d = source()
    d["sources"]["postanthesis_2015"]["reported_treatment_minus_unmanipulated_seed_mass"][1] = copy.deepcopy(
        d["sources"]["postanthesis_2015"]["reported_treatment_minus_unmanipulated_seed_mass"][0]
    )
    with pytest.raises(ValueError, match="missing/duplicate"):
        audit_dalechampia_temporal_bracts(d)


def test_invalid_source_DOI_and_missing_covariate_claim():
    d = source()
    d["sources"]["pollinator_antagonist_2013"]["doi"] = "10.unknown/example"
    with pytest.raises(ValueError, match="DOI changed"):
        audit_dalechampia_temporal_bracts(d)
    d = source()
    d["sources"]["pollinator_antagonist_2013"]["causal_sch_conflict_budget_L_measured"] = True
    with pytest.raises(ValueError, match="causal SCH L"):
        audit_dalechampia_temporal_bracts(d)


def test_output_summary_contains_no_source_free_direct_architecture_claim():
    v = audit_dalechampia_temporal_bracts(source())
    assert "positive post-pollination retained-bract female seed-mass benefit" in v["ecological_claim_ceiling"]
    assert v["source_dois"]["postanthesis_2015"] == "10.1111/1365-2435.12427"

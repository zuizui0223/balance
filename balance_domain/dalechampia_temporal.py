"""Quantify *reported* Dalechampia bract benefits without cross-study promotion.

Pélabon et al. 2015: bract removal/shading contrasts for 4-week seed mass.
Pérez-Barrales et al. 2013: observational selection on floral bract size.
Pélabon et al. 2012: a separate greenhouse resin-gland investment assay.

Never combine these distinct cohorts/fitness components into SCH L, K, Phi,
net structural S/D worldlines, or a new independent biological replication.
The normal-reference intervals below use reported point estimates and SEs;
they are NOT the source paper's exact mixed-effects confidence intervals.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from math import isfinite

SCHEMA = "DALECHAMPIA_TEMPORAL_BRACT_SOURCE_V1"
SOURCE_DOIS = {
    "postanthesis_2015": "10.1111/1365-2435.12427",
    "pollinator_antagonist_2013": "10.1111/j.1600-0706.2013.20780.x",
    "resin_cost_2012": "10.1093/aob/mcs091",
}
CONTRASTS = {
    "POSTANTHESIS_BRACTS_REMOVED_MINUS_CONTROL",
    "POSTANTHESIS_BRACTS_SHADED_MINUS_CONTROL",
    "BRAC_EDGE_CUT_CONTROL_MINUS_CONTROL",
}
Z95_REFERENCE = Decimal("1.96")


def _num(value: object, label: str, *, positive=False) -> Decimal:
    if type(value) not in (int, float, Decimal):
        raise ValueError(f"{label} must be a finite reported numeric value")
    try:
        x = Decimal(str(value))
    except (ValueError, InvalidOperation) as exc:
        raise ValueError(f"{label} must be a finite reported numeric value") from exc
    if not x.is_finite() or (positive and x <= 0):
        raise ValueError(f"{label} must be a finite {'positive' if positive else 'numeric'} value")
    return x


def _integer(value: object, label: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{label} must be positive integer")
    return value


def _rounded(v: Decimal, digits: int = 4) -> float:
    out = float(round(v, digits))
    if not isfinite(out):
        raise ValueError("cannot serialize nonfinite source arithmetic")
    return out


def _normal_reference_interval(point: Decimal, se: Decimal) -> list[float]:
    return [_rounded(point - Z95_REFERENCE * se),
            _rounded(point + Z95_REFERENCE * se)]


def audit_dalechampia_temporal_bracts(record: dict) -> dict:
    """Re-express source values on explicitly **separate** estimand lanes."""
    if not isinstance(record, dict) or set(record) != {
        "schema_version", "status", "system", "cross_source_rule",
        "sources", "inference_limits",
    }:
        raise ValueError("Dalechampia source schema differs from registered contract")
    if record["schema_version"] != SCHEMA:
        raise ValueError("Dalechampia schema version mismatch")
    if record["status"] != "SOURCE_REPORTED_ANCHORS_NOT_RAW_DATA":
        raise ValueError("cannot treat source numbers as a raw biological dataset")
    if record["system"] != "Dalechampia scandens":
        raise ValueError("source taxon mismatch")
    if record["cross_source_rule"] != "DISTINCT_CONTEXTS_NO_POOLED_NET_FITNESS_OR_STRUCTURAL_BALANCE":
        raise ValueError("cannot join observational conflict to unrelated experimental fitness")
    source = record["sources"]
    if not isinstance(source, dict) or set(source) != set(SOURCE_DOIS):
        raise ValueError("Dalechampia source coverage mismatch")
    for name, doi in SOURCE_DOIS.items():
        if source[name].get("doi") != doi:
            raise ValueError(f"{name} source DOI changed")
        if not str(source[name].get("url", "")).startswith("https://"):
            raise ValueError(f"{name} original source URL required")

    design = source["postanthesis_2015"]
    if _integer(design.get("n_maternal_plants"), "2015 plant count") != 39:
        raise ValueError("2015 registered source plant count changed")
    if _integer(design.get("n_complete_four_treatments"), "2015 complete cases") != 33:
        raise ValueError("2015 registered four-arm support changed")
    if design.get("sampling_phase") != "seed mass at four weeks after pollination, before full maturity":
        raise ValueError("2015 early-harvest seed-mass estimand changed")
    if design.get("response") != "individual seed mass, mg per seed":
        raise ValueError("2015 response units changed")
    if design.get("treatments_are_distinct_independent_maternal_seed_mass_contrasts") is not False:
        raise ValueError("2015 contrasts share maternal clusters")
    if design.get("experimental_manipulation_beyond_photosynthesis_possible") is not True:
        raise ValueError("2015 bract treatments may also change microclimate/protection")
    control = _num(design.get("control_mean_seed_mass_mg"), "2015 control seed mass", positive=True)
    treatment_rows = design.get("reported_treatment_minus_unmanipulated_seed_mass")
    if not isinstance(treatment_rows, list) or len(treatment_rows) != 3:
        raise ValueError("three published 2015 treatment contrasts required")
    observed_contrasts = set()
    effects = []
    for item in treatment_rows:
        if not isinstance(item, dict) or set(item) != {"contrast", "point_mg", "se_mg"}:
            raise ValueError("2015 contrast source fields changed")
        name = item.get("contrast")
        if name not in CONTRASTS or name in observed_contrasts:
            raise ValueError("missing/duplicate 2015 treatment contrast")
        observed_contrasts.add(name)
        point = _num(item["point_mg"], f"{name}.point_mg")
        se = _num(item["se_mg"], f"{name}.se_mg", positive=True)
        low, high = _normal_reference_interval(point, se)
        effects.append({
            "contrast": name,
            "source_treatment_minus_control_seed_mass_mg": _rounded(point),
            "source_standard_error_mg": _rounded(se),
            "normal_reference_95_interval_mg": [low, high],
            "control_minus_treatment_benefit_mg": _rounded(-point),
            "point_difference_percent_of_reported_control_mean": _rounded(point / control * 100, 2),
            "evidence_of_negative_treatment_effect_under_normal_reference": high < 0,
            "exact_mixed_model_95_interval_reproduced": False,
        })
    if observed_contrasts != CONTRASTS:
        raise ValueError("2015 registered contrast coverage missing")

    gas = design.get("area_gross_photosynthesis_umol_m2_s")
    if not isinstance(gas, dict) or set(gas) != {
        "green_bracts_mean", "green_bracts_se", "white_bracts_mean",
        "white_bracts_se", "leaves_mean", "leaves_se",
        "source_does_not_supply_cross_stage_covariance",
    }:
        raise ValueError("gas exchange values do not match reported source fields")
    if gas["source_does_not_supply_cross_stage_covariance"] is not True:
        raise ValueError("no reported green/white paired uncertainty for ratio")
    green = _num(gas["green_bracts_mean"], "green gas-exchange mean", positive=True)
    white = _num(gas["white_bracts_mean"], "white gas-exchange mean", positive=True)
    for key in ("green_bracts_se", "white_bracts_se", "leaves_mean", "leaves_se"):
        _num(gas[key], f"gas.{key}", positive=True)
    if "not direct isotope tracing" not in design.get("authors_carbon_budget_model", ""):
        raise ValueError("carbon balance calculation is not direct carbon tracing")

    conflict = source["pollinator_antagonist_2013"]
    if not all(conflict.get(key) is True for key in (
        "pollinators_favour_larger_bracts",
        "seed_predators_oviposit_more_on_larger_bracts",
        "net_selection_tended_stabilizing",
    )):
        raise ValueError("2013 observational conflict evidence cannot be silently reassigned")
    if conflict.get("causal_sch_conflict_budget_L_measured") is not False:
        raise ValueError("2013 source does not identify causal SCH L")

    resin = source["resin_cost_2012"]
    if resin.get("reported_table3_contrast") != (
        "removed male inflorescence plus gland minus removed staminate flowers with gland retained"
    ):
        raise ValueError("2012 resin contrast identity changed")
    if _integer(resin.get("n_matched_for_reported_contrast"), "2012 paired support") != 51:
        raise ValueError("2012 source contrast sample count changed")
    if resin.get("reported_seed_mass_cost_detected") is not False or resin.get("cost_zero_established") is not False:
        raise ValueError("2012 nonsignificance is not cost equivalence")
    if resin.get("treatment_occurred_after_gland_development") is not True:
        raise ValueError("2012 manipulation could not remove prior construction costs")
    resin_point = _num(resin.get("contrast_seed_mass_mg"), "2012 resin estimate")
    resin_se = _num(resin.get("contrast_seed_mass_se_mg"), "2012 resin SE", positive=True)
    limits = record.get("inference_limits")
    if not isinstance(limits, dict) or set(limits) != {
        "cross_study_male_and_female_fitness_combined",
        "common_sch_L_and_S_D_worldlines",
        "structural_architecture_cost_identified",
        "direct_structural_balance_occupancy_identified",
        "causal_carbon_transfer_traced_with_label",
        "cross_study_meta_analysis_permitted",
        "new_independent_cluster_count",
    }:
        raise ValueError("source claim ceiling contract missing")
    if any(limits.get(k) is not False for k in limits if k != "new_independent_cluster_count"):
        raise ValueError("source evidence does not identify structural BALANCE or causal carbon tracing")
    if type(limits["new_independent_cluster_count"]) is not int or limits["new_independent_cluster_count"] != 0:
        raise ValueError("cross-publication synthesis cannot inflate independent clusters")
    return {
        "schema_version": "DALECHAMPIA_TEMPORAL_BRACT_REPORTED_READOUT_V1",
        "status": "SOURCE_REPORTED_FUNCTIONAL_RETENTION_BENEFIT_NOT_BALANCE",
        "source_dois": SOURCE_DOIS,
        "reference_interval_rule": "point +/- 1.96 * source SE; normal approximation, not mixed-model interval",
        "postanthesis_2015": {
            "n_maternal_plants": 39,
            "n_complete_four_treatments": 33,
            "response": design["sampling_phase"],
            "reported_control_seed_mass_mg": _rounded(control),
            "contrasts": effects,
            "green_to_white_bract_gross_photosynthesis_mean_ratio": _rounded(green / white, 4),
            "ratio_has_valid_statistical_interval": False,
            "bract_greening_same_anatomical_organ": True,
            "carbon_translocation_to_seeds_independently_traced": False,
            "causal_mechanism_isolation_to_photosynthesis_only": False,
        },
        "observational_conflict_2013": {
            "pollinator_seed_predator_bract_size_opposition_reported": True,
            "quantified_sch_L_from_same_experiment": False,
        },
        "resin_cost_2012": {
            "contrast": resin["reported_table3_contrast"],
            "point_mg": _rounded(resin_point),
            "normal_reference_95_interval_mg": _normal_reference_interval(resin_point, resin_se),
            "cost_equivalence_established": False,
            "cost_of_structure_or_prior_development_identified": False,
        },
        "cross_study_joint_fitness_estimated": False,
        "structural_S_D_worldlines_identified": False,
        "architecture_cost_K_identified": False,
        "direct_BALANCE_occupancy_identified": False,
        "extra_independent_biological_clusters": 0,
        "ecological_claim_ceiling": (
            "positive post-pollination retained-bract female seed-mass benefit in "
            "2015 greenhouse context; 2013 conflict and 2012 resin assays are "
            "separate source contexts; not direct architecture value"
        ),
    }

"""Cross-context floral function-pair multiplex, never a species-level causal trait.

One biological species can be studied for distinct conflicts in distinct
anatomical subsystems and field/laboratory contexts. The source conditional
architecture is indexed by *functional-pair and tested structure*.

This readout joins ALL 22 U2 source-screened original reviewed systems against
the ALL-29-record outcome-enriched plant-macro pilot. It does not select only
conflict-positive results as its sampling frame. Both sources are deliberately
nonexchangeable and all rows remain SCREENED not independently double-coded.

The four overlap cases are a limited *comparative counterexample atlas*, not
four independent new biological clusters, prevalence, a species-level binary
architecture state, a source-independent fitness meta-analysis, or BALANCE
L>0 with separate net structural Delta_W<0.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json

from .plant_macro import load_plant_macro_ledger
from .plant_u2_screen import load_u2_conflict_screen

SCHEMA = "BALANCE_PLANT_CONFLICT_MULTIPLEX_READOUT_V1"
ANCHOR_SCHEMA = "BALANCE_PLANT_CONFLICT_MULTIPLEX_PRIMARY_ANCHORS_V1"
U2 = "U2_BARRETT_2002"
PILOT = "PLANT_PILOT_V1"
ALIAS = {"Solanum_rostratum_historical": "Solanum_rostratum"}
EXPECTED_OVERLAPS = {
    "Narcissus_assoanus",
    "Polemonium_viscosum",
    "Ipomopsis_aggregata",
    "Solanum_rostratum",
}
EXPECTED_CASE_TYPES = {
    "Narcissus_assoanus":
       "WITHIN_FUNCTION_PAIR_LATER_EXPERIMENTAL_POTENTIAL_VERSUS_FIELD",
    "Polemonium_viscosum":
       "DUAL_POSITIVE_DIFFERENT_FUNCTIONS_DIFFERENT_STRUCTURES",
    "Ipomopsis_aggregata":
       "POSITIVE_SEXUAL_INTERFERENCE_VS_NECTAR_ROBBER_UNRESOLVED",
    "Solanum_rostratum":
       "HISTORICAL_NONTEST_VS_MODERN_DIFFERENT_FUNCTION_POSITIVE",
}
REQUIRED_FILES = (
    "data/BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
    "data/BALANCE_PLANT_U2_SCREENING_V1.csv",
    "data/BALANCE_PLANT_MACRO_PILOT_V1.csv",
    "data/BALANCE_PLANT_CONFLICT_MULTIPLEX_PRIMARY_ANCHORS_V1.json",
)


def _canonical(group: str, *, frame: str) -> str:
    if not isinstance(group, str) or not group:
        raise ValueError("source biological group cannot be missing")
    if frame == U2 and group in ALIAS:
        return ALIAS[group]
    if group in ALIAS:
        raise ValueError("historical Solanum label alias only valid in U2 source")
    return group


def _groups(rows: list[dict[str,str]], frame:str) -> dict[str,list[dict[str,str]]]:
    pairs: dict[str,list[dict[str,str]]]=defaultdict(list)
    for r in rows:
        pairs[_canonical(r["dependency_group"],frame=frame)].append(r)
    return dict(pairs)


def _check_source_anchor(anchor: dict) -> None:
    if not isinstance(anchor,dict) or not (
        (isinstance(anchor.get("doi"),str) and len(anchor["doi"])>=12
         and anchor["doi"].startswith("10."))
        or anchor.get("id")=="Todd_1882_American_Naturalist"
    ):
        raise ValueError("each original source anchor requires its exact DOI or registered Todd 1882 identity")
    if not isinstance(anchor.get("confirmed_claim"),str) or len(anchor["confirmed_claim"])<40:
        raise ValueError("source claim explanation missing")
    if not isinstance(anchor.get("role"),str) or not anchor["role"]:
        raise ValueError("source role missing")
    q=anchor.get("quantified_source_values",{})
    if not isinstance(q,dict):
        raise ValueError("source quantitative anchors must remain a dict of published values")
    for k,v in q.items():
        if not isinstance(k,str) or not k or type(v) not in (float,int):
            raise ValueError("quantitative anchors need numeric source figures, not inferred mechanisms")
        if v<0:
            raise ValueError("source-reported reduction magnitude cannot be negative")


def _verified_anchor_registry(registry:dict) -> dict[str,dict]:
    if not isinstance(registry,dict) or registry.get("schema_version")!=ANCHOR_SCHEMA:
        raise ValueError("registered primary-article source schema mismatch")
    if registry.get("status")!="SOURCE_REPORTED_CROSS_CONTEXT_ANCHORS_NO_RAW_REANALYSIS":
        raise ValueError("reported source evidence cannot be labelled raw-data reproduction")
    for key in (
        "review_and_pilot_nonexchangeable",
        "selected_cases_are_intersections_of_COMPLETE_SOURCE_UNIVERSES_NOT_PREVALENCE",
        "independent_double_adjudication_complete",
        "source_effects_on_different_fitness_and_tissue_scales_not_poolable",
        "direct_structural_BALANCE_occupancy_identified",
        "new_independent_biological_clusters",
    ):
        if key not in registry:
            raise ValueError(f"source claim ceiling missing {key}")
    if (registry["review_and_pilot_nonexchangeable"] is not True or
        registry["selected_cases_are_intersections_of_COMPLETE_SOURCE_UNIVERSES_NOT_PREVALENCE"] is not True or
        registry["independent_double_adjudication_complete"] is not False or
        registry["source_effects_on_different_fitness_and_tissue_scales_not_poolable"] is not True or
        registry["direct_structural_BALANCE_occupancy_identified"] is not False or
        type(registry["new_independent_biological_clusters"]) is not int or
        registry["new_independent_biological_clusters"]!=0):
        raise ValueError("cross-source experiment has no qualifying new independent biology or structural BALANCE result")
    if registry.get("sampling_frame_a")!=U2 or registry.get("sampling_frame_b")!=PILOT:
        raise ValueError("source sampling universe identities changed")
    cases=registry.get("cases")
    if not isinstance(cases,list) or len(cases)!=4:
        raise ValueError("four registered within-species cross-frame cases required")
    out={}
    for c in cases:
        if not isinstance(c,dict):
            raise ValueError("case source anchor must be a map")
        group=c.get("dependency_group")
        if group not in EXPECTED_OVERLAPS or group in out:
            raise ValueError("unexpected or duplicate source case")
        if c.get("interpretive_class")!=EXPECTED_CASE_TYPES[group]:
            raise ValueError("source-specific ecological interpretation class altered")
        if c.get("source_contexts_distinct") is not True or (
            c.get("quant_effects_combine_across_studies") is not False
        ):
            raise ValueError("cannot pool source physiological, seed and architecture outcomes")
        original=c.get("source_anchors")
        if not isinstance(original,list) or len(original)!=2:
            raise ValueError("source case must distinguish exactly two published studies")
        for item in original:
            _check_source_anchor(item)
        out[group]=c
    if set(out)!=EXPECTED_OVERLAPS:
        raise ValueError("source registry incompletely represents selected overlap")
    # Lock author/source-specific *quantitative* facts; these are not new
    # estimates. Prevent accidental mixing of incompatible 1989/2001 units.
    pole=out["Polemonium_viscosum"]["source_anchors"]
    narc=out["Narcissus_assoanus"]["source_anchors"]
    if (
        pole[0].get("doi")!="10.1002/j.1537-2197.1989.tb15152.x"
        or pole[1].get("doi")!="10.1111/j.0014-3820.2001.tb01313.x"
        or pole[0].get("quantified_source_values")!={
            "year_one_self_precedence_hours":24,
            "first_year_compatible_pollen_germination_reduction_percent":32,
            "first_year_seed_set_reduction_percent":40,
        } or pole[1].get("quantified_source_values")!={
            "genetic_corolla_length_flare_correlation":0.70
        }
        or narc[1].get("doi")!="10.1111/j.1420-9101.2004.00767.x"
        or narc[1].get("quantified_source_values")!={
            "simultaneous_self_cross_vs_cross_seed_reduction_percent":20,
            "prior_self_24h_then_cross_seed_reduction_percent":60,
        }
    ):
        raise ValueError("original printed effect anchors changed without source review")
    return out


def analyze_flower_multiplex(
    u2_direct_conflict: list[dict[str,str]],
    u2_architecture: list[dict[str,str]],
    plant_pilot: list[dict[str,str]],
    source_registry: dict,
)->dict:
    """One output per overlapping SPECIES, with TWO labelled functional edges."""
    cases=_verified_anchor_registry(source_registry)
    if any(len(rows)!=n for rows,n in [
        (u2_direct_conflict,22),(u2_architecture,22),(plant_pilot,29)
    ]):
        raise ValueError("two entire source frames must be retained: 22+22+29")
    x=_groups(u2_direct_conflict,U2)
    y=_groups(u2_architecture,U2)
    z=_groups(plant_pilot,PILOT)
    if len(x)!=22 or len(y)!=22 or set(x)!=set(y):
        raise ValueError("U2 source conflict/architecture group identities do not align")
    if len(z)!=28:
        raise ValueError("plant macro pilot must preserve 28 unique dependency groups")
    if any(len(r)!=1 for r in x.values()) or any(len(r)!=1 for r in y.values()):
        raise ValueError("U2 biological groups are unique in strict source frame")
    for group in x:
        a,b=x[group][0],y[group][0]
        if a["conflict_status"]!=b["conflict_status"]:
            raise ValueError("U2 strict conflict source versus architecture screen disagrees")
        if b["adjudication_status"]!="SCREENED" or b["primary_model_eligible"]!="false":
            raise ValueError("do not promote U2 source-only rows to confirmatory")
        if b["conflict_family"]!="SEXUAL_INTERFERENCE":
            raise ValueError("U2 sex-function pairing changed")
    if any(
        row["sampling_frame_id"]!=PILOT or row["adjudication_status"]!="SCREENED"
        or row["primary_model_eligible"]!="false"
        for row in plant_pilot
    ):
        raise ValueError("plant pilot cannot become a confirmatory denominator")
    if set(_canonical(g,frame=U2) for g in x)&set(z)!=EXPECTED_OVERLAPS:
        raise ValueError("overlap of U2 complete review and plant pilot differs from predeclared source overlap")
    if set(cases)!=set(x)&set(z):
        raise ValueError("registered source anchors differ from source-screen overlap")

    joined=[]
    for group in sorted(cases):
        u=x[group][0]
        uc=y[group][0]
        pr=z[group]
        if len(pr)!=1 or pr[0]["unit_type"]!="SPECIES":
            raise ValueError("cross-frame focal cases require one explicit species-level pilot row")
        plant=pr[0]
        if not (
            plant["conflict_status"]==cases[group]["expected_pilot"]
            and u["conflict_status"]==cases[group]["expected_u2"]
            and plant["architecture_mode"]==cases[group]["expected_pilot_arch"]
            and uc["architecture_mode"]==cases[group]["expected_u2_arch"]
        ):
            raise ValueError("function-pair source status or architecture altered")
        # Taxonomy equality is checked by accepted *species* rather than
        # automatically fuzzy matching names or silently merging clades.
        if uc["system_taxon"]!=plant["system_taxon"]:
            raise ValueError(f"species identity label mismatch for {group}")
        out={
            "dependency_group":group,
            "taxon":plant["system_taxon"],
            "u2_original_source_id":uc["source_id"],
            "u2_source_basis":uc["source_basis"],
            "u2_tested_pair":[uc["function_a"],uc["function_b"]],
            "u2_structure_tested":uc["shared_structure"],
            "u2_conflict_status":uc["conflict_status"],
            "u2_architecture_mode":uc["architecture_mode"],
            "pilot_original_source_id":plant["source_id"],
            "pilot_source_basis":plant["source_basis"],
            "pilot_tested_pair":[plant["function_a"],plant["function_b"]],
            "pilot_structure_tested":plant["shared_structure"],
            "pilot_conflict_family":plant["conflict_family"],
            "pilot_conflict_status":plant["conflict_status"],
            "pilot_architecture_mode":plant["architecture_mode"],
            "source_indexed_interpretation":cases[group]["interpretive_class"],
            "recorded_studies_have_identical_function_pair_and_structural_coordinate":False,
            "same_population_year_and_field_environment_established":False,
            "both_source_positive_different_architecture":(
                uc["conflict_status"]=="POSITIVE"
                and plant["conflict_status"]=="POSITIVE"
                and uc["architecture_mode"]!=plant["architecture_mode"]
            ),
            "source_anchor_publications":cases[group]["source_anchors"],
            "causal_change_in_architecture_between_studies_established":False,
            "net_structural_BALANCE_identified":False,
            "new_independent_biological_cluster":False,
        }
        joined.append(out)
    positives=[r for r in joined if r["both_source_positive_different_architecture"]]
    if len(positives)!=1 or positives[0]["dependency_group"]!="Polemonium_viscosum":
        raise ValueError("registered dual-positive multipair organization cannot be silently changed")

    return {
        "schema_version":SCHEMA,
        "status":"FOUR_SOURCE_SCREENED_SPECIES_MULTIPLEX_EXAMPLES_NOT_PREVALENCE",
        "total_source_screened_records":len(u2_architecture)+len(plant_pilot),
        "n_distinct_source_dependency_groups":len(set(x)|set(z)),
        "n_u2_strict_sexual_interference_source_species":len(x),
        "n_outcome_enriched_plant_pilot_rows":len(plant_pilot),
        "n_distinct_species_dependency_groups_in_pilot":len(z),
        "n_cross_source_species_overlaps":len(joined),
        "n_source_dual_positive_distinct_architecture_cases":len(positives),
        "n_source_status_asymmetric_or_unresolved_cases":len(joined)-len(positives),
        "registered_taxonomic_merge_alias":{
            "Solanum_rostratum_historical":"Solanum_rostratum"
        },
        "source_cases":joined,
        "new_biological_inference":(
            "Polemonium_viscosum carries directly evidenced interference "
            "for self-versus-outcross pollen, with temporal and spatial "
            "pollen-stigma separation, and a distinct direct "
            "pollinator-versus-ant-predation tradeoff in corolla shape "
            "while corolla remains integrated. Species-level labels "
            "cannot collapse tested function pair and organ/scale."
        ),
        "experimental_vs_field_exposure_modulation_case":"Narcissus_assoanus",
        "source_sample_outcome_blind":False,
        "source_pair_outcomes_and_contexts_nonexchangeable":True,
        "independent_double_coding_completed":False,
        "not_natural_conflict_prevalence":True,
        "not_evolutionary_state_transition":True,
        "not_causal_architecture_value_or_net_fitness":True,
        "structural_BALANCE_occupancy_identified":False,
        "additional_independent_biological_clusters":0,
    }


def analyze_multiplex_sources(paths:dict[str,Path])->dict:
    if set(paths)!=set(REQUIRED_FILES):
        raise ValueError("must provide complete exact 22+29 original source and anchor files")
    original=load_u2_conflict_screen(paths[REQUIRED_FILES[0]])
    arch=load_plant_macro_ledger(paths[REQUIRED_FILES[1]])
    pilot=load_plant_macro_ledger(paths[REQUIRED_FILES[2]])
    anchor=json.loads(paths[REQUIRED_FILES[3]].read_text(encoding="utf-8"))
    out=analyze_flower_multiplex(original,arch,pilot,anchor)
    out["original_source_sha256"]={
        k:hashlib.sha256(p.read_bytes()).hexdigest()
        for k,p in sorted(paths.items())
    }
    return out

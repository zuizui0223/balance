"""Source-screen comparative test: floral conflict is FUNCTION-PAIR specific.

Joins TWO frozen review-defined sampling frames:
  U1 47 plant taxa from broad herbivory/pollination review
  U2 22 species from male/female sexual-interference review

This analysis has an important narrow positive ecological conclusion:
the same two species occur in both frames with NO DEMONSTRATED conflict
under U1 studies but DIRECT POSITIVE interference under U2 studies.
The functions, trait coordinates and primary experiments DIFFER; never
recode this as a temporal ecological state switch in the same flowers.

All values are source-screened, NOT independently double adjudicated,
natural plant-population prevalence, cross-frame exchangeable sampling,
structural BALANCE occupancy, or evidence that conflict is truly absent.
"""
from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path

from .plant_u1_full_screen import build_u1_full47_conflict_screen
from .plant_u1_screen import load_u1_blind_screen
from .plant_u1_production_screen import load_u1_production_blind_screen
from .plant_u2_screen import load_u2_conflict_screen
from .plant_macro import load_plant_macro_ledger, primary_architecture_class

SCHEMA="BALANCE_PLANT_FUNCTION_PAIR_CROSS_FRAME_SCREEN_V1"
U1_FRAME="U1_HAAS_LORTIE_2020_HERBIVORY_POLLINATION"
U2_FRAME="U2_BARRETT_2002_MALE_FEMALE_INTERFERENCE"
U1_CONFLICT_POSITIVE="POSITIVE"
U2_CONFLICT_POSITIVE="POSITIVE"
REGISTERED_OVERLAP={
    "Mimulus_aurantiacus",
    "Ipomopsis_aggregata",
}
U2_POSITIVE_MODES={
    "SHARED_INTEGRATED":4,
    "TEMPORAL_SEPARATION":1,
    "SPATIAL_SEPARATION":1,
    "TEMPORAL_AND_SPATIAL_SEPARATION":1,
    "POLYMORPHIC_OR_MOSAIC":1,
}
HISTORICAL_TAXON_LABEL_ALIASES={
    # Todd's 1882 Cassia chamaecrista label is retained beside the
    # current Chamaecrista fasciculata species name. Never generalize
    # this exception to fuzzy name matching or phylogenetic synonyms.
    "Chamaecrista_fasciculata_historical":(
        "Chamaecrista fasciculata",
        "Chamaecrista fasciculata (Todd: Cassia chamaecrista)",
    ),
}
U2_NEGATIVE_MODES={
    "POLYMORPHIC_OR_MOSAIC":9,
    "SPATIAL_SEPARATION":1,
    "TEMPORAL_SEPARATION":1,
    "UNRESOLVED":3,
}
REQUIRED_SOURCE_PATHS=(
    "data/BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv",
    "data/BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv",
    "data/BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
    "data/BALANCE_PLANT_U2_SCREENING_V1.csv",
)


def _unique_ids(rows:list[dict],key:str,universe:str)->dict[str,dict]:
    grouped={}
    for row in rows:
        value=row.get(key)
        if not isinstance(value,str) or not value:
            raise ValueError(f"{universe} missing biological dependency group")
        if value in grouped:
            raise ValueError(f"{universe} duplicate dependency group {value!r}")
        grouped[value]=row
    return grouped


def analyze_cross_frame_rows(
    u1:list[dict[str,str]],
    u2_conflict:list[dict[str,str]],
    u2_architecture:list[dict[str,str]],
) -> dict:
    """Use all 47+22 source-scope records, not cherry-picked matched positives."""
    if len(u1)!=47:
        raise ValueError("U1 source universe is not the frozen 47 records")
    if len(u2_conflict)!=22 or len(u2_architecture)!=22:
        raise ValueError("U2 conflict + architecture must each cover all 22 source groups")
    actual=[r["universe_record_id"] for r in u1]
    if actual != [f"U1_{i:03d}" for i in range(1,48)]:
        raise ValueError("U1 source universe order/coverage changed")
    if [r["universe_record_id"] for r in u2_conflict]!=[
        f"U2_{i:03d}" for i in range(1,23)
    ]:
        raise ValueError("U2 source universe order/coverage changed")
    U1=_unique_ids(u1,"dependency_group","U1")
    U2=_unique_ids(u2_conflict,"dependency_group","U2 conflict")
    U2arch=_unique_ids(u2_architecture,"dependency_group","U2 architecture")
    if set(U2)!=set(U2arch):
        raise ValueError("different source specimens or taxa in U2 conflict vs architecture")
    if any(r["architecture_status"]!="NOT_IDENTIFIED" for r in u1):
        raise ValueError("U1 conflict source-screen does NOT identify architecture")
    if any(r["screen_decision"] not in {"PASS_CONFLICT_GATE","FAIL_CONFLICT_GATE","HOLD_FOR_FULL_TEXT"} for r in u1):
        raise ValueError("U1 unknown source-screen gate")
    if any(r["sampling_frame_id"]!="U2_BARRETT_2002" or r["adjudication_status"]!="SCREENED"
           or r["primary_model_eligible"]!="false" for r in u2_architecture):
        raise ValueError("U2 remains SCREENED; no confirmatory model eligibility")

    for group,from_source in U2.items():
        a=U2arch[group]
        if from_source["conflict_status"]!=a["conflict_status"]:
            raise ValueError(f"U2 conflict/architecture source disagreement for {group}")
        if from_source["taxon_raw"]!=a["system_taxon"]:
            if (group not in HISTORICAL_TAXON_LABEL_ALIASES or
                    (from_source["taxon_raw"],a["system_taxon"]) !=
                    HISTORICAL_TAXON_LABEL_ALIASES[group]):
                raise ValueError(f"U2 taxon identity discordance for {group}")
        if a["conflict_family"]!="SEXUAL_INTERFERENCE":
            raise ValueError("U2 shared function pair changed to a different mechanism")

    u1counts=Counter(x["conflict_status"] for x in u1)
    u2counts=Counter(x["conflict_status"] for x in u2_conflict)
    if u1counts!={"NO_DEMONSTRATED_CONFLICT":46,"ALIGNED_NO_CONFLICT":1}:
        raise ValueError("frozen U1 positive/negative source-screen result changed")
    if u2counts!={"POSITIVE":8,"NO_DEMONSTRATED_CONFLICT":14}:
        raise ValueError("frozen U2 source-screen status changed")
    positive=[v for v in u2_architecture if v["conflict_status"]=="POSITIVE"]
    nonpositive=[v for v in u2_architecture if v["conflict_status"]!="POSITIVE"]
    p_modes=Counter(r["architecture_mode"] for r in positive)
    n_modes=Counter(r["architecture_mode"] for r in nonpositive)
    if p_modes != U2_POSITIVE_MODES or n_modes != U2_NEGATIVE_MODES:
        raise ValueError("source-screen U2 architecture state distribution changed")

    overlaps=sorted(set(U1)&set(U2))
    if set(overlaps) != REGISTERED_OVERLAP:
        raise ValueError("registered cross-review shared taxa changed")
    matched=[]
    for id_ in overlaps:
        h=U1[id_]
        c=U2[id_]
        a=U2arch[id_]
        if h["taxon_raw"]!=c["taxon_raw"]:
            raise ValueError("same source group has inconsistent taxon name")
        if h["conflict_status"]!="NO_DEMONSTRATED_CONFLICT" or (
            c["conflict_status"]!="POSITIVE"
        ):
            raise ValueError("registered shared-species mechanism asymmetry was altered")
        matched.append({
            "dependency_group":id_,
            "species":c["taxon_raw"],
            "u1_review_frame":U1_FRAME,
            "u1_universe_record":h["universe_record_id"],
            "u1_conflict_status":h["conflict_status"],
            "u1_reason_code":h["reason_code"],
            "u1_source_basis":h["source_basis"],
            "u2_review_frame":U2_FRAME,
            "u2_universe_record":c["universe_record_id"],
            "u2_conflict_status":c["conflict_status"],
            "u2_conflict_reason_code":c["reason_code"],
            "u2_source_basis":c["source_basis"],
            "u2_resolved_architecture_mode":a["architecture_mode"],
            "u2_structural_module_division":a["structural_module_division"],
            "u2_primary_source_basis":a["source_basis"],
            "same_functions_or_trait_coordinate_measured":False,
            "same_population_year_or_experimental_context_established":False,
            "cross_study_interaction_causally_identified":False,
            "absence_of_U1_conflict_proven":False,
            "new_biological_cluster_created":False,
        })

    eligible_arch=[r for r in positive if r["architecture_mode"] not in {
        "POLYMORPHIC_OR_MOSAIC","UNRESOLVED","NA"
    }]
    u2_primary=Counter(primary_architecture_class(r["architecture_mode"])
                       for r in positive)
    return {
        "schema_version":SCHEMA,
        "status":"SCREENED_PAIR_SPECIFIC_CONFLICT_HETEROGENEITY_NOT_CONFIRMATORY",
        "screened_review_frames":{
            "U1":{
                "source_universe":U1_FRAME,
                "n_review_taxon_records":47,
                "source_screen_conflict_status_counts":dict(sorted(u1counts.items())),
                "n_demonstrated_same_coordinate_conflicts":0,
                "architecture_states_inferred":False,
                "independent_double_coding_completed":False,
            },
            "U2":{
                "source_universe":U2_FRAME,
                "n_review_species_records":22,
                "source_screen_conflict_status_counts":dict(sorted(u2counts.items())),
                "n_demonstrated_same_coordinate_conflicts":8,
                "screened_positive_conflict_architecture_mode_counts":dict(sorted(p_modes.items())),
                "screened_no_demonstrated_conflict_architecture_mode_counts":dict(sorted(n_modes.items())),
                "positive_conflict_primary_architecture_classes":dict(sorted(u2_primary.items())),
                "n_source_positive_resolved_architecture":len(eligible_arch),
                "n_source_positive_unresolved_mosaic_architecture":len(positive)-len(eligible_arch),
                "adjudication_status":"SCREENED",
                "independent_double_coding_completed":False,
            },
        },
        "n_source_scope_records_across_frames":69,
        "n_distinct_dependency_groups_across_frames":len(set(U1)|set(U2)),
        "n_shared_species_between_frames":len(matched),
        "shared_species_mechanism_specific_contrasts":matched,
        "ecological_interpretation":(
            "Two source-overlapping species have experimentally demonstrated "
            "male-female reproductive interference in U2 source contexts but "
            "no DEMONSTRATED shared-coordinate herbivory-pollination conflict "
            "in U1 source contexts. This is function-pair/study-context "
            "specificity of conflict evidence, not a same-year ecological "
            "state switch, proof of absence, or a general species prevalence."
        ),
        "nonexchangeable_review_sampling_frames":True,
        "study_designs_or_functions_differ_across_frame_matches":True,
        "positive_source_screen_not_independently_adjudicated":True,
        "do_not_fisher_exact_test_U1_versus_U2":True,
        "not_natural_prevalence_or_survey_inclusion_probability":True,
        "not_net_structural_architecture_fitness_or_BALANCE_occupancy":True,
        "new_independent_biological_clusters":0,
    }


def analyze_cross_frame_sources(paths:dict[str,Path])->dict:
    if set(paths)!=set(REQUIRED_SOURCE_PATHS):
        raise ValueError("must supply all four frozen source ledgers with exact identities")
    u1_first=load_u1_blind_screen(paths[REQUIRED_SOURCE_PATHS[0]])
    u1_later=load_u1_production_blind_screen(paths[REQUIRED_SOURCE_PATHS[1]])
    build_u1_full47_conflict_screen(paths[REQUIRED_SOURCE_PATHS[0]],
                                    paths[REQUIRED_SOURCE_PATHS[1]])
    u2_source=load_u2_conflict_screen(paths[REQUIRED_SOURCE_PATHS[2]])
    u2_modes=load_plant_macro_ledger(paths[REQUIRED_SOURCE_PATHS[3]])
    out=analyze_cross_frame_rows(u1_first+u1_later,u2_source,u2_modes)
    out["original_screening_source_sha256"]={
        key:hashlib.sha256(path.read_bytes()).hexdigest()
        for key,path in sorted(paths.items())
    }
    out["source_file_names_are_provenance_not_current_live_web_queries"]=True
    return out

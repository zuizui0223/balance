"""Source-screen timing x function-pair x architecture common-support audit.

The two original literature screening frames are selected in NONEXCHANGEABLE
ways and are NEVER pooled into prevalence or a causal sample. The source's
'conflict_timing_geometry=SIMULTANEOUS' is a qualitative code, *not* the
same-coordinate pointwise C identified in PAYOFF/SLK, nor a direct observation
of concurrent optimized demands. No row presently measures reversible
within-individual PLASTIC policy fitness or a heritable evolutionary origin.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
from pathlib import Path
from typing import Any

from .plant_architecture_source_patterns import (
    REPO_ROOT, U2_PATH, PILOT_PATH, load_screen
)

TIMING_STATES = {
    "SIMULTANEOUS", "SEQUENTIAL_WITHIN_UNIT", "SEASONALLY_ALTERNATING",
    "MIXED", "CONTEXT_DEPENDENT", "UNRESOLVED",
}
ARCHITECTURE_MODES = {
    "SHARED_INTEGRATED", "TEMPORAL_SEPARATION", "SPATIAL_SEPARATION",
    "TEMPORAL_AND_SPATIAL_SEPARATION", "POLYMORPHIC_OR_MOSAIC",
    "AMONG_FLOWER_MODULE_DIVISION", "WITHIN_FLOWER_DIVISION_OF_LABOUR",
    "UNRESOLVED",
}
STRICT_STRUCTURAL = {
    "AMONG_FLOWER_MODULE_DIVISION", "WITHIN_FLOWER_DIVISION_OF_LABOUR",
}
U3_MATCHED = "data/BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"
U3_DEPENDENCE = "data/BALANCE_PLANT_U3_DEPENDENCE_V1.csv"


def _count(values) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _stratified_screen(
    rows: list[dict[str, str]], source: str, sha: str
) -> dict[str, Any]:
    positive=[x for x in rows if x["conflict_status"]=="POSITIVE"]
    families: dict[str, list[dict[str,str]]] = defaultdict(list)
    for row in positive:
        if row["conflict_timing_geometry"] not in TIMING_STATES:
            raise ValueError("unrecognized source timing geometry")
        if row["architecture_mode"] not in ARCHITECTURE_MODES:
            raise ValueError("unrecognized source architecture")
        families[row["conflict_family"]].append(row)

    family_readouts={}
    conditional_2x2_support=[]
    for family, members in sorted(families.items()):
        simultaneous=[x for x in members if x["conflict_timing_geometry"]=="SIMULTANEOUS"]
        non_sim=[x for x in members if x["conflict_timing_geometry"]!="SIMULTANEOUS"]
        # Use only explicit yes/no structural states in the 2x2 support audit;
        # never silently code source-'unresolved' as 0.
        verified=[x for x in members if x["structural_module_division"] in {"true","false"}]
        cells={
            "simultaneous_structural":sum(
                x["conflict_timing_geometry"]=="SIMULTANEOUS" and
                x["structural_module_division"]=="true" for x in verified),
            "simultaneous_nonstructural":sum(
                x["conflict_timing_geometry"]=="SIMULTANEOUS" and
                x["structural_module_division"]=="false" for x in verified),
            "other_timing_structural":sum(
                x["conflict_timing_geometry"]!="SIMULTANEOUS" and
                x["structural_module_division"]=="true" for x in verified),
            "other_timing_nonstructural":sum(
                x["conflict_timing_geometry"]!="SIMULTANEOUS" and
                x["structural_module_division"]=="false" for x in verified),
        }
        complete=all(value>0 for value in cells.values())
        if complete:
            conditional_2x2_support.append(family)
        family_readouts[family]={
            "positive_source_rows":len(members),
            "timing_codes":_count(x["conflict_timing_geometry"] for x in members),
            "architecture_codes":_count(x["architecture_mode"] for x in members),
            "simultaneous_architecture_codes":_count(
                x["architecture_mode"] for x in simultaneous),
            "structural_statuses":_count(x["structural_module_division"] for x in members),
            "structural_2x2_source_cells":cells,
            "complete_within_family_timing_x_structure_support":complete,
            "source_rows_other_timing":len(non_sim),
        }
    simult=[x for x in positive if x["conflict_timing_geometry"]=="SIMULTANEOUS"]
    return {
        "source":source,
        "source_sha256":sha,
        "source_rows":len(rows),
        "positive_source_rows":len(positive),
        "positive_by_family":family_readouts,
        "positive_source_timing_codes":_count(x["conflict_timing_geometry"] for x in positive),
        "simultaneous_source_tag_count":len(simult),
        "simultaneous_source_architecture_codes":_count(x["architecture_mode"] for x in simult),
        "within_function_family_complete_timing_structural_2x2":conditional_2x2_support,
        "source_timing_tag_is_direct_same_coordinate_C_measurement":False,
        "source_architecture_codes_measure_reversible_phenotypic_policy":False,
        "source_architecture_codes_identify_genetic_origin":False,
    }


def _source_u3(base: Path) -> dict[str, Any]:
    path=base / U3_MATCHED
    dep_path=base / U3_DEPENDENCE
    raw=path.read_bytes(); dep_raw=dep_path.read_bytes()
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    dep=list(csv.DictReader(dep_raw.decode("utf-8-sig").splitlines()))
    required={"pair_id","taxon_role","taxon","architecture_mode",
              "pollen_fate_conflict_status","source_id","extraction_status"}
    if len(rows)!=8 or not required.issubset(rows[0]):
        raise ValueError("U3 must contain the frozen 4 PASS source matched pairs")
    if any(r["extraction_status"]!="EXTRACTED" for r in rows):
        raise ValueError("U3 source extraction not final")
    pairs=defaultdict(dict)
    for r in rows:
        if r["taxon_role"] not in {"CASE","CONTROL"}:
            raise ValueError("unknown case-control source status")
        if r["taxon_role"] in pairs[r["pair_id"]]:
            raise ValueError("duplicate U3 case/control role")
        pairs[r["pair_id"]][r["taxon_role"]]=r
    if len(pairs)!=4 or any(set(x)!={"CASE","CONTROL"} for x in pairs.values()):
        raise ValueError("four PASS matched comparisons required")
    dmap={x["pair_id"]:x for x in dep}
    if len(dmap)!=len(dep) or any(
        key not in dmap or dmap[key]["adjudication_state"]!="PASS"
        or dmap[key]["analysis_inclusion_state"]!="CURRENT_PASS_PAIR"
        for key in pairs
    ):
        raise ValueError("U3 PASS pair/dependence gate is not concordant")
    blocks={dmap[k]["dependence_block_id"] for k in pairs}
    cases=[p["CASE"] for p in pairs.values()]
    controls=[p["CONTROL"] for p in pairs.values()]
    if any(r["architecture_mode"]!="WITHIN_FLOWER_DIVISION_OF_LABOUR"
           or r["pollen_fate_conflict_status"]!="POSITIVE" for r in cases):
        raise ValueError("U3 source case architecture and positive conflict changed")
    unresolved=[r["taxon"] for r in controls if r["pollen_fate_conflict_status"]=="UNRESOLVED"]
    control_positive=[r for r in controls if r["pollen_fate_conflict_status"]=="POSITIVE"]
    return {
        "source":U3_MATCHED,
        "source_sha256":hashlib.sha256(raw).hexdigest(),
        "dependence_source":U3_DEPENDENCE,
        "dependence_source_sha256":hashlib.sha256(dep_raw).hexdigest(),
        "pass_case_control_pairs":len(pairs),
        "independent_frozen_dependence_blocks":len(blocks),
        "case_conflict_positive":len(cases),
        "control_conflict_positive":len(control_positive),
        "unresolved_controls":sorted(unresolved),
        "control_positive_routing_codes":_count(x["architecture_mode"] for x in control_positive),
        "morphology_equivalent_to_routing_proven_false_in_current_source_sample":True,
        "reversible_plasticity_measured_by_this_ledger":False,
        "not_independent_of_u2_or_pilot_without_species_dependency_audit":True,
    }


def analyze(base: Path=REPO_ROOT) -> dict[str, Any]:
    """Read registered files in place. This never opens V4 confirmatory codes."""
    u2,sha2=load_screen(base,U2_PATH,"U2_BARRETT_2002")
    pilot,shaP=load_screen(base,PILOT_PATH,"PLANT_PILOT_V1")
    a=_stratified_screen(u2,U2_PATH,sha2)
    b=_stratified_screen(pilot,PILOT_PATH,shaP)
    u3=_source_u3(base)
    return {
        "schema":"BALANCE_FUNCTION_TIMING_ARCHITECTURE_COMMON_SUPPORT_V1",
        "claim_level":"REAL_ORIGINAL_SOURCE_SCREEN_DESCRIPTIVE_ONLY",
        "U2":a,"PLANT_PILOT":b,"U3":u3,
        "universe_pooled":False,
        "full_conditional_timing_to_structure_effect_identified":False,
        "rule":"SOURCE_TIMING_CODE_DOES_NOT_EQUAL_FUNCTIONAL_OVERLAP_STRENGTH",
        "unresolved_not_absent":True,
        "no_source_receipt_for_reversible_same_individual_policy":True,
        "no_source_receipt_for_matched_S_P_D_total_fitness":True,
        "no_source_receipt_for_heritable_module_origin":True,
        "prohibited_claims":[
            "timing or function-pair effects inferred from unmatched source-selected cases",
            "exact concurrent optima or C inferred from SIMULTANEOUS tag",
            "source timing separation reclassified as genotype-validated reversible plasticity",
            "ecological route conflated with visible stamen heteranthery",
            "U2, pilot and U3 source rows pooled as independent taxa or natural prevalence",
            "structural differentiation caused by observed trade-off",
        ],
    }

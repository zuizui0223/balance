"""Source-preserving mechanism vs visible floral architecture crosscheck.

Joins the *selected* BALANCE U3 matched pollen-fate screen (8 taxon rows,
4 PASS pairs, 3 taxonomic dependence blocks) to *published-article* Clarkia
taxon/mechanism evidence. This is NOT random-sampled angiosperm prevalence,
a statistical meta-effect, a genetically inferred origin, or an estimate of
SCH L, SLK Phi, or PAYOFF environment-memory parameters.

The ecological mechanism is more precise than "heteranthery=yes/no":
  ROLE_DIVISION_WITHIN_FLOWER
  ROLE_DIVISION_AMONG_FLOWERS
  TEMPORAL_POLLEN_DOSING_SOURCE_FAVORED
  UNRESOLVED

Clarkia and Solanum both have distinct anthers, but source investigations
implicate different route classes. Among U3 nonheterantherous controls,
different functional divisions exist despite no focal morphological dimorphism.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

from .clarkia_published_receipts import RECEIPT as CLARKIA_SOURCE, ROOT

U3="data/BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"
DEP="data/BALANCE_PLANT_U3_DEPENDENCE_V1.csv"
ROUTE={
    "WITHIN_FLOWER_DIVISION_OF_LABOUR":"ROLE_DIVISION_WITHIN_FLOWER",
    "AMONG_FLOWER_MODULE_DIVISION":"ROLE_DIVISION_AMONG_FLOWERS",
    "UNRESOLVED":"UNRESOLVED",
}
ALLOWED_MORPH={"CASE":"VISIBLE_HETERANTHERY",
               "CONTROL":"NO_VISIBLE_HETERANTHERY"}
NO_CAUSAL_ORIGIN=True


def _csv(path: Path) -> tuple[list[dict[str,str]],str]:
    blob=path.read_bytes()
    rows=list(csv.DictReader(blob.decode("utf-8-sig").splitlines()))
    if not rows or len(set(rows[0]))!=len(rows[0]):
        raise ValueError("source CSV empty or inconsistent")
    return rows,hashlib.sha256(blob).hexdigest()


def _source_clarkia(path: Path) -> tuple[dict,str]:
    blob=path.read_bytes(); data=json.loads(blob.decode("utf-8"))
    if (data.get("schema")!="BALANCE_CLARKIA_KAY2020_PUBLISHED_STATISTICS_V1"
            or data.get("provenance_status")!="PUBLISHED_ARTICLE_TEXT_NOT_RAW_DATA_REANALYSIS"
            or data.get("source",{}).get("paper_doi")!="10.1098/rspb.2020.2593"
            or data.get("source_data_raw_access_status")!="HOLD_RAW_FILES_401_403"):
        raise ValueError("Clarkia source must remain published-only, raw-HOLD")
    required={"TIMING_11_SPECIES","POLLEN_FATE_CYLINDRICA",
              "DOSE_EXPOSED_POLLEN","DOSE_EXPORTED_POLLEN"}
    raw={r["id"]:r["source_report"] for r in data.get("receipts",[])}
    if not required.issubset(raw) or raw["TIMING_11_SPECIES"]["p"]>=.05:
        raise ValueError("Published timing/functional-source receipt changed")
    if not (raw["POLLEN_FATE_CYLINDRICA"]["p"]>.05
            and raw["DOSE_EXPORTED_POLLEN"]["p"]>.05):
        raise ValueError("Cannot promote no-difference tests to significance")
    return data,hashlib.sha256(blob).hexdigest()


def analyze(base: Path=ROOT) -> dict:
    u3,u3_hash=_csv(base/U3)
    dep,dep_hash=_csv(base/DEP)
    cl,cl_hash=_source_clarkia(base/CLARKIA_SOURCE)
    if len(u3)!=8:
        raise ValueError("Expect original four U3 matched case-control pairs")
    matched=defaultdict(dict)
    for r in u3:
        role=r.get("taxon_role")
        if role not in ALLOWED_MORPH or role in matched[r["pair_id"]]:
            raise ValueError("U3 case/control status not exactly matched")
        matched[r["pair_id"]][role]=r
    if len(matched)!=4 or any(set(g)!=set(ALLOWED_MORPH) for g in matched.values()):
        raise ValueError("U3 original four pairs not preserved")
    d={r["pair_id"]:r for r in dep}
    if len(d)!=len(dep) or any(
        pid not in d or d[pid]["adjudication_state"]!="PASS"
        or d[pid]["analysis_inclusion_state"]!="CURRENT_PASS_PAIR"
        for pid in matched
    ):
        raise ValueError("U3 frozen PASS source dependence not preserved")
    blocks={d[pid]["dependence_block_id"] for pid in matched}
    if blocks!={"U3_DEP_SOLANUM_01","U3_DEP_MELASTOMATEAE_01","U3_DEP_SENNA_01"}:
        raise ValueError("U3 source dependence blocks changed")
    # Frozen unresolved controls are NOT forced to shared/negative or plastic.
    expected_unresolved={
        "Osbeckia chinensis":("UNRESOLVED","UNRESOLVED"),
        "Senna covesii":("UNRESOLVED","POSITIVE"),
    }
    taxa=[]
    for pid in sorted(matched):
        for role in ("CASE","CONTROL"):
            r=matched[pid][role]
            if r["architecture_mode"] not in ROUTE:
                raise ValueError("Unexpected source-defined U3 routing class")
            if role=="CASE" and (
                    r["architecture_mode"]!="WITHIN_FLOWER_DIVISION_OF_LABOUR"
                    or r["pollen_fate_conflict_status"]!="POSITIVE"):
                raise ValueError("Case morphological mechanism changed")
            if r["taxon"] in expected_unresolved and (
                r["architecture_mode"],r["pollen_fate_conflict_status"]
            )!=expected_unresolved[r["taxon"]]:
                raise ValueError("Unresolved source case was promoted without new evidence")
            taxa.append({
                "taxon":r["taxon"],"visible_morphology":ALLOWED_MORPH[role],
                "functional_mechanism":ROUTE[r["architecture_mode"]],
                "pollen_fate_source_status":r["pollen_fate_conflict_status"],
                "tested_focal_role":"U3_"+role,
                "source_programme":"BALANCE_U3_ORIGINAL_STUDY_SCREEN",
                "dependence_block":d[pid]["dependence_block_id"],
                "source_id":r["source_id"],
                "source_evidence_level":"SOURCE_SCREENED_EXPERIMENTAL_ROUTE",
                "reversible_plasticity_not_measured":True,
                "historical_origin_identified":False,
            })
    # Both species are source-study examples; the 2020 study constitutes ONE
    # provenance programme and ONE genus/phylogenetic dependence block.
    for species,fate in (
        ("Clarkia cylindrica","BOTH_WHORLS_SCOPA_AND_STIGMA_NO_DETECTED_DIFFERENCE"),
        ("Clarkia unguiculata","TIMED_EXPOSURE_AND_VISITATION_EXPERIMENT_NO_DIRECT_WHORL_FATE_TEST"),
    ):
        taxa.append({
            "taxon":species,
            "visible_morphology":"VISIBLE_HETERANTHERY",
            "functional_mechanism":"TEMPORAL_POLLEN_DOSING_SOURCE_FAVORED",
            "pollen_fate_source_status":fate,
            "tested_focal_role":"CLARKIA_SOURCE_EXPERIMENTAL_CASE",
            "source_programme":"KAY2020_SAME_PAPER",
            "dependence_block":"CLARKIA_ONE_GENUS_ONE_PAPER",
            "source_id":"Kay_Jogesh_Tataru_Akiba_2020_RSPB_DOI_10.1098/rspb.2020.2593",
            "source_evidence_level":"ORIGINAL_ARTICLE_STATISTICS_ONLY",
            "reversible_plasticity_not_measured":True,
            "historical_origin_identified":False,
        })
    if len(taxa)!=10 or len({r["taxon"] for r in taxa})!=10:
        raise ValueError("Ten unique selected taxa/source contrasts required")
    by_morph=defaultdict(list)
    for r in taxa:
        by_morph[r["visible_morphology"]].append(r)
    observed={
        morph:dict(sorted(Counter(x["functional_mechanism"] for x in group).items()))
        for morph,group in sorted(by_morph.items())
    }
    m_true=[x for x in taxa if x["visible_morphology"]=="VISIBLE_HETERANTHERY"]
    m_false=[x for x in taxa if x["visible_morphology"]=="NO_VISIBLE_HETERANTHERY"]
    return{
        "schema":"BALANCE_POLLEN_ARCHITECTURE_CROSS_MECHANISM_V1",
        "status":"SELECTED_SOURCE_FUNCTIONAL_NONBIJECTION_NOT_MACRO_EFFECT",
        "provenance":{
            "u3_screen_source":U3,"u3_source_sha256":u3_hash,
            "u3_dependence_source":DEP,"u3_dependence_sha256":dep_hash,
            "clarkia_published_source":str(CLARKIA_SOURCE),
            "clarkia_source_sha256":cl_hash,
            "clarkia_raw_source_effects_recomputed":False,
        },
        "distinct_source_taxa":len(taxa),
        "u3_taxon_rows":8,
        "u3_pass_pairs":4,
        "u3_taxonomic_dependence_blocks":len(blocks),
        "clarkia_focal_taxa":2,
        "clarkia_independent_original_papers":1,
        "dependence_blocks_in_combined_selected_comparison":len(blocks)+1,
        "selected_morphology_by_mechanism":observed,
        "visible_heteranthery_cases":len(m_true),
        "no_visible_heteranthery_controls":len(m_false),
        "constructive_morphology_nonidentifiability":{
            "heteranthery_has_both_within_flower_role_division_and_temporal_dosing":(
                observed["VISIBLE_HETERANTHERY"].get("ROLE_DIVISION_WITHIN_FLOWER",0)>0
                and observed["VISIBLE_HETERANTHERY"].get("TEMPORAL_POLLEN_DOSING_SOURCE_FAVORED",0)>0),
            "nonheterantherous_within_flower_role_division_exists":any(
                r["functional_mechanism"]=="ROLE_DIVISION_WITHIN_FLOWER" for r in m_false),
            "nonheterantherous_among_flower_role_division_exists":any(
                r["functional_mechanism"]=="ROLE_DIVISION_AMONG_FLOWERS" for r in m_false),
            "two_control_routes_unresolved":sum(
                r["functional_mechanism"]=="UNRESOLVED" for r in m_false)==2,
        },
        "selected_taxon_evidence_rows":taxa,
        "source_dependent_nonrepresentative_selection":True,
        "not_independent_taxon_macro_prevalence":True,
        "not_real_same_context_S_P_D_comparative_fitness":True,
        "no_reversible_within_genotype_policy_assay":True,
        "no_identified_same_axis_conflict_loss":True,
        "no_genetically_inherited_transition_or_historical_causality":True,
        "no_binary_morphology_determines_mechanism":True,
    }

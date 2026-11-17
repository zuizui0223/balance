#!/usr/bin/env python3
"""Audit two same-paper five-stage co-reports in original 776-effect meta workbook.

Crucial: same paper+species is *not* same experimental contrast or stage
mediation. This is a source identity / grain inspection, not meta-inference.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from scripts.audit_larceny_meta_stage_pairability import (
    SOURCE_SHA256,source_rows
)

STAGES=("nectar volume","visitation rate","pollen deposition","fruit set","seed set")
TARGETS=(
    (29,"Corydalis_caseana","10.1111/oik.05440"),
    (101,"Gentiana_straminea",None),
)

def _summarize_stage(rows:list[dict])->dict:
    values=[float(r["yi"]) for r in rows]
    if not values:
        raise ValueError("Stage is absent from purported five-stage programme")
    sign="positive" if all(v>0 for v in values) else (
         "negative" if all(v<0 for v in values) else "mixed")
    return {
        "n_effects":len(rows),
        "effects":sorted(int(r["ID"]) for r in rows),
        "experiment_levels":sorted({r["experiment_level"] for r in rows}),
        "sign_category":sign,
        "min_lnRR":min(values),
        "max_lnRR":max(values),
        "covariance_with_other_endpoints_in_meta":None,
    }

def inspect_study(records:list[dict],ref_id:int,species:str,doi:str|None)->dict:
    rows=[r for r in records if r["ref-ID"]==ref_id and r["species"]==species]
    if not rows:
        raise ValueError(f"Missing intended original paper/species {ref_id}/{species}")
    stages={stage:_summarize_stage([
        r for r in rows if r["sub_response_variable"]==stage
    ]) for stage in STAGES}
    common=set(stages[STAGES[0]]["experiment_levels"])
    for s in STAGES[1:]:
        common.intersection_update(stages[s]["experiment_levels"])
    f=[r for r in rows if r["sub_response_variable"]=="fruit set"]
    s=[r for r in rows if r["sub_response_variable"]=="seed set"]
    diffs=[float(sr["yi"]-fr["yi"]) for fr,sr in itertools.product(f,s)]
    title_set={str(r["title"]) for r in rows}
    refs={str(r["reference"]) for r in rows}
    if len(title_set)!=1 or len(refs)!=1:
        raise ValueError(f"Source citation text drift for ref-ID {ref_id}")
    return {
        "ref_ID":ref_id,"species":species,"source_title":next(iter(title_set)),
        "meta_reference_label":next(iter(refs)),
        "source_paper_doi":doi,
        "original_publication_doi_independently_confirmed":doi is not None,
        "original_workbook_independently_downloaded_this_audit":False,
        "total_effects":len(rows),
        "stages":stages,
        "all_stages_have_common_experiment_level":bool(common),
        "common_experiment_levels":sorted(common),
        "five_stage_cartesian_products_not_real_paths":math.prod(
            stages[stage]["n_effects"] for stage in STAGES),
        "possible_fruit_seed_cross_products_not_matched_pairs":len(diffs),
        "seed_minus_fruit_all_hypothetical_cross_products":{
            "minimum":min(diffs),"maximum":max(diffs),
            "negative":sum(x<0 for x in diffs),
            "positive":sum(x>0 for x in diffs),
            "zero":sum(x==0 for x in diffs),
            "combinations_are_not_correlated_effect_sizes":True,
        },
        "fruit_minus_seed_order_is_pairing_invariant":all(x<0 for x in diffs) or all(x>0 for x in diffs),
        "shared_experimental_contrast_id_present_in_meta":False,
        "all_five_stages_same_cohort_verified":False,
        "same_treatment_and_control_contrast_verified":False,
        "endpoint_covariance_identified":False,
        "structural_architecture_cost_or_fitness_measured":False,
        "original_plant_study_count_increment":0,
        "provenance_limit":(
            "Published Oikos 2018 and Dryad 10.5061/dryad.bh6hs70 independently verified. "
            "This run reads ONLY the 2025 meta workbook, not Heiling's original 2018 XLSX."
            if ref_id==29 else
            "Meta-workbook gives Zhang et al., 2020 and thesis-like source title; original "
            "publication DOI, original experimental contrasts, individual subjects and "
            "original dataset not independently confirmed here."
        ),
    }

def audit(source:Path)->dict:
    original=source_rows(Path(source))  # exact original SHA, 776 effects, 153 papers gate
    z=[inspect_study(original,*item) for item in TARGETS]
    if [s["total_effects"] for s in z]!=[11,36]:
        raise ValueError("Frozen 2018/2020 source row denominations changed")
    if any(s["all_stages_have_common_experiment_level"] for s in z):
        raise ValueError("Source grain structure changed; require independent re-adjudication")
    return {
       "schema":"BALANCE_2025_META_TWO_FULL_STAGE_SOURCES_IDENTITY_V1",
       "original_meta_xlsx_sha256":SOURCE_SHA256,
       "original_meta_data_doi":"10.6084/m9.figshare.27129204",
       "source_effects":len(original),
       "meta_source_papers":len({r["ref-ID"] for r in original}),
       "paper_species_candidates":len(z),
       "sources":z,
       "scope_guards":{
          "two_existing_published_studies_not_new_study_discoveries":True,
          "five_stage_paper_overlap_does_not_verify_same_flower":True,
          "both_five_stage_programmes_cross_recorded_experiment_levels":True,
          "no_common_treatment_or_control_IDs_in_original_meta":True,
          "no_2020_original_DOI_or_data_fabricated":True,
          "no_reconstructed_experimental_covariance":True,
          "all_cross_products_reported_only_as_hypothetical_ambiguity":True,
          "no_mediation_or_architecture_fitness_claim":True,
          "original_U6_21_taxa_42_coders_V4_outcomes_untouched":True,
       },
       "interpretation":(
          "Heiling Corydalis: independently published prior test of non-discrimination, "
          "visitor prevalence, and pollen saturation, not a newly discovered mechanism. "
          "Zhang Gentiana: published-meta rows show opposite endpoint signs but individual-"
          "flower pollen deposition vs whole-plant fruit/seed units and unknown treatment "
          "match prevent a causal transmission estimate. Zero identified full paths is "
          "lack of source-level linkage, not observed absence of ecological paths."
       ),
    }

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-meta",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=audit(args.original_meta)
    if args.out.exists():
        raise FileExistsError("Refuse overwrite of source-frozen audit")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "sources":[{
            "ref_ID":s["ref_ID"],"species":s["species"],"total_effects":s["total_effects"],
            "common_experiment_levels":s["common_experiment_levels"],
            "hypothetical_five_stage_products":s["five_stage_cartesian_products_not_real_paths"],
            "fruit_seed_diffs":s["seed_minus_fruit_all_hypothetical_cross_products"],
        } for s in result["sources"]]
    },indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()

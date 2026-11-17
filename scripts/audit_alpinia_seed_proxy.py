#!/usr/bin/env python3
"""Alpinia per-opened-flower seed proxy: sampled-fruit sensitivity, not realized fitness.

Uses PLOS 2015 original supplementary S2, 16 summary cells.
Seed-per-flower is an extrapolation assuming sampled mature fruits represent all fruits.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CSV_PATH=ROOT/"data/external/alpinia_2015/S2_EXTRACTED_16_CELLS.csv"
CSV_SHA256="ad52b6ca136b63b9dd049ec01993636869c5e16635c4e2e6b77e96f741ab374c"
PLOS_DOC_SHA256="d3f659090ed0d581e34a45c03e7879e5fb107796f23ea078548be041621880ee"
HEADERS=("year","treatment","direction","inflorescences","flowers","fruits","seeds_in_sample","sampled_fruits")
NUMBERS=("year","inflorescences","flowers","fruits","seeds_in_sample","sampled_fruits")
YEARS=(2005,2007)
DIRS=("W-E","N-S","E-W","S-N")
TREATMENTS=("Robbed","Unrobbed")

def validate(rows:list[dict])->list[dict]:
    if len(rows)!=16:
        raise ValueError("Original source needs exactly 16 summary cells")
    encountered=set()
    for row in rows:
        if tuple(row.keys())!=HEADERS:
            raise ValueError("Source fields and order changed")
        year,treatment,direction=row["year"],row["treatment"],row["direction"]
        if year not in YEARS or treatment not in TREATMENTS or direction not in DIRS:
            raise ValueError("Unexpected study year/treatment/direction")
        key=(year,treatment,direction)
        if key in encountered:
            raise ValueError("Source has duplicate year/treatment/direction")
        encountered.add(key)
        if any(type(row[name]) is not int or row[name]<0 for name in NUMBERS):
            raise ValueError("Source count is not a nonnegative integer")
        if row["inflorescences"]!=60:
            raise ValueError("Original 60-inflorescence cell denominator changed")
        if not 0<row["sampled_fruits"]<=row["fruits"]<=row["flowers"]:
            raise ValueError("Impossible sampled-fruit/fruit/flower denominator")
        if row["seeds_in_sample"]<=0:
            raise ValueError("Original sampled seeds must be positive")
    full={(year,treatment,direction) for year in YEARS for treatment in TREATMENTS for direction in DIRS}
    if encountered!=full:
        raise ValueError("Source has incomplete stratum factorial")
    return rows

def load_csv(path:Path=CSV_PATH)->list[dict]:
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=CSV_SHA256:
        raise ValueError("Original S2 source SHA256 changed")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if tuple(reader.fieldnames or ())!=HEADERS:
        raise ValueError("Original source header changed")
    return validate([{key:(v if key in ("treatment","direction") else int(v))
                      for key,v in row.items()} for row in reader])

def _stage(rows:list[dict])->dict:
    flowers=sum(row["flowers"] for row in rows)
    fruits=sum(row["fruits"] for row in rows)
    seeds=sum(row["seeds_in_sample"] for row in rows)
    sampled=sum(row["sampled_fruits"] for row in rows)
    fruit_rate=fruits/flowers
    seeds_per_fruit=seeds/sampled
    return {
        "flower_n":flowers,"fruit_n":fruits,"sampled_fruit_n":sampled,
        "seeds_counted_in_sample":seeds,"fruit_set_fraction":fruit_rate,
        "sampled_seed_per_fruit":seeds_per_fruit,
        "sampled_fruit_fraction":sampled/fruits,
        "seed_per_original_flower_proxy":fruit_rate*seeds_per_fruit,
    }

def _contrast(robbed:dict,unrobbed:dict)->dict:
    rf=robbed["fruit_set_fraction"]/unrobbed["fruit_set_fraction"]
    rs=robbed["sampled_seed_per_fruit"]/unrobbed["sampled_seed_per_fruit"]
    ri=rf*rs
    return {
        "robbed_to_unrobbed_fruit_set_ratio":rf,
        "robbed_to_unrobbed_sampled_seed_per_fruit_ratio":rs,
        "seed_per_flower_proxy_ratio":ri,
        "seed_per_flower_proxy_relative_difference":ri-1,
        "required_seed_per_fruit_ratio_for_break_even":1/rf,
        "relative_multiplier_needed_to_erase_proxy_deficit":1/ri if ri<1 else None,
        "equal_opposite_relative_mean_errors_required":(1-ri)/(1+ri) if ri<1 else 0,
        # Scenario only: true mean of ALL fruits differs by at most +/- eps
        # from observed sampled-fruit mean, independently in each plot class.
        "ratio_band_if_sample_mean_bias_at_most_15pct":[ri*.85/1.15,ri*1.15/.85],
        "ratio_band_if_sample_mean_bias_at_most_20pct":[ri*.80/1.20,ri*1.20/.80],
    }

def analyze(rows:list[dict])->dict:
    validate(rows)
    get=lambda year,t:[r for r in rows if (year is None or r["year"]==year) and r["treatment"]==t]
    overall={t.lower():_stage(get(None,t)) for t in TREATMENTS}
    pooled=_contrast(overall["robbed"],overall["unrobbed"])
    years={}
    for year in YEARS:
        yr={t.lower():_stage(get(year,t)) for t in TREATMENTS}
        years[str(year)]={**yr,**_contrast(yr["robbed"],yr["unrobbed"])}
    strata=[]
    for year in YEARS:
        for direction in DIRS:
            robbed=_stage([r for r in rows if r["year"]==year and r["direction"]==direction and r["treatment"]=="Robbed"])
            unrobbed=_stage([r for r in rows if r["year"]==year and r["direction"]==direction and r["treatment"]=="Unrobbed"])
            cr=_contrast(robbed,unrobbed)
            strata.append({
                "year":year,"direction":direction,
                "robbed_seed_per_flower_proxy":robbed["seed_per_original_flower_proxy"],
                "unrobbed_seed_per_flower_proxy":unrobbed["seed_per_original_flower_proxy"],
                "seed_per_flower_proxy_ratio":cr["seed_per_flower_proxy_ratio"],
                "fruit_set_fraction_difference":robbed["fruit_set_fraction"]-unrobbed["fruit_set_fraction"],
                "sampled_seed_per_fruit_difference":robbed["sampled_seed_per_fruit"]-unrobbed["sampled_seed_per_fruit"],
            })
    return {
        "schema":"BALANCE_ALPINIA_2015_SAMPLED_FRUIT_SEED_PROXY_V1",
        "claim_level":"CONDITIONAL_COMPOSITE_INDEX_NOT_REALIZED_FEMALE_FITNESS",
        "original_source_doi":"10.1371/journal.pone.0144585",
        "original_s2_doc_sha256":PLOS_DOC_SHA256,
        "source_csv_sha256":CSV_SHA256,
        "source_n_cells":len(rows),"overall":overall,"pooled":pooled,"years":years,
        "year_direction":{
            "rows":strata,
            "lower_proxy_in_robbed":sum(s["seed_per_flower_proxy_ratio"]<1 for s in strata),
            "equal_stratum_proxy_ratio":sum(s["robbed_seed_per_flower_proxy"] for s in strata)/sum(s["unrobbed_seed_per_flower_proxy"] for s in strata),
            "min_stratum_proxy_ratio":min(s["seed_per_flower_proxy_ratio"] for s in strata),
            "max_stratum_proxy_ratio":max(s["seed_per_flower_proxy_ratio"] for s in strata)},
        "claim_guards":{
            "seeds_per_flower_proxy_is_directly_measured":False,
            "population_average_seed_per_fruit_verified":False,
            "experimental_squirrel_robbing_causal_effect_estimated":False,
            "independent_cluster_robust_ci_identified_from_s2":False,
            "true_seed_set_percentage_from_ovule_denominator":False,
            "strict_BALANCE_worldline_measured":False,
            "eight_strata_are_independent_evolutionary_replicates":False,
            "original_V4_independent_coder_outcomes_changed":False,
        },
        "interpretation":"Product of fruit-set fraction and mean seeds per sampled mature fruit. It is an index assuming sampled fruits represent all fruit. No source-observed realized seeds per flower, causal treatment response, or architectural fitness is identified.",
    }

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=CSV_PATH)
    parser.add_argument("--original-doc",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.original_doc and hashlib.sha256(args.original_doc.read_bytes()).hexdigest()!=PLOS_DOC_SHA256:
        raise ValueError("Original PLOS S2 DOC SHA256 does not match")
    result=analyze(load_csv(args.source))
    if args.output.exists():
        raise FileExistsError("Refuse overwrite source-authenticated readout")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"overall":result["overall"],"pooled":result["pooled"],
                      "year_direction":{k:v for k,v in result["year_direction"].items() if k!="rows"}},indent=2))
if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Published PLOS 2015 Alpinia S2 stage audit, independent of V4 model/outcomes.

Data grain: 16 summary cells (year x robbed status x compass direction).
Individual flower / inflorescence responses are NOT available in S2.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CSV_PATH = BASE / "data/external/alpinia_2015/S2_EXTRACTED_16_CELLS.csv"
CSV_SHA256 = "ad52b6ca136b63b9dd049ec01993636869c5e16635c4e2e6b77e96f741ab374c"
ORIGINAL_DOC_SHA256 = "d3f659090ed0d581e34a45c03e7879e5fb107796f23ea078548be041621880ee"
COLS = ("year","treatment","direction","inflorescences","flowers","fruits","seeds_in_sample","sampled_fruits")
N = ("inflorescences","flowers","fruits","seeds_in_sample","sampled_fruits")
DIRS = ("W-E","N-S","E-W","S-N")

def validate(rows):
    if len(rows) != 16:
        raise ValueError("Expected 16 source summary cells")
    keys = set()
    for row in rows:
        if set(row) != set(COLS):
            raise ValueError("Changed source columns")
        key = row["year"],row["treatment"],row["direction"]
        if key in keys:
            raise ValueError("Duplicate source stratum")
        keys.add(key)
        if row["year"] not in (2005,2007) or row["treatment"] not in ("Robbed","Unrobbed") or row["direction"] not in DIRS:
            raise ValueError("Unexpected source year, treatment or direction")
        if any(type(row[c]) is not int or row[c] < 0 for c in N):
            raise ValueError("Non-integer or negative source value")
        if row["inflorescences"] != 60 or not 0 < row["sampled_fruits"] <= row["fruits"] <= row["flowers"]:
            raise ValueError("Invalid source denominator or number of fruits")
    expected = {(y,t,d) for y in (2005,2007) for t in ("Robbed","Unrobbed") for d in DIRS}
    if keys != expected:
        raise ValueError("Incomplete source design")
    return rows

def load_csv(path=CSV_PATH):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != CSV_SHA256:
        raise ValueError("Original S2 16-cell extract checksum changed")
    import io
    rd=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if tuple(rd.fieldnames or ()) != COLS:
        raise ValueError("Source field names changed")
    return validate([{
        k: v if k in ("treatment","direction") else int(v)
        for k,v in row.items()
    } for row in rd])

def extract_source_doc_text(text):
    """Read antiword output, including blank inherited year and treatment cells."""
    rows=[]
    year=None
    treatment=None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        p=[x.strip() for x in line.strip().strip("|").split("|")]
        if len(p)!=7 or p[2] not in DIRS:
            continue
        if p[0]:
            year=int(p[0])
        if p[1]:
            treatment=p[1]
        if year is None or treatment is None:
            raise ValueError("Missing year or treatment in original S2")
        z=p[6].split("/")
        if len(z)!=2:
            raise ValueError("Sampled fruits denominator missing")
        a=[int(p[3]),int(p[4]),int(p[5]),int(z[0]),int(z[1])]
        rows.append(dict(zip(COLS,(year,treatment,p[2],*a))))
    return validate(rows)

def _pool(rows):
    out={k:sum(r[k] for r in rows) for k in N}
    out["fruit_set_rate"]=out["fruits"]/out["flowers"]
    # A S2 seed count divided by sampled FRUITS is not % of ovules fertilized.
    out["seeds_per_sampled_fruit"]=out["seeds_in_sample"]/out["sampled_fruits"]
    return out

def analyze(rows):
    validate(rows)
    treatments=("Robbed","Unrobbed")
    main={t:_pool([r for r in rows if r["treatment"]==t]) for t in treatments}
    years={str(y):{t:_pool([r for r in rows if r["year"]==y and r["treatment"]==t])
                    for t in treatments} for y in (2005,2007)}
    index={(r["year"],r["direction"],r["treatment"]):r for r in rows}
    pairs=[]
    for y in (2005,2007):
        for direction in DIRS:
            robbed=index[y,direction,"Robbed"]
            intact=index[y,direction,"Unrobbed"]
            fruit_diff=robbed["fruits"]/robbed["flowers"]-intact["fruits"]/intact["flowers"]
            seed_diff=robbed["seeds_in_sample"]/robbed["sampled_fruits"]-intact["seeds_in_sample"]/intact["sampled_fruits"]
            pairs.append({"year":y,"direction":direction,
                          "fruit_rate_difference":fruit_diff,
                          "seeds_per_sampled_fruit_difference":seed_diff})
    a,b=main["Robbed"],main["Unrobbed"]
    fd=[p["fruit_rate_difference"] for p in pairs]
    sd=[p["seeds_per_sampled_fruit_difference"] for p in pairs]
    return {
      "schema":"BALANCE_ALPINIA_2015_ORIGINAL_STAGE_GATE_V1",
      "original_article_doi":"10.1371/journal.pone.0144585",
      "source_supplement":"https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0144585.s002&type=supplementary",
      "original_doc_sha256":ORIGINAL_DOC_SHA256,
      "source_16cell_csv_sha256":CSV_SHA256,
      "sampling":"aggregated original S2 only; year x direction x natural robbery/guarded plot status",
      "by_treatment":main,
      "by_year":years,
      "contrasts":{
          "fruit_rate_difference_percentage_points":100*(a["fruit_set_rate"]-b["fruit_set_rate"]),
          "fruit_rate_ratio":a["fruit_set_rate"]/b["fruit_set_rate"],
          "fruit_rate_negative_cells":sum(v<0 for v in fd),
          "seed_per_sampled_fruit_difference":a["seeds_per_sampled_fruit"]-b["seeds_per_sampled_fruit"],
          "sampled_seed_negative_cells":sum(v<0 for v in sd),
          "sampled_seed_positive_cells":sum(v>0 for v in sd),
          "sampled_seed_zero_cells":sum(v==0 for v in sd),
      },
      "paired_source_strata":pairs,
      "claim_guards":{
          "not_eight_independent_biological_studies":True,
          "cannot_infer_seed_set_percentage_without_ovule_denominator":True,
          "no_individual_flower_or_inflorescence_rows":True,
          "no_source_supported_clustered_confidence_interval":True,
          "no_causal_nectar_only_effect":True,
          "no_shared_vs_separate_architecture_fitness_test":True,
          "no_original_U6_V4_architecture_changes":True,
      }
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-doc",type=Path)
    p.add_argument("--antiword-text",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    rows=load_csv()
    if args.source_doc:
        if hashlib.sha256(args.source_doc.read_bytes()).hexdigest()!=ORIGINAL_DOC_SHA256:
            raise ValueError("Original PLOS S2 DOC source SHA256 mismatch")
    if args.antiword_text:
        observed=extract_source_doc_text(args.antiword_text.read_text(encoding="utf-8"))
        if observed != rows:
            raise ValueError("Source DOC text and frozen 16-cell CSV differ")
    result=analyze(rows)
    if args.output.exists():
        raise FileExistsError("Refuse overwriting original-source results")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(result["contrasts"],indent=2))

if __name__=="__main__":
    main()

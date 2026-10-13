"""Exact-source 2013 Pedicularis fruit-set ANCOVA sensitivity, not inference.

Only the original 74-row fit is compared with the published F. Exclusions
and leave-one-out analyses are post-outcome robustness diagnostics. No patch
IDs, fruit counts or original SPSS syntax are reconstructed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import tempfile
from pathlib import Path
from zipfile import ZipFile

from scripts.adjudicate_pedicularis_2013_raw_workbook import (
    SOURCE_SHA256, _invert, ancova_fruit_set,
)
from scripts.audit_pedicularis_2013_fruit_set_ancova import load_fruit_rows
from scripts.retrieve_pedicularis_2013_dryad_bytes import verify_zip

ROOT = Path(__file__).resolve().parents[1]
ZIP_SHA256 = "e002c369ad864c2de22365b070c0551370c5d6c2cd6a10f80655865f0612f185"


def fit(rows, *, coding="effect", response_divisor=1.0):
    """One five-parameter row-level OLS; report F and adjusted contrasts."""
    if coding not in ("effect", "dummy"):
        raise ValueError("invalid factor coding")
    if not math.isfinite(response_divisor) or response_divisor <= 0:
        raise ValueError("invalid response divisor")
    rows = list(rows)
    if len(rows) < 10:
        raise ValueError("insufficient source rows")
    for r in rows:
        if len(r) != 6 or any(
            isinstance(r[i], bool) or r[i] not in (1, 2) for i in range(3)
        ):
            raise ValueError("invalid source category")
        if (isinstance(r[3], bool) or not isinstance(r[3], (int, float))
            or not math.isfinite(r[3]) or r[3] <= 0 or int(r[3]) != r[3]):
            raise ValueError("invalid flower count")
        if (isinstance(r[4], bool) or not isinstance(r[4], (int, float))
            or not math.isfinite(r[4]) or not 0 <= r[4] <= 100):
            raise ValueError("invalid fruit-set percent")
    n, k = len(rows), 5
    mean_flowers = math.fsum(r[3] for r in rows)/n
    encode = (lambda v: 2*v-3) if coding == "effect" else (lambda v: v-1)
    x = [[1., float(encode(r[0])), float(encode(r[1])),
          float(encode(r[0])*encode(r[1])), float(r[3]-mean_flowers)]
         for r in rows]
    y = [float(r[4])/response_divisor for r in rows]
    gram = [[math.fsum(v[i]*v[j] for v in x) for j in range(k)]
            for i in range(k)]
    inv = _invert(gram)
    xy = [math.fsum(v[i]*yy for v, yy in zip(x, y)) for i in range(k)]
    beta = [math.fsum(inv[i][j]*xy[j] for j in range(k))
            for i in range(k)]
    rss = math.fsum((yy-math.fsum(a*b for a,b in zip(v,beta)))**2
                    for v,yy in zip(x,y))
    df = n-k
    if rss <= 1e-24*max(1.,math.fsum(yy*yy for yy in y)):
        raise ValueError("zero or degenerate residual uncertainty")
    f = {name: beta[i]**2/((rss/df)*inv[i][i])
         for i,name in enumerate(("year","density","interaction","flowers"),1)}
    if any(not math.isfinite(v) or v < 0 for v in f.values()):
        raise ValueError("invalid F statistic")
    if coding=="effect":
        contrast={"2005":2*(beta[2]-beta[3])*response_divisor,
                  "2011":2*(beta[2]+beta[3])*response_divisor}
    else:
        contrast={"2005":beta[2]*response_divisor,
                  "2011":(beta[2]+beta[3])*response_divisor}
    return {
        "n":n,"df_residual":df,"F":f,
        "interaction_partial_eta_squared":f["interaction"]/(f["interaction"]+df),
        "conditional_dense_minus_sparse_fruit_set_pp":contrast,
        "patch_cluster_robust":False,
    }


def diagnose(rows, four_rows, sixteen_rows, original_receipt):
    """Source-defined case deletions and all-rows leave-one-out sensitivity."""
    rows = list(rows)
    four, sixteen = set(four_rows), set(sixteen_rows)
    if len(rows)!=74 or len(four)!=4 or len(sixteen)!=16 or four & sixteen:
        raise ValueError("expected 74 rows and distinct 4+16 source flags")
    if min(four|sixteen)<2 or max(four|sixteen)>75:
        raise ValueError("flagged Excel row outside original fruit sheet")
    cases={}
    for name, drop in (
        ("all_74",set()),
        ("exclude_four_fruit_set_denominator_flags",four),
        ("exclude_twenty_nested_denominator_flags",four|sixteen),
    ):
        sample=[r for i,r in enumerate(rows,2) if i not in drop]
        out=fit(sample)
        ref=ancova_fruit_set(sample)
        if any(abs(out["F"][key]-ref["F"][key])>1e-7 for key in out["F"]):
            raise ValueError("published-model OLS engine and diagnostic disagree")
        cases[name]={"excluded_source_excel_rows":sorted(drop),**out}
    base=cases["all_74"]["F"]
    original=original_receipt.get("comparisons",{})
    if set(original)!=set(base) or any(
        abs(base[key]-original[key]["recomputed_F"])>1e-7 for key in base
    ):
        raise ValueError("previously frozen full 74-row source fit changed")
    coding=fit(rows,coding="dummy")["F"]["interaction"]
    fraction=fit(rows,response_divisor=100.)["F"]["interaction"]
    if any(abs(value-base["interaction"])>1e-7 for value in (coding,fraction)):
        raise ValueError("interaction changed under invariant coding or scaling")
    loo=[(i,fit([r for j,r in enumerate(rows,2) if j!=i])["F"]["interaction"])
         for i in range(2,76)]
    values=[f for _,f in loo]
    most_changed=sorted(loo,key=lambda pair:abs(pair[1]-base["interaction"]),
                        reverse=True)[:5]
    return {
        "schema_version":"PEDICULARIS_2013_FRUIT_SET_SENSITIVITY_V1",
        "status":"SOURCE_VERIFIED_SENSITIVITY_PUBLISHED_INTERACTION_UNRESOLVED",
        "published_full_interaction_F":original["interaction"]["published_F"],
        "full_interaction_F_matched":original["interaction"]["matches_printed_precision"],
        "original_24F_replay_unchanged":True,
        "source_defined_fruit_set_flag_rows":sorted(four),
        "source_defined_predation_flag_rows":sorted(sixteen),
        "models":cases,
        "coding_invariance":{
            "effect_coding_interaction_F":base["interaction"],
            "dummy_coding_interaction_F":coding,
            "fraction_response_interaction_F":fraction},
        "leave_one_spike_out_interaction_F":{
            "n_fits":len(loo),"min":min(values),"median":statistics.median(values),
            "max":max(values),
            "five_largest_abs_changes":[
                {"excel_row":i,"interaction_F":f,
                 "abs_change":abs(f-base["interaction"])}
                for i,f in most_changed]},
        "exclusion_fits_are_not_original_2013_model_reproduction":True,
        "source_error_proven":False,
        "post_outcome_exploratory_not_confirmatory":True,
        "original_SPSS_code_recovered":False,
        "actual_patch_membership_known":False,
        "causal_density_or_BALANCE_claim_identified":False,
    }


def audit_zip(source_zip):
    data=Path(source_zip).read_bytes()
    if hashlib.sha256(data).hexdigest()!=ZIP_SHA256:
        raise ValueError("source ZIP hash drifted")
    meta=verify_zip(data)
    if meta["source_sha256"]!=SOURCE_SHA256:
        raise ValueError("original XLSX hash drifted")
    with ZipFile(source_zip) as z:
        workbook_data=z.read("raw data.xlsx")
    with tempfile.TemporaryDirectory(prefix="pedicularis-ancova-") as dirname:
        workbook=Path(dirname)/"raw data.xlsx"
        workbook.write_bytes(workbook_data)
        rows,groups=load_fruit_rows(workbook)
        freeze=json.loads((ROOT/"data/PEDICULARIS_2013_FRUIT_INTEGER_DENOMINATOR_FREEZE_V1.json").read_text())
        if freeze.get("original_workbook_sha256")!=SOURCE_SHA256 or freeze.get("biological_rows")!=74:
            raise ValueError("source denominator manifest drifted")
        original=json.loads((ROOT/"data/PEDICULARIS_2013_FRUIT_SET_ANCOVA_AUDIT_V1.json").read_text())
        report=diagnose(rows,
            freeze["fruit_set_integer_incompatible_source_excel_rows"],
            freeze["predation_given_compatible_fruit_incompatible_source_excel_rows"],
            original)
        report.update({
            "verified_original_workbook_sha256":SOURCE_SHA256,
            "verified_original_zip_sha256":ZIP_SHA256,
            "source_group_counts":groups,
            "source_excel_rows":[2,75],
            "source_original_bytes_verified":True})
        return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():
        raise ValueError("refusing to overwrite source receipt")
    report=audit_zip(args.source_zip)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("x",encoding="utf-8") as f:
        json.dump(report,f,indent=2,sort_keys=True)
        f.write("\n")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()

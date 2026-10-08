"""Exact-source 2013 Pedicularis workbook audit and published ANOVA reproduction.

Requires artifact_tool *only when reading the XLSX*. The published ANOVA F
statistics are replicated with ordinary unclustered 2x2 effect-coded OLS.
This is a numerical/model-specification reproduction, not a cluster-robust
density analysis: the original workbook contains no plant_id or patch_id.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

SOURCE_SHA256 = "d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380"
SOURCE_BYTES = 89597
SOURCE_MD5 = "10a98383677bbd2a01e19a86c350fdd3"
FRUIT_SHEET = "fruit set and fruit predation"
SEED_SHEET = "seed set and seed predatioin"
EXPECTED_FRUIT_HEADER = [
    "year","density","size","flowers","fruit set","fruit predation"
]
EXPECTED_SEED_HEADER = [
    "year","density","size","intial seed set","fianl seed set",
    "seed predation"
]
EXPECTED_COUNTS_FRUIT = {
    "2005_sparse_large": 6, "2005_dense_large": 10,
    "2011_sparse_small": 9, "2011_sparse_large": 17,
    "2011_dense_small": 7, "2011_dense_large": 25,
}
EXPECTED_COUNTS_SEED = {
    "2005_sparse_large": 273, "2005_dense_large": 308,
    "2011_sparse_small": 391, "2011_sparse_large": 679,
    "2011_dense_small": 187, "2011_dense_large": 1092,
}

# Published Xia et al. Biology Letters (2013) table values are F statistics
# for density, factor (year in Table 1 or size in Table 2) and interaction.
PUBLISHED_F = {
    "Table1_initial_seed_set": {
        "factor": 0.507, "density": 3.767, "interaction": 1.241,
        "n": 2602, "df_residual": 2598
    },
    "Table1_final_seed_set": {
        "factor": 11.954, "density": 39.025, "interaction": 0.426,
        "n": 2930, "df_residual": 2926
    },
    "Table1_seed_predation": {
        "factor": 46.571, "density": 166.220, "interaction": 4.250,
        "n": 2930, "df_residual": 2926
    },
    "Table2_initial_seed_set": {
        "factor": 41.221, "density": 27.348, "interaction": 44.556,
        "n": 2051, "df_residual": 2047
    },
    "Table2_final_seed_set": {
        "factor": 1.025, "density": 26.958, "interaction": 0.023,
        "n": 2349, "df_residual": 2345
    },
    "Table2_seed_predation": {
        "factor": 45.029, "density": 317.878, "interaction": 106.270,
        "n": 2349, "df_residual": 2345
    },
}


def _invert(a):
    n = len(a)
    aug = [[float(x) for x in row] +
           [float(i == j) for j in range(n)]
           for i, row in enumerate(a)]
    magnitude = max(abs(x) for row in a for x in row)
    if not magnitude:
        raise ValueError("empty or singular regression")
    for i in range(n):
        pivot = max(range(i,n), key=lambda j: abs(aug[j][i]))
        if abs(aug[pivot][i]) < magnitude*1e-12:
            raise ValueError("regression rank deficiency")
        aug[i],aug[pivot] = aug[pivot],aug[i]
        v = aug[i][i]
        aug[i] = [x/v for x in aug[i]]
        for j in range(n):
            if i != j:
                mul = aug[j][i]
                aug[j] = [x-mul*y for x,y in zip(aug[j],aug[i])]
    return [row[n:] for row in aug]


def anova_two_factor(rows, outcome, factor):
    """Effect coding: x=(2*code-3). Returns unclustered coefficient t-squared."""
    selected = [r for r in rows if r[outcome] is not None]
    n = len(selected)
    if n < 8:
        raise ValueError("insufficient outcome support")
    x = [
        [1.0,float(2*r[factor]-3),float(2*r[1]-3),
         float((2*r[factor]-3)*(2*r[1]-3))]
        for r in selected
    ]
    y = [float(r[outcome]) for r in selected]
    k = 4
    gram = [[math.fsum(v[i]*v[j] for v in x) for j in range(k)]
            for i in range(k)]
    inv = _invert(gram)
    xy = [math.fsum(v[i]*yy for v,yy in zip(x,y)) for i in range(k)]
    beta = [math.fsum(inv[i][j]*xy[j] for j in range(k))
            for i in range(k)]
    rss = math.fsum((yy-math.fsum(a*b for a,b in zip(v,beta)))**2
                    for v,yy in zip(x,y))
    df = n-k
    if df <= 0 or rss <= 1e-24*max(1.0,math.fsum(yy*yy for yy in y)):
        raise ValueError("degenerate outcome, no residual uncertainty")
    mse = rss/df
    stats = [(beta[i]**2)/(mse*inv[i][i]) for i in (1,2,3)]
    if any(not math.isfinite(s) or s < 0 for s in stats):
        raise ValueError("nonfinite F statistic")
    return {
        "n": n, "df_residual": df, "factor": stats[0],
        "density": stats[1], "interaction": stats[2],
        "inferential_unit": "FLOWER_CAPSULE_ROW_UNCLUSTERED",
        "patch_cluster_robust": False,
    }


def _source_rows(header, data, expected_header, group_count):
    if list(header) != expected_header:
        raise ValueError("published source workbook column schema changed")
    if len(data) != sum(group_count.values())+2:
        raise ValueError("source worksheet data/legend row count changed")
    if (data[-2][:3] != ["1=2005","1=sparse","1=small"]
            or data[-1][:3] != ["2=2011","2=dense","2=large"]):
        raise ValueError("source category legend changed")
    rows = data[:-2]
    counts = Counter()
    for row in rows:
        if len(row) != 6 or any(row[j] not in (1,2) for j in (0,1,2)):
            raise ValueError("source group factor code invalid")
        if any(row[j] is None for j in (4,5)):
            raise ValueError("required final outcome missing")
        if any(not isinstance(row[j],(int,float)) for j in (3,4,5)
               if row[j] is not None):
            raise ValueError("unexpected nonnumeric source outcome")
        year = "2005" if row[0]==1 else "2011"
        density = "sparse" if row[1]==1 else "dense"
        size = "small" if row[2]==1 else "large"
        counts[f"{year}_{density}_{size}"] += 1
    if dict(counts) != group_count:
        raise ValueError("raw category support differs from exact Dryad workbook")
    return rows, dict(sorted(counts.items()))


def initial_seed_missingness_bounds(seed_rows):
    """Partial-identification bounds, not imputed complete-case records.

    A missing initial rate is allowed in [0,100] percent, regardless of
    observed final zero and 100% predation. Missingness is outcome-dependent.
    """
    results={}
    for year in (1,2):
        by_density={}
        for den in (1,2):
            group=[r for r in seed_rows if r[0]==year and r[1]==den]
            if not group:
                raise ValueError("empty source year-density cell")
            obs=[float(r[3]) for r in group if r[3] is not None]
            missing=[r for r in group if r[3] is None]
            if any(r[5]!=100 or r[4]!=0 for r in missing):
                raise ValueError("initial missingness no longer aligns with predation=100/final=0")
            if any(x<0 or x>100 for x in obs):
                raise ValueError("source observed initial rate outside [0,100]")
            n=len(group)
            total=math.fsum(obs)
            by_density["sparse" if den==1 else "dense"]={
                "n_total":n,
                "n_initial_observed":len(obs),
                "n_initial_missing":len(missing),
                "missing_fraction":len(missing)/n,
                "observed_initial_mean_percent":total/len(obs) if obs else None,
                "population_mean_identification_lower_percent":total/n,
                "population_mean_identification_upper_percent":
                    (total+100*len(missing))/n,
                "all_missing_predation_100_final_0":True,
            }
        sparse=by_density["sparse"]; dense=by_density["dense"]
        results["2005" if year==1 else "2011"]={
            "by_density":by_density,
            "dense_minus_sparse_initial_mean_identified_interval_percent_points":[
                dense["population_mean_identification_lower_percent"]
                    - sparse["population_mean_identification_upper_percent"],
                dense["population_mean_identification_upper_percent"]
                    - sparse["population_mean_identification_lower_percent"],
            ],
        }
    return {
        "status":"INITIAL_SEED_RATE_OUTCOME_DEPENDENT_MISSINGNESS_HOLD",
        "missing_value_assumption":"unknown initial rate between 0 and 100 percent; NO imputation",
        "groups":results,
        "causal_pollination_or_fertilization_effect_identified":False,
    }


def audit_workbook(path: Path):
    blob = path.read_bytes()
    if (len(blob)!=SOURCE_BYTES or
            hashlib.md5(blob).hexdigest()!=SOURCE_MD5 or
            hashlib.sha256(blob).hexdigest()!=SOURCE_SHA256):
        raise ValueError("original Dryad raw workbook bytes changed")
    # Import lazily. Scientific calculations below have no third-party
    # dependencies; artifact_tool only extracts original cell values.
    from artifact_tool import Blob,SpreadsheetFile
    book = SpreadsheetFile.import_xlsx(Blob.load(str(path)))
    names = [book.worksheets.get_item_at(i).name for i in range(3)]
    if names != ["pollination rate",FRUIT_SHEET,SEED_SHEET]:
        raise ValueError("original workbook sheet order changed")
    fruit_data = book.worksheets.get_item(FRUIT_SHEET).get_range("A1:F77").values
    seed_data = book.worksheets.get_item(SEED_SHEET).get_range("A1:F2933").values
    fruits, fruit_counts = _source_rows(fruit_data[0], fruit_data[1:],
                                        EXPECTED_FRUIT_HEADER,
                                        EXPECTED_COUNTS_FRUIT)
    seeds, seed_counts = _source_rows(seed_data[0], seed_data[1:],
                                     EXPECTED_SEED_HEADER,
                                     EXPECTED_COUNTS_SEED)
    missing_initial = sum(r[3] is None for r in seeds)
    if missing_initial != 328:
        raise ValueError("initial seed missingness changed")
    missingness = initial_seed_missingness_bounds(seeds)
    if (missingness["groups"]["2011"]["by_density"]["sparse"]["n_initial_missing"]!=246
            or missingness["groups"]["2011"]["by_density"]["dense"]["n_initial_missing"]!=52):
        raise ValueError("initial missingness year-density pattern changed")
    studies = {
        "Table1_initial_seed_set": (seeds,3,0),
        "Table1_final_seed_set": (seeds,4,0),
        "Table1_seed_predation": (seeds,5,0),
        "Table2_initial_seed_set": ([r for r in seeds if r[0]==2],3,2),
        "Table2_final_seed_set": ([r for r in seeds if r[0]==2],4,2),
        "Table2_seed_predation": ([r for r in seeds if r[0]==2],5,2),
    }
    models = {}
    for name,(rows,outcome,factor) in studies.items():
        model = anova_two_factor(rows,outcome,factor)
        pub = PUBLISHED_F[name]
        if model["n"] != pub["n"] or model["df_residual"] != pub["df_residual"]:
            raise ValueError(f"{name} row/df reproduction failed")
        for key in ("factor","density","interaction"):
            if abs(model[key]-pub[key]) > 0.00055:
                raise ValueError(f"{name} {key} published F mismatch")
        models[name] = model

    poll = book.worksheets.get_item("pollination rate").get_range("A1:D9").values
    if (poll[0] != [2011,"sparse","dense","total"]
            or poll[5] != [2005,"sparse","dense","total"]):
        raise ValueError("pollination aggregation sheet schema changed")
    return {
        "schema_version":"PEDICULARIS_2013_SOURCE_STRUCTURE_AND_ANOVA_V1",
        "status":"PUBLISHED_UNCLUSTERED_SEED_ANOVA_REPRODUCED_PATCH_ID_ABSENT",
        "source_doi":"10.5061/dryad.6cv06",
        "source_sha256":SOURCE_SHA256,
        "source_original_bytes":SOURCE_BYTES,
        "sheet_names":names,
        "fruit_stem_rows":len(fruits),
        "seed_capsule_rows":len(seeds),
        "seed_initial_rate_missing_rows":missing_initial,
        "initial_seed_missingness_bounded_audit":missingness,
        "source_legend_rows_not_biological_records":4,
        "fruit_group_counts":fruit_counts,
        "seed_group_counts":seed_counts,
        "raw_column_headers":{
            "fruit":EXPECTED_FRUIT_HEADER, "seed":EXPECTED_SEED_HEADER,
            "pollination":["year_or_label","sparse","dense","total"],
        },
        "patch_id_present":False, "plant_id_present":False,
        "seed_to_fruit_stem_join_identifiable":False,
        "original_models":models,
        "published_F_statistic_match_count":18,
        "published_F_statistic_total_comparisons":18,
        "patch_clustered_effect_estimable":False,
        "original_2013_findings_disproved":False,
        "causal_patch_density_effect_identified":False,
        "BALANCE_architecture_occupancy_identified":False,
        "claim_ceiling":(
            "published_fixed_effect_ANOVA_numerically_reproduced_"
            "without_patch_level_uncertainty_no_causal_density_claim"
        ),
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--workbook",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():
        raise ValueError("refusing to overwrite an existing source audit receipt")
    result=audit_workbook(args.workbook)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                        encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "fruit_stem_rows":result["fruit_stem_rows"],
        "seed_capsule_rows":result["seed_capsule_rows"],
        "initial_seed_missing":result["seed_initial_rate_missing_rows"],
        "matched_F_statistics":result["published_F_statistic_match_count"],
        "patch_id_present":result["patch_id_present"],
    },sort_keys=True))


if __name__ == "__main__":
    main()

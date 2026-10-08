"""Reproduce Xia et al. (2013) source ANOVA F, without inventing patch IDs.

The model reproduces published **unclustered** 2x2 ANOVA by effect-coded
OLS. The F-statistics do not identify patch-robust uncertainty because the
source workbook contains density/size category labels but no patch identifier.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from math import isfinite
from statistics import mean

WORKBOOK_SHA256 = "d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380"
PUBLISHED = {
    "Table1_initial_seed_set": {"n": 2602, "df": 2598, "year": .507, "density": 3.767, "interaction": 1.241},
    "Table1_final_seed_set": {"n": 2930, "df": 2926, "year": 11.954, "density": 39.025, "interaction": .426},
    "Table1_seed_predation": {"n": 2930, "df": 2926, "year": 46.571, "density": 166.220, "interaction": 4.250},
    "Table2_initial_seed_set": {"n": 2051, "df": 2047, "size": 41.221, "density": 27.348, "interaction": 44.556},
    "Table2_final_seed_set": {"n": 2349, "df": 2345, "size": 1.025, "density": 26.958, "interaction": .023},
    "Table2_seed_predation": {"n": 2349, "df": 2345, "size": 45.029, "density": 317.878, "interaction": 106.270},
    "Table2_fruit_set": {"n": 58, "df": 54, "size": .206, "density": 2.368, "interaction": 3.060},
    "Table2_fruit_predation": {"n": 58, "df": 54, "size": 4.573, "density": 26.314, "interaction": 10.605},
}


def inverse(matrix):
    """Numerically straightforward small full-rank Gram inverse."""
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("non-square OLS matrix")
    a = [[float(v) for v in matrix[i]] + [float(i == j) for j in range(n)]
         for i in range(n)]
    scale = max(abs(v) for row in matrix for v in row)
    if scale == 0:
        raise ValueError("rank-deficient OLS")
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(a[i][j]))
        if abs(a[pivot][j]) < 1e-12 * scale:
            raise ValueError("rank-deficient OLS")
        a[j], a[pivot] = a[pivot], a[j]
        z = a[j][j]
        a[j] = [v / z for v in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [p - factor*q for p, q in zip(a[i], a[j])]
    return [row[n:] for row in a]


def effect_ols_F(records, response_index: int, factor_index: int):
    """Regress response on [1, +/-factor, +/-density, interaction].

    One row is a source workbook row (seed unit or harvested-spike row).
    These rows are *not* regarded as independent patch replicates.
    """
    rows = []
    for rec in records:
        if len(rec) != 6:
            raise ValueError("source workbook records require exactly six fields")
        if rec[response_index] is None:
            continue
        if (rec[1] not in (1, 2) or rec[factor_index] not in (1, 2)
                or isinstance(rec[response_index], bool)):
            raise ValueError("invalid density/factor/response")
        try:
            response = float(rec[response_index])
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("non-numeric source response") from exc
        if not isfinite(response):
            raise ValueError("nonfinite source response")
        fac, dens = (2 * float(rec[factor_index]) - 3,
                     2 * float(rec[1]) - 3)
        rows.append(([1., fac, dens, fac * dens], response))
    n = len(rows)
    if n <= 4:
        raise ValueError("too few independent source rows for OLS")
    xx = [[sum(x[i]*x[j] for x,y in rows) for j in range(4)] for i in range(4)]
    xx_inv = inverse(xx)
    xy = [sum(x[i]*y for x,y in rows) for i in range(4)]
    beta = [sum(xx_inv[i][j]*xy[j] for j in range(4)) for i in range(4)]
    ss = sum((y-sum(a*b for a,b in zip(x,beta)))**2 for x,y in rows)
    mse = ss/(n-4)
    if mse <= 0:
        raise ValueError("degenerate residual variance")
    ff = {}
    for j, label in [(1,"factor"),(2,"density"),(3,"interaction")]:
        variance = mse*xx_inv[j][j]
        if variance <= 0:
            raise ValueError("degenerate model uncertainty")
        ff[label] = beta[j]**2/variance
    return {"n":n,"residual_df":n-4,"F":ff}


def audit(source_seed_rows, source_fruit_rows):
    seeds = [r for r in source_seed_rows if len(r) == 6 and r[0] in (1,2)]
    fruits = [r for r in source_fruit_rows if len(r) == 6 and r[0] in (1,2)]
    if len(seeds) != 2930 or len(fruits) != 74:
        raise ValueError("Dryad source-row support drift")
    summary = {}
    for family, response, factor, yr in [
        ("Table1_initial_seed_set",3,0,None),
        ("Table1_final_seed_set",4,0,None),
        ("Table1_seed_predation",5,0,None),
        ("Table2_initial_seed_set",3,2,2),
        ("Table2_final_seed_set",4,2,2),
        ("Table2_seed_predation",5,2,2),
        ("Table2_fruit_set",4,2,2),
        ("Table2_fruit_predation",5,2,2),
    ]:
        source = seeds if "seed" in family else fruits
        selected = source if yr is None else [r for r in source if r[0] == yr]
        fitted = effect_ols_F(selected,response,factor)
        target = PUBLISHED[family]
        if fitted["n"] != target["n"] or fitted["residual_df"] != target["df"]:
            raise ValueError(f"{family}: support does not match printed paper")
        names = ("year" if factor == 0 else "size", "density", "interaction")
        found = {k: fitted["F"][v] for k,v in zip(names,("factor","density","interaction"))}
        for k, value in found.items():
            if abs(value-target[k]) >= .00055:
                raise ValueError(f"{family}: published F mismatch for {k}: {value}")
        summary[family] = {
            "n":fitted["n"],"residual_df":fitted["residual_df"],
            "published_F":{k:target[k] for k in names},
            "reproduced_F":found,
            "published_precision_match":True,
            "inferential_unit":"unclustered_source_rows_not_independent_density_patches",
        }

    def group_n(rows):
        return {"_".join(map(str,k)):v for k,v in sorted(
            Counter((int(r[0]),int(r[1]),int(r[2])) for r in rows).items())}
    means = {}
    for year,density in [(1,1),(1,2),(2,1),(2,2)]:
        each = [r for r in seeds if r[0]==year and r[1]==density]
        key = f"{year}_{density}"
        means[key] = {"n":len(each)}
        for label,col in [("initial_seed_set",3),("final_seed_set",4),
                          ("seed_predation",5)]:
            values = [float(r[col]) for r in each if r[col] is not None]
            means[key][label] = {"n":len(values),"mean":mean(values)}
    return {
        "schema_version":"PEDICULARIS_2013_DRYAD_UNCLUSTERED_REPRODUCTION_V1",
        "status":"24_PUBLISHED_F_MATCH_PATCH_LEVEL_UNCERTAINTY_NOT_IDENTIFIABLE",
        "raw_workbook_sha256":WORKBOOK_SHA256,
        "seed_rows":len(seeds),"fruit_rows":len(fruits),
        "seed_initial_missing":sum(r[3] is None for r in seeds),
        "seed_group_n":group_n(seeds),"fruit_group_n":group_n(fruits),
        "density_by_year_seed_descriptives":means,
        "tested_models":len(summary),
        "published_F_tests":sum(len(v["published_F"]) for v in summary.values()),
        "models":summary,
        "patch_id_present":False,"plant_id_present":False,
        "patch_cluster_uncertainty_estimated":False,
        "original_article_disproved":False,
        "claim_ceiling":"unclustered_published_test_reproduced_no_patch_inference_or_causal_density",
    }

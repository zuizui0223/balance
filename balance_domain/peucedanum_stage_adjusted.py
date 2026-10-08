"""Exploratory paired-stage associations with size controls and HC3 uncertainty.

Uses standard-library WLS, fully paired initial/final observations and no
external numeric dependency. This is not causal selection or mediation.
"""
from __future__ import annotations

from collections import defaultdict
from math import erfc, isfinite, log, log1p, sqrt
from statistics import fmean, pstdev
from typing import Iterable, Mapping

FIELDS = ("perfect_flower_count", "male_flower_count", "flower_stem_height",
          "initial_fruit_count", "intact_fruit_count")


def _value(row, key):
    raw = str(row.get(key, "") or "").strip()
    if not raw:
        return None
    try:
        x = float(raw)
    except ValueError as exc:
        raise ValueError(f"non-numeric {key}") from exc
    if not isfinite(x):
        raise ValueError(f"nonfinite {key}")
    return x


def _invert(matrix):
    n = len(matrix)
    aug = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)]
           for i, row in enumerate(matrix)]
    scale = max(abs(x) for row in matrix for x in row)
    if scale <= 0:
        raise ValueError("rank deficient")
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(aug[i][k]))
        if abs(aug[pivot][k]) < 1e-10 * scale:
            raise ValueError("rank deficient")
        aug[k], aug[pivot] = aug[pivot], aug[k]
        v = aug[k][k]
        aug[k] = [a / v for a in aug[k]]
        for i in range(n):
            if i != k:
                factor = aug[i][k]
                aug[i] = [a - factor*b for a, b in zip(aug[i], aug[k])]
    return [row[n:] for row in aug]


def _fit(rows, predictor):
    if len(rows) < 12:
        return {"status": "INSUFFICIENT_SAMPLE", "n": len(rows)}
    raw = [[log1p(m) if predictor == "log_male_count" else h/(h+m),
            log(h), height] for h, m, height, initial, final in rows]
    columns = list(zip(*raw))
    means, scales = [fmean(c) for c in columns], [pstdev(c) for c in columns]
    if min(scales) < 1e-10:
        return {"status": "INSUFFICIENT_PREDICTOR_VARIATION", "n": len(rows)}
    X = [[1.0] + [(v-mu)/sd for v,mu,sd in zip(r, means, scales)] for r in raw]
    Y = [(final-initial)/h for h,m,height,initial,final in rows]
    W = [h for h,m,height,initial,final in rows]
    k = len(X[0])
    gram = [[sum(w*x[i]*x[j] for w,x in zip(W,X)) for j in range(k)]
            for i in range(k)]
    try:
        inv = _invert(gram)
    except ValueError:
        return {"status": "RANK_DEFICIENT", "n": len(rows)}
    xy = [sum(w*x[i]*y for w,x,y in zip(W,X,Y)) for i in range(k)]
    coef = [sum(inv[i][j]*xy[j] for j in range(k)) for i in range(k)]
    residual = [y-sum(xi*bi for xi,bi in zip(x,coef)) for x,y in zip(X,Y)]
    var = 0.0
    for x,w,e in zip(X,W,residual):
        leverage = w*sum(x[i]*inv[i][j]*x[j] for i in range(k) for j in range(k))
        if leverage >= 1-1e-10:
            return {"status": "UNSTABLE_LEVERAGE", "n": len(rows)}
        impact = sum(inv[1][i]*x[i] for i in range(k))
        var += (w*e*impact/(1-leverage))**2
    se = sqrt(max(0.0, var))
    if not (isfinite(coef[1]) and isfinite(se)):
        return {"status": "NONFINITE_FIT", "n": len(rows)}
    if se <= 1e-12:
        return {"status": "DEGENERATE_OUTCOME", "n": len(rows),
                "coefficient_per_sd": coef[1], "se_hc3": se, "p_normal_hc3": None}
    z = coef[1]/se
    return {"status": "EXPLORATORY_FIT", "n": len(rows),
            "coefficient_per_sd": coef[1], "se_hc3": se, "z_hc3": z,
            "p_normal_hc3": erfc(abs(z)/sqrt(2.0))}


def _bh(fits):
    tested = sorted((row["p_normal_hc3"], i) for i,row in enumerate(fits)
                    if row.get("p_normal_hc3") is not None)
    q = 1.0
    for idx in range(len(tested)-1,-1,-1):
        p, row_index = tested[idx]
        q = min(q, p*len(tested)/(idx+1), 1.0)
        fits[row_index]["q_bh_within_variant"] = q
    return len(tested)


def analyze_adjusted(rows: Iterable[Mapping[str,str]]) -> dict:
    grouped = defaultdict(list)
    counts = defaultdict(int)
    for row in rows:
        year,plot = str(row.get("year","")),str(row.get("population_id",""))
        if not year or not plot:
            raise ValueError("missing year/plot")
        counts[(year,plot)] += 1
        values = [_value(row,key) for key in FIELDS]
        if any(v is None for v in values):
            continue
        h,m,height,initial,final = values
        if h<=0 or m<0 or height<=0 or min(initial,final)<0:
            raise ValueError("invalid count/height domain")
        if max(initial,final)>h:
            raise ValueError("fruit count exceeds perfect flower count")
        grouped[(year,plot)].append(values)
    if not counts:
        raise ValueError("empty survey")
    variants = {}
    for predictor in ("log_male_count","perfect_fraction"):
        for exclude in (False,True):
            key = predictor + ("_excluding_nonnested" if exclude else "_all_pairs")
            fitted = []
            for (year,plot) in sorted(counts):
                eligible = grouped[(year,plot)]
                if exclude:
                    eligible = [v for v in eligible if v[4]<=v[3]]
                fitted.append({"year": year, "plot": plot, **_fit(eligible,predictor)})
            variants[key] = {"n_nonnull_tests": _bh(fitted), "cells": fitted}
    return {
        "schema_version": "PEUCEDANUM_STAGE_ADJUSTED_EXPLORATORY_V1",
        "response": "final_minus_initial_fruit_rate_paired",
        "weights": "perfect_flower_count",
        "size_controls": ["log_perfect_flower_count","flower_stem_height"],
        "primary_predictor": "log1p_male_flower_count",
        "status": "EXPLORATORY_ASSOCIATION_ONLY",
        "variants": variants,
        "claim_ceiling": "no_causal_mediation_selection_reversal_or_BALANCE_occupancy",
    }

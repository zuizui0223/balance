#!/usr/bin/env python3
"""Fail-closed Q1B reanalysis of the public Impatiens capensis factorial dataset.

The analysis is fixed before inspecting Q1B results:
- public Dryad archive DOI 10.5061/dryad.0j96d17, version download 4805;
- restrict to Robbing == N, leaving the randomized 2x2 Pollination x Florivory design;
- common reproductive component: Average_CH_Fruits_Per_Day;
- pre-treatment trait coordinates: Early_Season_Flower_Redness and
  Early_Season_Condensed_Tannins;
- nuisance covariate: Date_of_First_CH_Flower;
- within each of the four treatment cells, relative fitness is outcome / cell mean;
- traits/covariate are standardized once across the complete-case 2x2 subset;
- multivariate OLS is fit in every cell;
- stratified plant bootstrap jointly propagates the four treatment slopes.

No raw observation is written to disk. Only aggregate sufficient statistics are emitted.
"""
from __future__ import annotations

import io
import json
import math
import random
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

ARCHIVE_URL = "https://datadryad.org/api/v2/versions/4805/download"
STUDY_DOI = "10.1002/ajb2.1182"
DATA_DOI = "10.5061/dryad.0j96d17"
OUTCOME = "Average_CH_Fruits_Per_Day"
TRAITS = ("Early_Season_Flower_Redness", "Early_Season_Condensed_Tannins")
PHENOLOGY = "Date_of_First_CH_Flower"
BOOTSTRAPS = 2000
SEED = 20260909
TREATMENT_ORDER = (("N", "Y"), ("Y", "Y"), ("N", "N"), ("Y", "N"))
# (Pollination, Florivory): open/present, supplemented/present, open/absent, supplemented/absent
C = np.array([[1,-1,0,0],[0,0,1,-1],[1,0,-1,0],[0,1,0,-1]], dtype=float)
CONTRAST_NAMES = (
    "pollinator_given_florivory_present",
    "pollinator_given_florivory_absent",
    "florivory_given_open_pollination",
    "florivory_given_supplemented_pollination",
)


def num(x):
    try:
        y = float(str(x).strip())
        return y if math.isfinite(y) else None
    except Exception:
        return None


def find_processed_csv(blob: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith("processed_data.csv")]
        if len(names) != 1:
            raise RuntimeError(f"expected one Processed_Data.csv, found {names}")
        return zf.read(names[0]).decode("utf-8-sig", errors="replace")


def parse_rows(text: str):
    import csv
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    needed = {"Robbing", "Pollination", "Florivory", OUTCOME, PHENOLOGY, *TRAITS}
    missing = needed - set(reader.fieldnames or [])
    if missing:
        raise RuntimeError(f"missing required columns: {sorted(missing)}")
    for r in reader:
        if str(r["Robbing"]).strip().upper() != "N":
            continue
        p = str(r["Pollination"]).strip().upper()
        h = str(r["Florivory"]).strip().upper()
        if (p, h) not in TREATMENT_ORDER:
            continue
        vals = {k: num(r[k]) for k in (OUTCOME, PHENOLOGY, *TRAITS)}
        if any(v is None for v in vals.values()):
            continue
        vals["Pollination"] = p
        vals["Florivory"] = h
        rows.append(vals)
    return rows


def design(rows, means, sds):
    y = np.array([r[OUTCOME] for r in rows], dtype=float)
    if len(y) < 8 or y.mean() <= 0:
        raise RuntimeError("insufficient cell size or nonpositive mean fitness")
    y = y / y.mean()
    X = np.ones((len(rows), 1 + len(TRAITS) + 1), dtype=float)
    for j, t in enumerate(TRAITS, start=1):
        X[:, j] = [(r[t] - means[t]) / sds[t] for r in rows]
    X[:, -1] = [(r[PHENOLOGY] - means[PHENOLOGY]) / sds[PHENOLOGY] for r in rows]
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return beta


def slopes_for_sample(cells, means, sds, rng=None):
    result = {t: [] for t in TRAITS}
    for key in TREATMENT_ORDER:
        source = cells[key]
        if rng is None:
            sample = source
        else:
            sample = [source[rng.randrange(len(source))] for _ in source]
        b = design(sample, means, sds)
        for j, t in enumerate(TRAITS, start=1):
            result[t].append(float(b[j]))
    return result


def main(out_path: str):
    req = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "balance-q1b/1"})
    with urllib.request.urlopen(req, timeout=90) as fh:
        text = find_processed_csv(fh.read())
    rows = parse_rows(text)
    if len(rows) < 60:
        raise RuntimeError(f"too few complete-case no-robbing rows: {len(rows)}")

    means = {}
    sds = {}
    for k in (*TRAITS, PHENOLOGY):
        a = np.array([r[k] for r in rows], dtype=float)
        means[k] = float(a.mean())
        sds[k] = float(a.std(ddof=1))
        if not sds[k] > 0:
            raise RuntimeError(f"zero SD for {k}")

    cells = {k: [r for r in rows if (r["Pollination"], r["Florivory"]) == k] for k in TREATMENT_ORDER}
    n_by_cell = {f"poll_{p}_flor_{h}": len(v) for (p,h),v in cells.items()}
    if min(n_by_cell.values()) < 12:
        raise RuntimeError(f"cell size below preregistered floor 12: {n_by_cell}")

    observed = slopes_for_sample(cells, means, sds)
    rng = random.Random(SEED)
    boot = {t: [] for t in TRAITS}
    for _ in range(BOOTSTRAPS):
        s = slopes_for_sample(cells, means, sds, rng)
        for t in TRAITS:
            boot[t].append(s[t])

    traits_out = {}
    positive_any = False
    for t in TRAITS:
        b = np.array(observed[t], dtype=float)
        B = np.array(boot[t], dtype=float)
        theta = C @ b
        theta_boot = B @ C.T
        cov_b = np.cov(B, rowvar=False, ddof=1)
        cov_theta = np.cov(theta_boot, rowvar=False, ddof=1)
        se_theta = np.sqrt(np.diag(cov_theta))
        ci = np.quantile(theta_boot, [0.025, 0.975], axis=0)
        # Biological positive Q1B flag is point-estimate opposition in at least one
        # factorial context pair. Statistical uncertainty is retained separately.
        opp1 = theta[0] * theta[2] < 0  # both mediated effects with florivory present/open context
        opp2 = theta[1] * theta[3] < 0
        positive = bool(opp1 or opp2)
        positive_any = positive_any or positive
        traits_out[t] = {
            "treatment_slopes": dict(zip([f"poll_{p}_flor_{h}" for p,h in TREATMENT_ORDER], map(float,b))),
            "treatment_slope_covariance": cov_b.tolist(),
            "mediated_contrasts": {CONTRAST_NAMES[i]: {"estimate": float(theta[i]), "bootstrap_se": float(se_theta[i]), "ci95": [float(ci[0,i]), float(ci[1,i])]} for i in range(4)},
            "mediated_contrast_covariance": cov_theta.tolist(),
            "opposed_agent_point_pattern": positive,
            "opposition_contexts": {"florivory_present_open_pair": bool(opp1), "florivory_absent_supplemented_pair": bool(opp2)},
        }

    report = {
        "analysis": "balance_impatiens_q1b_preregistered_raw_bootstrap",
        "study_doi": STUDY_DOI,
        "data_doi": DATA_DOI,
        "archive_url": ARCHIVE_URL,
        "subset": "Robbing == N; randomized Pollination x Florivory 2x2",
        "outcome": OUTCOME,
        "fitness_contract": "common chasmogamous fruit-rate reproductive component; not lifetime fitness",
        "traits_predeclared": list(TRAITS),
        "n_complete": len(rows),
        "n_by_cell": n_by_cell,
        "bootstrap_replicates": BOOTSTRAPS,
        "bootstrap_seed": SEED,
        "joint_uncertainty_provenance": "stratified_raw_plant_bootstrap",
        "traits": traits_out,
        "q1b_positive_point_pattern_any_predeclared_trait": positive_any,
        "effect_size_state": "JOINT_MULTICONTRAST_READY" if positive_any else "JOINT_MULTICONTRAST_READY_NEGATIVE_OR_BOUNDARY",
        "promotion_guard": "A positive state requires point-estimate opposition among the predeclared same-trait mediated contrasts; all predeclared traits are reported. No trait is selected post hoc.",
        "claim_ceiling": "Q1B R-layer factorial selection pattern on a reproductive component; not direct BALANCE occupancy or W_S*/W_D*",
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"effect_size_state": report["effect_size_state"], "positive": positive_any, "n": len(rows), "n_by_cell": n_by_cell}))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_impatiens_q1b_reanalysis.py OUTPUT.json")
    main(sys.argv[1])

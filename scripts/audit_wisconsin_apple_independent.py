#!/usr/bin/env python3
"""Source-verified Wisconsin apple orchard composition and frost diagnostics.

Mallinger & Gratton (2014): Dryad 10.5061/dryad.t75c4.
47 orchard-years, but bee counts missing for all 11 rows in 2011. The
complete analysis includes 36 orchard-years from 21 unique orchards.
Original XLSX must match source-published MD5. No V4 inputs are opened.
"""
import argparse
import collections
import hashlib
import json
import math
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

MD5 = "5445fb585421e6d9b1f5b5869342bbb4"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REQUIRED = ("Orchard name", "Year", "Proportion fruit set open branches",
            "Wild bee abundance", "wild bee abundance per 1 week",
            "Wild bee species richness ", "Honey bee abundance",
            "Proportion frost damage", "management")
MODELS = {
    "null": (),
    "total": ("total",),
    "total_share": ("total", "share"),
    "total_rich": ("total", "rich"),
    "total_both": ("total", "share", "rich"),
}
SCOPES = {
    "pooled_year_frost": ((2012, 2013), ("year", "frost")),
    "pooled_year_only": ((2012, 2013), ("year",)),
    "pooled_year_frost_management": ((2012, 2013), ("year", "frost", "management")),
    "frost_2012": ((2012,), ("frost",)),
    "no_frost_2012": ((2012,), ()),
    "year_2013": ((2013,), ()),
}

def read_original(path):
    raw = Path(path).read_bytes()
    if hashlib.md5(raw).hexdigest() != MD5:
        raise ValueError("Original Dryad/Zenodo workbook MD5 mismatch")
    with ZipFile(path) as z:
        shared = ["".join(t.text or "" for t in si.iter(NS + "t"))
                  for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(NS + "si")]
        table = []
        for row in ET.fromstring(z.read("xl/worksheets/sheet2.xml")).iter(NS + "row"):
            vals = {}
            for cell in row.findall(NS + "c"):
                letters = re.match("([A-Z]+)", cell.attrib["r"]).group(1)
                j = 0
                for ch in letters:
                    j = j * 26 + ord(ch) - 64
                value = cell.find(NS + "v")
                if value is None:
                    v = None
                elif cell.attrib.get("t") == "s":
                    v = shared[int(value.text)]
                else:
                    try:
                        v = float(value.text)
                    except (TypeError, ValueError):
                        v = value.text
                vals[j - 1] = v
            if vals:
                table.append(vals)
    if len(table) != 48:
        raise ValueError("Original XLSX must have header plus 47 orchard-years")
    headers = [table[0].get(j) for j in range(14)]
    if any(k not in headers for k in REQUIRED):
        raise ValueError("Original source workbook schema drift")
    rows = [dict(zip(headers, [record.get(j) for j in range(14)]))
            for record in table[1:]]
    ids, years = [], collections.Counter()
    for r in rows:
        garden, year = int(r["Orchard name"]), int(r["Year"])
        ids.append((garden, year))
        years[year] += 1
        if not (0 <= r["Proportion fruit set open branches"] <= 1
                and 0 <= r["Proportion frost damage"] <= 1):
            raise ValueError("Invalid fruit or frost proportion")
        bee = [r[n] for n in ("Wild bee abundance", "wild bee abundance per 1 week",
                             "Wild bee species richness ", "Honey bee abundance")]
        if year == 2011:
            if not all(v in ("NA", None) for v in bee):
                raise ValueError("2011 missing bees must remain missing")
        elif year in (2012, 2013):
            if any(not isinstance(v, (int, float)) or not math.isfinite(v)
                   or v < 0 for v in bee) or r["Wild bee species richness "] <= 0:
                raise ValueError("Missing or invalid observed bees")
        else:
            raise ValueError("Invalid year")
    if (len(set(ids)), len(set(k for k, _ in ids))) != (47, 21):
        raise ValueError("Orchard dependence or orchard-year identities changed")
    if dict(years) != {2011: 11, 2012: 17, 2013: 19}:
        raise ValueError("Original annual counts changed")
    return rows, hashlib.sha256(raw).hexdigest()

def complete(rows, weekly=True):
    out = []
    for r in rows:
        if int(r["Year"]) == 2011:
            continue
        wild = float(r["wild bee abundance per 1 week"] if weekly
                     else r["Wild bee abundance"])
        honey = float(r["Honey bee abundance"])
        total = wild + honey
        if total <= 0:
            raise ValueError("Undefined total and share")
        out.append(dict(orchard=int(r["Orchard name"]), year=int(r["Year"]),
                        fruit=float(r["Proportion fruit set open branches"]),
                        frost=float(r["Proportion frost damage"]), total=total,
                        share=wild / total, rich=float(r["Wild bee species richness "]),
                        organic=float(r["management"] == "org")))
    if len(out) != 36 or len(set(r["orchard"] for r in out)) != 21:
        raise ValueError("Complete-case support shifted")
    return out

def grouped_cv(rows, predictors):
    import numpy as np
    rows = sorted(rows, key=lambda r: (r["orchard"], r["year"]))
    y = np.array([math.asin(math.sqrt(r["fruit"])) for r in rows])
    gardens = np.array([r["orchard"] for r in rows])
    features = {
        "year": lambda r: float(r["year"] == 2013),
        "frost": lambda r: r["frost"],
        "total": lambda r: math.log1p(r["total"]),
        "share": lambda r: r["share"],
        "rich": lambda r: math.log1p(r["rich"]),
        "management": lambda r: r["organic"],
    }
    X = np.array([[1.] + [features[k](r) for k in predictors] for r in rows])
    if np.linalg.matrix_rank(X) != X.shape[1]:
        raise ValueError("Full design rank failed")
    all_err, orchard_mse = [], []
    for g in sorted(set(gardens)):
        keep = gardens != g
        test = ~keep
        if np.linalg.matrix_rank(X[keep]) != X.shape[1]:
            raise ValueError("Holdout design rank failed")
        beta = np.linalg.lstsq(X[keep], y[keep], rcond=None)[0]
        er = y[test] - X[test] @ beta
        all_err.extend(er.tolist())
        orchard_mse.append(float(np.mean(er * er)))
    return {
        "n_rows": len(rows), "n_orchards": len(set(gardens)),
        "rmse_orchard_equal": float(np.sqrt(np.mean(orchard_mse))),
        "rmse_row_equal": float(np.sqrt(np.mean(np.square(all_err)))),
    }

def analyze(path):
    source, sha = read_original(path)
    out = {}
    for key, (years, ctx) in SCOPES.items():
        rows = [r for r in complete(source) if r["year"] in years]
        fits = {name: grouped_cv(rows, ctx + cols) for name, cols in MODELS.items()}
        ref = fits["total"]["rmse_orchard_equal"]
        out[key] = {
            "n_rows": len(rows), "n_orchards": len(set(r["orchard"] for r in rows)),
            "models": fits,
            "delta_vs_total_pct": {
                name: 100 * (1 - fit["rmse_orchard_equal"] / ref)
                for name, fit in fits.items()},
        }
    raw = complete(source, weekly=False)
    fits = {k: grouped_cv(raw, ("year", "frost") + v)
            for k, v in MODELS.items()}
    ref = fits["total"]["rmse_orchard_equal"]
    out["pooled_raw_abundance_sensitivity"] = {
        "n_rows": len(raw), "models": fits,
        "delta_vs_total_pct": {
            k: 100 * (1 - x["rmse_orchard_equal"] / ref) for k, x in fits.items()},
    }
    return {
        "schema": "BALANCE_WISCONSIN_APPLE_INDEPENDENT_ORIGINAL_V1",
        "source_doi": "10.5061/dryad.t75c4", "original_md5": MD5,
        "original_sha256": sha, "original_orchard_years": 47,
        "observed_orchard_years": 36, "independent_orchards": 21,
        "independent_studies": 1, "frozen_V4_opened": False,
        "direct_BALANCE_worldline": False, "results": out,
        "limits": ["2011 NA must not be imputed as bee absence",
                   "Abundance is not a plant-specific visitation rate",
                   "Repeated orchard years share the same holdout",
                   "Frost is observational, not a randomized intervention",
                   "Prediction changes are not comparable meta-analysis effects"],
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = analyze(args.source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for name, panel in result["results"].items():
        print(name, "n=", panel["n_rows"],
              "total RMSE=", panel["models"]["total"]["rmse_orchard_equal"],
              "both Δ%=", panel["delta_vs_total_pct"]["total_both"])

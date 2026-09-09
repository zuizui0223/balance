#!/usr/bin/env python3
"""Extract Sletvold et al. 2015 records from the public Caruso et al. floral-selection Dryad files.

Fail-closed public-data utility: discover latest Dryad version, download spreadsheet
files in memory, emit only header + rows matching the focal DOI/author/year. No
selection estimate is reconstructed here and no Q1B promotion is performed.
"""
from __future__ import annotations
import io, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

DATASET_DOI = "10.5061/dryad.2v8c5g0"
FOCAL_TOKENS = ("14-0119.1", "sletvold", "moritz", "2015")
UA = {"User-Agent": "balance-q1b-caruso-extractor/1"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as fh:
        return json.load(fh)


def get_bytes(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as fh:
        return fh.read()


def discover_files():
    encoded = urllib.parse.quote("doi:" + DATASET_DOI, safe="")
    ds = get_json("https://datadryad.org/api/v2/datasets/" + encoded)
    href = ((ds.get("_links") or {}).get("latestVersion") or {}).get("href")
    if not href:
        raise RuntimeError(f"latestVersion missing: keys={list(ds)}")
    ver = get_json(href if href.startswith("http") else "https://datadryad.org" + href)
    files_href = ((ver.get("_links") or {}).get("files") or {}).get("href")
    if not files_href:
        vid = ver.get("id") or str(href).rstrip('/').split('/')[-1]
        files_href = f"/api/v2/versions/{vid}/files"
    files = get_json(files_href if files_href.startswith("http") else "https://datadryad.org" + files_href)
    return ds, ver, files.get("_embedded", {}).get("stash:files", files.get("files", []))


def norm(v):
    return "" if v is None else str(v).strip()


def match_row(vals):
    s = " | ".join(norm(v).lower() for v in vals)
    # DOI token is sufficient; author/year fallback requires both Sletvold and Moritz.
    return "14-0119.1" in s or ("sletvold" in s and "moritz" in s and "2015" in s)


def main(out):
    import openpyxl
    ds, ver, files = discover_files()
    result = {"dataset_doi": DATASET_DOI, "dataset_version": ver.get("versionNumber"), "matched": [], "files_seen": []}
    for f in files:
        name = f.get("path") or f.get("fileName") or f.get("name") or ""
        result["files_seen"].append(name)
        if not name.lower().endswith((".xlsx", ".xlsm")):
            continue
        dl = ((f.get("_links") or {}).get("stash:download") or {}).get("href") or f.get("downloadUrl")
        if not dl:
            continue
        blob = get_bytes(dl if dl.startswith("http") else "https://datadryad.org" + dl)
        wb = openpyxl.load_workbook(io.BytesIO(blob), read_only=True, data_only=True)
        for ws in wb.worksheets:
            rows = list(ws.iter_rows(values_only=True))
            for i, vals in enumerate(rows):
                if match_row(vals):
                    # capture nearby plausible header rows so column identity is auditable
                    header_candidates = []
                    for j in range(max(0, i-4), i):
                        header_candidates.append({"row_number": j+1, "values": [norm(v) for v in rows[j]]})
                    result["matched"].append({
                        "file": name,
                        "sheet": ws.title,
                        "row_number": i+1,
                        "values": [norm(v) for v in vals],
                        "preceding_rows": header_candidates,
                    })
    if not result["matched"]:
        raise RuntimeError(f"no Sletvold/Moritz 2015 rows found; files={result['files_seen']}")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"matched_rows": len(result["matched"]), "files_seen": result["files_seen"]}))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: extract_gymnadenia_from_caruso_dryad.py OUTPUT.json")
    main(sys.argv[1])

#!/usr/bin/env python3
"""Extract Sletvold et al. 2015 records from the public Caruso et al. floral-selection Dryad files.

Fail-closed public-data utility: discover current Dryad version, download spreadsheet
files in memory, emit only header + rows matching the focal DOI/author/year. No
selection estimate is reconstructed here and no Q1B promotion is performed.
"""
from __future__ import annotations
import io, json, sys, urllib.parse, urllib.request
from pathlib import Path

DATASET_DOI = "10.5061/dryad.2v8c5g0"
UA = {"User-Agent": "balance-q1b-caruso-extractor/1"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as fh:
        return json.load(fh)


def get_bytes(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as fh:
        return fh.read()


def abs_url(href):
    return href if href.startswith("http") else "https://datadryad.org" + href


def discover_files():
    encoded = urllib.parse.quote("doi:" + DATASET_DOI, safe="")
    ds = get_json("https://datadryad.org/api/v2/datasets/" + encoded)

    # Dryad has returned two valid shapes over time:
    # (a) a dataset wrapper with _links.latestVersion; or
    # (b) the current version object directly (id/versionNumber/_links present).
    latest = ((ds.get("_links") or {}).get("latestVersion") or {}).get("href")
    if latest:
        ver = get_json(abs_url(latest))
    elif ds.get("id") is not None and ds.get("versionNumber") is not None:
        ver = ds
    else:
        raise RuntimeError(f"unrecognized Dryad dataset/version shape: keys={list(ds)}")

    files_href = ((ver.get("_links") or {}).get("files") or {}).get("href")
    if not files_href:
        vid = ver.get("id")
        if vid is None:
            raise RuntimeError(f"Dryad version id missing: keys={list(ver)}")
        files_href = f"/api/v2/versions/{vid}/files"

    files = get_json(abs_url(files_href))
    embedded = files.get("_embedded", {})
    file_rows = embedded.get("stash:files") or embedded.get("files") or files.get("files") or []
    return ds, ver, file_rows


def norm(v):
    return "" if v is None else str(v).strip()


def match_row(vals):
    s = " | ".join(norm(v).lower() for v in vals)
    return "14-0119.1" in s or ("sletvold" in s and "moritz" in s and "2015" in s)


def main(out):
    import openpyxl
    ds, ver, files = discover_files()
    result = {
        "dataset_doi": DATASET_DOI,
        "dataset_version": ver.get("versionNumber"),
        "dataset_version_id": ver.get("id"),
        "matched": [],
        "files_seen": [],
    }
    for f in files:
        name = f.get("path") or f.get("fileName") or f.get("name") or ""
        result["files_seen"].append(name)
        if not name.lower().endswith((".xlsx", ".xlsm")):
            continue
        dl = ((f.get("_links") or {}).get("stash:download") or {}).get("href") or f.get("downloadUrl")
        if not dl:
            continue
        blob = get_bytes(abs_url(dl))
        wb = openpyxl.load_workbook(io.BytesIO(blob), read_only=True, data_only=True)
        for ws in wb.worksheets:
            rows = list(ws.iter_rows(values_only=True))
            for i, vals in enumerate(rows):
                if match_row(vals):
                    header_candidates = []
                    for j in range(max(0, i - 4), i):
                        header_candidates.append({"row_number": j + 1, "values": [norm(v) for v in rows[j]]})
                    result["matched"].append({
                        "file": name,
                        "sheet": ws.title,
                        "row_number": i + 1,
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

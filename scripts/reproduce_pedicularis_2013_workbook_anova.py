#!/usr/bin/env python3
"""Exact verified Dryad XLSX -> 24 published F audit (non-clustered).

Requires the artifact_tool spreadsheet reader in the analysis environment.
No openpyxl/pandas input normalization; the XLSX must match frozen SHA256.
Run on the workbook extracted from verified Dryad version 11193.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from balance_domain.pedicularis_2013_anova import WORKBOOK_SHA256, audit

FRUIT_HEADERS = ["year","density","size","flowers","fruit set","fruit predation"]
SEED_HEADERS = ["year","density","size","intial seed set","fianl seed set","seed predation"]


def inspect_verified_workbook(path: Path):
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != WORKBOOK_SHA256:
        raise ValueError("2013 source workbook SHA256 mismatch")
    # Imported lazily: package pytest and baseline BALANCE CI do not
    # depend on an external spreadsheet interface. The user-facing
    # reproducible XLSX workflow uses the installed artifact_tool.
    from artifact_tool import Blob, SpreadsheetFile
    w = SpreadsheetFile.import_xlsx(Blob.load(str(path)))
    names = [
        "pollination rate",
        "fruit set and fruit predation",
        "seed set and seed predatioin",
    ]
    fruit = w.worksheets.get_item(names[1]).get_range("A1:F77").values
    seed = w.worksheets.get_item(names[2]).get_range("A1:F2933").values
    if fruit[0] != FRUIT_HEADERS or seed[0] != SEED_HEADERS:
        raise ValueError("original Dryad sheet header changed")
    receipt = audit(seed[1:], fruit[1:])
    receipt["source_doi"] = "10.5061/dryad.6cv06"
    receipt["source_version_id"] = 11193
    receipt["source_workbook_bytes"] = path.stat().st_size
    receipt["source_workbook_md5"] = hashlib.md5(path.read_bytes()).hexdigest()
    receipt["source_sheet_names"] = names
    receipt["source_seed_column_names"] = SEED_HEADERS
    receipt["source_fruit_column_names"] = FRUIT_HEADERS
    if receipt["source_workbook_bytes"] != 89597:
        raise ValueError("verified Dryad workbook byte count changed")
    if receipt["source_workbook_md5"] != "10a98383677bbd2a01e19a86c350fdd3":
        raise ValueError("verified Dryad workbook source MD5 changed")
    return receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workbook",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():
        raise ValueError("refusing to overwrite a source audit receipt")
    result=inspect_verified_workbook(args.workbook)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "seed_rows":result["seed_rows"],
        "fruit_rows":result["fruit_rows"],
        "published_F_tests":result["published_F_tests"],
        "patch_cluster_uncertainty_estimated":result["patch_cluster_uncertainty_estimated"],
    },sort_keys=True))


if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Exact-source-bound exploratory paired stage-size adjustment."""
import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path

from balance_domain.peucedanum_ingest import NORMALIZED_FIELDS
from balance_domain.peucedanum_stage_adjusted import analyze_adjusted

NORMALIZED_SHA256 = "ed6bf4c5301309283ca2e3d2033fdab1e253d46ed94bbba5fde1f3ee43281dbc"


def run(input_file: Path, output_file: Path):
    if output_file.exists():
        raise ValueError("adjusted-stage output must not be overwritten")
    if hashlib.sha256(input_file.read_bytes()).hexdigest() != NORMALIZED_SHA256:
        raise ValueError("verified source-normalized CSV SHA256 changed")
    with input_file.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != NORMALIZED_FIELDS:
            raise ValueError("verified normalized CSV schema changed")
        rows = list(reader)
    if len(rows) != 685:
        raise ValueError("source row count changed")
    result = analyze_adjusted(rows)
    for name, variant in result["variants"].items():
        if len(variant["cells"]) != 19:
            raise ValueError(f"stage model lost an observed plot-year cell: {name}")
        fitted_n = sum(cell["n"] for cell in variant["cells"])
        expected_n = 605 if name.endswith("_excluding_nonnested") else 608
        if fitted_n != expected_n:
            raise ValueError(f"stage fit support drift: {name}: {fitted_n}")
        if variant["n_nonnull_tests"] != 17:
            raise ValueError(f"stage estimability drift: {name}")
    result["source_normalized_csv_sha256"] = NORMALIZED_SHA256
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output_file.parent,
        prefix=".stage-adjusted-", suffix=".tmp", delete=False,
    ) as handle:
        temp = Path(handle.name)
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.replace(temp, output_file)
    finally:
        if temp.exists():
            temp.unlink()
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--normalized", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = run(args.normalized, args.out)
    for name, variant in result["variants"].items():
        admissible = [cell for cell in variant["cells"]
                      if cell.get("p_normal_hc3") is not None]
        best = min(admissible, key=lambda c: c["p_normal_hc3"])
        print(json.dumps({
            "variant": name, "tested_cells": len(admissible),
            "strongest_cell": f'{best["year"]}-{best["plot"]}',
            "smallest_nominal_p": best["p_normal_hc3"],
            "minimum_BH_q": min(c["q_bh_within_variant"] for c in admissible),
            "claim_ceiling": result["claim_ceiling"],
        }, sort_keys=True))


if __name__ == "__main__":
    main()

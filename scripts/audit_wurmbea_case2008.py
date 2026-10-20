#!/usr/bin/env python3
"""Recover exact Wurmbea 2008 voucher ndhF accessions and conditional payoff bounds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from balance_domain.wurmbea_case2008_ndhf import run
from balance_domain.wurmbea_case2008_four_locus import run as run_four_locus
from balance_domain.wurmbea_fitness_threshold import analyze_thresholds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    output = args.outdir
    output.mkdir(parents=True, exist_ok=True)
    genetic = run(output)
    multilocus = run_four_locus(output)
    conditional = analyze_thresholds()
    with (output / "wurmbea_case2008_conditional_thresholds.json").open("x", encoding="utf-8") as f:
        json.dump(conditional, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({
        "ndhf_status": genetic["status"],
        "focal_population_contrasts": genetic["focal_population_contrasts"],
        "source_accessions": {
            "expected": genetic["ndhf_accessions_expected"],
            "recovered": genetic["ndhf_accessions_recovered"],
            "missing": genetic["ndhf_accessions_missing"],
        },
        "focal_four_locus": {
            "status": multilocus["status"],
            "accessions_expected": multilocus["source_unique_accessions_expected"],
            "accessions_verified": multilocus["accessions_verified"],
            "failures": multilocus["accessions_failed"],
            "within_taxon_pairwise": multilocus["focal_groups"],
        },
        "conditional_fitness_thresholds": conditional,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

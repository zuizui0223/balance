"""Report published Mayberry 2024 results with optional paired CSV diagnostics.

Only bytes matching the archived Dryad file qualify as original trial data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from balance_domain.bee_learning_dual_function import (
    load_original_paired_csv, published_dual_function_audit,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv", type=Path, help="Local trial summary CSV to compare with the Dryad archive"
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    trial_analysis = load_original_paired_csv(args.csv) if args.csv else None
    verified = trial_analysis is not None and trial_analysis["provenance"]["verified_original"]
    output = {
        "published_original_source": published_dual_function_audit(),
        "real_original_csv_supplied": verified,
        "raw_trial_analysis": trial_analysis if verified else None,
        "candidate_trial_analysis": None if verified else trial_analysis,
    }
    text = json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

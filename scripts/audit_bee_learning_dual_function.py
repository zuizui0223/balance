"""Published Mayberry 2024 dual-function results, with optional original CSV.

By default, this script reproduces source-reported summary claims ONLY.
Original row-level paired description runs ONLY with an explicit --csv
pointing to an actual locally available Dryad file. No file is downloaded
or fabricated, and synthetic test records are not used here.
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
        "--csv", type=Path, help="Real original Dryad summary CSV, when available"
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    output = {
        "published_original_source": published_dual_function_audit(),
        "real_original_csv_supplied": bool(args.csv),
        "raw_trial_analysis": (
            load_original_paired_csv(args.csv) if args.csv else None
        ),
    }
    text = json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

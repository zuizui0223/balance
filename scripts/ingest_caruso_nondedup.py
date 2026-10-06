#!/usr/bin/env python3
"""Freeze the local Caruso et al. non-duplicated Dryad workbook into Stage-A inventories."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.caruso_ingest import ingest_caruso_nondedup  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=Path,
        help="Local Exp_stud_NOTdup_Dryad.xls downloaded from Dryad.",
    )
    parser.add_argument(
        "out_dir",
        type=Path,
        help="New immutable output directory; must not already exist.",
    )
    args = parser.parse_args()
    print(json.dumps(
        ingest_caruso_nondedup(args.source, args.out_dir),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()

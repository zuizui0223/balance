#!/usr/bin/env python3
"""Validate a complete BALANCE plant human-return bundle in one fail-closed pass."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_human_return_intake import (  # noqa: E402
    required_return_paths,
    write_human_return_intake,
)


DEFAULT_OUT = ROOT / "release" / "generated" / "plant_human_return_intake"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--return-dir",
        type=Path,
        required=True,
        help=(
            "Directory containing all six coder-return worksheets. Reviewed U2/U6 predictor "
            "receipt frames are optional as a pair; supplying only one fails closed."
        ),
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--list-required",
        action="store_true",
        help="Print the canonical required return basenames and exit.",
    )
    args = parser.parse_args()

    if args.list_required:
        print(json.dumps(
            {
                key: path.name
                for key, path in required_return_paths(args.return_dir).items()
            },
            indent=2,
            sort_keys=True,
        ))
        return

    print(json.dumps(
        write_human_return_intake(
            root=ROOT,
            return_dir=args.return_dir,
            out_dir=args.out_dir,
        ),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()

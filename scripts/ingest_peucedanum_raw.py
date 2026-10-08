#!/usr/bin/env python3
"""Inventory or normalize local Peucedanum public raw-data files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.peucedanum_ingest import (  # noqa: E402
    inventory_peucedanum_sources,
    normalize_peucedanum_sources,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser(
        "inventory",
        help="Freeze file/table identity only; do not assign biological semantics.",
    )
    inventory.add_argument("sources", nargs="+", type=Path)
    inventory.add_argument("--out-dir", type=Path, required=True)

    normalize = sub.add_parser(
        "normalize",
        help="Apply a source-verified mapping and emit normalized rows.",
    )
    normalize.add_argument("sources", nargs="+", type=Path)
    normalize.add_argument("--mapping", type=Path, required=True)
    normalize.add_argument("--out-dir", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "inventory":
        out = inventory_peucedanum_sources(args.sources, args.out_dir)
    else:
        out = normalize_peucedanum_sources(
            args.sources,
            args.mapping,
            args.out_dir,
        )
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

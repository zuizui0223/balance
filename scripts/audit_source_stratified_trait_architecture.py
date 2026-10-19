#!/usr/bin/env python3
"""Print real, source-stratified architecture/conflict counts without inference."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from balance_domain.plant_architecture_source_patterns import analyze


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Optional new JSON receipt. Existing files are never overwritten.",
    )
    args = parser.parse_args()
    data = analyze()
    text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(text)
        print(f"Wrote source-stratified exploration: {args.out}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()

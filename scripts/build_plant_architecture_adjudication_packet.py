#!/usr/bin/env python3
"""Build a post-reliability BALANCE plant architecture adjudication packet."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_architecture_adjudication import (  # noqa: E402
    build_architecture_adjudication_packet,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("PRIMARY", "EXTERNAL"), required=True)
    parser.add_argument("--intake-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    print(json.dumps(
        build_architecture_adjudication_packet(
            root=ROOT,
            intake_dir=args.intake_dir,
            scope=args.scope,
            out_dir=args.out_dir,
        ),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()

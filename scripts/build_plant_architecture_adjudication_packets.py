#!/usr/bin/env python3
"""Build BALANCE post-agreement architecture-adjudication packets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_architecture_adjudication import (  # noqa: E402
    build_architecture_adjudication_packets,
)


DEFAULT_OUT = (
    ROOT / "release" / "generated" / "plant_architecture_adjudication_packets"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--intake-dir",
        type=Path,
        required=True,
        help="Canonical workspace produced by audit_plant_human_returns.py.",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    print(json.dumps(
        build_architecture_adjudication_packets(
            root=ROOT,
            intake_dir=args.intake_dir,
            out_dir=args.out_dir,
        ),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()

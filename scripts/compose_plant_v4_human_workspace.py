#!/usr/bin/env python3
"""Compose validated BALANCE plant human-review workspaces for V4."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_v4_workspace import (  # noqa: E402
    compose_v4_human_input_workspace,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-adjudication-dir", type=Path, required=True)
    parser.add_argument("--predictor-intake-dir", type=Path, required=True)
    parser.add_argument("--external-adjudication-dir", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    print(json.dumps(
        compose_v4_human_input_workspace(
            root=ROOT,
            primary_adjudication_dir=args.primary_adjudication_dir,
            predictor_intake_dir=args.predictor_intake_dir,
            external_adjudication_dir=args.external_adjudication_dir,
            out_dir=args.out_dir,
        ),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()

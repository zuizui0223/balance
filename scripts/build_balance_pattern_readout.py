from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.pattern_ledger import (  # noqa: E402
    MIDDLE_CLASSES,
    PATTERN_CLASSES,
    REQUIRED,
    _validated_rows,
    build_pattern_readout,
    load_pattern_ledger,
)


def build(path: Path) -> dict:
    """Backward-compatible script surface for the canonical package builder."""
    return build_pattern_readout(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(args.ledger)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()

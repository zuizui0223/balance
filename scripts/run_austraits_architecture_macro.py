#!/usr/bin/env python3
"""Acquire frozen AusTraits and record only an independent structural-opportunity audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from balance_domain.austraits_architecture_macro import fetch_and_analyze

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    receipt = fetch_and_analyze(args.out_dir)
    print(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()

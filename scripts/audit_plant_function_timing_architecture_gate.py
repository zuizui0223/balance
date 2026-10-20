#!/usr/bin/env python3
"""Source-hashed U2/PILOT/U3 timing, function-family and architecture support."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from balance_domain.plant_function_timing_architecture_gate import analyze


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    payload=json.dumps(analyze(),indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as f:
            f.write(payload)
    else:
        print(payload,end="")


if __name__=="__main__":
    main()

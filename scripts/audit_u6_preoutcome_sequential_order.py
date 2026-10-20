#!/usr/bin/env python3
"""Read original U6 3/3 ordered visitor source cases without opening V4."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from balance_domain.u6_preoutcome_sequential_order import analyze


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    blob=json.dumps(analyze(),sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as f:
            f.write(blob)
    else:
        print(blob,end="")


if __name__=="__main__":
    main()

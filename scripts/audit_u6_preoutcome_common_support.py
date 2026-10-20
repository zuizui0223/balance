#!/usr/bin/env python3
"""Report architecture-blind pollen-theft source opportunity and identity."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from balance_domain.u6_preoutcome_common_support import analyze


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    text=json.dumps(analyze(),indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as f:
            f.write(text)
    else:
        print(text,end="")


if __name__=="__main__":
    main()

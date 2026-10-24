#!/usr/bin/env python3
"""Output source-level U6 ecology evidence without promoting independent coder outcomes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from balance_domain.u6_original_source_ecology_pilot import analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    result=analyze()
    data=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as h:
            h.write(data)
    else:
        print(data,end="")


if __name__=="__main__":
    main()

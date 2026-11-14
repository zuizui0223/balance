#!/usr/bin/env python3
"""Audit remaining six source observations, not independent U6 response codes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from balance_domain.u6_last6_source_function_ecology import analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    result=analyze()
    output=json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as h:
            h.write(output)
    else:
        print(output,end="")


if __name__=="__main__":
    main()

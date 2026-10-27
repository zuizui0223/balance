#!/usr/bin/env python3
"""Source-linked evidence for six additional U6 studies, without coding V4."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from balance_domain.u6_next6_source_function_ecology import analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    text=json.dumps(analyze(),ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as out:
            out.write(text)
    else:
        print(text,end="")


if __name__=="__main__":
    main()

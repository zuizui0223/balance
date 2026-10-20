#!/usr/bin/env python3
"""Read original U3 + published Clarkia mechanism receipts without pooled inference."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from balance_domain.pollen_architecture_mechanism_crosscheck import analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    data=analyze()
    content=json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as fp:
            fp.write(content)
    else:
        print(content,end="")


if __name__=="__main__":
    main()

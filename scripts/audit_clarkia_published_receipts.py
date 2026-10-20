#!/usr/bin/env python3
"""Audit Kay 2020 published numeric claims without pretending to fit raw Dryad."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from balance_domain.clarkia_published_receipts import analyze


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    readout=analyze()
    text=json.dumps(readout,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as fh:
            fh.write(text)
    else:
        print(text,end="")


if __name__=="__main__":
    main()

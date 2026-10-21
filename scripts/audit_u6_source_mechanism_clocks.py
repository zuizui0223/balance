#!/usr/bin/env python3
"""Report source-clock/anatomy evidence for frozen first six U6 taxa only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from balance_domain.u6_source_mechanism_clocks import analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    output=json.dumps(analyze(),sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("x",encoding="utf-8") as handle:
            handle.write(output)
    else:
        print(output,end="")


if __name__=="__main__":
    main()

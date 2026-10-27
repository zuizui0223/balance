#!/usr/bin/env python3
"""Post-open family-conditional EXACT GloBI documentation versus GBIF rank audit.

All 48 original species, all 96 original GBIF count API responses and the
unaltered source GloBI name/key coverage table are independently hash-verified
by balance_domain.gbif_occurrence_effort before any statistical calculation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from balance_domain.gbif_globi_family_exact_rank import real_source_rank_audit


def build_readout(root:Path,out:Path)->dict:
    if out.exists():
        raise ValueError("refusing to overwrite existing family-conditional source readout")
    data=real_source_rank_audit(root)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as fh:
        json.dump(data,fh,sort_keys=True,indent=2,allow_nan=False)
        fh.write("\n")
    return data


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=ROOT)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    r=build_readout(args.repo_root,args.out)
    x=r["family_conditional_source_analyses"]["name_exact_all_occurrence"]
    s=r["family_conditional_source_analyses"]["direct_GBIF_key_all_occurrence"]
    print(json.dumps({
        "status":r["status"],
        "n_species":48,
        "mixed_families":x["n_informative_mixed_documentation_families"],
        "exact_conditional_arrangements":x["exact_conditional_label_assignments"],
        "name_match_right_tail_exploratory_p":x["right_tail_conditional_p"],
        "direct_key_matched_species":r["n_GloBI_direct_GBIF_key_documented"],
        "direct_key_right_tail_exploratory_p":s["right_tail_conditional_p"],
        "causal_ecological_conflict_identified":False,
        "strict_BALANCE_worldline_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

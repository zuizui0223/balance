#!/usr/bin/env python3
"""Offline original Dryad V2 provenance screen with a strict source-claim ceiling.

This is not a live download. For complete reanalysis first obtain both
official Dryad text files, compare their exact MD5 and byte length, and
then audit original row structure before fitting independent biological
models. The output does not run a mixed-effects model or identify bract
photosynthesis-specific causality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.dalechampia_method_scope import (
    FILE_IDENTITIES,
    audit_dalechampia_method_scope,
    verify_exact_dryad_bytes,
)


def build_receipt(source: Path, out: Path, seed_file: Path | None = None,
                  gas_file: Path | None = None) -> dict:
    if out.exists():
        raise ValueError("Dalechampia Dryad integrity receipt output already exists")
    if (seed_file is None) != (gas_file is None):
        raise ValueError("both original Dryad seed and gas files must be supplied together")
    source_bytes = source.read_bytes()
    contract = json.loads(source_bytes)
    if seed_file is None:
        result = audit_dalechampia_method_scope(contract)
    else:
        seed_data=seed_file.read_bytes()
        gas_data=gas_file.read_bytes()
        result=verify_exact_dryad_bytes(
            contract,
            {FILE_IDENTITIES[46163][0]: seed_data,
             FILE_IDENTITIES[46164][0]: gas_data},
        )
    result["source_contract_sha256"] = hashlib.sha256(source_bytes).hexdigest()
    result["source_contract_path"] = "data/DALECHAMPIA_POSTANTHESIS_METHOD_AND_DRYAD_V2.json"
    result["historical_source_doi"] = "10.5061/dryad.nb675"
    result["direct_mechanism_and_BALANCE_not_identified"] = True
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=out.parent,
        prefix=".dalechampia-dryad-", suffix=".tmp", delete=False,
    ) as handle:
        temporary=Path(handle.name)
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.replace(temporary,out)
    finally:
        if temporary.exists():
            temporary.unlink()
    return result


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",type=Path,
        default=ROOT/"data/DALECHAMPIA_POSTANTHESIS_METHOD_AND_DRYAD_V2.json")
    parser.add_argument("--seed-file",type=Path)
    parser.add_argument("--gas-file",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=build_receipt(args.contract,args.out,args.seed_file,args.gas_file)
    print(json.dumps({
        "status":result["status"],
        "raw_file_bytes_verified":result["raw_file_bytes_verified"],
        "raw_reanalysis_executed":result["raw_reanalysis_executed"],
        "bract_specific_causal_effect_identified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()

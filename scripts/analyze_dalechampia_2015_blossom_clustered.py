#!/usr/bin/env python3
"""Source-verified original Dryad blossom-level maternal cluster sensitivity.

Use only original files whose sizes+MD5s match archived Dryad version 11209.
Retrospective estimator; original 2015 nlme mixed model is not reconstructed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from balance_domain.dalechampia_blossom_clustered import (
    analyze_authenticated_blossom_clusters,
)
from balance_domain.dalechampia_method_scope import FILE_IDENTITIES


def run(contract_path: Path, seed_path: Path, gas_path: Path, out_path: Path) -> dict:
    if out_path.exists():
        raise ValueError("refuse to overwrite prior original-data sensitivity receipt")
    contract_bytes = contract_path.read_bytes()
    file_bytes = {
        FILE_IDENTITIES[46163][0]: seed_path.read_bytes(),
        FILE_IDENTITIES[46164][0]: gas_path.read_bytes(),
    }
    contract = json.loads(contract_bytes)
    result = analyze_authenticated_blossom_clusters(contract, file_bytes)
    result["source_contract_sha256"] = hashlib.sha256(contract_bytes).hexdigest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("x", encoding="utf-8") as fh:
        json.dump(result, fh, sort_keys=True, indent=2)
        fh.write("\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--seed-file", type=Path, required=True)
    parser.add_argument("--gas-file", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    readout = run(args.contract, args.seed_file, args.gas_file, args.out)
    print(json.dumps({
        "status": readout["status"],
        "registered_abortion_proxy_is_numeric_not_morphological": True,
        "published_seed_mass_mixed_model_reproduced": False,
        "direct_structural_BALANCE_identified": False,
        "model_count": len(readout["analyses"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

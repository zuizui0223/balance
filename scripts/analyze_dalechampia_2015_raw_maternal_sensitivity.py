#!/usr/bin/env python3
"""Independent mother-paired sensitivity after exact original Dryad file validation.

The original 2015 mixed-effects model is NOT reproduced here. A numeric mass
>=20 mg proxy does not independently identify authors' seed-coat morphology.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from balance_domain.dalechampia_raw_sensitivity import analyze_authenticated_dalechampia
from balance_domain.dalechampia_method_scope import FILE_IDENTITIES


def build_readout(contract_path: Path, seed_path: Path, gas_path: Path,
                  out: Path, recovery_receipt: Path | None = None) -> dict:
    if out.exists():
        raise ValueError("refusing to overwrite source sensitivity readout")
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    files = {
        FILE_IDENTITIES[46163][0]: seed_path.read_bytes(),
        FILE_IDENTITIES[46164][0]: gas_path.read_bytes(),
    }
    if recovery_receipt is not None:
        r = json.loads(recovery_receipt.read_text(encoding="utf-8"))
        if (r.get("status") !=
                "ORIGINAL_DRYAD_BYTES_AND_ROW_SUPPORT_VERIFIED_NO_MODEL"
                or r.get("raw_file_bytes_verified") is not True):
            raise ValueError("source recovery receipt not source-parser verified")
        for name, raw in files.items():
            if r.get("source_file_sha256", {}).get(name) != hashlib.sha256(raw).hexdigest():
                raise ValueError("source recovery SHA256 differs from supplied raw text")

    result = analyze_authenticated_dalechampia(contract, files)
    result["contract_sha256"] = hashlib.sha256(contract_bytes).hexdigest()
    result["original_files_sha256"] = {
        name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(files.items())
    }
    # Source materials are immutable; only write a new receipt.
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as writer:
        json.dump(result, writer, sort_keys=True, indent=2)
        writer.write("\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--seed-file", type=Path, required=True)
    parser.add_argument("--gas-file", type=Path, required=True)
    parser.add_argument("--recovery-receipt", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = build_readout(
        args.contract, args.seed_file, args.gas_file, args.out, args.recovery_receipt,
    )
    print(json.dumps({
        "status": report["status"],
        "n_seed_records": report["n_seed_records"],
        "n_blossoms": report["n_blossoms"],
        "n_maternal_plants": report["n_maternal_plants_with_any_seed_record"],
        "original_2015_published_model_reproduced": False,
        "structural_BALANCE_identified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

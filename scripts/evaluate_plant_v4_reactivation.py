#!/usr/bin/env python3
"""Evaluate BALANCE V4 reactivation evidence from immutable fit/input workspaces."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from balance_domain.plant_reactivation import (  # noqa: E402
    evaluate_v4_reactivation_evidence,
)


FIT_RECEIPT = "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1.json"
ANALYSIS_RECEIPT = "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json"
HUMAN_RECEIPT = "BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json"
ASSEMBLY = "BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv"
ASSEMBLY_READOUT = "BALANCE_PLANT_V4_ASSEMBLY_READOUT.json"
PRIMARY_POSTFIT = "BALANCE_PLANT_V4_PRIMARY_POSTFIT_SUMMARY.json"
GENERALITY_POSTFIT = "BALANCE_PLANT_V4_TEMPORAL_GENERALITY_POSTFIT_SUMMARY.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"required V4 evidence file is missing: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"V4 evidence file must be a JSON object: {path}")
    return data


def _require_hash(*, label: str, path: Path, expected: object) -> str:
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"{label} expected SHA256 is missing or invalid")
    observed = _sha256(path)
    if observed != expected:
        raise ValueError(f"{label} SHA256 mismatch: {observed} != {expected}")
    return observed


def evaluate_from_workspaces(*, input_dir: Path, fit_dir: Path) -> dict:
    """Verify the immutable evidence chain and evaluate reactivation eligibility."""
    fit_receipt_path = fit_dir / FIT_RECEIPT
    fit_receipt = _load_json(fit_receipt_path)
    if (
        fit_receipt.get("schema_version")
        != "BALANCE_PLANT_V4_FIT_EXECUTION_RECEIPT_V1"
    ):
        raise ValueError("V4 fit execution receipt schema mismatch")

    analysis_receipt_path = input_dir / ANALYSIS_RECEIPT
    analysis_receipt = _load_json(analysis_receipt_path)
    if (
        analysis_receipt.get("schema_version")
        != "BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1"
    ):
        raise ValueError("V4 analysis-input receipt schema mismatch")
    _require_hash(
        label="analysis-input receipt",
        path=analysis_receipt_path,
        expected=fit_receipt.get("analysis_input_receipt_sha256"),
    )

    human_receipt_path = input_dir / HUMAN_RECEIPT
    human_receipt = _load_json(human_receipt_path)
    _require_hash(
        label="human-workspace receipt",
        path=human_receipt_path,
        expected=fit_receipt.get("source_human_workspace_receipt_sha256"),
    )
    if (
        analysis_receipt.get("source_human_workspace_receipt_sha256")
        != fit_receipt.get("source_human_workspace_receipt_sha256")
    ):
        raise ValueError(
            "fit and analysis receipts disagree on source human-workspace receipt SHA256"
        )

    assembly_path = input_dir / ASSEMBLY
    _require_hash(
        label="licensed assembly",
        path=assembly_path,
        expected=fit_receipt.get("licensed_assembly_sha256"),
    )

    receipt_hashes = analysis_receipt.get("files_sha256")
    if not isinstance(receipt_hashes, dict):
        raise ValueError("V4 analysis-input receipt lacks files_sha256")
    assembly_readout_path = input_dir / ASSEMBLY_READOUT
    _require_hash(
        label="assembly readout",
        path=assembly_readout_path,
        expected=receipt_hashes.get(ASSEMBLY_READOUT),
    )
    assembly_readout = _load_json(assembly_readout_path)

    postfit_outputs = fit_receipt.get("postfit_outputs")
    postfit_hashes = fit_receipt.get("postfit_output_sha256")
    if not isinstance(postfit_outputs, dict) or not isinstance(postfit_hashes, dict):
        raise ValueError("V4 fit execution receipt lacks postfit output maps")

    primary_path = fit_dir / PRIMARY_POSTFIT
    if "primary" in postfit_outputs:
        _require_hash(
            label="primary postfit summary",
            path=primary_path,
            expected=postfit_hashes.get("primary"),
        )
    elif fit_receipt.get("execution_status") == "COMPLETE":
        raise ValueError("complete V4 fit receipt lacks primary postfit summary")

    generality = None
    if "temporal_generality" in postfit_outputs:
        generality_path = fit_dir / GENERALITY_POSTFIT
        _require_hash(
            label="temporal-generality postfit summary",
            path=generality_path,
            expected=postfit_hashes.get("temporal_generality"),
        )
        generality = _load_json(generality_path)
    elif "TEMPORAL_GENERALITY" in set(fit_receipt.get("active_jobs") or ()):
        raise ValueError(
            "V4 fit receipt activated temporal generality but lacks postfit summary"
        )

    evidence = evaluate_v4_reactivation_evidence(
        human_workspace_receipt=human_receipt,
        assembly_readout=assembly_readout,
        fit_execution_receipt=fit_receipt,
        temporal_generality_postfit_summary=generality,
    )
    return {
        **evidence,
        "evidence_provenance": {
            "fit_execution_receipt_sha256": _sha256(fit_receipt_path),
            "analysis_input_receipt_sha256": _sha256(analysis_receipt_path),
            "human_workspace_receipt_sha256": _sha256(human_receipt_path),
            "licensed_assembly_sha256": _sha256(assembly_path),
            "assembly_readout_sha256": _sha256(assembly_readout_path),
            "primary_postfit_summary_sha256": (
                _sha256(primary_path) if primary_path.is_file() else None
            ),
            "temporal_generality_postfit_summary_sha256": (
                _sha256(fit_dir / GENERALITY_POSTFIT)
                if (fit_dir / GENERALITY_POSTFIT).is_file()
                else None
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--fit-dir", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate_from_workspaces(
        input_dir=args.input_dir.resolve(),
        fit_dir=args.fit_dir.resolve(),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

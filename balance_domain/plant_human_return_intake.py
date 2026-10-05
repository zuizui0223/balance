"""Fail-closed staged intake for returned BALANCE plant human-review files.

Architecture primary (U2+U6), architecture external validation (U1), and predictor
receipt review are operationally independent return stages. Each stage is validated
atomically when supplied; partial files within a stage fail closed. This module does
not adjudicate disagreements or fit a model.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from .plant_agreement_report import build_lane_agreement_report
from .plant_coder_return import merge_coder_returns, write_merged_coder_returns
from .plant_predictor_adjudication import build_predictor_adjudication_readout
from .plant_u2_screen import load_u2_conflict_screen


CODER_RETURN_BASENAMES = {
    ("U1", "CODER_A"): "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv",
    ("U1", "CODER_B"): "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv",
    ("U2", "CODER_A"): "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv",
    ("U2", "CODER_B"): "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv",
    ("U6", "CODER_A"): "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv",
    ("U6", "CODER_B"): "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv",
}
PREDICTOR_RETURN_BASENAMES = {
    "U2": "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    "U6": "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
}
U2_PREDICTOR_V2_BASENAME = (
    "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv"
)
U2_PREDICTOR_V2_FROZEN_BASENAME = (
    "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2_FROZEN.csv"
)
U2_PREDICTOR_V2_FREEZE_RECEIPT = (
    "BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json"
)
U2_PREDICTOR_EXPANSION_TEMPLATE = (
    "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"
)

PRIMARY_ARCHITECTURE_KEYS = (
    "U2_CODER_A",
    "U2_CODER_B",
    "U6_CODER_A",
    "U6_CODER_B",
)
EXTERNAL_ARCHITECTURE_KEYS = (
    "U1_CODER_A",
    "U1_CODER_B",
)
PREDICTOR_KEYS = (
    "U2_PREDICTOR",
    "U6_PREDICTOR",
)

MERGED_BASENAMES = {
    "U1": "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
    "U2": "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
    "U6": "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required_return_paths(return_dir: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for (lane, coder), basename in CODER_RETURN_BASENAMES.items():
        paths[f"{lane}_{coder}"] = return_dir / basename
    for lane, basename in PREDICTOR_RETURN_BASENAMES.items():
        paths[f"{lane}_PREDICTOR"] = return_dir / basename
    paths["U2_PREDICTOR_V2"] = return_dir / U2_PREDICTOR_V2_BASENAME
    return paths


def _complete_stage_or_pending(
    paths: dict[str, Path],
    keys: tuple[str, ...],
    *,
    label: str,
) -> bool:
    present = [paths[key].is_file() for key in keys]
    if any(present) and not all(present):
        missing = [key for key, exists in zip(keys, present) if not exists]
        raise ValueError(
            f"{label} return stage is incomplete; missing canonical files: "
            + ", ".join(missing)
        )
    return all(present)


def _validate_return_surface_presence(
    return_dir: Path,
    *,
    u2_v2_freeze_dir: Path | None = None,
) -> tuple[dict[str, Path], dict[str, bool], str | None]:
    paths = required_return_paths(return_dir)

    u2_v1_present = paths["U2_PREDICTOR"].is_file()
    u2_v2_present = paths["U2_PREDICTOR_V2"].is_file()
    u6_present = paths["U6_PREDICTOR"].is_file()

    if u2_v1_present and u2_v2_present:
        raise ValueError(
            "predictor review is ambiguous: supply exactly one U2 receipt version"
        )
    predictor_any = u2_v1_present or u2_v2_present or u6_present
    predictor_complete = (u2_v1_present ^ u2_v2_present) and u6_present
    if predictor_any and not predictor_complete:
        raise ValueError(
            "predictor review return stage is incomplete; require U6 V1 plus exactly "
            "one U2 receipt version (V1 or V2)"
        )

    predictor_version = (
        "V2" if u2_v2_present else ("V1" if u2_v1_present else None)
    )
    if predictor_version == "V2" and u2_v2_freeze_dir is None:
        raise ValueError(
            "U2 V2 predictor review requires --u2-v2-freeze-dir with the frozen V2 "
            "receipt frame and freeze receipt"
        )
    if predictor_version != "V2" and u2_v2_freeze_dir is not None:
        raise ValueError(
            "U2 V2 freeze workspace was supplied without a U2 V2 predictor return"
        )

    stages = {
        "primary_architecture": _complete_stage_or_pending(
            paths,
            PRIMARY_ARCHITECTURE_KEYS,
            label="primary architecture",
        ),
        "external_validation": _complete_stage_or_pending(
            paths,
            EXTERNAL_ARCHITECTURE_KEYS,
            label="external-validation architecture",
        ),
        "predictor_review": predictor_complete,
    }
    if not any(stages.values()):
        raise ValueError(
            "no complete human-return stage supplied; provide a complete primary "
            "architecture stage, external-validation stage, predictor-review stage, "
            "or any combination"
        )
    return paths, stages, predictor_version


def _validate_u2_v2_freeze_workspace(
    *,
    root: Path,
    freeze_dir: Path,
) -> tuple[dict, Path]:
    receipt_path = freeze_dir / U2_PREDICTOR_V2_FREEZE_RECEIPT
    frame_path = freeze_dir / U2_PREDICTOR_V2_BASENAME
    if not receipt_path.is_file() or not frame_path.is_file():
        raise ValueError(
            "U2 V2 freeze workspace must contain the frozen V2 frame and freeze receipt"
        )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema_version") != "BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2":
        raise ValueError("U2 V2 freeze receipt schema mismatch")
    if receipt.get("status") != "FROZEN_SCREENED_AWAITING_INDEPENDENT_ADJUDICATION":
        raise ValueError("U2 V2 freeze receipt status mismatch")
    if receipt.get("v2_receipt_frame") != U2_PREDICTOR_V2_BASENAME:
        raise ValueError("U2 V2 freeze receipt frame basename mismatch")
    if receipt.get("v2_receipt_frame_sha256") != _sha256(frame_path):
        raise ValueError("U2 V2 frozen receipt frame SHA256 mismatch")

    data = root / "data"
    if receipt.get("v1_receipts_sha256") != _sha256(
        data / PREDICTOR_RETURN_BASENAMES["U2"]
    ):
        raise ValueError("U2 V2 freeze is not bound to the current V1 receipt frame")
    if receipt.get("expansion_template_sha256") != _sha256(
        data / U2_PREDICTOR_EXPANSION_TEMPLATE
    ):
        raise ValueError("U2 V2 freeze is not bound to the current expansion template")
    return receipt, frame_path


def _lane_kwargs(root: Path, lane: str) -> dict[str, Path]:
    data = root / "data"
    if lane == "U1":
        return {"u1_sample_path": data / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"}
    if lane == "U2":
        return {"u2_sample_path": data / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"}
    if lane == "U6":
        return {"u6_freeze_path": data / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"}
    raise ValueError(f"unknown lane {lane!r}")


def _write_disagreements(path: Path, lane: str, report: dict) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "lane",
                "field",
                "dependency_group",
                "coder_a_value",
                "coder_b_value",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for field, items in report["exact_disagreements"].items():
            for item in items:
                writer.writerow({"lane": lane, "field": field, **item})


def _merge_and_report_lane(
    *,
    root: Path,
    paths: dict[str, Path],
    lane: str,
) -> tuple[list[dict[str, str]], dict]:
    merged = merge_coder_returns(
        lane=lane,
        coder_a_path=paths[f"{lane}_CODER_A"],
        coder_b_path=paths[f"{lane}_CODER_B"],
        **_lane_kwargs(root, lane),
    )
    with tempfile.TemporaryDirectory(prefix="balance-plant-return-intake-") as tmp:
        coding_path = Path(tmp) / MERGED_BASENAMES[lane]
        write_merged_coder_returns(coding_path, merged, lane=lane)
        agreement = build_lane_agreement_report(
            lane=lane,
            coding_path=coding_path,
            **_lane_kwargs(root, lane),
        )
    return merged, agreement


def validate_human_return_bundle(
    *,
    root: Path,
    return_dir: Path,
    u2_v2_freeze_dir: Path | None = None,
) -> dict:
    """Validate any complete human-return stages without persistent side effects."""
    paths, stages, predictor_version = _validate_return_surface_presence(
        return_dir,
        u2_v2_freeze_dir=u2_v2_freeze_dir,
    )
    merged: dict[str, list[dict[str, str]]] = {}
    agreement: dict[str, dict] = {}

    if stages["external_validation"]:
        merged["U1"], agreement["U1"] = _merge_and_report_lane(
            root=root,
            paths=paths,
            lane="U1",
        )
    if stages["primary_architecture"]:
        for lane in ("U2", "U6"):
            merged[lane], agreement[lane] = _merge_and_report_lane(
                root=root,
                paths=paths,
                lane=lane,
            )

    predictor: dict[str, dict | None] = {"U2": None, "U6": None}
    u2_v2_freeze_receipt = None
    u2_v2_frozen_frame = None
    if stages["predictor_review"]:
        if predictor_version == "V2":
            u2_v2_freeze_receipt, u2_v2_frozen_frame = (
                _validate_u2_v2_freeze_workspace(
                    root=root,
                    freeze_dir=u2_v2_freeze_dir,
                )
            )
            reviewed_u2 = paths["U2_PREDICTOR_V2"]
            frozen_u2 = u2_v2_frozen_frame
        else:
            reviewed_u2 = paths["U2_PREDICTOR"]
            frozen_u2 = root / "data" / PREDICTOR_RETURN_BASENAMES["U2"]
        frozen_u6 = root / "data" / PREDICTOR_RETURN_BASENAMES["U6"]
        predictor = {
            "U2": build_predictor_adjudication_readout(
                reviewed_u2,
                frozen_u2,
            ),
            "U6": build_predictor_adjudication_readout(
                paths["U6_PREDICTOR"],
                frozen_u6,
            ),
        }

    primary_reliability_pass: bool | None = None
    if stages["primary_architecture"]:
        primary_reliability_pass = all(
            agreement[lane]["reliability_pass"] for lane in ("U2", "U6")
        )

    external_validation_reliability_pass: bool | None = None
    if stages["external_validation"]:
        external_validation_reliability_pass = agreement["U1"]["reliability_pass"]

    u2_source_positive_groups = sorted(
        row["dependency_group"]
        for row in load_u2_conflict_screen(
            root / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
        )
        if row["conflict_status"] == "POSITIVE"
    )
    u2_complete_predictor_groups = (
        set(predictor["U2"]["clusters_with_three_adjudicated_receipts"])
        if predictor["U2"] is not None
        else set()
    )
    u2_missing_source_positive_groups = sorted(
        set(u2_source_positive_groups) - u2_complete_predictor_groups
    )
    predictor_primary_complete = (
        stages["predictor_review"]
        and predictor["U2"] is not None
        and predictor["U6"] is not None
        and not u2_missing_source_positive_groups
        and predictor["U6"]["n_clusters_with_three_adjudicated_receipts"] == 21
    )

    if not stages["primary_architecture"]:
        architecture_next = "AWAIT_PRIMARY_ARCHITECTURE_RETURNS"
        primary_status = "PENDING"
    elif not primary_reliability_pass:
        architecture_next = "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS"
        primary_status = "RELIABILITY_FAIL"
    else:
        architecture_next = "SOURCE_ADJUDICATION"
        primary_status = "RELIABILITY_PASS"

    if not stages["external_validation"]:
        external_validation_next = "AWAIT_U1_EXTERNAL_VALIDATION_RETURNS"
        external_status = "PENDING"
    elif not external_validation_reliability_pass:
        external_validation_next = (
            "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS"
        )
        external_status = "RELIABILITY_FAIL"
    else:
        external_validation_next = "SOURCE_ADJUDICATION"
        external_status = "RELIABILITY_PASS"

    if not stages["predictor_review"]:
        predictor_next = "AWAIT_PREDICTOR_ADJUDICATION_RETURNS"
        predictor_status = "PENDING"
    elif predictor_primary_complete:
        predictor_next = "PREDICTOR_ADJUDICATION_COMPLETE"
        predictor_status = "COMPLETE"
    else:
        predictor_next = "RESOLVE_REJECTED_OR_INCOMPLETE_PRIMARY_PREDICTOR_RECEIPTS"
        predictor_status = "INCOMPLETE"

    return {
        "analysis": "balance_plant_human_return_intake",
        "input_files": {
            key: {
                "basename": path.name,
                "received": path.is_file(),
                **({"sha256": _sha256(path)} if path.is_file() else {}),
            }
            for key, path in sorted(paths.items())
        },
        "stage_received": stages,
        "merged_rows": merged,
        "agreement": agreement,
        "predictor_adjudication": predictor,
        "u2_predictor_receipt_version": predictor_version,
        "u2_source_positive_predictor_groups": u2_source_positive_groups,
        "u2_missing_source_positive_predictor_groups": (
            u2_missing_source_positive_groups
        ),
        "u2_v2_freeze_receipt": u2_v2_freeze_receipt,
        "u2_v2_frozen_frame_sha256": (
            _sha256(u2_v2_frozen_frame)
            if u2_v2_frozen_frame is not None
            else None
        ),
        "primary_architecture_returns_received": stages["primary_architecture"],
        "external_validation_returns_received": stages["external_validation"],
        "predictor_returns_received": stages["predictor_review"],
        "primary_return_status": primary_status,
        "external_validation_return_status": external_status,
        "predictor_return_status": predictor_status,
        "primary_reliability_pass": primary_reliability_pass,
        "external_validation_reliability_pass": external_validation_reliability_pass,
        "external_validation_adjudication_allowed": (
            external_validation_reliability_pass is True
        ),
        "predictor_primary_complete": predictor_primary_complete,
        "primary_architecture_next_step": architecture_next,
        "external_validation_next_step": external_validation_next,
        "predictor_next_step": predictor_next,
        "ready_for_architecture_adjudication": primary_reliability_pass is True,
        "ready_for_v4_assembly": False,
        "v4_assembly_blocker": (
            "architecture adjudication is a separate post-reliability human gate"
        ),
        "claim_ceiling": "validated_human_return_intake_only_no_biological_result",
    }


def write_human_return_intake(
    *,
    root: Path,
    return_dir: Path,
    out_dir: Path,
    u2_v2_freeze_dir: Path | None = None,
) -> dict:
    """Validate supplied return stages, then atomically create one immutable workspace."""
    result = validate_human_return_bundle(
        root=root,
        return_dir=return_dir,
        u2_v2_freeze_dir=u2_v2_freeze_dir,
    )

    if out_dir.exists():
        raise ValueError(
            "human return intake output directory already exists; choose a new "
            "workspace so earlier intake evidence is never silently overwritten"
        )
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(
        prefix=f".{out_dir.name}.tmp-",
        dir=out_dir.parent,
    ))

    try:
        merged_paths: dict[str, str] = {}
        agreement_paths: dict[str, str] = {}
        disagreement_paths: dict[str, str] = {}

        for lane in sorted(result["merged_rows"]):
            merged_name = MERGED_BASENAMES[lane]
            merged_path = tmp_dir / merged_name
            write_merged_coder_returns(
                merged_path,
                result["merged_rows"][lane],
                lane=lane,
            )
            merged_paths[lane] = merged_name

            report_name = f"BALANCE_PLANT_{lane}_AGREEMENT_REPORT_V1.json"
            report_path = tmp_dir / report_name
            report_path.write_text(
                json.dumps(result["agreement"][lane], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            agreement_paths[lane] = report_name

            disagreement_name = f"BALANCE_PLANT_{lane}_DISAGREEMENTS_V1.csv"
            disagreement_path = tmp_dir / disagreement_name
            _write_disagreements(
                disagreement_path,
                lane,
                result["agreement"][lane],
            )
            disagreement_paths[lane] = disagreement_name

        predictor_paths: dict[str, str] = {}
        predictor_frame_paths: dict[str, str] = {}
        predictor_frozen_frame_paths: dict[str, str] = {}
        predictor_freeze_receipt_paths: dict[str, str] = {}
        if result["predictor_returns_received"]:
            u2_reviewed_basename = (
                U2_PREDICTOR_V2_BASENAME
                if result["u2_predictor_receipt_version"] == "V2"
                else PREDICTOR_RETURN_BASENAMES["U2"]
            )
            reviewed_sources = {
                "U2": return_dir / u2_reviewed_basename,
                "U6": return_dir / PREDICTOR_RETURN_BASENAMES["U6"],
            }
            for lane in ("U2", "U6"):
                reviewed_source = reviewed_sources[lane]
                reviewed_target = tmp_dir / reviewed_source.name
                shutil.copyfile(reviewed_source, reviewed_target)
                predictor_frame_paths[lane] = reviewed_target.name

                name = f"BALANCE_PLANT_{lane}_PREDICTOR_ADJUDICATION_READOUT_V1.json"
                path = tmp_dir / name
                path.write_text(
                    json.dumps(
                        result["predictor_adjudication"][lane],
                        indent=2,
                        sort_keys=True,
                    ) + "\n",
                    encoding="utf-8",
                )
                predictor_paths[lane] = name

            if result["u2_predictor_receipt_version"] == "V2":
                if u2_v2_freeze_dir is None:
                    raise ValueError("internal error: missing U2 V2 freeze workspace")
                frozen_source = u2_v2_freeze_dir / U2_PREDICTOR_V2_BASENAME
                frozen_target = tmp_dir / U2_PREDICTOR_V2_FROZEN_BASENAME
                shutil.copyfile(frozen_source, frozen_target)
                predictor_frozen_frame_paths["U2"] = frozen_target.name

                freeze_receipt_source = (
                    u2_v2_freeze_dir / U2_PREDICTOR_V2_FREEZE_RECEIPT
                )
                freeze_receipt_target = tmp_dir / U2_PREDICTOR_V2_FREEZE_RECEIPT
                shutil.copyfile(freeze_receipt_source, freeze_receipt_target)
                predictor_freeze_receipt_paths["U2"] = freeze_receipt_target.name

        receipt = {
            key: value
            for key, value in result.items()
            if key != "merged_rows"
        }
        receipt["outputs"] = {
            "merged_ledgers": merged_paths,
            "agreement_reports": agreement_paths,
            "disagreement_ledgers": disagreement_paths,
            "predictor_reviewed_frames": predictor_frame_paths,
            "predictor_frozen_frames": predictor_frozen_frame_paths,
            "predictor_freeze_receipts": predictor_freeze_receipt_paths,
            "predictor_readouts": predictor_paths,
        }
        receipt["output_sha256"] = {
            family: {
                lane: _sha256(tmp_dir / basename)
                for lane, basename in mapping.items()
            }
            for family, mapping in receipt["outputs"].items()
        }
        receipt_name = "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json"
        receipt_path = tmp_dir / receipt_name
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        tmp_dir.rename(out_dir)
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return {
        "receipt": str(out_dir / receipt_name),
        "primary_architecture_returns_received": result[
            "primary_architecture_returns_received"
        ],
        "external_validation_returns_received": result[
            "external_validation_returns_received"
        ],
        "predictor_returns_received": result["predictor_returns_received"],
        "primary_return_status": result["primary_return_status"],
        "external_validation_return_status": result[
            "external_validation_return_status"
        ],
        "predictor_return_status": result["predictor_return_status"],
        "u2_predictor_receipt_version": result["u2_predictor_receipt_version"],
        "primary_reliability_pass": result["primary_reliability_pass"],
        "external_validation_reliability_pass": result[
            "external_validation_reliability_pass"
        ],
        "predictor_primary_complete": result["predictor_primary_complete"],
        "primary_architecture_next_step": result[
            "primary_architecture_next_step"
        ],
        "external_validation_next_step": result[
            "external_validation_next_step"
        ],
        "predictor_next_step": result["predictor_next_step"],
        "ready_for_v4_assembly": False,
    }

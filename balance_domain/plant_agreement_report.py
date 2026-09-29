"""Canonical agreement report for returned BALANCE plant independent coding."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .plant_macro_agreement import (
    AGREEMENT_FIELDS,
    build_agreement_report_from_rows,
    load_double_coding,
)
from .plant_u1 import load_u1_sample
from .plant_u2 import load_u2_double_code_sample
from .plant_u6 import (
    U6_AGREEMENT_FIELDS,
    build_u6_pass2_agreement_from_rows,
    load_u6_pass1_freeze_manifest,
    load_u6_pass2_double_coding,
)


LANES = {"U1", "U2", "U6"}


def _expected_generic_groups(
    lane: str,
    *,
    u1_sample_path: Path | None,
    u2_sample_path: Path | None,
) -> set[str]:
    if lane == "U1":
        if u1_sample_path is None:
            raise ValueError("U1 agreement requires u1_sample_path")
        return {row["dependency_group"] for row in load_u1_sample(u1_sample_path)}
    if lane == "U2":
        if u2_sample_path is None:
            raise ValueError("U2 agreement requires u2_sample_path")
        return {
            row["dependency_group"]
            for row in load_u2_double_code_sample(u2_sample_path)
        }
    raise ValueError(f"generic agreement unsupported for lane {lane!r}")


def _generic_disagreements(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        grouped[row["cluster_id"]][row["coder_id"]] = row
    out: dict[str, list[dict[str, str]]] = {}
    for field in AGREEMENT_FIELDS:
        items = []
        for group in sorted(grouped):
            pair = grouped[group]
            a = pair["CODER_A"][field]
            b = pair["CODER_B"][field]
            if a != b:
                items.append({
                    "dependency_group": group,
                    "coder_a_value": a,
                    "coder_b_value": b,
                })
        out[field] = items
    return out


def _u6_disagreements(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        grouped[row["dependency_group"]][row["coder_id"]] = row
    out: dict[str, list[dict[str, str]]] = {}
    for field in U6_AGREEMENT_FIELDS:
        items = []
        for group in sorted(grouped):
            pair = grouped[group]
            a = pair["CODER_A"][field]
            b = pair["CODER_B"][field]
            if a != b:
                items.append({
                    "dependency_group": group,
                    "coder_a_value": a,
                    "coder_b_value": b,
                })
        out[field] = items
    return out


def build_lane_agreement_report(
    *,
    lane: str,
    coding_path: Path,
    u1_sample_path: Path | None = None,
    u2_sample_path: Path | None = None,
    u6_freeze_path: Path | None = None,
) -> dict:
    """Build a normalized lane agreement report and exact disagreement ledger."""
    if lane not in LANES:
        raise ValueError(f"unknown plant coding lane {lane!r}")

    if lane == "U6":
        if u6_freeze_path is None:
            raise ValueError("U6 agreement requires u6_freeze_path")
        rows = load_u6_pass2_double_coding(coding_path, u6_freeze_path)
        if any(row["coding_status"] != "CODED" for row in rows):
            raise ValueError("U6 agreement requires every coding_status=CODED")
        raw_report = build_u6_pass2_agreement_from_rows(rows)
        disagreements = _u6_disagreements(rows)
    else:
        rows = load_double_coding(coding_path)
        expected = _expected_generic_groups(
            lane,
            u1_sample_path=u1_sample_path,
            u2_sample_path=u2_sample_path,
        )
        observed = {row["cluster_id"] for row in rows}
        if observed != expected:
            raise ValueError(
                f"{lane} agreement groups disagree with frozen sample; "
                f"missing={sorted(expected-observed)}, extra={sorted(observed-expected)}"
            )
        if {row["coder_id"] for row in rows} != {"CODER_A", "CODER_B"}:
            raise ValueError(f"{lane} agreement requires CODER_A and CODER_B")
        raw_report = build_agreement_report_from_rows(rows)
        disagreements = _generic_disagreements(rows)

    normalized_fields = {}
    failed_fields = []
    for field, stats in raw_report["fields"].items():
        normalized_fields[field] = {
            "n_pairs": stats["n_pairs"],
            "raw_agreement": stats["raw_agreement"],
            "cohen_kappa": stats["cohen_kappa"],
            "gwet_ac1": stats["gwet_ac1"],
            "codebook_repair_trigger": stats["codebook_repair_trigger"],
            "disagreement_groups": [
                item["dependency_group"] for item in disagreements[field]
            ],
        }
        if stats["codebook_repair_trigger"]:
            failed_fields.append(field)

    return {
        "analysis": "balance_plant_independent_coder_agreement_gate",
        "lane": lane,
        "n_dependency_groups": raw_report["n_dependency_groups"],
        "workflow_threshold_raw_agreement": 0.80,
        "fields": normalized_fields,
        "exact_disagreements": disagreements,
        "failed_fields": failed_fields,
        "reliability_pass": not failed_fields,
        "adjudication_allowed": not failed_fields,
        "next_step": (
            "SOURCE_ADJUDICATION"
            if not failed_fields
            else "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS"
        ),
        "claim_ceiling": "coder_reliability_gate_only_no_biological_result",
    }

"""Frozen dependence blocks for the U3 matched heteranthery lane."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from .plant_u3_adjudication import load_u3_control_adjudication


FIELDS = (
    "pair_id",
    "case_taxon",
    "control_taxon",
    "case_family",
    "case_genus",
    "control_genus",
    "dependence_block_id",
    "dependence_scope",
    "shared_control_group",
    "control_reuse_status",
    "adjudication_state",
    "analysis_inclusion_state",
    "dependence_rule",
    "notes",
)

SCOPES = {
    "SAME_GENUS_SINGLE_PAIR",
    "SAME_GENUS_SHARED_CONTROL",
    "SAME_GENUS_MULTI_PAIR",
    "SAME_TRIBE_DIFFERENT_GENUS",
}
REUSE = {
    "UNIQUE_CONTROL",
    "REUSED_CONTROL_TWO_PAIRS",
    "UNIQUE_CONTROL_WITHIN_BLOCK",
}
ADJUDICATION = {"PASS", "OPEN"}
INCLUSION = {"CURRENT_PASS_PAIR", "HELD_OPEN"}
RULE = "COUNT_AT_DEPENDENCE_BLOCK_NOT_NAIVE_PAIR"
EXPECTED_BLOCKS = {
    "U3_DEP_SOLANUM_01",
    "U3_DEP_MONOCHORIA_01",
    "U3_DEP_SENNA_01",
    "U3_DEP_MELASTOMATEAE_01",
}


def load_u3_dependence(
    path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> list[dict[str, str]]:
    adjudication = load_u3_control_adjudication(
        adjudication_path, pair_path, case_path, universe_path
    )
    adjudication_by_pair = {r["pair_id"]: r for r in adjudication}

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 dependence columns must match canonical order")
        rows = list(reader)

    if len(rows) != len(adjudication_by_pair):
        raise ValueError("U3 dependence map must cover every registered primary pair")

    seen: set[str] = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 dependence schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        row.update(clean)

        pair_id = clean["pair_id"]
        if not pair_id or pair_id in seen:
            raise ValueError(f"row {n} pair_id must be unique and frozen")
        seen.add(pair_id)
        if pair_id not in adjudication_by_pair:
            raise ValueError(f"row {n} dependence row references unknown pair")

        adj = adjudication_by_pair[pair_id]
        if clean["case_taxon"] != adj["case_taxon"]:
            raise ValueError(f"row {n} case taxon disagrees with adjudication")
        if clean["control_taxon"] != adj["control_taxon"]:
            raise ValueError(f"row {n} control taxon disagrees with adjudication")
        if clean["adjudication_state"] != adj["decision"]:
            raise ValueError(f"row {n} adjudication_state disagrees with canonical decision")
        expected_inclusion = (
            "CURRENT_PASS_PAIR" if adj["decision"] == "PASS" else "HELD_OPEN"
        )
        if clean["analysis_inclusion_state"] != expected_inclusion:
            raise ValueError(f"row {n} inclusion state disagrees with adjudication")
        if clean["dependence_scope"] not in SCOPES:
            raise ValueError(f"row {n} invalid dependence_scope")
        if clean["control_reuse_status"] not in REUSE:
            raise ValueError(f"row {n} invalid control_reuse_status")
        if clean["dependence_rule"] != RULE:
            raise ValueError(f"row {n} must retain the frozen dependence rule")
        if not clean["dependence_block_id"] or not clean["case_family"]:
            raise ValueError(f"row {n} dependence block and family must be frozen")

    if seen != set(adjudication_by_pair):
        raise ValueError("U3 dependence coverage disagrees with pair adjudication")

    blocks = {r["dependence_block_id"] for r in rows}
    if blocks != EXPECTED_BLOCKS:
        raise ValueError(f"U3 dependence block set drift: {sorted(blocks)}")

    by_block: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_block[row["dependence_block_id"]].append(row)

    mono = by_block["U3_DEP_MONOCHORIA_01"]
    if len(mono) != 2 or {r["control_taxon"] for r in mono} != {"Monochoria australasica"}:
        raise ValueError("Monochoria block must preserve the two-pair shared-control dependence")
    if any(r["control_reuse_status"] != "REUSED_CONTROL_TWO_PAIRS" for r in mono):
        raise ValueError("Monochoria shared control reuse must be explicit")

    senna = by_block["U3_DEP_SENNA_01"]
    if len(senna) != 2 or {r["case_genus"] for r in senna} != {"Senna"}:
        raise ValueError("Senna pairs must remain in one genus-level dependence block")

    return rows


def build_u3_dependence_readout(
    path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    rows = load_u3_dependence(
        path, adjudication_path, pair_path, case_path, universe_path
    )
    pass_rows = [r for r in rows if r["adjudication_state"] == "PASS"]
    pass_blocks = {r["dependence_block_id"] for r in pass_rows}
    all_blocks = {r["dependence_block_id"] for r in rows}
    control_counts = Counter(r["control_taxon"] for r in rows)
    reused = sorted(t for t, n in control_counts.items() if n > 1)
    block_sizes = Counter(r["dependence_block_id"] for r in rows)
    return {
        "analysis": "balance_plant_u3_dependence_v1",
        "n_registered_pairs": len(rows),
        "n_dependence_blocks": len(all_blocks),
        "dependence_block_sizes": dict(sorted(block_sizes.items())),
        "n_pass_pairs": len(pass_rows),
        "n_pass_dependence_blocks": len(pass_blocks),
        "pass_dependence_blocks": sorted(pass_blocks),
        "n_reused_controls": len(reused),
        "reused_controls": reused,
        "naive_pair_independence_allowed": False,
        "dependence_specification_frozen": True,
        "claim_ceiling": (
            "taxonomic_and_shared_control_dependence_blocking_only_"
            "not_phylogenetic_covariance_not_effect_estimate_not_model_readiness"
        ),
    }

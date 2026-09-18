"""Agreement diagnostics for independent BALANCE plant-macro coding."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


FIELDS = (
    "cluster_id",
    "coder_id",
    "conflict_status",
    "architecture_mode",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
    "notes",
)

AGREEMENT_FIELDS = (
    "conflict_status",
    "architecture_mode",
    "module_substrate",
    "conflict_timing_geometry",
    "conflict_spatial_geometry",
)

_MISSING = {"", "none", "null", "nan", "required_before_use"}


def _text(value: object, field: str, row_number: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"row {row_number} {field} must be a string")
    text = value.strip()
    if text.casefold() in _MISSING:
        raise ValueError(f"row {row_number} {field} must be frozen")
    return text


def load_double_coding(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("double-coding columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("double-coding ledger must contain at least one row")

    out: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside canonical schema")
        clean = dict(row)
        for field in FIELDS[:-1]:
            clean[field] = _text(row.get(field), field, row_number)
        key = (clean["cluster_id"], clean["coder_id"])
        if key in seen:
            raise ValueError(f"duplicate cluster/coder pair {key!r}")
        seen.add(key)
        clean["notes"] = (row.get("notes") or "").strip()
        out.append(clean)
    return out


def _paired(rows: Iterable[dict[str, str]]) -> dict[str, tuple[dict[str, str], dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    coder_ids: set[str] = set()
    for row in rows:
        grouped[row["cluster_id"]].append(row)
        coder_ids.add(row["coder_id"])

    if len(coder_ids) != 2:
        raise ValueError(
            f"agreement analysis requires exactly two coder IDs, found {sorted(coder_ids)}"
        )

    out = {}
    for cluster_id, group in grouped.items():
        if len(group) != 2:
            raise ValueError(
                f"cluster {cluster_id!r} must have exactly two independent coder rows"
            )
        if group[0]["coder_id"] == group[1]["coder_id"]:
            raise ValueError(f"cluster {cluster_id!r} repeats one coder")
        out[cluster_id] = (group[0], group[1])
    return out


def _cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        raise ValueError("agreement requires at least one paired cluster")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    cats = set(ca) | set(cb)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1.0 - pe)


def _gwet_ac1(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        raise ValueError("agreement requires at least one paired cluster")
    po = sum(x == y for x, y in zip(a, b)) / n
    cats = sorted(set(a) | set(b))
    q = len(cats)
    if q <= 1:
        return 1.0
    combined = Counter(a + b)
    p = {c: combined[c] / (2 * n) for c in cats}
    pe = sum(p[c] * (1.0 - p[c]) for c in cats) / (q - 1)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1.0 - pe)


def build_agreement_report_from_rows(rows: list[dict[str, str]]) -> dict:
    pairs = _paired(rows)
    fields = {}

    for field in AGREEMENT_FIELDS:
        cluster_ids = sorted(pairs)
        a = [pairs[c][0][field] for c in cluster_ids]
        b = [pairs[c][1][field] for c in cluster_ids]
        n = len(cluster_ids)
        disagreements = [
            c for c in cluster_ids if pairs[c][0][field] != pairs[c][1][field]
        ]
        fields[field] = {
            "n_pairs": n,
            "raw_agreement": (n - len(disagreements)) / n,
            "cohen_kappa": _cohen_kappa(a, b),
            "gwet_ac1": _gwet_ac1(a, b),
            "coder_a_marginals": dict(sorted(Counter(a).items())),
            "coder_b_marginals": dict(sorted(Counter(b).items())),
            "disagreement_clusters": disagreements,
            "codebook_repair_trigger": ((n - len(disagreements)) / n) < 0.80,
        }

    return {
        "analysis": "balance_plant_macro_independent_coder_agreement",
        "n_dependency_groups": len(pairs),
        "fields": fields,
        "workflow_threshold_raw_agreement": 0.80,
    }


def build_agreement_report(path: Path) -> dict:
    return build_agreement_report_from_rows(load_double_coding(path))

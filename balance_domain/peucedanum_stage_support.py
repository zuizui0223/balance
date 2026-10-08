"""Noninferential stage-support and impossible-count audit for Peucedanum."""
from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from typing import Iterable, Mapping


def _count(row: Mapping[str, str], key: str) -> int | None:
    raw = str(row.get(key, "") or "").strip()
    if not raw:
        return None
    try:
        d = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"invalid {key} count") from exc
    if not d.is_finite() or d < 0 or d != d.to_integral_value():
        raise ValueError(f"nonnegative integer required for {key}")
    return int(d)


def audit_stage_support(rows: Iterable[Mapping[str, str]]) -> dict:
    cells: dict[tuple[str, str], Counter] = defaultdict(Counter)
    failures: list[dict] = []
    seen = set()
    n = 0
    for row in rows:
        n += 1
        year, plot = str(row.get("year", "")).strip(), str(row.get("population_id", "")).strip()
        provenance = tuple(str(row.get(k, "")).strip() for k in
                           ("dataset_id", "source_file", "source_sheet", "source_row_number"))
        if not year or not plot or not all(provenance) or provenance in seen:
            raise ValueError("missing or duplicated source-row identity")
        seen.add(provenance)
        c = cells[(year, plot)]
        c["source_rows"] += 1
        h = _count(row, "perfect_flower_count")
        initial = _count(row, "initial_fruit_count")
        final = _count(row, "intact_fruit_count")
        eggs = _count(row, "predator_egg_count")
        for key, value in (("perfect", h), ("initial", initial), ("final", final), ("eggs", eggs)):
            if value is None:
                c["missing_" + key] += 1
        if h is not None and h > 0 and initial is not None:
            c["initial_rate_rows"] += 1
        if h is not None and h > 0 and final is not None:
            c["final_rate_rows"] += 1
        if initial is not None and initial > 0 and final is not None:
            c["conditional_survival_rows"] += 1
        if eggs is not None and initial is not None and initial > 0 and final is not None:
            c["egg_survival_joint_rows"] += 1
        reasons = []
        if h is not None and initial is not None and initial > h:
            reasons.append("initial_exceeds_perfect_flowers")
        if initial is not None and final is not None and final > initial:
            reasons.append("final_exceeds_initial")
        if h is not None and final is not None and final > h:
            reasons.append("final_exceeds_perfect_flowers")
        if reasons:
            failures.append({"source_row_number": provenance[-1], "year": year,
                             "plot": plot, "reasons": reasons})
            c["count_inconsistent_rows"] += 1
    if n == 0:
        raise ValueError("no source rows")
    by_cell = [{"year": y, "plot": p, **dict(sorted(c.items()))}
               for (y, p), c in sorted(cells.items())]
    totals = Counter()
    for c in cells.values():
        totals.update(c)
    return {
        "schema_version": "BALANCE_PEUCEDANUM_STAGE_SUPPORT_AUDIT_V1",
        "status": "COUNT_INCONSISTENCY_HOLD" if failures else "STAGE_SUPPORT_AUDITED",
        "source_rows": n,
        "observed_plot_year_cells": len(cells),
        "totals": dict(sorted(totals.items())),
        "by_year_plot": by_cell,
        "count_inconsistencies": failures,
        "claim_ceiling": "observation_support_only_no_selection_or_mediation_inference",
    }

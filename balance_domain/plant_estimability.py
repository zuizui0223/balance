"""Pre-confirmatory class-support audit for the BALANCE plant macro model."""
from __future__ import annotations

from collections import Counter
from typing import Iterable

from .plant_macro import PRIMARY_ARCHITECTURE_CLASSES, primary_architecture_class


def class_support_from_rows(rows: Iterable[dict[str, str]]) -> dict:
    """Count resolved four-class outcomes among source-screened conflict-positive rows.

    This is a design/estimability diagnostic only. SCREENED rows are never promoted to
    confirmatory evidence by this function.
    """
    rows = list(rows)
    positive = [r for r in rows if r["conflict_status"] == "POSITIVE"]
    classes = []
    unresolved_positive = []
    for row in positive:
        try:
            classes.append(primary_architecture_class(row["architecture_mode"]))
        except ValueError:
            unresolved_positive.append(row["cluster_id"])

    counts = Counter(classes)
    ordered = {name: counts.get(name, 0) for name in PRIMARY_ARCHITECTURE_CLASSES}
    missing = [name for name, n in ordered.items() if n == 0]

    return {
        "n_records": len(rows),
        "n_conflict_positive": len(positive),
        "n_resolved_positive_architecture": len(classes),
        "class_counts": ordered,
        "missing_primary_classes": missing,
        "all_primary_classes_present": not missing,
        "unresolved_positive_architecture_clusters": sorted(unresolved_positive),
    }


def combined_class_support(lanes: dict[str, Iterable[dict[str, str]]]) -> dict:
    """Combine class-presence diagnostics without implying pooled prevalence."""
    lane_rows = {name: list(rows) for name, rows in lanes.items()}
    lane_readouts = {name: class_support_from_rows(rows) for name, rows in lane_rows.items()}

    combined_rows = [row for rows in lane_rows.values() for row in rows]
    combined = class_support_from_rows(combined_rows)

    return {
        "analysis": "balance_plant_preconfirmatory_class_support",
        "lanes": lane_readouts,
        "combined_screening_support": combined,
        "primary_response": "architecture_class4",
        "fit_gate": (
            "do_not_fit_confirmatory_multinomial_until_independent_coding_receipt_"
            "and_dependence_gates_close_and_primary_classes_have_support"
        ),
        "no_response_recoding_on_missing_class": True,
        "claim_ceiling": "screening_estimability_diagnostic_not_prevalence_or_confirmatory_result",
    }

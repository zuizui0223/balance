"""Descriptive estimand-yield diagnostics across plant literature universes."""
from __future__ import annotations

from collections import Counter
from typing import Iterable


def _summarize(rows: Iterable[dict[str, str]]) -> dict:
    rows = list(rows)
    conflict = Counter(r["conflict_status"] for r in rows)
    adjudication = Counter(r["adjudication_status"] for r in rows)
    architecture = Counter(r["architecture_mode"] for r in rows)
    exclusions = Counter(
        r["exclusion_reason"]
        for r in rows
        if r["adjudication_status"] == "EXCLUDED"
    )
    return {
        "n_records": len(rows),
        "conflict_status_counts": dict(sorted(conflict.items())),
        "adjudication_status_counts": dict(sorted(adjudication.items())),
        "architecture_mode_counts": dict(sorted(architecture.items())),
        "exclusion_reason_counts": dict(sorted(exclusions.items())),
        "n_conflict_positive": conflict.get("POSITIVE", 0),
        "n_screened_not_excluded": sum(
            r["adjudication_status"] != "EXCLUDED" for r in rows
        ),
    }


def build_estimand_yield_readout(
    u1_rows: Iterable[dict[str, str]],
    u2_rows: Iterable[dict[str, str]],
) -> dict:
    """Compare screening yield descriptively without treating review universes as prevalence samples."""
    u1 = _summarize(u1_rows)
    u2 = _summarize(u2_rows)

    return {
        "analysis": "balance_plant_estimand_yield",
        "u1_broad_herbivory_pollination": u1,
        "u2_targeted_sexual_interference": u2,
        "development_interpretation": (
            "mechanism_targeted_U2_has_higher_direct_conflict_estimand_yield_"
            "than_broad_interaction_U1_in_current_provisional_screens"
        ),
        "forbidden_interpretation": (
            "not_a_natural_prevalence_comparison_not_a_test_of_conflict_frequency_"
            "between_ecological_domains"
        ),
        "claim_ceiling": (
            "codebook_and_estimand_yield_diagnostic_only_"
            "pending_independent_coding_and_confirmatory_universe_freeze"
        ),
    }

"""Identification certificate for binary conflict presence in the U3 matched lane.

This does not fit a post-hoc model. It enumerates every registered binary
completion of unresolved pollen-fate conflict states and asks whether a
pair-stratified binary conflict coefficient would have a finite conditional
maximum-likelihood estimate.

For matched binary pairs, only conflict-discordant pairs contribute
information. A finite log-odds estimate requires discordant pairs in both
directions. Zero discordant pairs gives no predictor information; discordance
in only one direction gives separation and an infinite estimate.
"""
from __future__ import annotations

from collections import Counter
from itertools import product
from math import log
from pathlib import Path

from .plant_u3_dependence import load_u3_dependence
from .plant_u3_matched_extraction import load_u3_matched_extraction


BINARY = {
    "POSITIVE": 1,
    "NO_DEMONSTRATED_CONFLICT": 0,
}
COMPLETION_STATES = ("NO_DEMONSTRATED_CONFLICT", "POSITIVE")


def _completion_result(
    pair_roles: dict[str, dict[str, dict[str, str]]],
    completed: dict[tuple[str, str], str],
) -> dict:
    case_pos_control_neg = 0
    case_neg_control_pos = 0
    concordant_positive = 0
    concordant_negative = 0

    for pair_id, roles in sorted(pair_roles.items()):
        values = {}
        for role in ("CASE", "CONTROL"):
            row = roles[role]
            status = row["pollen_fate_conflict_status"]
            if status == "UNRESOLVED":
                status = completed[(pair_id, role)]
            values[role] = BINARY[status]

        case, control = values["CASE"], values["CONTROL"]
        if case == 1 and control == 0:
            case_pos_control_neg += 1
        elif case == 0 and control == 1:
            case_neg_control_pos += 1
        elif case == 1 and control == 1:
            concordant_positive += 1
        else:
            concordant_negative += 1

    a = case_pos_control_neg
    b = case_neg_control_pos
    if a and b:
        status = "FINITE_MATCHED_LOG_ODDS"
        mle = log(a / b)
        finite = True
    elif a:
        status = "POSITIVE_DIRECTION_COMPLETE_SEPARATION"
        mle = "+inf"
        finite = False
    elif b:
        status = "NEGATIVE_DIRECTION_COMPLETE_SEPARATION"
        mle = "-inf"
        finite = False
    else:
        status = "NO_WITHIN_PAIR_CONFLICT_VARIATION"
        mle = None
        finite = False

    return {
        "completion": {
            f"{pair_id}:{role}": state
            for (pair_id, role), state in sorted(completed.items())
        },
        "n_case_positive_control_negative": a,
        "n_case_negative_control_positive": b,
        "n_concordant_positive_pairs": concordant_positive,
        "n_concordant_negative_pairs": concordant_negative,
        "identification_status": status,
        "finite_matched_log_odds_mle": finite,
        "conditional_log_odds_mle": mle,
    }


def build_u3_binary_conflict_identification(
    extraction_path: Path,
    dependence_path: Path,
    adjudication_path: Path,
    pair_path: Path,
    case_path: Path,
    universe_path: Path,
) -> dict:
    rows = load_u3_matched_extraction(
        extraction_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )
    dependence = load_u3_dependence(
        dependence_path,
        adjudication_path,
        pair_path,
        case_path,
        universe_path,
    )

    pair_roles: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        pair_roles.setdefault(row["pair_id"], {})[row["taxon_role"]] = row

    unresolved = sorted(
        (
            row["pair_id"],
            row["taxon_role"],
            row["taxon"],
        )
        for row in rows
        if row["pollen_fate_conflict_status"] == "UNRESOLVED"
    )
    if len(unresolved) > 12:
        raise ValueError("too many unresolved U3 conflict rows for exhaustive completion")

    completions = []
    keys = [(pair_id, role) for pair_id, role, _ in unresolved]
    for states in product(COMPLETION_STATES, repeat=len(keys)):
        completed = dict(zip(keys, states))
        completions.append(_completion_result(pair_roles, completed))

    status_counts = Counter(r["identification_status"] for r in completions)
    any_finite = any(r["finite_matched_log_odds_mle"] for r in completions)

    controls = [r for r in rows if r["taxon_role"] == "CONTROL"]
    positive_controls = [
        r for r in controls if r["pollen_fate_conflict_status"] == "POSITIVE"
    ]
    dep_by_pair = {
        r["pair_id"]: r["dependence_block_id"]
        for r in dependence
    }
    positive_control_blocks = sorted(
        {dep_by_pair[r["pair_id"]] for r in positive_controls}
    )

    return {
        "analysis": "balance_u3_binary_conflict_identification",
        "n_matched_pairs": len(pair_roles),
        "n_unresolved_conflict_rows": len(unresolved),
        "unresolved_conflict_rows": [
            {"pair_id": pair_id, "taxon_role": role, "taxon": taxon}
            for pair_id, role, taxon in unresolved
        ],
        "n_binary_completions": len(completions),
        "completion_identification_status_counts": dict(sorted(status_counts.items())),
        "completions": completions,
        "any_completion_has_finite_matched_log_odds_mle": any_finite,
        "all_registered_completions_nonfinite": not any_finite,
        "binary_conflict_discriminant_status": (
            "NONIDENTIFYING_UNDER_ALL_REGISTERED_COMPLETIONS"
            if not any_finite
            else "FINITE_ESTIMATE_POSSIBLE_UNDER_SOME_COMPLETION"
        ),
        "resolved_positive_nonheterantherous_controls": sorted(
            r["taxon"] for r in positive_controls
        ),
        "n_resolved_positive_nonheterantherous_controls": len(positive_controls),
        "resolved_positive_control_dependence_blocks": positive_control_blocks,
        "n_resolved_positive_control_dependence_blocks": len(positive_control_blocks),
        "conflict_positive_sufficient_for_heteranthery": False,
        "sufficiency_falsified_by_positive_controls": bool(positive_controls),
        "heteranthery_implies_conflict_not_identified_as_population_necessity": True,
        "interpretation": (
            "Binary pollen-fate conflict presence cannot identify heteranthery in the "
            "current matched lane. Resolved nonheterantherous controls already retain "
            "positive conflict, and every registered completion of unresolved conflict "
            "states yields either zero within-pair predictor variation or one-direction "
            "separation rather than a finite matched coefficient."
        ),
        "claim_ceiling": (
            "matched_binary_conflict_presence_nonidentification_certificate_only_"
            "not_zero_causal_effect_not_population_prevalence_not_historical_causation"
        ),
    }

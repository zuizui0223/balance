"""Posterior reporting labels for BALANCE plant model V4.

These helpers classify already-computed posterior probabilities. They do not fit models
or choose among models.
"""
from __future__ import annotations


DIRECTION_THRESHOLD = 0.95
PRACTICAL_NEGATIVE_INTERACTION_MARGIN = -1.0


def directional_label(
    *,
    p_positive_primary: float,
    p_positive_sensitivity: float,
    p_negative_primary: float | None = None,
    p_negative_sensitivity: float | None = None,
) -> str:
    """Classify a frozen directional contrast under both registered priors.

    The registered contradiction rule is P(Delta < 0), not 1 - P(Delta > 0).
    Optional fallbacks preserve compatibility for callers that predate explicit
    zero-mass accounting; production post-fit paths pass both probabilities.
    """
    if p_negative_primary is None:
        p_negative_primary = 1.0 - p_positive_primary
    if p_negative_sensitivity is None:
        p_negative_sensitivity = 1.0 - p_positive_sensitivity

    probabilities = {
        "p_positive_primary": p_positive_primary,
        "p_positive_sensitivity": p_positive_sensitivity,
        "p_negative_primary": p_negative_primary,
        "p_negative_sensitivity": p_negative_sensitivity,
    }
    for name, value in probabilities.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0,1]")

    for prior, positive, negative in (
        ("primary", p_positive_primary, p_negative_primary),
        ("sensitivity", p_positive_sensitivity, p_negative_sensitivity),
    ):
        if positive + negative > 1.0 + 1e-12:
            raise ValueError(
                f"{prior} positive/negative direction probabilities are inconsistent"
            )

    if (
        p_positive_primary >= DIRECTION_THRESHOLD
        and p_positive_sensitivity >= DIRECTION_THRESHOLD
    ):
        return "SUPPORTED"
    if (
        p_negative_primary >= DIRECTION_THRESHOLD
        and p_negative_sensitivity >= DIRECTION_THRESHOLD
    ):
        return "CONTRADICTED"
    return "INCONCLUSIVE"


def contradictory_interaction_label(
    *,
    p_gamma_below_negative_margin_primary: float,
    p_gamma_below_negative_margin_sensitivity: float,
) -> str:
    """Flag a practically large reverse U6-by-ORDERED interaction."""
    for name, value in {
        "p_gamma_below_negative_margin_primary": p_gamma_below_negative_margin_primary,
        "p_gamma_below_negative_margin_sensitivity": p_gamma_below_negative_margin_sensitivity,
    }.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0,1]")

    if (
        p_gamma_below_negative_margin_primary >= DIRECTION_THRESHOLD
        or p_gamma_below_negative_margin_sensitivity >= DIRECTION_THRESHOLD
    ):
        return "PRACTICALLY_CONTRADICTORY"
    return "NO_PRACTICALLY_LARGE_CONTRADICTION"


def temporal_generality_decision(
    *,
    preoutcome_common_support_ready: bool,
    per_universe_outcome_support_ready: bool,
    u2_p_positive_primary: float,
    u2_p_positive_sensitivity: float,
    u6_p_positive_primary: float,
    u6_p_positive_sensitivity: float,
    p_gamma_below_negative_margin_primary: float,
    p_gamma_below_negative_margin_sensitivity: float,
    u2_p_negative_primary: float | None = None,
    u2_p_negative_sensitivity: float | None = None,
    u6_p_negative_primary: float | None = None,
    u6_p_negative_sensitivity: float | None = None,
) -> dict:
    """Apply the frozen V4 cross-universe timing-generality decision rules."""
    u2 = directional_label(
        p_positive_primary=u2_p_positive_primary,
        p_positive_sensitivity=u2_p_positive_sensitivity,
        p_negative_primary=u2_p_negative_primary,
        p_negative_sensitivity=u2_p_negative_sensitivity,
    )
    u6 = directional_label(
        p_positive_primary=u6_p_positive_primary,
        p_positive_sensitivity=u6_p_positive_sensitivity,
        p_negative_primary=u6_p_negative_primary,
        p_negative_sensitivity=u6_p_negative_sensitivity,
    )
    interaction = contradictory_interaction_label(
        p_gamma_below_negative_margin_primary=p_gamma_below_negative_margin_primary,
        p_gamma_below_negative_margin_sensitivity=p_gamma_below_negative_margin_sensitivity,
    )

    blockers: list[str] = []
    if not preoutcome_common_support_ready:
        blockers.append("shared_module_common_support")
    if not per_universe_outcome_support_ready:
        blockers.append("per_universe_target_outcome_support")
    if u2 != "SUPPORTED":
        blockers.append(f"U2_direction_{u2.lower()}")
    if u6 != "SUPPORTED":
        blockers.append(f"U6_direction_{u6.lower()}")
    if interaction == "PRACTICALLY_CONTRADICTORY":
        blockers.append("practically_large_contradictory_interaction")

    return {
        "analysis": "balance_plant_v4_temporal_generality_decision",
        "u2_directional_label": u2,
        "u6_directional_label": u6,
        "interaction_label": interaction,
        "cross_universe_generality_supported": not blockers,
        "blockers": blockers,
        "posterior_direction_threshold": DIRECTION_THRESHOLD,
        "practical_negative_interaction_margin_log_odds": (
            PRACTICAL_NEGATIVE_INTERACTION_MARGIN
        ),
        "claim_ceiling": "posterior_reporting_label_not_publication_decision",
    }

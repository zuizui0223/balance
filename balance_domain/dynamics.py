"""Minimal dynamic persistence model for BALANCE/Differentiation switching."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SwitchingCostResult:
    phi: float
    horizon: float
    cost_shared_to_diff: float
    cost_diff_to_shared: float
    forward_threshold: float
    reverse_threshold: float
    hysteresis_width: float
    shared_stays: bool
    differentiated_stays: bool
    history_dependent: bool


def switching_cost_state(
    phi: float,
    horizon: float,
    cost_shared_to_diff: float,
    cost_diff_to_shared: float,
) -> SwitchingCostResult:
    """Evaluate finite-horizon architecture persistence.

    `phi` is the per-unit-horizon instantaneous advantage of differentiation
    (`R-K`).  Starting shared, switching is worth it only if T*phi > C_SD.
    Starting differentiated, switching back is worth it only if
    -T*phi > C_DS.

    Therefore the history-dependent band is
        -C_DS/T <= phi <= C_SD/T.
    """
    T = float(horizon)
    csd = float(cost_shared_to_diff)
    cds = float(cost_diff_to_shared)
    p = float(phi)
    if T <= 0:
        raise ValueError("horizon must be positive")
    if csd < 0 or cds < 0:
        raise ValueError("switching costs must be non-negative")

    forward = csd / T
    reverse = -cds / T
    shared_stays = p <= forward
    differentiated_stays = p >= reverse
    history_dependent = shared_stays and differentiated_stays
    return SwitchingCostResult(
        phi=p,
        horizon=T,
        cost_shared_to_diff=csd,
        cost_diff_to_shared=cds,
        forward_threshold=forward,
        reverse_threshold=reverse,
        hysteresis_width=forward - reverse,
        shared_stays=shared_stays,
        differentiated_stays=differentiated_stays,
        history_dependent=history_dependent,
    )

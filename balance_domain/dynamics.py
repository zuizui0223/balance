"""Minimal dynamic persistence model for BALANCE/Differentiation switching."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import math


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


def _fraction_to_float(value: F, name: str) -> float:
    """Convert one exact finite model quantity without inventing 0/inf."""
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale switching units"
        ) from exc
    if not math.isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale switching units"
        )
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale switching units")
    return out


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

    Threshold algebra is evaluated exactly at the supplied-float level. A
    mathematically finite nonzero threshold or width that cannot be represented
    by the float-valued receipt fails closed rather than becoming ``0`` or
    ``inf``. Once the exact thresholds have been safely projected onto the
    public float-valued receipt surface, the state decisions use those same
    returned thresholds so the reported boundary and the reported switch state
    cannot contradict one another by one rounding unit.
    """
    try:
        T = float(horizon)
        csd = float(cost_shared_to_diff)
        cds = float(cost_diff_to_shared)
        p = float(phi)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("phi, horizon, and switching costs must be finite numeric values") from exc
    if not all(math.isfinite(value) for value in (p, T, csd, cds)):
        raise ValueError("phi, horizon, and switching costs must be finite")
    if T <= 0:
        raise ValueError("horizon must be positive")
    if csd < 0 or cds < 0:
        raise ValueError("switching costs must be non-negative")

    t_q = F.from_float(T)
    csd_q = F.from_float(csd)
    cds_q = F.from_float(cds)
    forward_q = csd_q / t_q
    reverse_q = -cds_q / t_q
    width_q = forward_q - reverse_q

    forward = _fraction_to_float(forward_q, "forward switching threshold")
    reverse = _fraction_to_float(reverse_q, "reverse switching threshold")
    width = _fraction_to_float(width_q, "hysteresis width")
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
        hysteresis_width=width,
        shared_stays=shared_stays,
        differentiated_stays=differentiated_stays,
        history_dependent=history_dependent,
    )

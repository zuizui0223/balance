"""Pure numerical helper for the frozen first Q1B pooled summary.

The first allowed pool is fixed at three independent positive clusters, so the
modified Knapp-Hartung interval uses df=2.  This module intentionally has no
NumPy or network dependency so the registered pooling algebra can be tested in
the ordinary package CI independently of the Impatiens reanalysis workflow.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction as F
import math
from typing import Sequence


T975_DF2 = 4.302652729911275


def _fraction_to_float(value: F, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float"
        ) from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} is finite mathematically but not representable as float")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision")
    return out


def _fraction_decimal(value: F) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _decimal_to_float(value: Decimal, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} is finite mathematically but not representable as float")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision")
    return out


def dl_mkh(yi: Sequence[float], vi: Sequence[float]) -> dict[str, object]:
    """Frozen first-pool DL + modified-KH calculation for exactly k=3.

    The manuscript contract fixes the first allowed pool at three independent
    positive clusters, hence df=2 and :data:`T975_DF2`.  Other sample sizes are
    rejected rather than silently reusing a df=2 critical value.

    All inverse-variance algebra is exact at the supplied-float level.  Only
    the irrational square root and confidence-interval endpoints use
    high-range :class:`~decimal.Decimal` arithmetic before conversion back to
    the float-valued JSON surface.
    """
    try:
        y = tuple(float(value) for value in yi)
        v = tuple(float(value) for value in vi)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Q1B pooling inputs must be finite numeric values") from exc
    if len(y) != 3 or len(v) != 3:
        raise ValueError("first Q1B pool is frozen at exactly k=3 (df=2)")
    if not all(math.isfinite(value) for value in (*y, *v)):
        raise ValueError("Q1B pooling inputs must be finite")
    if not all(value > 0.0 for value in v):
        raise ValueError("Q1B within-study variances must be strictly positive")

    yq = tuple(F.from_float(value) for value in y)
    vq = tuple(F.from_float(value) for value in v)
    weights = tuple(F(1, 1) / value for value in vq)
    sum_w = sum(weights, F(0, 1))
    mu_f_q = sum(
        (weight * estimate for weight, estimate in zip(weights, yq)), F(0, 1)
    ) / sum_w
    Q_q = sum(
        (weight * (estimate - mu_f_q) ** 2 for weight, estimate in zip(weights, yq)),
        F(0, 1),
    )

    df = 2
    c_q = sum_w - sum((weight * weight for weight in weights), F(0, 1)) / sum_w
    if c_q <= 0:
        raise ValueError("Q1B inverse-variance geometry is degenerate")
    tau2_q = max(F(0, 1), (Q_q - df) / c_q)

    random_weights = tuple(F(1, 1) / (variance + tau2_q) for variance in vq)
    sum_wr = sum(random_weights, F(0, 1))
    mu_q = sum(
        (weight * estimate for weight, estimate in zip(random_weights, yq)),
        F(0, 1),
    ) / sum_wr
    q_q = sum(
        (weight * (estimate - mu_q) ** 2 for weight, estimate in zip(random_weights, yq)),
        F(0, 1),
    ) / df
    se2_q = max(F(1, 1), q_q) / sum_wr
    i2_q = (
        max(F(0, 1), (Q_q - df) / Q_q) * 100
        if Q_q > 0
        else F(0, 1)
    )

    mu_f = _fraction_to_float(mu_f_q, "fixed-effect mean")
    Q = _fraction_to_float(Q_q, "Cochran Q")
    tau2 = _fraction_to_float(tau2_q, "DerSimonian-Laird tau^2")
    mu = _fraction_to_float(mu_q, "random-effects mean")
    I2 = _fraction_to_float(i2_q, "I^2")

    with localcontext() as ctx:
        ctx.prec = 80
        se_decimal = _fraction_decimal(se2_q).sqrt()
        mu_decimal = _fraction_decimal(mu_q)
        t_decimal = Decimal.from_float(T975_DF2)
        lo_decimal = mu_decimal - t_decimal * se_decimal
        hi_decimal = mu_decimal + t_decimal * se_decimal
    se = _decimal_to_float(se_decimal, "modified Knapp-Hartung standard error")
    ci = [
        _decimal_to_float(lo_decimal, "modified Knapp-Hartung lower CI"),
        _decimal_to_float(hi_decimal, "modified Knapp-Hartung upper CI"),
    ]

    return {
        "k": 3,
        "mu_random": mu,
        "se_mkh": se,
        "ci95_mkh": ci,
        "tau2_DL": tau2,
        "Q_fixed": Q,
        "I2_percent": I2,
        "mu_fixed": mu_f,
    }

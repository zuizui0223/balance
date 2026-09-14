"""Design monotone BALANCE sweeps for a target hysteresis-width resolution.

If the forward and reverse maximum forcing increments are ``delta_up`` and
``delta_down``, the finite-step overestimation of hysteresis width is bounded by
``delta_up + delta_down``. This module allocates a declared total error budget
between two sweep spans to minimize the required integer number of intervals.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from math import inf, isfinite, nextafter


@dataclass(frozen=True)
class HysteresisResolutionDesign:
    forward_span: float
    reverse_span: float
    width_error_budget: float
    forward_intervals: int
    reverse_intervals: int
    total_intervals: int
    forward_step: float
    reverse_step: float
    guaranteed_width_inflation: float
    continuous_optimal_forward_step: float
    continuous_optimal_reverse_step: float
    continuous_interval_lower_bound: float


def _ceil_fraction(value: Fraction) -> int:
    """Return the exact ceiling of a positive Fraction."""
    if value <= 0:
        raise ValueError("ceiling helper requires a positive value")
    return -(-value.numerator // value.denominator)


def _finite_positive_float(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite positive number, not boolean")
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite positive number") from exc
    if not isfinite(out) or out <= 0.0:
        raise ValueError(f"{name} must be a finite positive number")
    return out


def _fraction_point(value: Fraction, name: str) -> float:
    """Convert a positive actionable quantity without inventing zero/infinity."""
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is not float-representable; change design scale") from exc
    if not isfinite(out):
        raise ValueError(f"{name} is not float-representable; change design scale")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; change design scale")
    return out


def _fraction_upper(value: Fraction, name: str, *, cap: float | None = None) -> float:
    """Return a conservative finite upper float for an exact nonnegative value."""
    out = _fraction_point(value, name)
    if Fraction.from_float(out) < value:
        out = nextafter(out, inf)
    if cap is not None:
        out = min(out, cap)
    if not isfinite(out):
        raise ValueError(f"{name} upper certificate is not float-representable")
    return out


def _decimal_point(value: Decimal, name: str) -> float:
    try:
        out = float(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"{name} is not float-representable; change design scale") from exc
    if not isfinite(out):
        raise ValueError(f"{name} is not float-representable; change design scale")
    if value != 0 and out == 0.0:
        raise ValueError(f"{name} underflows float precision; change design scale")
    return out


def _decimal_lower(value: Decimal, name: str) -> float:
    """Conservatively expose a positive continuous lower bound."""
    out = _decimal_point(value, name)
    if Decimal.from_float(out) > value:
        out = nextafter(out, -inf)
    if not isfinite(out) or (value > 0 and out <= 0.0):
        raise ValueError(f"{name} cannot be represented as a positive finite lower bound")
    return out


def _inflation_exact(
    total: int,
    n_up: int,
    forward_span: Fraction,
    reverse_span: Fraction,
) -> Fraction:
    if total < 2 or not 1 <= n_up < total:
        raise ValueError("interval allocation must split a total >= 2")
    return forward_span / n_up + reverse_span / (total - n_up)


def _minimum_inflation_index(
    total: int,
    forward_span: Fraction,
    reverse_span: Fraction,
) -> int:
    """Return the smallest n_up minimizing inflation for a fixed total.

    For

        f(n) = su/n + sd/(N-n),

    the discrete difference changes sign at most once because the first term's
    marginal decrease shrinks with n while the second term's marginal increase
    grows. The first index satisfying ``f(n+1) >= f(n)`` is therefore the
    smallest global minimizer. Exact Fraction comparisons avoid numerical
    tolerance changing the integer optimum.
    """
    if total < 2:
        raise ValueError("total intervals must be at least two")

    lo = 1
    hi = total - 1
    while lo < hi:
        n_up = (lo + hi) // 2
        # f(n+1) - f(n) >= 0 iff
        # sd*n*(n+1) >= su*(N-n-1)*(N-n).
        left = reverse_span * n_up * (n_up + 1)
        right = forward_span * (total - n_up - 1) * (total - n_up)
        if left >= right:
            hi = n_up
        else:
            lo = n_up + 1
    return lo


def _total_is_feasible(
    total: int,
    forward_span: Fraction,
    reverse_span: Fraction,
    budget: Fraction,
) -> bool:
    n_up = _minimum_inflation_index(total, forward_span, reverse_span)
    return _inflation_exact(total, n_up, forward_span, reverse_span) <= budget


def _first_feasible_up_allocation(
    total: int,
    forward_span: Fraction,
    reverse_span: Fraction,
    budget: Fraction,
) -> int:
    """Return the smallest feasible n_up for the minimum feasible total.

    This preserves the historical deterministic tie-break: among designs with
    the same minimum total interval count, prefer the smaller forward count.
    Convexity makes the feasible allocations contiguous around the minimizer,
    so the left edge is found by binary search.
    """
    minimizer = _minimum_inflation_index(total, forward_span, reverse_span)
    if _inflation_exact(total, minimizer, forward_span, reverse_span) > budget:
        raise RuntimeError("requested total has no feasible interval allocation")

    lo = 1
    hi = minimizer
    while lo < hi:
        n_up = (lo + hi) // 2
        if _inflation_exact(total, n_up, forward_span, reverse_span) <= budget:
            hi = n_up
        else:
            lo = n_up + 1
    return lo


def optimal_hysteresis_resolution_design(
    *,
    forward_span: float,
    reverse_span: float,
    width_error_budget: float,
) -> HysteresisResolutionDesign:
    """Return the exact minimum-total-interval two-sweep design.

    For integer interval counts ``n_up,n_down`` the guarantee is

        forward_span/n_up + reverse_span/n_down <= width_error_budget.

    The integer feasibility problem is evaluated exactly at the supplied-float
    level. Continuous square-root diagnostics are evaluated with high-range
    ``Decimal`` arithmetic so a representable final diagnostic is not lost to
    an overflowing binary-float intermediate. Actionable step sizes and final
    diagnostics fail closed if a nonzero finite value cannot be represented on
    the float-valued receipt surface.

    Runtime is ``O((log N)^2)`` in the returned total interval count rather than
    scanning every candidate forward count up to ``N``.
    """
    su = _finite_positive_float(forward_span, "forward_span")
    sd = _finite_positive_float(reverse_span, "reverse_span")
    eta = _finite_positive_float(width_error_budget, "width_error_budget")

    su_exact = Fraction.from_float(su)
    sd_exact = Fraction.from_float(sd)
    eta_exact = Fraction.from_float(eta)

    # Continuous diagnostics are not used to choose the integer design, but are
    # reported as the relaxation benchmark. High-range Decimal arithmetic avoids
    # root_sum**2 overflow when the final dimensionless lower bound is ordinary.
    with localcontext() as ctx:
        ctx.prec = 100
        su_d = Decimal.from_float(su)
        sd_d = Decimal.from_float(sd)
        eta_d = Decimal.from_float(eta)
        root_up = su_d.sqrt()
        root_down = sd_d.sqrt()
        root_sum = root_up + root_down
        delta_up_d = eta_d * root_up / root_sum
        delta_down_d = eta_d * root_down / root_sum
        lower_bound_d = root_sum * root_sum / eta_d

    delta_up_cont = _decimal_point(delta_up_d, "continuous optimal forward step")
    delta_down_cont = _decimal_point(delta_down_d, "continuous optimal reverse step")
    lower_bound = _decimal_lower(lower_bound_d, "continuous interval lower bound")

    # Constructive equal-budget allocation gives an exact feasible upper bound:
    # su/n_up <= eta/2 and sd/n_down <= eta/2.
    n_up_equal = max(1, _ceil_fraction(2 * su_exact / eta_exact))
    n_down_equal = max(1, _ceil_fraction(2 * sd_exact / eta_exact))
    upper_total = n_up_equal + n_down_equal

    # Any feasible total N must satisfy (su+sd)/N <= eta because each of its
    # two interval counts is at most N. This exact lower bound is weaker than
    # the continuous square-root bound but needs no irrational rounding.
    lower_total = max(2, _ceil_fraction((su_exact + sd_exact) / eta_exact))

    lo = lower_total
    hi = upper_total
    while lo < hi:
        total = (lo + hi) // 2
        if _total_is_feasible(total, su_exact, sd_exact, eta_exact):
            hi = total
        else:
            lo = total + 1

    total = lo
    n_up = _first_feasible_up_allocation(
        total,
        su_exact,
        sd_exact,
        eta_exact,
    )
    n_down = total - n_up
    exact_guaranteed = _inflation_exact(total, n_up, su_exact, sd_exact)
    if exact_guaranteed > eta_exact:
        raise RuntimeError("integer design failed declared hysteresis-width precision")

    forward_step_exact = su_exact / n_up
    reverse_step_exact = sd_exact / n_down
    forward_step = _fraction_point(forward_step_exact, "forward interval step")
    reverse_step = _fraction_point(reverse_step_exact, "reverse interval step")
    guaranteed = _fraction_upper(
        exact_guaranteed,
        "guaranteed width inflation",
        cap=eta,
    )

    return HysteresisResolutionDesign(
        forward_span=su,
        reverse_span=sd,
        width_error_budget=eta,
        forward_intervals=n_up,
        reverse_intervals=n_down,
        total_intervals=total,
        forward_step=forward_step,
        reverse_step=reverse_step,
        guaranteed_width_inflation=guaranteed,
        continuous_optimal_forward_step=delta_up_cont,
        continuous_optimal_reverse_step=delta_down_cont,
        continuous_interval_lower_bound=lower_bound,
    )

"""Design monotone BALANCE sweeps for a target hysteresis-width resolution.

If the forward and reverse maximum forcing increments are ``delta_up`` and
``delta_down``, the finite-step overestimation of hysteresis width is bounded by
``delta_up + delta_down``. This module allocates a declared total error budget
between two sweep spans to minimize the required integer number of intervals.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, nextafter, sqrt


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

    The continuous relaxation allocates step sizes in proportion to square
    roots of sweep spans. For the integer problem, feasibility at a fixed total
    interval count is a one-dimensional discrete-convex problem, so its minimum
    is found by binary search. A second binary search finds the smallest feasible
    total. Input floats are converted to their exact binary rational values for
    every feasibility comparison, eliminating scale-dependent epsilon decisions.

    Runtime is ``O((log N)^2)`` in the returned total interval count rather than
    scanning every candidate forward count up to ``N``.
    """
    su = float(forward_span)
    sd = float(reverse_span)
    eta = float(width_error_budget)
    if not all(isfinite(x) for x in (su, sd, eta)):
        raise ValueError("spans and error budget must be finite")
    if su <= 0.0 or sd <= 0.0 or eta <= 0.0:
        raise ValueError("spans and error budget must be positive")

    root_up = sqrt(su)
    root_down = sqrt(sd)
    root_sum = root_up + root_down
    delta_up_cont = eta * (root_up / root_sum)
    delta_down_cont = eta * (root_down / root_sum)
    lower_bound = (root_sum * root_sum) / eta

    su_exact = Fraction.from_float(su)
    sd_exact = Fraction.from_float(sd)
    eta_exact = Fraction.from_float(eta)

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

    # Report a conservative float upper envelope of the exact rational
    # inflation. If the nearest float rounds down, move one representable value
    # upward; never report above the user-supplied budget, which is itself an
    # exact upper bound after the exact feasibility check above.
    guaranteed = min(
        eta,
        nextafter(float(exact_guaranteed), float("inf")),
    )

    return HysteresisResolutionDesign(
        forward_span=su,
        reverse_span=sd,
        width_error_budget=eta,
        forward_intervals=n_up,
        reverse_intervals=n_down,
        total_intervals=total,
        forward_step=su / n_up,
        reverse_step=sd / n_down,
        guaranteed_width_inflation=guaranteed,
        continuous_optimal_forward_step=delta_up_cont,
        continuous_optimal_reverse_step=delta_down_cont,
        continuous_interval_lower_bound=lower_bound,
    )

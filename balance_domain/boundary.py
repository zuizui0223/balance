"""Canonical two-margin boundary logic for BALANCE-domain occupancy.

BALANCE is the intersection of two positive margins:

    conflict_margin = L > 0
    reserve_margin  = rho > 0

Callers may derive ``rho`` from different representations (for example
``rho = K-sL = -Phi`` or ``rho = W_S* - W_D* = -Delta``), but state and path
geometry should be decided only once, here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal, Sequence


# Purely numerical boundary band for point-estimate APIs. Measurement or
# inferential uncertainty belongs in the interval/receipt layer, not here.
DEFAULT_BOUNDARY_TOLERANCE = 1e-12

ReservePosition = Literal["POSITIVE", "INTERFACE", "NEGATIVE"]


@dataclass(frozen=True)
class TwoMarginPoint:
    conflict_margin: float
    reserve_margin: float
    conflict_active: bool
    reserve_position: ReservePosition
    middle_active: bool


@dataclass(frozen=True)
class TwoMarginPath:
    points: tuple[TwoMarginPoint, ...]
    middle_intervals: tuple[tuple[float, float], ...]
    middle_width: float


def _level_crossing(
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    level: float,
) -> float:
    """Interpolate a finite level crossing without overflow-prone differences."""
    if y1 == y0:
        crossing = 0.5 * x0 + 0.5 * x1
    else:
        scale = max(abs(y0), abs(y1), abs(level))
        if scale == 0.0:
            crossing = 0.5 * x0 + 0.5 * x1
        else:
            sy0 = y0 / scale
            sy1 = y1 / scale
            slevel = level / scale
            fraction = (slevel - sy0) / (sy1 - sy0)
            if not math.isfinite(fraction):
                raise ValueError("boundary crossing fraction must remain finite")
            crossing = (1.0 - fraction) * x0 + fraction * x1
    if not math.isfinite(crossing):
        raise ValueError("boundary crossing coordinate must remain finite; rescale environment units")
    return crossing


def classify_two_margin_point(
    conflict_margin: float,
    reserve_margin: float,
    *,
    tolerance: float = DEFAULT_BOUNDARY_TOLERANCE,
) -> TwoMarginPoint:
    """Classify one context from the two BALANCE-defining margins.

    ``tolerance`` defines the numerical interface band. Conflict is active
    only when ``L > tolerance``. The architecture reserve is positive only
    when ``rho > tolerance`` and negative only when ``rho < -tolerance``.
    """
    L = float(conflict_margin)
    rho = float(reserve_margin)
    tol = float(tolerance)
    if not all(math.isfinite(value) for value in (L, rho, tol)):
        raise ValueError("two-margin inputs and tolerance must be finite")
    if L < 0:
        raise ValueError("conflict margin must be non-negative")
    if tol < 0:
        raise ValueError("tolerance must be non-negative")

    conflict_active = L > tol
    if rho > tol:
        reserve_position: ReservePosition = "POSITIVE"
    elif rho < -tol:
        reserve_position = "NEGATIVE"
    else:
        reserve_position = "INTERFACE"

    return TwoMarginPoint(
        conflict_margin=L,
        reserve_margin=rho,
        conflict_active=conflict_active,
        reserve_position=reserve_position,
        middle_active=conflict_active and reserve_position == "POSITIVE",
    )


def positive_support_monotone(
    values: Sequence[float],
    *,
    tolerance: float = DEFAULT_BOUNDARY_TOLERANCE,
) -> bool:
    """Return whether positive support, once entered, never disappears.

    The magnitude may rise or fall. Only the support pattern relative to the
    registered tolerance is constrained.
    """
    vals = tuple(float(value) for value in values)
    tol = float(tolerance)
    if not vals:
        raise ValueError("at least one support value is required")
    if not all(math.isfinite(value) for value in (*vals, tol)):
        raise ValueError("support values and tolerance must be finite")
    if any(value < 0 for value in vals):
        raise ValueError("support values must be non-negative")
    if tol < 0:
        raise ValueError("tolerance must be non-negative")
    active = tuple(value > tol for value in vals)
    return all(not active[i] or active[i + 1] for i in range(len(active) - 1))


def analyze_two_margin_path(
    environment: Sequence[float],
    conflict_margin: Sequence[float],
    reserve_margin: Sequence[float],
    *,
    tolerance: float = DEFAULT_BOUNDARY_TOLERANCE,
) -> TwoMarginPath:
    """Find piecewise-linear intervals where both BALANCE margins are positive.

    Entry into the intersection occurs at the later of the two boundary
    crossings; exit occurs at the earlier one. This handles simultaneous
    changes in conflict support and architecture reserve symmetrically.

    All returned environmental coordinates and the total middle width are
    required to remain finite. Extremely wide but finite input coordinates may
    therefore still be analyzed when the identified BALANCE interval itself is
    representable; only an unrepresentable derived width fails closed.
    """
    x = tuple(float(value) for value in environment)
    L = tuple(float(value) for value in conflict_margin)
    rho = tuple(float(value) for value in reserve_margin)
    tol = float(tolerance)
    n = len(x)
    if n < 2 or not (len(L) == len(rho) == n):
        raise ValueError("environment and both margins must have equal length >= 2")
    if not all(math.isfinite(value) for values in (x, L, rho) for value in values) or not math.isfinite(tol):
        raise ValueError("two-margin path values and tolerance must be finite")
    if any(x[i + 1] <= x[i] for i in range(n - 1)):
        raise ValueError("environment must be strictly increasing")
    if any(value < 0 for value in L):
        raise ValueError("conflict margin must be non-negative")
    if tol < 0:
        raise ValueError("tolerance must be non-negative")

    points = tuple(
        classify_two_margin_point(li, ri, tolerance=tol)
        for li, ri in zip(L, rho)
    )

    intervals: list[tuple[float, float]] = []
    in_middle = False
    start: float | None = None
    for i, point in enumerate(points):
        if point.middle_active and not in_middle:
            start = x[i]
            if i > 0:
                candidates: list[float] = []
                if L[i - 1] <= tol < L[i]:
                    candidates.append(
                        _level_crossing(x[i - 1], x[i], L[i - 1], L[i], tol)
                    )
                if rho[i - 1] <= tol < rho[i]:
                    candidates.append(
                        _level_crossing(x[i - 1], x[i], rho[i - 1], rho[i], tol)
                    )
                if candidates:
                    start = max(candidates)
            in_middle = True

        if in_middle and not point.middle_active:
            end = x[i]
            if i > 0:
                candidates = []
                if L[i - 1] > tol >= L[i]:
                    candidates.append(
                        _level_crossing(x[i - 1], x[i], L[i - 1], L[i], tol)
                    )
                if rho[i - 1] > tol >= rho[i]:
                    candidates.append(
                        _level_crossing(x[i - 1], x[i], rho[i - 1], rho[i], tol)
                    )
                if candidates:
                    end = min(candidates)
            if start is None:
                raise RuntimeError("internal two-margin path state lost interval start")
            intervals.append((float(start), float(end)))
            in_middle = False
            start = None

    if in_middle:
        if start is None:
            raise RuntimeError("internal two-margin path state lost interval start")
        intervals.append((float(start), x[-1]))

    lengths = []
    for begin, end in intervals:
        if begin < x[0] - tol or end > x[-1] + tol or end < begin:
            raise ValueError("middle-world interval lies outside the registered path")
        length = end - begin
        if not math.isfinite(length):
            raise ValueError("middle-world interval width must remain finite; rescale environment units")
        lengths.append(length)
    width = sum(lengths)
    if not math.isfinite(width):
        raise ValueError("middle-world width must remain finite; rescale environment units")
    if width < -tol:
        raise ValueError("middle-world width must be non-negative")

    return TwoMarginPath(
        points=points,
        middle_intervals=tuple(intervals),
        middle_width=width,
    )

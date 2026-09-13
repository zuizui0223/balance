"""Two-sided world certificate and geometry for Chapter 2 BALANCE.

SCH and BITA contribute complementary inequalities:

- SCH-facing condition: a real shared-axis conflict exists, ``L > 0``.
- BITA-facing condition: differentiated architecture is not yet favoured,
  ``Phi = sL - K < 0``.

BALANCE is their intersection. When all terms use a common fitness scale,
this module also locates a point inside the middle world relative to its two
bounding surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import math

from .boundary import classify_two_margin_point, two_margin_middle_position


@dataclass(frozen=True)
class MiddleWorldCertificate:
    conflict_load: float
    decoupling: float
    architecture_cost: float
    recoverable_loss: float
    architecture_margin: float
    sch_conflict_active: bool
    bita_differentiation_favoured: bool
    state: str
    sch_boundary_distance: float | None
    bita_boundary_distance: float | None
    middle_position: float | None
    two_sided_depth: float | None


@dataclass(frozen=True)
class BalanceDomainGeometry:
    decoupling: float
    architecture_cost: float
    finite_bita_boundary: bool
    critical_conflict_load: float | None
    equal_margin_conflict_load: float | None
    max_two_sided_depth: float | None
    equal_margin_fraction_of_conflict_width: float | None
    criticality_index_at_equal_margin: float | None
    architecture_pressure_ratio_at_equal_margin: float | None
    sch_limited_width: float | None
    bita_limited_width: float | None
    bita_to_sch_width_ratio: float | None


def _positive_fraction_to_float(value: F, name: str) -> float:
    """Convert a positive exact geometry quantity without inventing 0/inf."""
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale fitness units"
        ) from exc
    if not math.isfinite(out):
        raise ValueError(
            f"{name} is finite mathematically but not representable as float; rescale fitness units"
        )
    if out == 0.0:
        raise ValueError(f"{name} underflows float precision; rescale fitness units")
    return out


def balance_domain_geometry(decoupling: float, architecture_cost: float) -> BalanceDomainGeometry:
    """Return the one-dimensional BALANCE geometry on its theorem domain.

    This helper implements the positive-cost geometry of Propositions 4--5 in
    ``theory/MIDDLE_WORLD_RESULTS_V1.md`` and therefore requires ``K>0``.
    Degenerate ``K=0`` contexts remain valid inputs to :func:`classify_middle_world`,
    but they have no positive-width BALANCE interval and must not be promoted to
    an interior deepest-point geometry.

    For ``s>0`` and ``K>0`` the static middle world is ``0 < L < K/s``. The
    equal-margin point is ``K/(1+s)``. All finite-interval quantities are
    evaluated exactly at the supplied-float level before conversion back to
    float. A mathematically finite positive boundary/width/ratio that cannot be
    represented by the float-valued API fails closed rather than appearing as
    ``inf`` or ``0`` while ``finite_bita_boundary`` remains true.
    """
    s = float(decoupling)
    K = float(architecture_cost)
    if not math.isfinite(s) or not math.isfinite(K):
        raise ValueError("inputs must be finite")
    if not 0 <= s <= 1:
        raise ValueError("decoupling must lie in [0,1]")
    if K <= 0:
        raise ValueError("architecture_cost must be positive for BALANCE domain geometry")

    if s == 0:
        return BalanceDomainGeometry(
            decoupling=s,
            architecture_cost=K,
            finite_bita_boundary=False,
            critical_conflict_load=None,
            equal_margin_conflict_load=None,
            max_two_sided_depth=None,
            equal_margin_fraction_of_conflict_width=None,
            criticality_index_at_equal_margin=None,
            architecture_pressure_ratio_at_equal_margin=None,
            sch_limited_width=None,
            bita_limited_width=None,
            bita_to_sch_width_ratio=None,
        )

    s_q = F.from_float(s)
    k_q = F.from_float(K)
    one = F(1, 1)
    lcrit_q = k_q / s_q
    lequal_q = k_q / (one + s_q)
    sch_width_q = lequal_q
    bita_width_q = k_q / (s_q * (one + s_q))
    fraction_q = s_q / (one + s_q)
    pressure_q = fraction_q
    skew_q = one / s_q

    Lcrit = _positive_fraction_to_float(lcrit_q, "critical conflict load")
    Lequal = _positive_fraction_to_float(lequal_q, "equal-margin conflict load")
    sch_width = _positive_fraction_to_float(sch_width_q, "SCH-limited width")
    bita_width = _positive_fraction_to_float(bita_width_q, "BITA-limited width")
    fraction = _positive_fraction_to_float(fraction_q, "equal-margin fraction of conflict width")
    pressure_equal = _positive_fraction_to_float(pressure_q, "architecture-pressure ratio at equal margin")
    skew = _positive_fraction_to_float(skew_q, "BITA-to-SCH width ratio")

    return BalanceDomainGeometry(
        decoupling=s,
        architecture_cost=K,
        finite_bita_boundary=True,
        critical_conflict_load=Lcrit,
        equal_margin_conflict_load=Lequal,
        max_two_sided_depth=Lequal,
        equal_margin_fraction_of_conflict_width=fraction,
        criticality_index_at_equal_margin=0.5,
        architecture_pressure_ratio_at_equal_margin=pressure_equal,
        sch_limited_width=sch_width,
        bita_limited_width=bita_width,
        bita_to_sch_width_ratio=skew,
    )


def classify_middle_world(
    conflict_load: float,
    decoupling: float,
    architecture_cost: float,
    *,
    tolerance: float = 1e-12,
) -> MiddleWorldCertificate:
    """Classify one context in the three-world programme."""
    L = float(conflict_load)
    s = float(decoupling)
    K = float(architecture_cost)
    tol = float(tolerance)

    if not all(math.isfinite(x) for x in (L, s, K, tol)):
        raise ValueError("inputs must be finite")
    if L < 0 or K < 0:
        raise ValueError("conflict_load and architecture_cost must be non-negative")
    if not 0 <= s <= 1:
        raise ValueError("decoupling must lie in [0,1]")
    if tol <= 0:
        raise ValueError("tolerance must be positive")

    R = s * L
    phi = R - K
    rho = -phi
    point = classify_two_margin_point(L, rho, tolerance=tol)
    sch_active = point.conflict_active
    bita_favoured = point.reserve_position == "NEGATIVE"

    if not sch_active:
        state = "SCH_NO_CONFLICT_WORLD"
    elif point.reserve_position == "INTERFACE":
        state = "BALANCE_BITA_INTERFACE"
    elif point.reserve_position == "POSITIVE":
        state = "BALANCE_MIDDLE_WORLD"
    else:
        state = "BITA_DIFFERENTIATION_WORLD"

    if state == "BALANCE_MIDDLE_WORLD":
        xi = two_margin_middle_position(L, rho)
        depth = min(L, rho)
        sch_distance = L
        bita_distance = rho
    else:
        xi = None
        depth = None
        sch_distance = None
        bita_distance = None

    return MiddleWorldCertificate(
        conflict_load=L,
        decoupling=s,
        architecture_cost=K,
        recoverable_loss=R,
        architecture_margin=phi,
        sch_conflict_active=sch_active,
        bita_differentiation_favoured=bita_favoured,
        state=state,
        sch_boundary_distance=sch_distance,
        bita_boundary_distance=bita_distance,
        middle_position=xi,
        two_sided_depth=depth,
    )

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
import math


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
    sch_limited_width: float | None
    bita_limited_width: float | None
    bita_to_sch_width_ratio: float | None


def balance_domain_geometry(decoupling: float, architecture_cost: float) -> BalanceDomainGeometry:
    """Return the one-dimensional BALANCE geometry when ``s`` and ``K`` are fixed.

    For ``s>0`` the static middle world is

        0 < L < K/s.

    In the common fitness-margin coordinates used by :func:`classify_middle_world`,
    the point equally far from the SCH boundary and the BITA boundary satisfies

        L = K-sL,

    hence

        L_equal = K/(1+s).

    At this point ``xi=1/2`` and the two-sided depth ``min(L, K-sL)`` is maximal.
    It is *not* generally halfway along the conflict-load interval ``(0, K/s)``.

    The interval can be split into a SCH-boundary-limited segment and a
    BITA-boundary-limited segment. Their widths are

        W_S = K/(1+s)
        W_B = K/[s(1+s)]

    and therefore ``W_B/W_S = 1/s``.  Architecture cost ``K`` scales the whole
    interval, whereas decoupling ``s`` controls its normalized skew/shape.

    When ``s=0`` no finite BITA-facing boundary exists: added dimensionality
    recovers none of the conflict load. The equal-margin point is therefore not
    treated as a unique finite domain centre.
    """
    s = float(decoupling)
    K = float(architecture_cost)
    if not math.isfinite(s) or not math.isfinite(K):
        raise ValueError("inputs must be finite")
    if not 0 <= s <= 1:
        raise ValueError("decoupling must lie in [0,1]")
    if K < 0:
        raise ValueError("architecture_cost must be non-negative")

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
            sch_limited_width=None,
            bita_limited_width=None,
            bita_to_sch_width_ratio=None,
        )

    Lcrit = K / s
    Lequal = K / (1.0 + s)
    sch_width = Lequal
    bita_width = Lcrit - Lequal
    fraction = None if Lcrit == 0 else Lequal / Lcrit
    q_equal = None if K == 0 else s * Lequal / K
    skew = None if sch_width == 0 else bita_width / sch_width
    return BalanceDomainGeometry(
        decoupling=s,
        architecture_cost=K,
        finite_bita_boundary=True,
        critical_conflict_load=Lcrit,
        equal_margin_conflict_load=Lequal,
        max_two_sided_depth=Lequal,
        equal_margin_fraction_of_conflict_width=fraction,
        criticality_index_at_equal_margin=q_equal,
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
    """Classify one context in the three-world programme.

    Parameters
    ----------
    conflict_load
        Fitness-scale loss created by forcing the functions onto one shared
        coordinate. ``L = 0`` is the SCH-facing no-conflict boundary.
    decoupling
        Fraction ``s`` of the conflict load recoverable by adding dimensionality.
    architecture_cost
        Additional architecture cost ``K`` on the same fitness scale.

    Returns
    -------
    MiddleWorldCertificate
        In the BALANCE state, ``middle_position`` is

            xi = L / (L + rho),  rho = K - sL,

        so xi -> 0 approaches the SCH-facing boundary and xi -> 1 approaches
        the BITA-facing differentiation boundary. ``two_sided_depth`` is
        ``min(L, rho)`` and measures how deeply the context lies inside the
        middle world in the common fitness units.
    """
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
    sch_active = L > tol
    bita_favoured = phi > tol

    if not sch_active:
        state = "SCH_NO_CONFLICT_WORLD"
    elif abs(phi) <= tol:
        state = "BALANCE_BITA_INTERFACE"
    elif phi < 0:
        state = "BALANCE_MIDDLE_WORLD"
    else:
        state = "BITA_DIFFERENTIATION_WORLD"

    if state == "BALANCE_MIDDLE_WORLD":
        rho = K - R
        denom = L + rho
        xi = L / denom if denom > 0 else None
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

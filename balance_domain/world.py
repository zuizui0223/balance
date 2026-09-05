"""Two-sided world certificate for Chapter 2 BALANCE.

SCH and BITA contribute complementary inequalities:

- SCH-facing condition: a real shared-axis conflict exists, ``L > 0``.
- BITA-facing condition: differentiated architecture is not yet favoured,
  ``Phi = sL - K < 0``.

BALANCE is their intersection.  When all terms use a common fitness scale,
this module also locates a point inside the middle world relative to its two
bounding surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass


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
        coordinate.  ``L = 0`` is the SCH-facing no-conflict boundary.
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

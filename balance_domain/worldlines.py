"""Direct comparison of the shared and differentiated optimized worldlines."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorldlineComparison:
    shared_optimum_fitness: float
    differentiated_optimum_fitness: float
    conflict_load: float
    direct_worldline_gap: float
    decomposed_gap: float | None
    parallel_world_residual: float | None
    bridge_consistent: bool | None
    state: str


def compare_worldlines(
    shared_optimum_fitness: float,
    differentiated_optimum_fitness: float,
    conflict_load: float,
    *,
    decoupling: float | None = None,
    architecture_cost: float | None = None,
    tolerance: float = 1e-9,
) -> WorldlineComparison:
    """Compare the two optimized architecture worldlines on one fitness scale.

    ``direct_worldline_gap = W_D* - W_S*``.

    When ``decoupling`` and ``architecture_cost`` are also supplied, the
    function checks the programme-level bridge identity

        W_D* - W_S* = sL - K.

    and reports

        delta_parallel = (W_D* - W_S*) - (sL - K).

    A non-zero residual is a *candidate* parallel-world shift, not proof of
    one. Scale mismatch, context mismatch, cost-definition mismatch and
    omitted ecological channels must be excluded first.
    """
    Ws = float(shared_optimum_fitness)
    Wd = float(differentiated_optimum_fitness)
    L = float(conflict_load)
    tol = float(tolerance)
    if L < 0:
        raise ValueError("conflict_load must be non-negative")
    if tol <= 0:
        raise ValueError("tolerance must be positive")

    direct = Wd - Ws
    decomposed = None
    residual = None
    consistent = None

    if (decoupling is None) != (architecture_cost is None):
        raise ValueError("decoupling and architecture_cost must be supplied together")
    if decoupling is not None and architecture_cost is not None:
        s = float(decoupling)
        K = float(architecture_cost)
        if not 0 <= s <= 1:
            raise ValueError("decoupling must lie in [0,1]")
        if K < 0:
            raise ValueError("architecture_cost must be non-negative")
        decomposed = s * L - K
        residual = direct - decomposed
        consistent = abs(residual) <= tol

    if L <= tol:
        if direct > tol:
            state = "OUTSIDE_REGISTERED_SCH_CONFLICT"
        else:
            state = "SCH_NO_CONFLICT_WORLD"
    elif direct < -tol:
        state = "BALANCE_MIDDLE_WORLD"
    elif abs(direct) <= tol:
        state = "ARCHITECTURE_CRITICAL_INTERFACE"
    else:
        state = "BITA_DIFFERENTIATION_WORLD"

    return WorldlineComparison(
        shared_optimum_fitness=Ws,
        differentiated_optimum_fitness=Wd,
        conflict_load=L,
        direct_worldline_gap=direct,
        decomposed_gap=decomposed,
        parallel_world_residual=residual,
        bridge_consistent=consistent,
        state=state,
    )

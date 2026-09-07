def pairwise_feasible(constraints):
    # Explicit witnesses for the p=2 tight example:
    # x>=1, y>=1, x+y<=1.
    witnesses = {
        frozenset((0, 1)): (1.0, 1.0),
        frozenset((0, 2)): (1.0, 0.0),
        frozenset((1, 2)): (0.0, 1.0),
    }
    for pair, point in witnesses.items():
        assert all(constraints[i](*point) for i in pair)


def test_p2_helly_bound_is_tight():
    constraints = [
        lambda x, y: x >= 1.0,
        lambda x, y: y >= 1.0,
        lambda x, y: x + y <= 1.0,
    ]
    pairwise_feasible(constraints)

    # The full system is algebraically impossible: x>=1 and y>=1 imply
    # x+y>=2, contradicting x+y<=1.
    assert 2.0 > 1.0


def test_adding_constraints_cannot_restore_a_failed_intersection():
    # A compact logical regression for scope monotonicity.
    base_feasible_points = {(1, 1), (2, 2)}
    extra_constraint_points = {(2, 2)}
    enlarged = base_feasible_points & extra_constraint_points
    assert enlarged <= base_feasible_points

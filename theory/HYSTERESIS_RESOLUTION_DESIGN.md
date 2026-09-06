# Optimal forcing resolution for a declared hysteresis-width precision

The inverse BALANCE result bounds finite-step hysteresis inflation by

```text
delta_up + delta_down.
```

This turns a desired width precision into an experimental-design problem.

Suppose the increasing and decreasing forcing sweeps cover spans

```text
S_up > 0,
S_down > 0,
```

using `n_up` and `n_down` equal-width intervals. Then

```text
delta_up   = S_up/n_up,
delta_down = S_down/n_down.
```

To guarantee discretization inflation no larger than a declared `eta`, require

```text
S_up/n_up + S_down/n_down <= eta.
```

## Continuous relaxation

Ignoring integer interval counts temporarily, minimize

```text
N = S_up/delta_up + S_down/delta_down
```

subject to

```text
delta_up + delta_down = eta.
```

The first-order condition gives

```text
delta_up/delta_down
= sqrt(S_up/S_down).
```

Therefore

```text
delta_up*
= eta sqrt(S_up)/(sqrt(S_up)+sqrt(S_down)),

delta_down*
= eta sqrt(S_down)/(sqrt(S_up)+sqrt(S_down)).
```

The relaxed minimum interval count is

```text
N_min,cont
= (sqrt(S_up)+sqrt(S_down))^2/eta.
```

This is a lower bound for every integer design.

## Exact integer design

The implementation searches the finite integer feasible set and returns the
minimum `n_up+n_down` satisfying the declared error budget.  It uses the equal
error allocation as a constructive feasible upper bound, then computes the
smallest reverse count for each candidate forward count.

For equal spans

```text
S_up=S_down=1,
eta=0.1,
```

the continuous optimum is exactly integer:

```text
n_up=20,
n_down=20,
N_total=40,
delta_up=delta_down=0.05.
```

For unequal spans, equal step-error allocation is generally inefficient. The
larger sweep should receive a larger absolute step budget in proportion to the
square root of its span.

Implementation:

```text
balance_domain/hysteresis_resolution_design.py
tests/test_hysteresis_resolution_design.py
```

## Relation to biological inference

This design controls only the deterministic **forcing-grid discretization**
contribution to the observed hysteresis width. Measurement error in `Phi`,
biological process noise, time-varying switching costs and uncertain horizons
remain separate uncertainty sources and should not be hidden inside `eta` unless
a larger model explicitly combines them.

Thus the experimental contract should carry at least

```text
forcing spans,
forward/reverse interval counts,
maximum forcing increments,
declared width-discretization tolerance.
```

## Claim boundary

The square-root allocation is optimal for this two-sweep interval-count problem
under the registered deterministic BALANCE threshold model. It is not a general
optimal-design theorem for arbitrary noisy hysteresis experiments.

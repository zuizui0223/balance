# Empirical identification contract: switching records

Status: optional inverse route for the existing deterministic switching-cost
model. All bundled examples are synthetic. This is separate from BALANCE's
primary static middle-world certificate L>0 and Delta_W<0.

## Minimum records and assumptions

Record the ordered Phi values AND retained architecture states in an increasing
and a decreasing path. Each path must contain an actual preswitch stay record.
Declare one calibrated Phi scale, a matched fixed external context, fixed costs
and the same payoff horizon T, and the instantaneous deterministic update rule.

Under that model:

    F=C_SD/T >= 0; R=-C_DS/T <= 0.

At equality the old state stays. For first switches bracketed by actual records:

    last_up_stay <= F < first_up_switch
    first_down_switch < R <= last_down_stay.

These brackets use local observed increments rather than a global maximum step,
and preserve open/closed endpoints. They can be tighter than the earlier
maximum-step envelope. They are not confidence intervals: Phi/state measurement
error, detection delays and variable costs/horizons require additional models.

## What is identified

The two thresholds identify two cost/horizon ratios, not absolute costs. For any
c>0, (C_SD,C_DS,T) and (c*C_SD,c*C_DS,c*T) have identical thresholds. Sampling
more finely cannot remove that symmetry. Sampling duration must not be silently
substituted for the payoff horizon.

With independently supplied T in [T_lo,T_hi], propagate that interval to each
cost and their sum. `cost_scale_identified=True` means T is supplied exactly on
the declared Phi scale, NOT that a finitely bracketed cost is a point estimate.
When T is unknown, absolute-cost fields are None rather than guessed.

## Censoring and inconsistent data

No observed switch is a censored path. A right/left unbounded endpoint is stored
as None; it does not mean zero cost or a switch at the final sample. The remaining
one-sided constraint is retained. Non-monotone paths, recrossing under monotone
forcing, and empty intersections with nonnegative costs are rejected.

## Synthetic witness

Upward: shared at 0.10, first differentiated at 0.12.
Downward: differentiated at -0.05, first shared at -0.08.

    F in [0.10,0.12)
    R in (-0.08,-0.05]
    W=F-R in [0.15,0.20).

When independent T=10:

    C_SD in [1.0,1.2)
    C_DS in [0.5,0.8)
    C_SD+C_DS in [1.5,2.0).

When T in [8,12], total cost is in [1.2,2.4), not the interval obtained by
plugging in T's midpoint. These are projections of the conditional compatible
parameter set; they do not imply all marginal cost/horizon combinations are
jointly independent.

## Reproduce

From repository root:

    python -m balance_domain.empirical_identification
    python -m pytest -q tests/test_empirical_identification.py

Implementation: `balance_domain/empirical_identification.py`.
Related results: `balance_domain/hysteresis_interval.py` and
`theory/INVERSE_HYSTERESIS_IDENTIFICATION.md`.

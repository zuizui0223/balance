# A whole-budget plan for reset-enabled hysteresis identification

Status: optional extension of `BOUNDED_SWITCHING_DESIGN.md`. Synthetic examples
only. The primary static BALANCE certificate and switching dynamics are unchanged.

## State and objective

Use the earlier bounded-Phi identification receipt. Let w_F,w_R be the spans of
the nonnegative threshold brackets for `c_F=C_SD/T`, `c_R=C_DS/T`; the target is
`W=c_F+c_R`. Uncertainty in W is the SUM of the threshold spans, not the area of
a hysteresis curve. This sum is sharp for the declared Cartesian threshold set
and conservative if additional correlations constrain the two thresholds.

A matched reset to the old architecture is required before every query, preserving
context, costs, payoff horizon and instantaneous switching rule. State labels are
exact. Errors e_F,e_R bound actual minus nominal forcing and are fixed within each
direction. Integer costs are additive acquisition-resource costs, NOT architecture
switching costs C_SD,C_DS. Include reset effort in these resource costs when it
matters; outcome-dependent or state-dependent costs require a different model.

## Multi-query minimax recurrence

For a threshold bracket of span w and forcing-command error e, the earlier
one-query midpoint result is

    a(w)=min(w,w/2+e).

Induction gives the exact n-query worst remaining span

    w(n) = w                         if w <= 2e
         = 2e + (w-2e)/2^n          if w > 2e.

For a single query, one of the stay/switch branches has span at least a(w),
regardless of the nominal query. The midpoint attains that bound. The posterior
set is again an interval, so the same argument applies recursively. An adversary
can choose a consistent nested branch at each step; for a finite sequence the
retained nonempty intervals admit a fixed true threshold. Thus the recurrence
is a minimax statement in this declared query model, not just a simulation fit.

For positive integer costs k_F,k_R and budget B, solve

    minimize w_F(n_F)+w_R(n_R)
    subject to k_F*n_F+k_R*n_R <= B, n_F,n_R nonnegative integers.

The implementation enumerates forward counts and assigns all affordable remaining
reverse queries when they have positive gain. It compares exact rational remaining
spans, breaking ties by least spending, least total query count, then forward count.
It returns the entire smaller-budget frontier. The same per-query adversarial
lower bound also prevents an adaptive choice of directions from beating this
allocation in the Cartesian fixed-error model; midpoint queries achieve it.
Future nominal locations must nevertheless be recomputed from the ACTUAL updated
brackets. No future state outcome is supplied to the budget planner.

For equal costs, positive marginal gains form two halving sequences, so merging
by largest remaining gain is optimal. For unequal indivisible costs, greedily
ranking gain/cost can fail. For example, w_F=0.03,w_R=0.04,e_F=e_R=0,
k_F=2,k_R=3,B=3: forward has greater immediate gain per cost, but reverse alone
reduces total span to 0.05 rather than 0.055. The exact search chooses reverse.

## Registered synthetic budget frontier

Start from the previous example's threshold spans 0.03 and 0.04, equal unit costs,
and e_F=e_R=0.005.

| Budget | Forward queries | Reverse queries | Worst remaining W span |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0.0700 |
| 1 | 0 | 1 | 0.0550 |
| 2 | 1 | 1 | 0.0450 |
| 3 | 1 | 2 | 0.0375 |
| 4 | 2 | 2 | 0.0325 |

A target span <=0.033 therefore requires at least four unit-cost queries in this
model. The comparison counts acquisition units, not the number of field samples
needed to validate forcing calibration or the deterministic state rule.

## Precision floor versus exhausted search budget

The limiting span is

    min(w_F,2e_F)+min(w_R,2e_R).

If the target is below this limit, or equal while a positive excess remains, no
finite number of these queries guarantees it. If the target is above the limit
but not attained within B, the output instead says `not_reached_within_budget_cap`.
It never turns an exhausted numerical search budget into a structural impossibility.
Already narrow initial brackets are not widened to 2e. Zero command error permits
arbitrarily small spans, but not finite exact identification of a positive initial
continuous bracket using only binary queries.

This floor is specific to bounded-adversarial errors. Better calibration, a
validated stochastic noise model, known dependence, or another experiment can
change it. Increasing B alone does not change an unknown payoff-horizon scale.

## Apply actual outcomes and replan

`condition_reset_outcome` intersects the selected query's stay/switch inequality
with its current threshold bracket, retains open/closed endpoint semantics, and
rejects contradictory results. Only after this step should the remaining-budget
plan be recomputed. Absolute costs are reprojected only if independent horizon
bounds are supplied again; without them, the updated cost field is None rather
than being derived from an invented T or copied as though newly updated.

All endpoint arithmetic is rational; displayed uncertainty upper bounds round
outward and guaranteed improvements round downward. Decimal strings or Fraction
inputs preserve decimal values exactly; instrument rounding belongs in query error.

## Reproduce

    python -m balance_domain.budgeted_switching_design
    python -m pytest -q tests/test_budgeted_switching_design.py

Optional API: `plan_budgeted_reset_refinement`, `worst_span_after_queries`,
`condition_reset_outcome`.

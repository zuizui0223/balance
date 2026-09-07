# BALANCE adaptivity budget profile: executable zero-gap control

Status: optional diagnostic API for the existing bounded-adversarial reset model. It does not change the primary BALANCE middle-world certificate or switching dynamics.

## Comparison

Both methods use outcome-updated midpoint query **locations**. The only question is whether the next **direction** (forward versus reverse threshold) may depend on previous stay/switch outcomes.

For each declared budget `B`, compare

```text
V_fixed(B)    = exact optimum allocation of forward/reverse query counts
V_adaptive(B) = Bellman optimum when the next direction may depend on prior outcomes.
```

Smaller worst-case total threshold-span is better.

Implementation: `balance_domain/adaptivity_budget_profile.py`.

## Why the gap is exactly zero in this model

For one threshold with current span `w` and command-error bound `e`, a minimax midpoint query leaves

```text
a(w,e)=min(w,w/2+e)
```

under either possible state outcome. The two posterior intervals differ in location but not span.

The declared future-value state is therefore

```text
(w_F, w_R, remaining_budget, e_F, e_R, directional_costs).
```

Because the observed branch label does not change that sufficient state beyond the same deterministic span update, allowing future direction choice to condition on that label cannot improve the minimax span objective.

The executable profile raises if the Bellman result and the existing exact count-allocation result differ.

## Registered profile

For initial spans `(0.03,0.04)`, errors `(0.005,0.005)` and unit costs:

| Budget | Fixed optimum | Direction-adaptive optimum | Gap |
|---:|---:|---:|---:|
| 0 | 0.0700 | 0.0700 | 0 |
| 1 | 0.0550 | 0.0550 | 0 |
| 2 | 0.0450 | 0.0450 | 0 |
| 3 | 0.0375 | 0.0375 | 0 |
| 4 | 0.0325 | 0.0325 | 0 |

The test suite also checks independently seeded unequal-cost/error contracts.

## Relation to PAYOFF and MROD

PAYOFF and MROD have registered witnesses in which different first outcomes require scientifically different continuation measurements. Their adaptive gaps are positive at intermediate budgets.

BALANCE is the negative control:

```text
branch label changes interval location
but not the sufficient future-value state
-> no extra direction-routing advantage.
```

This is not a theorem that adaptivity never helps hysteresis experiments. Correlated thresholds, state-dependent costs, imperfect resets, state-label errors, changing calibration, or a location-sensitive/expected-loss objective can make outcome history relevant and require a new model.

## Reproduce

```bash
python -m pytest -q tests/test_adaptivity_budget_profile.py
```

# Negative control: no extra minimax gain from adaptive direction allocation

Status: regression/interpretation control for the existing bounded-adversarial
reset model. No new biological dynamics or field-data result is introduced.
The reference result remains `BUDGETED_SWITCHING_DESIGN.md`.

## Exactly what is being compared

The existing optimal method ALREADY updates its midpoint measurement location
using the actually retained threshold bracket. This is adaptive positioning and
must not be compared with a fictitious plan that fixes all numerical midpoints
in advance. The new control asks a narrower question: can choosing forward versus
reverse measurement according to previous responses outperform the optimum fixed
allocation of directional query counts in worst-case total width uncertainty?

Under the declared assumptions, it cannot. The threshold set is Cartesian, the
state labels are exact, query errors are fixed within each direction, matching
resets are possible and resource costs are additive. At a midpoint query, either
response leaves a threshold span

    a(w,e) = min(w,w/2+e).

The two responses have different interval locations but the same span. The future
span objective and acquisition costs depend on these spans, not the locations.
A direction-adaptive Bellman recursion therefore reduces to

    V(wF,wR,B) = min(
        wF+wR,
        V(a(wF,eF),wR,B-kF) if affordable,
        V(wF,a(wR,eR),B-kR) if affordable).

Its value equals the existing integer-allocation optimum using

    w(n)=w if w<=2e else 2e+(w-2e)/2^n.

The single-query minimax lower bound excludes improvement by non-midpoint commands;
midpoints attain it. The positive acquisition costs make the recursion finite.
This is a consequence of the existing model, not a universal theorem that
adaptivity never helps hysteresis experiments.

## Registered control

With initial spans (0.03,0.04), directional query errors (0.005,0.005) and unit
resource costs, both methods give the same worst remaining total span:

| Budget | Optimum span |
|---:|---:|
| 0 | 0.0700 |
| 1 | 0.0550 |
| 2 | 0.0450 |
| 3 | 0.0375 |
| 4 | 0.0325 |

The new regression test compares a recursive span-state optimizer with the existing
closed-form/count-allocation implementation over 200 independently seeded contracts,
including unequal integer costs, zero errors, precision floors and zero budgets.
Those finite tests check the implementation; they are not a substitute for the
conditional minimax argument.

## Relation to the sibling repositories

The PAYOFF adaptive-phase witness saves one of three measurements because the
first outcome determines which distance separates the remaining worlds. The MROD
joint-likelihood witness uses a context measurement to choose the relevant assay.
Their remaining tasks depend on which branch occurred. That particular advantage
is absent from the location-invariant Cartesian span objective used here.

Correlated thresholds, state-dependent costs, changing calibration, imperfect
resets, state-label errors or an expected-loss objective may alter this conclusion.
They must be independently declared rather than silently added to make adaptivity
look useful. The parent scientific models and primary BALANCE certificate are not
changed by this control.

Reproduce:

    python -m pytest -q tests/test_adaptive_allocation_control.py

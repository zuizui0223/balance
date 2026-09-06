# Pedicularis Experiment-B receipt — Chapter 2 / BALANCE

## Question

Given that SCH has already identified a real same-context conflict budget `L>0`, does enabling the water-defence state leave the shared/disabled worldline fitter, cross the architecture ordering, or remain unresolved?

BALANCE consumes exactly two matched receipts:

```text
THREE_WORLD_CONFLICT_HANDOFF_V1
PEDICULARIS_XY_SURFACE_HANDOFF_V1
```

The following fields must match exactly:

```text
context_id
population_id
season_id
fitness_scale_id
```

## Direct state classification

Let

```text
Delta_W = W_D* - W_S*
```

where for the functional-state Pedicularis comparison:

```text
W_S* = optimized fitness with water defence disabled / drained
W_D* = optimized fitness with water defence active / protected.
```

Then bounded inference is:

```text
L.lower95 > 0 and Delta_W.upper95 < 0
  -> FUNCTIONAL_STATE_BALANCE_IDENTIFIED

L.lower95 > 0 and Delta_W.lower95 > 0
  -> FUNCTIONAL_STATE_BITA_SIDE_IDENTIFIED

L.lower95 > 0 and Delta_W interval crosses 0
  -> FUNCTIONAL_STATE_ORDER_UNRESOLVED.
```

A point estimate is never used to override an interval crossing zero.

## Direct middle-world coordinates

Only after bounded BALANCE identification define the point summaries

```text
rho_direct = -Delta_W
xi_direct = L / (L + rho_direct)
d_B,direct = min(L, rho_direct).
```

These are direct worldline quantities; they do not require a prior `s,K` decomposition.

## Relationship to Chapter 3

The same x-by-water-y surface also contains `x0*`, `x1*`, `R_state`, and y-loading effects for BITA. BALANCE does not condition its direct worldline classification on the BITA surface status. This prevents selecting only already-positive differentiation cases.

## Claim ceiling

Because the drained and protected treatments retain the same cupulate bract architecture, this is a **functional-state middle-world** test. A structural-architecture BALANCE claim still requires a repeatable structural y coordinate and a separately justified maintenance/developmental cost lane.

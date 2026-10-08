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

## Intervention-selectivity caveat

The water-y state must be qualified independently of any perforation/handling required to create it. The 2015 historical drainage method pierced the bract base, so its treatment effect alone does not isolate water retention from physical injury/access. The qualification route and fail-closed fallback are in `docs/PEDICULARIS_WATER_PERFORATION_IDENTIFICATION_AUDIT_V1.md`. An unqualified package contrast remains `WATER_AND_PERFORATION_PACKAGE_EFFECT`, not a direct water-only fitness worldline.

## Geometry/partial-modularity limitation

The 2016 *P. rex* "exsertion" variable is a **ratio of two organ lengths**, `(flower_length-bract_height)/flower_length`, not the vertical position of a predator oviposition site relative to the changing water surface. The separate bract and corolla are already anatomical modules; toggling bract water is a **functional-state** intervention, not adding or removing a structural module. Before mechanistic interpretation of the x-by-water surface, prospectively measure both length exsertion and the directly verified site-to-waterline clearance with a common elevation datum; see `docs/PEDICULARIS_PARTIAL_MODULARITY_EXPOSURE_GEOMETRY_V1.md`. The additional geometry support is not required by the already-frozen numerical x-y handoff contract and must never be retrospectively inserted as an outcome-selected decision rule.

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
  -> FUNCTIONAL_STATE_ARCHITECTURE_FAVOURED_IDENTIFIED

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

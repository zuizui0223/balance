# BALANCE plant confirmatory model version history v1

## Purpose

This document records why the plant confirmatory model changed from V1 to V4.

Every transition below occurred **before any confirmatory architecture fit** and before U6
independent architecture coding. The response categories and raw coding ledger were not
changed to rescue an observed effect.

The version history is therefore a design/provenance record, not a sequence of
result-selected models.

## V1 — raw-category joint multinomial

Primary response:

```text
SHARED
NONSTRUCTURAL_SEPARATION
STRUCTURAL_MODULE_DIVISION
MOSAIC
```

Raw predictors:

```text
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

Planned joint multinomial parameter budget:

```text
42 fixed coefficients
before conflict-family adjustment
```

Status:

```text
SUPERSEDED_PRE_FIT_BY_V2_PARAMETER_BUDGET
```

Reason:

The anticipated conflict-positive evidence surface is measured in tens of biological
dependency groups, not hundreds. A 42+ coefficient primary fit would be dominated by sparse
categorical cells.

No architecture-effect estimate had been fit.

## V2 — low-dimensional three-axis model

V2 retained all raw coding but projected it to:

```text
module_opportunity2
temporal_exposure3
spatial_exposure2
```

Primary parameter budget:

```text
15 fixed coefficients
```

Status:

```text
SUPERSEDED_PRE_OUTCOME_BY_V3_SPATIAL_SUPPORT
```

Reason:

An architecture-blind source-support audit over the current conflict-positive U2+U6
surface produced:

```text
spatial_exposure2

SAME_UNIT    28
DISTRIBUTED   1
```

One dependence block could not defensibly carry the distributed-side primary coefficient.

Spatial coding was retained; only its primary-model role changed.

## V3 — module + timing primary model

Primary joint predictors:

```text
module_opportunity2
temporal_exposure3
```

Spatial exposure became a mandatory secondary support axis.

Primary parameter budget:

```text
12 fixed coefficients
```

Status:

```text
SUPERSEDED_PRE_OUTCOME_BY_V4_UNIVERSE_STRATIFICATION
```

Reason:

The next architecture-blind audit showed strong predictor-support differences across the
two conflict-focused universes:

```text
module opportunity
             U2   U6
SINGLE        5   21
MODULAR       3    0

temporal exposure
                         U2   U6
SIMULTANEOUS              3   18
ORDERED_OR_ALTERNATING    2    3
VARIABLE_CONTEXT          3    0
```

A pooled model with one intercept could let sampling-universe baseline differences leak into
common predictor slopes.

U1 also had a completed 47-group broad-interaction source screen with zero strict
conflict-positive rows, making its correct role external specificity validation rather than
a routing denominator.

## V4 — current universe-stratified routing model

Primary routing universes:

```text
U2 sexual interference
U6 pollen theft
```

U1 role:

```text
external broad-interaction specificity validation
```

Primary model:

```text
multinomial logit

universe-specific intercepts:
  U2
  U6

common slopes:
  module_opportunity2
  temporal_exposure3
```

Parameter budget:

```text
6 universe-intercept coefficients
9 common-slope coefficients
15 total
```

The full pre-outcome V4 predictor matrix is currently:

```text
common-slope rank              3 / 3
universe-stratified full rank  5 / 5
```

Thus the **main V4 predictor design is prospectively viable**.

## Generality is a stricter claim than model estimability

The current evidence surface does not yet license a cross-universe timing-generalization
claim.

Marginally:

```text
SIMULTANEOUS
ORDERED_OR_ALTERNATING
```

occur in both U2 and U6.

But the only module stratum shared across both universes is `SINGLE`, where the
architecture-blind source screen currently has:

```text
                         U2   U6
SIMULTANEOUS              1   18
ORDERED_OR_ALTERNATING    2    3
```

The frozen common-support gate requires at least two of each timing state in the same shared
module stratum within each universe.

After architecture coding, an additional outcome-support gate requires within each U2 and
U6:

```text
>= 2 NONSTRUCTURAL_SEPARATION blocks
>= 2 OTHER_ARCHITECTURE blocks
```

Therefore:

```text
V4 main model prospectively identifiable
!=
cross-universe generality already established
```

## Frozen invariants across V1-V4

The following were never changed to rescue a model result:

1. four-class primary architecture response;
2. raw architecture categories;
3. raw module/timing/spatial predictor codebook;
4. independent double-coding requirement;
5. outcome-independent predictor-receipt requirement;
6. no post-hoc class collapse;
7. no significance-triggered predictor deletion;
8. one biological dependence block is not counted as independent replication.

## Current fit prohibition

No V4 confirmatory fit is licensed yet.

Still open:

- U2 independent double coding;
- U2 reliability gate and post-coding adjudication;
- U6 independent double coding;
- U6 reliability gate and post-coding adjudication;
- independent adjudication of U2/U6 predictor receipts;
- final U2/U6 licensed model assembly;
- post-adjudication V4 estimability gate.

U1 independent coding/adjudication remains required for the external specificity claim but
does not block the V4 routing fit.

## Publication-status consequence

BALANCE remains:

```text
STATUS = DOI_MODULE / DORMANT_PAPER_BRANCH
ACTIVE_PUBLICATION_QUEUE = false
```

A successful V4 main coefficient alone does not reactivate the paper.

The prospectively frozen reactivation gate additionally requires common predictor support,
per-universe target-outcome support, universe-specific timing effects, directional
concordance, and no practically large contradictory universe-by-timing interaction.

See:

- `data/BALANCE_PLANT_V4_REACTIVATION_GATE_V1.json`
- `docs/PUBLICATION_STATUS.md`

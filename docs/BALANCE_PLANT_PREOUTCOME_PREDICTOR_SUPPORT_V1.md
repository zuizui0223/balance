# BALANCE plant pre-outcome predictor-support audit v1

## Status

Frozen before U6 independent architecture coding and before any confirmatory model fit.

This audit uses only:

- U2 groups that pass the frozen strict conflict gate;
- U6 groups admitted by the architecture-blind pollen-theft reconstruction;
- source-screened predictor receipts coded independently of focal architecture.

No architecture outcome is used.

Executable surface:

- `balance_domain/plant_preoutcome_support.py`
- `tests/test_plant_preoutcome_support.py`
- `data/BALANCE_PLANT_PREOUTCOME_PREDICTOR_SUPPORT_V1.json`

## Evidence surface

```text
U2 strict conflict-positive groups    8
U6 frozen conflict-first groups      21
total                                29
```

All 29 have source-screened values for:

```text
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

These are SCREENED values, not independently adjudicated values.

## Frozen support after primary contrast mapping

### Module opportunity

```text
SINGLE    26
MODULAR    3
```

Both levels exceed the preregistered minimum of two independent dependence blocks.

### Temporal exposure

```text
SIMULTANEOUS              21
ORDERED_OR_ALTERNATING     5
VARIABLE_CONTEXT           3
```

All three levels exceed the minimum support threshold.

### Spatial exposure

```text
SAME_UNIT                 28
DISTRIBUTED                1
```

The distributed side is carried by one source-screened dependence group only.

## Design decision

The frozen decision is:

```text
module_opportunity2
  -> primary

temporal_exposure3
  -> primary

spatial_exposure2
  -> secondary
```

This is the reason V3 supersedes V2.

Spatial exposure remains mandatory in the raw codebook and predictor-receipt system. It is
not erased or recoded. It is removed only from the **joint primary fixed-effect model**
because a one-block contrast would not support a defensible general coefficient.

## Consequence for the primary model

V3:

```text
architecture_class4
~ module_opportunity2
+ temporal_exposure3
```

Fixed-effect parameter budget:

```text
12 coefficients
```

The spatial axis receives:

1. support tables;
2. architecture cross-tabs;
3. universe-stratified summaries;
4. a separate spatial sensitivity only if final independent adjudication leaves at least
   two `DISTRIBUTED` dependence blocks.

## Why this is not outcome-driven simplification

At freeze:

- U6 architecture coding is still unstarted;
- U2/U6 predictor values are not independently adjudicated;
- no confirmatory model has been fit;
- no architecture coefficient, probability contrast, p-value, posterior interval, or
  direction of effect has been inspected.

The revision therefore responds to **design support**, not model performance.

## Ecological implication already visible

The currently registered direct-conflict literature is much richer in **same-unit conflict**
than in independently evidenced spatially distributed conflict.

That is a property of the current evidence surface, not yet a biological statement that
spatially distributed conflict is rare in nature.

The distinction matters:

```text
literature support scarcity
!=
ecological rarity
```

## Claim ceiling

This audit licenses model design only. It does not support any claim about architecture
routing effects.

# BALANCE plant U6 predictor-identifiability audit v1

## Status

Source-screen audit only. No U6 predictor is independently adjudicated yet.

Canonical receipt surface:

`data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv`.

## Frozen source-screen result

The 21 conflict-first U6 dependency groups contain:

```text
21 groups
63 predictor receipt slots

module_substrate resolved outcome-independently         21 / 21
conflict_timing_geometry resolved outcome-independently 21 / 21
conflict_spatial_geometry resolved outcome-independently 21 / 21

groups with all three SCREENED predictors               21 / 21
groups with all three ADJUDICATED predictors              0 / 21
```

Architecture labels were not used to assign these predictors.

## Conflict-bearing coordinate

For U6, pollen theft/consumption is coded at the **source-side pollen pool** where pollen has
two immediate fates:

```text
removed / consumed by a low-value visitor
versus
retained / exported for gamete transfer
```

This avoids defining a predictor from a later architectural state such as dioecy, dichogamy,
or heteranthery.

### Module substrate

All 21 source-screened U6 groups are currently:

```text
SINGLE_OR_CONTINUOUS
```

This means the direct conflict receipt itself exposes one common pollen pool rather than an
independently addressable pre-conflict module system.

It does **not** mean the mature flower lacks multiple organs or flowers.

### Timing exposure

```text
SIMULTANEOUS             18
SEQUENTIAL_WITHIN_UNIT    3
```

Sequential source-resolved groups are:

- `Clusia arrudae` — honeybee removal precedes the effective native-bee transfer measured
  from previously visited male flowers;
- `Crescentia alata` — social-bee pollen theft occurs before bat pollinator arrival;
- `Tolmiea menziesii` — effective fungus-gnat visits precede later male-phase pollen
  robbers.

No timing value is inferred merely from dichogamy.

### Spatial exposure

All 21 are currently:

```text
SAME_UNIT
```

The spatial coordinate is the source pollen pool at which removal and retention/export
compete. Destination stigmas, sexual individuals, or later separated architecture are not
used to define this predictor.

## Design implication

U6 is excellent for identifying a common pollen-fate conflict but weak for estimating
module or spatial contrasts by itself.

That is why U6 is combined only through the frozen U1/U2/U6 assembly contract and why model
V3 relies on pre-outcome support across universes rather than asking U6 to estimate every
axis internally.

Current U2 + U6 source-screen support:

```text
module opportunity:
  SINGLE   26
  MODULAR   3

temporal exposure:
  SIMULTANEOUS              21
  ORDERED_OR_ALTERNATING     5
  VARIABLE_CONTEXT           3

spatial exposure:
  SAME_UNIT                 28
  DISTRIBUTED                1
```

Thus module and timing remain primary V3 axes, while spatial exposure is secondary.

## Remaining gate

Every U6 receipt remains:

```text
adjudication_status = SCREENED
```

Independent predictor adjudication must still verify:

1. the raw predictor value;
2. that the cited source really supports it;
3. that the evidence is logically independent of the focal architecture outcome.

No SCREENED receipt licenses primary-model entry.

## Claim ceiling

This audit establishes source identifiability and the predictor-support geometry of U6. It
does not establish architecture associations or causal evolutionary effects.

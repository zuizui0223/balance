# BALANCE plant pre-outcome cross-universe generality audit v1

## Status

Frozen before U6 independent architecture coding and before any confirmatory architecture
model fit.

This audit uses predictor support only. No architecture outcome is used.

Executable surface:

- `balance_domain/plant_preoutcome_generality.py`
- `tests/test_plant_preoutcome_generality.py`

## Independent source universes

The current strict-conflict / conflict-first predictor surface contains:

```text
U2 sexual interference    8 groups
U6 pollen theft           21 groups
```

U1 currently contributes zero source-screen conflict-positive groups and therefore cannot
supply a predictor contrast before independent adjudication.

## Predictor support by universe

### Module opportunity

```text
             U2   U6
SINGLE        5   21
MODULAR       3    0
```

Both levels exist overall, but `MODULAR` is U2-only.

Therefore:

```text
SINGLE vs MODULAR
!= cross-universe replicated contrast
```

A module-opportunity association can still be estimated from U2 variation if final
architecture/class support permits, but it cannot currently be described as replicated
across conflict families/universes.

### Temporal exposure

```text
                         U2   U6
SIMULTANEOUS              3   18
ORDERED_OR_ALTERNATING    2    3
VARIABLE_CONTEXT          3    0
```

The contrast

```text
SIMULTANEOUS
versus
ORDERED_OR_ALTERNATING
```

is supported in both independent universes.

`VARIABLE_CONTEXT` is U2-only.

Thus the only two-level predictor contrast with **marginal representation in both
universes** is:

```text
temporal exposure:
SIMULTANEOUS vs ORDERED_OR_ALTERNATING
```

However, marginal representation is not enough for a clean cross-universe routing test.
The only module-opportunity level shared by both universes is `SINGLE`, and within that
common stratum the source-screen support is:

```text
                         U2   U6
SIMULTANEOUS              1   18
ORDERED_OR_ALTERNATING    2    3
```

The U2 simultaneous side therefore fails the frozen >=2-block common-support threshold.

More importantly, this is not merely a gate that waits for architecture coding. The only
U2 groups with complete outcome-independent predictor receipts are exactly the eight
current source-screen conflict-positive groups. Final V4 admission can only retain a
subset of those groups because predictor adjudication may accept/reject frozen values but
cannot fill an `UNRESOLVED` receipt. Subsetting cannot increase the
`SINGLE + SIMULTANEOUS` count above one.

Therefore the temporal contrast is a **prospective marginally replicated candidate whose
strict common-support generality route is unreachable under the frozen V4 receipt
surface**.

### Spatial exposure

```text
             U2   U6
SAME_UNIT      7   21
DISTRIBUTED    1    0
```

The distributed contrast is neither well supported overall nor replicated across universes.

## Claim hierarchy

The eventual architecture analysis must distinguish three different claim levels.

### Level G1 — cross-universe replicated

**No contrast currently passes the strict common-support gate.**

The temporal `SIMULTANEOUS vs ORDERED_OR_ALTERNATING` contrast is marginally represented
in both universes, but U2 has only one `SINGLE + SIMULTANEOUS` block. Under the current
frozen V4 receipt surface, final independent coding/adjudication cannot increase that
count: final U2 model rows are a subset of the eight groups with already-complete
outcome-independent predictor receipts.

Accordingly, Level G1 is **structurally unavailable in V4 as currently frozen**. It can be
reopened only by a prospectively versioned outcome-independent predictor-receipt expansion
completed before independent architecture outcomes are opened. The >=2 threshold itself is
not weakened.

### Level G2 — within-universe supported

Currently includes:

```text
module:
SINGLE vs MODULAR
  supported within U2 only

temporal:
VARIABLE_CONTEXT contrasts
  supported within U2 only
```

These can support mechanism-family-specific associations but not a universal plant rule.

### Level G3 — support-limited

Currently:

```text
spatial:
SAME_UNIT vs DISTRIBUTED
```

The distributed side has one source-screened block and is secondary.

## Sampling-universe adjustment

Because predictor support differs strongly between U2 and U6, a pooled coefficient must not
silently absorb baseline architecture differences among review universes.

The model/reporting stage therefore needs an explicit sampling-universe control or
stratification when estimating pooled associations.

This audit does not choose a biological winner between universes. It identifies where
replication exists.

## Ecological implication

The evidence architecture itself is informative.

The direct-conflict literature currently offers:

- broad replication of same-unit pollen/reproductive conflict;
- replication of simultaneous and ordered timing geometries across independent mechanisms;
- much weaker cross-family representation of pre-existing modularity and distributed
  conflict geometry.

Therefore temporal conflict geometry remains the strongest **candidate** for a general
routing principle, but the current evidence surface does not yet support a strict
cross-universe generality test.

That remains a hypothesis. Under frozen V4, the common-support step cannot pass; any future
attempt to test strict cross-universe generality requires a separately versioned
pre-outcome predictor expansion before architecture outcomes are opened.

## V4 main-design rank versus generality support

The common-support failure does **not** make the V4 primary predictor design singular.

Using the frozen source-screen predictor values only:

```text
common-slope design columns
  module_MODULAR
  temporal_ORDERED_OR_ALTERNATING
  temporal_VARIABLE_CONTEXT

rank = 3 / 3

full V4 design columns
  intercept_U2
  intercept_U6
  module_MODULAR
  temporal_ORDERED_OR_ALTERNATING
  temporal_VARIABLE_CONTEXT

rank = 5 / 5
```

Therefore the prospective design distinction is:

```text
V4 main predictor design
  full-rank / viable

strict cross-universe temporal generality sensitivity
  unreachable under frozen V4 predictor-receipt surface
```

The first statement concerns identifiability of the registered U2/U6 model matrix. The
second concerns the stronger claim that the timing association is independently replicated
within a shared biological substrate across both universes.

## Prospective post-outcome support gate

Even if the shared-module predictor support later reaches the frozen threshold, the
cross-universe timing claim has one additional gate after independent architecture coding.

Within **each** U2 and U6 universe:

```text
NONSTRUCTURAL_SEPARATION
  >= 2 independent dependence blocks

OTHER_ARCHITECTURE
  >= 2 independent dependence blocks
```

This is a support diagnostic for the target probability contrast, not a collapse of the
four-class response.

The purpose is to prevent a universe-specific
`P(NONSTRUCTURAL_SEPARATION | ORDERED) - P(NONSTRUCTURAL_SEPARATION | SIMULTANEOUS)`
contrast from being called a replication when one universe contains essentially no observed
target routing outcome.

Thus the current generality ladder is:

```text
marginal timing representation
-> common module-stratum predictor support
-> per-universe target-outcome support
-> fitted universe-specific contrasts
-> directional concordance
-> practical interaction check
```

Only the first step is currently satisfied prospectively.

## Claim ceiling

This audit licenses only statements about predictor support and prospective generality. It
does not establish any architecture association.

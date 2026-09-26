# BALANCE U3 prospective Senna covesii routing prediction v1

## Why freeze a prediction now

The current U3 matched lane has moved beyond the question of whether pollen-use
conflict exists. Three nonheterantherous controls are conflict-positive, but
only two have source-resolved routing.

Those two resolved controls show a simple discovery pattern:

```text
Solanum lycocarpum
  module substrate: REPEATED_FLOWERS
  route:            AMONG_FLOWER_MODULE_DIVISION

Senna spectabilis
  module substrate: SERIAL_WITHIN_FLOWER
  route:            WITHIN_FLOWER_DIVISION_OF_LABOUR
```

This is far too little evidence to claim a general rule. It is, however, enough
to freeze a **directional prospective prediction** for the one existing
conflict-positive control whose routing outcome remains unseen.

## Target

```text
Senna covesii
  conflict:         POSITIVE
  module substrate: SERIAL_WITHIN_FLOWER
  routing:          UNRESOLVED at freeze
```

Frozen prediction:

```text
Senna covesii
-> WITHIN_FLOWER_DIVISION_OF_LABOUR
```

The target must be classified only through the already frozen
`U3MEAS_SENCOV_001` source-resolved positional routing assay and equivalence
contract.

## What would support or falsify it

Support:

```text
source-resolved target classification
= WITHIN_FLOWER_DIVISION_OF_LABOUR
```

Falsification:

```text
source-resolved target classification
= any other registered architecture state
```

An `UNRESOLVED` result caused by insufficient precision is inconclusive rather
than supportive.

## Why this is useful

This turns the emerging BALANCE interpretation into a test rather than another
retrospective story.

The candidate mechanism is:

> once pollen-use conflict persists, pre-existing modular organization may
> constrain the organizational level at which pollen fates can be routed.

If `S. covesii` resolves outside the predicted within-flower state, that
candidate rule fails on its first frozen target.

## Dependence caveat

This is **not** an independent evolutionary replication. `S. covesii` shares
the frozen `U3_DEP_SENNA_01` block with the discovery taxon
`S. spectabilis`.

The test is therefore a prospective species-level validation of the directional
routing hypothesis inside the current matched programme. A genuine
cross-lineage confirmation still requires a future reopened or new dependence
block.

## Canonical surfaces

```text
data/BALANCE_PLANT_U3_SENCOV_ROUTING_PREDICTION_V1.json
balance_domain/plant_u3_sencov_prediction.py
tests/test_plant_u3_sencov_prediction.py
```

## Claim ceiling

This is a single-target prospective prediction. It is not evidence for a
general module-routing law, an independent-block replication, a causal effect,
or a historical evolutionary transition.

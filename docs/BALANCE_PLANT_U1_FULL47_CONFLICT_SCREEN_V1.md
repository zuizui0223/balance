# BALANCE plant U1 full-47 strict conflict source screen v1

## Status

The complete frozen Haas-Lortie U1 review universe has now been source-screened for the
registered BALANCE conflict estimand.

This is a **source-screen result**, not independent coder adjudication and not a prevalence
estimate.

Canonical executable surface:

- `balance_domain/plant_u1_full_screen.py`
- `data/BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv`
- `data/BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv`
- `tests/test_plant_u1_full_screen.py`

## Frozen denominator

```text
U1_001 ... U1_047
47 taxa / 47 dependency groups
```

No difficult taxon was replaced.

The first 20 form the independent reliability frame. The remaining 27 use the production
primary-study identities reconstructed from the review's Figshare analysis data.

## Source-screen result

```text
POSITIVE                    0
ALIGNED_NO_CONFLICT         1
NO_DEMONSTRATED_CONFLICT   46
UNRESOLVED_CANDIDATE        0

PASS_CONFLICT_GATE          0
FAIL_CONFLICT_GATE         47
HOLD_FOR_FULL_TEXT          0
```

Architecture was not inferred in the conflict screen.

## Two former unresolved cases

### Brassica nigra

The primary study explicitly framed a possible trade-off between herbivore-induced
phytochemical responses and pollinator interactions, but its results did not support the
registered conflict: visitation frequency was generally unaffected and the authors
concluded that no herbivory-pollination trade-off was evident.

The row is therefore closed as:

```text
NO_DEMONSTRATED_CONFLICT
FAIL_CONFLICT_GATE
```

### Myrmecophila tibicinis

The primary flower-morphology manipulation tested whether florivory-induced changes in size
or symmetry could alter pollination success. Effects on male/female pollination success
were nonsignificant and the paper concluded that florivory had little reproductive effect
beyond direct consumption of sexual structures.

The row is therefore closed as:

```text
NO_DEMONSTRATED_CONFLICT
FAIL_CONFLICT_GATE
```

## Ecological interpretation

The U1 result is stronger than "the broad herbivory-pollination literature has low yield."

Within this frozen 47-taxon review universe, direct damage, induced floral changes,
florivore effects on visitation, pollen limitation, herbivore-pollinator interactions, and
alternative reproductive routes are all common enough to enter the review literature.

What is not recovered at source-screen level is the stricter BALANCE object:

> one shared reproductive coordinate for which two functions or agents demonstrably favor
> opposing states.

Thus:

```text
interaction != conflict
pollination cost after herbivory != opposing optimum
same damaged flower != shared-coordinate trade-off
alternative reproductive route != conflict resolution
```

## Reliability ceiling

The 47-row screen does **not** make U1 fully confirmatory.

Still required:

1. the registered independent double-coding reliability exercise on the frozen first 20;
2. codebook repair if any core field falls below the registered agreement trigger;
3. adjudication under the independent protocol.

If independent coding overturns any source-screen conflict call, the adjudicated call
supersedes this source-screen ledger.

## Consequence for the primary model

At current source-screen level, U1 contributes no conflict-positive row to the U1/U2/U6
primary model assembly.

This is a specificity result, not grounds for dropping U1. U1 remains the broadest
interaction-defined universe and provides the strongest check against relabeling generic
plant-animal interaction studies as functional-conflict evidence.

## Claim ceiling

The source screen supports a statement about this frozen 47-taxon review universe only. It
does not estimate the natural prevalence of conflict across flowering plants and does not
show that herbivory-pollination conflict never occurs.

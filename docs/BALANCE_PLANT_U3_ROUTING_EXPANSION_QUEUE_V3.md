# BALANCE U3 prospective routing expansion queue v3

## Frozen order

```text
1  Bixaceae        Amoreuxia wrightii       EVIDENCE_CEILING_BLOCKED
2  Brassicaceae    Brassica rapa             EVIDENCE_CEILING_BLOCKED
3  Lythraceae      Lagerstroemia indica      IN_PROGRESS
4  Malvaceae       Mollia lepidota           NOT_STARTED
```

The order remains frozen before prospective control conflict or routing outcomes are inspected.

## Bixaceae

The nearest `Cochlospermum tetraporum` negative-architecture candidate remains species-level animal-pollination eligibility open. Farther bee-pollinated controls are not substituted. The dependence block is retained as missingness.

## Brassicaceae

Close rapa/oleracea-lineage and allied Brassiceae candidates retain tetradynamous stamens and fail the negative-architecture gate.

Family-level `Stanleya elata` and `S. pinnata` candidates pass the biological opportunity screen, but the common phylogenetic ranking needed to identify the closest eligible equal-stamen control is not source-closed.

Therefore Brassicaceae is also retained as an `EVIDENCE_CEILING_BLOCKED` dependence block rather than receiving a convenient distant control.

## Active case

The next active case is now:

```text
Lythraceae
Lagerstroemia indica
U3_DEP_LYTHRACEAE_01
status = IN_PROGRESS
```

No conflict or routing outcome from either blocked family was used to advance the queue.

## Claim ceiling

This queue controls prospective acquisition and preserves matching-stage missingness. It does not identify control-side conflict, routing architecture, effect size, or prevalence.

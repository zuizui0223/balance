# BALANCE plant U3 dependence specification v1

## Purpose

Freeze the non-independence structure of the six registered U3 matched pairs **before** any final comparative model is fit.

Pair count is not evolutionary replication count.

## Frozen blocks

The six pair records occupy four conservative taxonomic/shared-control blocks:

```text
U3_DEP_SOLANUM_01
  Solanum rostratum -> S. lycocarpum

U3_DEP_MONOCHORIA_01
  Monochoria korsakowii -> M. australasica
  Monochoria vaginalis  -> M. australasica

U3_DEP_SENNA_01
  Senna alata        -> S. spectabilis
  Senna bicapsularis -> S. covesii

U3_DEP_MELASTOMATEAE_01
  Melastoma malabathricum -> Osbeckia chinensis
```

The Monochoria block has the strongest dependence because both case rows reuse the exact same control. The Senna rows use different controls but remain one conservative genus/family block rather than two independent deep origins.

## Current PASS lane

Four pairs are currently adjudicated PASS:

```text
Solanum pair          -> 1 block
two Senna pairs       -> 1 block
Melastomateae pair    -> 1 block
```

Therefore the present matched extraction contains **4 PASS pairs but only 3 frozen dependence blocks**.

The two Monochoria pairs remain OPEN and belong prospectively to one fourth block if they later pass ecological eligibility.

## Analysis rule

Every row carries:

```text
COUNT_AT_DEPENDENCE_BLOCK_NOT_NAIVE_PAIR
```

This does not prescribe one statistical estimator. It prohibits treating six rows, or the current four PASS rows, as independent evolutionary origins.

A later phylogenetic covariance model may refine this conservative structure; it may not silently increase the number of independent biological units beyond the registered evidence.

## Claim ceiling

This file freezes taxonomic/shared-control dependence only. It is not a species-tree covariance matrix, an effect estimate, or evidence that the remaining U3 measurement gates are closed.

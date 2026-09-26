# BALANCE U3 Senna covesii routing estimability contract v1

## Purpose

The routing measurement contract defines **what to measure**. This document
defines **when that measurement is precise enough to classify routing** without
post-hoc sample-size or equivalence decisions.

The focal taxon is `Senna covesii`, a nonheterantherous control with positive
binary pollen-fate conflict and unresolved routing architecture.

## Primary estimand

Source-resolve pollen from the frozen positional groups:

```text
median   = four median fertile stamen positions
abaxial  = three abaxial fertile stamen positions
```

For each source group, define the probability that tracked pollen enters the
registered transfer fate rather than the groomable / reward fate.

The primary contrast is:

```text
Delta_route =
  logit(P(transfer fate | abaxial source))
  -
  logit(P(transfer fate | median source))
```

Lost or unclassified grains are retained as missing-fate information and are
never silently reassigned.

## Symmetric architecture decision

One absolute log-odds margin `m > 0` is frozen independently of the focal
Stage-0 position contrast.

For the final confidence interval `[L, U]`:

```text
L >  m or U < -m
  -> WITHIN_FLOWER_DIVISION_OF_LABOUR

L > -m and U < m
  -> SHARED_INTEGRATED

otherwise
  -> UNRESOLVED
```

This makes the two conclusions symmetric. A wide interval crossing zero is not
evidence of shared integration.

## Stage-0 role

Stage-0 may estimate only nuisance quantities:

- plant-level dependence;
- flower / visit overdispersion;
- source-label recovery;
- unresolved-fate fraction;
- pooled baseline transfer probability;
- attrition and loss reasons;
- pollen-quantity imbalance induced by the manipulation.

It may **not** supply `Delta_route` as the minimum meaningful effect and may not
be used to choose a convenient equivalence margin.

The margin must instead be justified before outcome inspection from biological
relevance, assay calibration/repeatability, theory, or independent prior
information.

## Precision-based scale

A fixed flower count is not invented now.

The final design scale is selected only after nuisance calibration and target
freezing. It must be adequate for both:

1. a true biologically meaningful outside-band routing contrast to be resolved;
2. a truly equivalent contrast to place its entire interval inside the same
   equivalence band.

Power and precision sensitivity must preserve plant-level clustering and
registered ranges for unstable nuisance quantities rather than defaulting them
to zero.

## Pollen-quantity guard

Selective shielding/removal can change the amount of available pollen.

A routing call is invalid if the apparent positional effect can be explained
only by that quantity difference. The design must either balance available
pollen or explicitly model the induced quantity change.

## Canonical surfaces

```text
balance_domain/plant_u3_sencov_estimability.py
data/BALANCE_PLANT_U3_SENCOV_ROUTING_POWER_TARGETS_TEMPLATE_V1.json
data/BALANCE_PLANT_U3_SENCOV_STAGE0_NUISANCE_TEMPLATE_V1.json
tests/test_plant_u3_sencov_estimability.py
```

## Claim ceiling

This is an estimability and power-input contract. It is not a routing result,
sample-size result, architecture assignment, or historical causal inference.

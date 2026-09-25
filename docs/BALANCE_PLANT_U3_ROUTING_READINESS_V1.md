# BALANCE U3 conflict-conditioned routing readiness v1

## Why the next U3 question changes

The current four-pair lane has established a negative result for the simplest proposed explanatory variable:

> binary pollen-fate conflict presence does not deterministically distinguish heteranthery from nonheteranthery.

All four cases are conflict-positive and three nonheterantherous controls are also conflict-positive. The remaining Osbeckia state cannot make a finite matched binary conflict coefficient estimable.

The next biologically informative target is therefore **routing architecture conditional on conflict**, not another binary presence test.

## Current routing information

Among the three directly conflict-positive controls:

```text
Solanum lycocarpum
  AMONG_FLOWER_MODULE_DIVISION

Senna spectabilis
  WITHIN_FLOWER_DIVISION_OF_LABOUR

Senna covesii
  architecture UNRESOLVED
```

Thus:

```text
positive controls                         3
positive controls with resolved routing   2
routing coverage                          2/3
distinct resolved routing states          2
resolved dependence blocks                2
shared-integrated positive controls        0
```

The fourth control, `Osbeckia chinensis`, is still conflict-unresolved and therefore cannot yet enter a conflict-conditioned routing comparison.

## What this already shows

Heteranthery morphology is not equivalent to within-flower functional division.

`Senna spectabilis` has equal fertile-stamen morphology under the frozen heteranthery gate, but direct experiments resolve within-flower functional pollen routing.

Likewise, positive pollen-fate conflict does not force one architectural solution: `S. lycocarpum` routes function among flowers whereas `S. spectabilis` routes it within the flower.

## Why no routing model is fit yet

Only two positive controls currently have resolved routing architecture, and they occupy two frozen dependence blocks. No positive control is currently source-secure as `SHARED_INTEGRATED`.

A fitted multinomial or binary architecture model at this stage would therefore be numerically fragile and heavily determined by the cases already used to discover the pattern.

No arbitrary minimum sample-size threshold is introduced after seeing these data. Routing measurement must first be completed, and then a separate prospective model plus sample-size/estimability contract must be frozen before any confirmatory routing effect is fit.

The current result is a readiness diagnostic, not an effect estimate.

## Prospective evidence priorities

The next evidence acquisition order is frozen as:

1. resolve the broader routing architecture of `Senna covesii`;
2. resolve `Osbeckia chinensis` pollen-fate conflict and, if positive, its routing architecture;
3. expand only through prospectively matched controls in new dependence blocks.

The third step must preserve the existing control protocol:

> select controls before extracting conflict strength or routing architecture.

No future control may be chosen because it supplies a desired architecture category.

## Executable surface

```text
balance_domain/plant_u3_routing_readiness.py
tests/test_plant_u3_routing_readiness.py
```

## Claim ceiling

This diagnostic identifies the next evidence target and documents already resolved routing diversity.

It does not estimate a routing effect, architecture prevalence, conflict strength, or historical causal transition probability.

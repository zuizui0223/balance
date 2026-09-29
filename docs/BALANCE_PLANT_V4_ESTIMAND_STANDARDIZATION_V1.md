# BALANCE plant V4 post-fit estimand standardization v1

## Status

Frozen before independent U2/U6 architecture outcomes are opened.

This document clarifies how the already-registered probability contrasts are to be
standardized after fitting. It does not add a new hypothesis or change any response,
predictor, prior, support gate, or posterior decision threshold.

Machine-readable contract:
`data/BALANCE_PLANT_V4_ESTIMAND_STANDARDIZATION_V1.json`.

## Why this freeze is needed

The registered hypotheses are probability contrasts, not raw logit coefficients:

```text
Delta_T =
P(NONSTRUCTURAL_SEPARATION | ORDERED_OR_ALTERNATING)
-
P(NONSTRUCTURAL_SEPARATION | SIMULTANEOUS)

Delta_M =
P(STRUCTURAL_MODULE_DIVISION | MODULAR)
-
P(STRUCTURAL_MODULE_DIVISION | SINGLE)
```

Because multinomial probabilities are nonlinear, a phrase such as “adjusted for module and
universe” is not enough to define one numerical posterior contrast. A standardization
surface and weighting rule must be fixed before outcomes are inspected.

## H_T primary standardization

Use the unique `universe_id x module_opportunity2` cells that actually occur in the final
licensed U2+U6 assembly.

Every supported cell receives equal weight.

Within each cell evaluate two counterfactuals:

```text
timing = SIMULTANEOUS
timing = ORDERED_OR_ALTERNATING
```

while holding universe and module opportunity fixed.

This avoids raw-row weighting, so the larger U6 literature universe cannot dominate the
pooled probability contrast merely by contributing more rows. It also does not create a
new universe-module combination absent from the licensed assembly.

## H_M U2 standardization

Restrict to U2.

Take every temporal-exposure level represented in the final licensed U2 assembly and give
each supported timing level equal weight. Within each level compare:

```text
module = SINGLE
module = MODULAR
```

No timing level absent from U2 is introduced.

## Cross-universe H_T standardization

The stronger generality contrast uses only module strata that pass the frozen common-support
gate:

```text
within the same module stratum:
  U2 SIMULTANEOUS >= 2 blocks
  U2 ORDERED >= 2 blocks
  U6 SIMULTANEOUS >= 2 blocks
  U6 ORDERED >= 2 blocks
```

Within each universe, retained common-support module strata receive equal weight.

For each retained stratum compare ORDERED versus SIMULTANEOUS while holding universe and
module fixed. If no module stratum passes the gate, the cross-universe contrast is not
computed.

## Posterior direction probabilities

For posterior contrast draws `Delta^(m)`:

```text
P(Delta > 0 | data)
= number of draws with Delta^(m) > 0 / number of draws

P(Delta < 0 | data)
= number of draws with Delta^(m) < 0 / number of draws
```

The frozen 0.95 decision rule is then applied under both registered common-slope priors.

The interaction contradiction check remains:

```text
P(gamma_U6xORDERED,NONSTRUCTURAL < -1 | data)
```

with the interaction prior fixed at its registered Normal(0, 0.75) under both common-slope
prior fits.

## Claim ceiling

These rules define post-fit estimands only. They do not establish an effect, generality,
historical causation, or publication eligibility.

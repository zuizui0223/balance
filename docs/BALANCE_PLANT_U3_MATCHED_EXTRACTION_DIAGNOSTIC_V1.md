# BALANCE plant U3 matched extraction diagnostic v1

## Purpose

Test whether the first source-adjudicated heteranthery case-control pairs are already capable of estimating the BALANCE matched conflict architecture question.

Canonical extraction:

```text
data/BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv
balance_domain/plant_u3_matched_extraction.py
```

## Current closed pairs

Two PRIMARY pairs have passed matched-control adjudication:

1. `Solanum rostratum` -> `Solanum lycocarpum`
2. `Melastoma malabathricum` -> `Osbeckia chinensis`

For both pairs:

- the case has within-flower structural division of labour;
- the control has an integrated/nonheterantherous stamen architecture;
- both have serial stamen modules;
- animal-pollination eligibility is source-secure.

## Critical result

The matched architecture contrast is source-secure, but the matched **conflict** contrast is not.

Current extraction:

```text
CASE conflict:
  POSITIVE 2 / 2
  direct functional division / pollen-fate experiment

CONTROL conflict:
  UNRESOLVED 2 / 2
  no matched pollen-reward-versus-gamete conflict experiment recovered
```

Therefore:

```text
matched_conflict_estimand_ready = false
```

## Why this matters

A nonheterantherous flower is not automatically a low-conflict state.

The absence of feeding-versus-pollinating anther differentiation can arise under at least three observational possibilities:

1. pollen-reward/gamete conflict is genuinely weak;
2. conflict is strong but retained within a shared architecture;
3. the relevant conflict has never been measured.

Treating all nonheterantherous controls as "low conflict" would mechanically create the desired association.

The programme therefore leaves control-side conflict as `UNRESOLVED` rather than imputing it from architecture.

## Consequence for U3

U3 is now split into two separate closure problems:

### Matching closure

```text
6 registered PRIMARY controls
2 adjudicated
4 open
```

### Conflict-measurement closure

Among the two adjudicated pairs:

```text
case-side direct conflict evidence       2 / 2
control-side matched conflict evidence   0 / 2
```

The U3 matched effect is not estimable until conflict evidence is recovered for controls or a different estimand is prospectively frozen.

## Legitimate near-term uses

The current U3 data can support:

- architecture/source audits;
- module-substrate matching;
- testing whether control selection can be done without predictor leakage;
- identifying exactly which control experiments are missing.

It cannot yet support:

```text
heteranthery ~ conflict strength
```

or a matched estimate that interprets control architecture as evidence of weak conflict.

## Next empirical search target

For each adjudicated control, search specifically for experiments or quantitative observations on:

```text
pollen removal by visitors
pollen deposited on stigmas / exported between flowers
visitor manipulation of stamens
pollen allocation or viability among equivalent stamens
pollen limitation / reward removal
```

The target is not merely another floral-description paper.

The target is evidence capable of adjudicating whether one undifferentiated stamen system experiences measurable pollen-reward versus gamete-function conflict.

## Claim ceiling

This diagnostic identifies missing matched measurement.

It does not imply that conflict is absent in `Solanum lycocarpum` or `Osbeckia chinensis`.

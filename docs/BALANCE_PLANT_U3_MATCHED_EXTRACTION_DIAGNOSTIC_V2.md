# BALANCE plant U3 matched extraction diagnostic v2

## Purpose

Update the matched-extraction status after both Senna replacement controls were adjudicated.

This version supersedes v1 as the current extraction diagnostic. V1 remains a historical snapshot from the two-pair stage.

Canonical surfaces:

```text
data/BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv
data/BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv
balance_domain/plant_u3_matched_extraction.py
tests/test_plant_u3_matched_extraction.py
```

## Current extraction set

Four PRIMARY pairs now pass control adjudication and therefore enter matched extraction:

1. `Solanum rostratum -> Solanum lycocarpum`
2. `Melastoma malabathricum -> Osbeckia chinensis`
3. `Senna alata -> Senna spectabilis`
4. `Senna bicapsularis -> Senna covesii`

The extraction contains exactly one CASE and one CONTROL row per PASS pair:

```text
4 pairs
8 rows
```

The two Monochoria pairs remain outside this extraction because their control adjudications are still OPEN.

## Conflict state

Current case-side pollen-fate conflict:

```text
POSITIVE     2 / 4
UNRESOLVED   2 / 4
```

Current control-side pollen-fate conflict:

```text
POSITIVE     1 / 4
UNRESOLVED   3 / 4
```

Therefore:

```text
matched_conflict_estimand_ready = false
```

The sole resolved control-side positive is `Solanum lycocarpum`.

Its sources independently establish pollen removal as reward plus visitor-dependent stigma contact / reproductive effectiveness. This is not inferred from the absence of heteranthery.

## Architecture state

Current control architecture:

```text
AMONG_FLOWER_MODULE_DIVISION   1 / 4
UNRESOLVED                     3 / 4
SHARED_INTEGRATED              0 / 4
```

Thus:

```text
matched_integrated_control_contrast_ready = false
```

`Solanum lycocarpum` remains the critical counterexample to the shortcut:

```text
nonheteranthery
=>
weak conflict or globally shared integration
```

It is nonheterantherous, retains positive pollen-reward/gamete-transfer conflict, and routes sex function across flower modules through andromonoecy.

## Module substrate

Module substrate is extracted only after control selection and is not forced to match the case.

Current controls:

```text
REPEATED_FLOWERS      1
SERIAL_WITHIN_FLOWER  3
```

Three of four pairs therefore share the same registered module-substrate class between case and control; the Solanum pair does not.

This mismatch is retained rather than repaired post hoc because module substrate is a BALANCE predictor, not a legal matching variable.

## Pair-level blockers

### Solanum rostratum -> Solanum lycocarpum

```text
control selection        CLOSED
case conflict            POSITIVE
control conflict         POSITIVE
control architecture     AMONG_FLOWER_MODULE_DIVISION
```

This pair is fully informative for the proposition that pollen-fate conflict can persist without heteranthery and can be routed at a different architectural level.

### Melastoma malabathricum -> Osbeckia chinensis

```text
control selection        CLOSED
case conflict            POSITIVE
control conflict         UNRESOLVED
control architecture     UNRESOLVED
```

The historical Osbeckia source establishes hymenopteran handling and stigma contact, but not the registered matched pollen-removal / gamete-transfer estimand. Another descriptive visitor record does not close this gate.

### Senna alata -> Senna spectabilis

```text
control selection        CLOSED
case conflict            UNRESOLVED
control conflict         UNRESOLVED
control architecture     UNRESOLVED
```

The case has source-secure differentiated fertile-stamen sets; the control has source-secure homomorphic fertile stamens and animal pollination. The missing evidence is a matched functional pollen-fate contrast, not control identity.

### Senna bicapsularis -> Senna covesii

```text
control selection        CLOSED
case conflict            UNRESOLVED
control conflict         UNRESOLVED
control architecture     UNRESOLVED
```

The case has differentiated stamens and reported pollen-quality differences, but that is not promoted to a complete reward-versus-gamete pollen-fate experiment. The control identity is already adjudicated and remains separate from this measurement gap.

## Consequence for the estimand

U3 currently licenses a matched heteranthery-present versus heteranthery-absent extraction with four closed pairs.

It does not yet license either of the stronger claims:

```text
heteranthery ~ measured conflict strength
```

or

```text
structural division of labour
vs
shared-integrated retention
```

because three of four controls remain conflict-unresolved and no control is currently coded `SHARED_INTEGRATED`.

## Next measurement targets

Priority should follow information gain, not easier case accumulation:

1. recover a quantitative pollen-fate experiment for `Osbeckia chinensis`, if one exists;
2. recover direct pollen-removal / gamete-transfer evidence for both members of each Senna pair;
3. resolve broader control architecture only from direct source evidence;
4. do not reopen already closed Senna control selection merely because the downstream conflict estimand is unresolved.

## Claim ceiling

This diagnostic supports the current four-pair matched extraction and identifies exactly which measurements prevent a conflict-effect estimate.

It does not infer low conflict from homomorphic stamens, does not infer shared integration from nonheteranthery, and does not convert unresolved matched measurements into negative evidence.

# BALANCE plant confirmatory estimability audit v1

## Status

Pre-confirmatory screening diagnostic only.

This audit does not change the frozen four-class response and does not promote SCREENED
rows to confirmatory evidence.

## Current outcome-blind support surface

The current source-screened first-20 lanes contain:

```text
U1 first 20:
  conflict-positive rows = 0

U2 source-closed screen:
  conflict-positive rows = 8
```

Among the eight U2 conflict-positive rows, the frozen four-class response is:

```text
SHARED                         4
NONSTRUCTURAL_SEPARATION      3
STRUCTURAL_MODULE_DIVISION    0
MOSAIC                         1
```

Thus the currently screened U1+U2 surface is missing the
`STRUCTURAL_MODULE_DIVISION` class entirely.

## Interpretation

This is an **estimability warning**, not a reason to redefine the response.

The registered primary response remains:

```text
SHARED
NONSTRUCTURAL_SEPARATION
STRUCTURAL_MODULE_DIVISION
MOSAIC
```

The programme must not react to the current empty structural cell by:

- collapsing the primary response to binary;
- importing outcome-selected U3 heteranthery cases into the denominator as though they were
  sampled like U1/U2;
- relabelling nonstructural separation as structural differentiation;
- fitting only the classes that happen to be populated and presenting that as the original
  confirmatory model.

## What can legitimately change the support surface

1. complete the remaining U1 source/evidence extraction beyond the first 20;
2. complete independent U1/U2 coding and adjudication;
3. admit any genuinely conflict-positive rows that survive the frozen gates;
4. develop a separately registered matched/case-control analysis for U3 structural systems.

The four-class model is fit only if the final independently coded confirmatory surface has
adequate class support.

If one class remains absent, the correct result is:

```text
PRIMARY_MULTINOMIAL_NOT_ESTIMABLE_UNDER_FROZEN_RESPONSE
```

not a post-hoc response rewrite.

## Targeted U1 structural recovery result

A bounded four-candidate U1 recovery queue was opened before any candidate was promoted:

```text
Ruellia nudiflora
Impatiens capensis
Isomeris arborea
Eichhornia crassipes
```

All four current primary-source screens terminate without promotion. Thus the current
outcome-blind U1/U2 surface still has:

```text
STRUCTURAL_MODULE_DIVISION = 0
```

The empty class is no longer an unspecified search gap. Under the current U1/U2 source
universe and strict conflict contract, no source-screened route repairs it.

This strengthens the instruction not to use U3 structural-positive cases as silent
denominator repair.

## U3 role

U3 currently supplies structural division-of-labour cases, but its review universe is
architecture-positive by construction. It is therefore informative for:

- matched case/control tests;
- morphology-routing non-identifiability;
- targeted structural-mechanism analyses;

but not as a drop-in denominator repair for the U1/U2 outcome-blind programme.

## Current combined screening ceiling

```text
n conflict-positive = 8
n primary classes represented = 3 / 4
missing class = STRUCTURAL_MODULE_DIVISION
confirmatory multinomial fit = NOT READY
```

Additional blockers remain independent coding, outcome-independent predictor receipts, and
final dependence/covariance freezing.

Executable audit:

- `balance_domain/plant_estimability.py`
- `tests/test_plant_estimability.py`

# BALANCE plant U3 matched extraction diagnostic v6

## Status

The U3 matched lane has now separated three questions that were previously bundled together:

1. **measurement completeness** — are case/control binary conflict states all resolved?
2. **binary effect estimability** — would those completed states identify a finite matched binary conflict coefficient?
3. **routing architecture** — where is a persistent conflict handled when heteranthery is absent?

Current state:

```text
PASS matched pairs                         4
case conflict POSITIVE                   4 / 4
control conflict POSITIVE                3 / 4
control conflict UNRESOLVED              1 / 4
pairs with both conflict states resolved 3 / 4

matched_conflict_measurement_complete    false
matched_binary_conflict_effect_finitely_estimable
                                         false
```

The sole unresolved control is `Osbeckia chinensis`.

## Why completing Osbeckia cannot rescue the binary effect

All four heteranthery cases are already conflict-positive.

The unresolved Osbeckia state therefore has only two admissible binary completions.

### Completion A — Osbeckia is conflict-positive

All four pairs are positive on both sides.

```text
within-pair conflict-status discordance = 0 pairs
```

There is no informative predictor contrast.

### Completion B — Osbeckia has no demonstrated conflict

Only the Melastoma/Osbeckia pair is discordant.

```text
case positive / control negative = 1 pair
case negative / control positive = 0 pairs
```

All discordance lies in one direction. A conditional binary coefficient is completely separated rather than finitely estimable.

Thus a qualifying Osbeckia source can complete the registered measurement table but cannot make binary conflict presence an estimable matched effect in this four-pair design.

## Partial-identification result

Without imputing Osbeckia:

```text
case conflict-positive fraction     [1.00, 1.00]
control conflict-positive fraction  [0.75, 1.00]
raw case-control difference         [0.00, 0.25]
informative-pair count              [0, 1]
```

These are deterministic matched-sample bounds, not confidence intervals, population prevalence, or causal effects.

## Biological consequence

Binary conflict presence is already falsified as a deterministic separator of heteranthery because three nonheterantherous controls are directly conflict-positive.

The current resolved controls demonstrate multiple routing states:

```text
Solanum lycocarpum
  conflict POSITIVE
  AMONG_FLOWER_MODULE_DIVISION

Senna spectabilis
  conflict POSITIVE
  WITHIN_FLOWER_DIVISION_OF_LABOUR
  despite equal fertile-stamen morphology

Senna covesii
  conflict POSITIVE
  broader routing architecture UNRESOLVED
```

The empirically useful variables are therefore distinct:

```text
conflict presence
!=
heteranthery morphology
!=
routing architecture
!=
conflict strength
```

## Consequence for next work

A further Osbeckia search remains useful for:

- completing the four-pair evidence table;
- determining whether the raw matched-sample binary difference is 0 or 0.25;
- recovering quantitative conflict-strength evidence if available;
- resolving the control's broader routing architecture.

It is **not** a route to a finite binary conflict-presence coefficient in the current matched design.

Future U3 inference should therefore prioritize conflict strength and routing architecture rather than treating binary conflict presence as the primary explanatory variable.

## Executable surfaces

```text
balance_domain/plant_u3_matched_extraction.py
balance_domain/plant_u3_partial_identification.py
tests/test_plant_u3_matched_extraction.py
tests/test_plant_u3_partial_identification.py
```

## Claim ceiling

This diagnostic establishes structural non-estimability of a finite binary conflict-presence coefficient for the current four matched pairs under every admissible completion of the sole unresolved control.

It does not estimate a population effect, natural prevalence, quantitative conflict strength, or historical causation.

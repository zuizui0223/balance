# BALANCE U2 predictor-identifiability audit v1

## Status

Source-screening audit only. No value in this document is independently adjudicated and
no SCREENED predictor licenses confirmatory model entry.

The audit asks:

> Can the three frozen confirmatory predictors be coded from primary-source evidence
> without reading the focal architecture outcome back into the predictor?

Canonical receipt surface:

`data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv`.

## Measurement rules

### Conflict exposure geometry

Timing and spatial geometry are defined from the state in which conflict is **exposed**,
not from the focal resolution architecture.

Allowed evidence includes an integrated baseline, an experimental self/cross-pollen
challenge, a manipulated resolution-disabled state, or direct localization of the
interacting units.

Observed protandry, herkogamy, flexistyly, tristyly, or sexual segregation cannot by
themselves license timing/spatial predictors.

### Module substrate

`module_substrate` is coded at the smallest pre-existing conflict-bearing unit that can be
independently addressed in the integrated/challenge state.

- one shared stigma/pistil/resource pathway -> `SINGLE_OR_CONTINUOUS`;
- repeated homologous within-flower challenge units -> `SERIAL_WITHIN_FLOWER`;
- repeated flowers as conflict-bearing units -> `REPEATED_FLOWERS`;
- conflict directly between distinct independently manipulable organs ->
  `PREEXISTING_SEPARATE_ORGANS`;
- multiple independently supported nested levels -> `MULTILEVEL`.

Generic organ multiplicity unrelated to the demonstrated conflict is ignored.

## First-pass conflict-positive U2 result

The source-level conflict-positive first-20 systems are:

```text
Campsis radicans
Asclepias exaltata
Mimulus aurantiacus
Polemonium viscosum
Eichhornia paniculata
Pontederia sagittata
Epilobium obcordatum
Ipomopsis aggregata
```

All eight now have outcome-independent SCREENED values for all three confirmatory
predictors.

| system | module substrate | timing exposure | spatial exposure |
|---|---|---|---|
| Campsis radicans | SINGLE_OR_CONTINUOUS | MIXED | SAME_UNIT |
| Asclepias exaltata | SERIAL_WITHIN_FLOWER | MIXED | SAME_UNIT |
| Mimulus aurantiacus | PREEXISTING_SEPARATE_ORGANS | SIMULTANEOUS | SAME_UNIT |
| Polemonium viscosum | SINGLE_OR_CONTINUOUS | SEQUENTIAL_WITHIN_UNIT | SAME_UNIT |
| Eichhornia paniculata | REPEATED_FLOWERS | SIMULTANEOUS | BETWEEN_MODULES |
| Pontederia sagittata | SINGLE_OR_CONTINUOUS | SEQUENTIAL_WITHIN_UNIT | SAME_UNIT |
| Epilobium obcordatum | SINGLE_OR_CONTINUOUS | MIXED | SAME_UNIT |
| Ipomopsis aggregata | SINGLE_OR_CONTINUOUS | SIMULTANEOUS | SAME_UNIT |

### Module-substrate distribution

```text
SINGLE_OR_CONTINUOUS             5
SERIAL_WITHIN_FLOWER             1
REPEATED_FLOWERS                 1
PREEXISTING_SEPARATE_ORGANS      1
MULTILEVEL                        0
```

### Timing distribution

```text
SIMULTANEOUS                     3
SEQUENTIAL_WITHIN_UNIT           2
MIXED                            3
```

### Spatial distribution

```text
SAME_UNIT                        7
BETWEEN_MODULES                  1
```

## Quantitative receipt state

Across the full frozen U2 first-20 frame:

```text
total receipt slots                              60
clusters                                        20

outcome-independent resolved module slots        8
outcome-independent resolved timing slots        8
outcome-independent resolved spatial slots       8

clusters with all three predictors SCREENED      8
clusters with all three predictors ADJUDICATED   0
```

Thus source identifiability is no longer the immediate blocker for the eight
conflict-positive U2 systems. The remaining gates are:

1. independent coder reproducibility;
2. source adjudication of each receipt;
3. final dependence/covariance freeze;
4. primary-response class support.

## Important limitation

Predictor support is highly uneven.

Spatial exposure is `SAME_UNIT` in 7/8 systems, and module substrate is
`SINGLE_OR_CONTINUOUS` in 5/8. Therefore even after adjudication, U2 alone is unlikely to
identify a rich three-predictor multinomial surface.

This is not a reason to recode U2. It means that U1 expansion and/or separately registered
matched structural analyses are needed for broader predictor support.

## Primary-source anchors

- Bertin & Sullivan 1988, *Campsis radicans*;
- Broyles & Wyatt 1993, *Asclepias exaltata*;
- Fetscher 2001, *Mimulus aurantiacus*;
- Galen, Gregory & Galloway 1989, *Polemonium viscosum*;
- Harder, Barrett & Cole 2000, *Eichhornia paniculata*;
- Scribailo & Barrett 1994, *Pontederia sagittata*;
- Seavey & Carter 1994, *Epilobium obcordatum*;
- Waser & Price 1991, *Ipomopsis aggregata*.

The source packet retains exact DOI/provenance identifiers.

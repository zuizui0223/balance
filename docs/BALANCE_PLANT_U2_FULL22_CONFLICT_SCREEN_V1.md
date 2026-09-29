# BALANCE plant U2 full-22 strict conflict source screen v1

## Status

The complete Barrett (2002) review-defined U2 sexual-interference universe is source-screen
closed.

Canonical surfaces:

- `data/BALANCE_PLANT_U2_BARRETT_REVIEW_UNIVERSE_V1.csv`
- `data/BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv`
- `balance_domain/plant_u2_screen.py`
- `tests/test_plant_u2_screen.py`

This is a source-screen result, not independent double-code adjudication and not a
prevalence estimate.

## Frozen denominator

```text
22 dependency groups
22 source-resolved species-level records
37 Barrett-review references covered
```

## Strict conflict result

```text
POSITIVE                    8
NO_DEMONSTRATED_CONFLICT   14
UNRESOLVED_CANDIDATE        0

PASS_CONFLICT_GATE          8
FAIL_CONFLICT_GATE         14
HOLD_FOR_FULL_TEXT          0
```

Positive direct-conflict groups:

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

## What qualifies as positive

The positive calls require direct evidence that both functions bear on one registered
reproductive decision or resource and that one function measurably interferes with the
other.

Examples include:

- prior/simultaneous self pollen reducing subsequent outcross fertility;
- a female organ experimentally reducing male pollen export;
- geitonogamous selfing reducing outcrossed siring success;
- mixed self/outcross pollen reducing seed production through ovule usurpation.

Observed separation alone does not qualify.

## Important negatives

The 14 non-positive groups include several striking floral architectures:

- stigma-height dimorphism in *Narcissus*;
- tristyly in *Pontederia cordata*;
- pollen/stigma segregation in *Wahlenbergia*;
- flexistyly in *Alpinia*;
- enantiostyly in four *Wachendorfia* species;
- historical heteranthery observations in *Solanum* and *Chamaecrista*.

These remain `NO_DEMONSTRATED_CONFLICT` when the registered primary source does not
directly isolate the sexual-interference cost.

This produces a useful empirical separation:

```text
visible reproductive architecture
!=
direct conflict identification
```

## U1-U2 contrast

Current source-screen yields:

```text
U1 broad herbivory-pollination universe
  0 / 47 strict conflict positive

U2 mechanism-targeted sexual-interference universe
  8 / 22 strict conflict positive
```

These fractions must **not** be interpreted as natural prevalence or compared as though the
universes were exchangeable.

The valid conclusion is methodological/ecological:

> a broad interaction-defined literature surface contains many effects on pollination and
> reproduction but almost no direct shared-coordinate conflict receipts, whereas a
> mechanism-targeted sexual-interference literature recovers direct conflict substantially
> more often.

## Predictor source-screen state

All eight U2 positive groups have source-screened, outcome-independent values for all three
raw predictors:

```text
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

They remain `SCREENED`, not `ADJUDICATED`.

## Reliability gate

The frozen first 20 include all eight current source-screen positives.

The independent coding packet now contains:

```text
20 dependency groups
40 blank coder rows
CODER_A + CODER_B for every group
primary-source-only blinded packet
```

Independent coding can overturn source-screen calls. Adjudicated values take precedence.

## Claim ceiling

The source screen supports statements about the frozen Barrett-review universe only. It
does not estimate the prevalence of sexual interference across flowering plants and does
not prove that observed architectures evolved because of the identified conflict.

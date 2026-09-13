# Pedicularis Q1/Q3 minimum pilot size v1

## Purpose

Size the manipulation/selectivity pilot for **qualification**, not biological effect detection.

The pilot asks two fail-closed questions:

```text
Q1  can A be shifted by the registered amount without moving D or other protected floral states beyond tolerance?
Q3  can E_G alter seed-predator exposure while leaving pollinator handling and the registered A/D states inside tolerance?
```

A conventional non-significant off-target effect is not sufficient. Promotion requires equivalence-compatible uncertainty.

## Preferred unit: matched within-plant contrasts

Whenever biologically feasible, use matched flowers within the same plant / inflorescence so that the qualification contrast is based on paired differences rather than independent plants.

This is preferred because the intervention question is local:

```text
same plant background
+ assigned manipulation difference
-> realized target shift
+ off-target paired differences
```

The paired-difference SD, not the raw among-plant SD, is the relevant planning scale.

## Planning envelope

For a symmetric equivalence margin expressed in units of the paired-difference SD, with one-sided alpha = 0.05 and target power = 0.80 when the true off-target effect is zero, the normal-approximation planning envelope is:

| equivalence margin / paired-difference SD | complete matched pairs | with 5% loss | with 10% loss |
|---:|---:|---:|---:|
| 0.20 | 155 | 164 | 173 |
| 0.25 | 99 | 105 | 110 |
| 0.30 | 69 | 73 | 77 |
| 0.40 | 39 | 42 | 44 |
| 0.50 | 25 | 27 | 28 |

These are not claims about Pedicularis variance. They show how strongly the pilot size depends on the tolerated leakage relative to the paired-difference SD.

## Consequence for field planning

A very small pilot is useful only for mechanical feasibility. It is not enough to certify selectivity unless the allowed off-target margin is broad relative to the paired-difference variation.

Registered two-stage execution:

```text
Stage A: mechanical feasibility screen
~12-20 plants / matched blocks
purpose: reject obviously damaging or nonselective methods quickly
no qualification claim

Stage B: equivalence qualification
sample size determined by the tightest protected endpoint
using paired-difference SD from Stage A
purpose: formal Q1/Q3 PASS / FAIL / INCONCLUSIVE
```

Stage A therefore prevents wasting ~40-100+ plants on a manipulation that is visibly unusable. It cannot promote the system to execution-qualified status.

## Endpoint families that can drive sample size

### Q1 / A manipulation

Target shift:

```text
realized exsertion
```

Protected off-target endpoints:

```text
bract water volume/state
flower opening geometry other than registered exsertion
flower orientation
manipulation damage
flower longevity
nectar/reward proxy where feasible
```

Q1 passes only if the intended exsertion shift is achieved and all preregistered protected endpoints satisfy their own equivalence criteria.

### Q3 / E_G manipulation

Target shift:

```text
seed-predator access / attack / oviposition proxy
```

Protected off-target endpoints:

```text
pollinator access or handling
realized A state
realized D state
flower damage caused by exclusion/removal apparatus
flower longevity
```

Q3 passes only if predator exposure changes in the intended direction and protected endpoints remain inside their registered tolerances.

## The tightest gate determines n

Do not average tolerance requirements across endpoints.

```text
n_Q1 = max(required n across Q1 protected endpoints)
n_Q3 = max(required n across Q3 protected endpoints)
```

If one endpoint requires much greater precision than the others, it determines the qualification sample size.

## Multiplicity rule

The qualification programme is conjunctive: all protected endpoints must pass. The primary protection against false promotion is the fail-closed rule itself.

Do not rescue a failed endpoint by multiple-testing adjustment, endpoint deletion, or redefining the tolerance after seeing the data. If family-wise calibration is desired, it must be specified before Stage B and propagated through the sample-size calculation.

## Promotion states

```text
MECHANICALLY_FEASIBLE
= target manipulation works without obvious collapse/damage in Stage A

Q1_QUALIFIED
= target A shift established
+ all protected Q1 endpoints equivalence-compatible

Q3_QUALIFIED
= predator intervention established
+ all protected Q3 endpoints equivalence-compatible

PILOT_QUALIFIED
= Q1_QUALIFIED + Q3_QUALIFIED
```

`PILOT_QUALIFIED` still does not authorize the powered biological experiment until the combined 16-cell technical dry run confirms that the qualified interventions remain selective when crossed with D and E_P.

## Immediate planning default

Before Stage A data exist, use the following operational envelope only for logistics:

```text
mechanical screen: 12-20 matched plants/blocks
formal qualification likely range: ~25-80+ matched plants/blocks
```

The lower end corresponds roughly to a 0.5-SD equivalence margin; the upper end reaches the ~0.3-SD range after modest loss. Margins must be biologically justified in raw units before Stage B. Do not preregister an SD-standardized tolerance merely because it produces a convenient sample size.

## Reproducibility

`scripts/build_pedicularis_q1_q3_equivalence_grid.py` regenerates the standardized planning envelope.

# Pedicularis rex focal crossed-experiment qualification v1

## Decision

`Pedicularis rex` remains the leading shared biological platform for the BALANCE–BITA–SLK focal programme, but it is **PROVISIONALLY QUALIFIED, NOT YET EXECUTION-QUALIFIED**.

The criterion is not whether the system is biologically interesting. The criterion is whether one population-season can support the same-context causal sequence:

```text
real conflict
-> matched shared-vs-differentiated worldline
-> focal A x D interaction
-> selective antagonist allocation
-> selective pollinator allocation
-> four-way separability diagnostic
-> independent remaining-channel assay
-> optional SLK transport
```

## Existing support

Published work already supports two important biological premises.

1. Corolla exsertion is associated with opposing functional consequences in the same species: greater exsertion is associated with increased pollination success and increased seed predation.
2. Water retained in the cupulate bracts is experimentally supported as a seed-herbivore defence: draining water increases seed predation, while published visitation measurements did not show discrimination by legitimate pollinators between drained and intact flowers.

These results make the exsertion × water-defence system biologically coherent, but they do not by themselves identify the full causal allocation required by BITA or the architecture-value chain required by SLK.

## Qualification matrix

| Gate | Requirement | Current status | Promotion rule |
|---|---|---|---|
| Q1 | `A` and `D` are manipulable as independent focal contrasts | **OPEN** | Demonstrate a validated causal manipulation of exsertion `A` that preserves flower viability and does not mechanically alter the registered water-defence `D`; confirm the drainage/retention contrast for `D`. |
| Q2 | Pollinator intervention is selective | **PARTIAL** | Use pollinator exclusion/access or controlled hand-pollination protocol and show that it does not change `A`, `D`, antagonist exposure, or the remaining-channel assay. |
| Q3 | Antagonist intervention is selective | **OPEN** | Establish a seed-predator exclusion/exposure intervention independent of the water-retention manipulation; water drainage itself cannot serve as `E_G`. |
| Q4 | One common reproductive fitness scale is available | **PASS-IN-PRINCIPLE** | Freeze `undamaged mature viable seeds per focal flower` and retain all component readouts needed to diagnose why it changes. |
| Q5 | Pollinator-independent reproductive baseline is measurable | **PASS-IN-PRINCIPLE** | Measure reproduction under pollinator exclusion / controlled pollination rather than assuming zero; estimate `m0_delta`. |
| Q6 | Full `A x D x E_G x E_P` is feasible | **OPEN** | Pilot all 16 cells with treatment validation before outcome inspection; fail if any intervention collapses the A or D contrast. |
| Q7 | Four-way separability is estimable | **OPEN** | Pre-register the `A:D:E_G:E_P` term as an identification diagnostic, not a nuisance interaction. |
| Q8 | Remaining joint channel has an independent assay | **OPEN** | Run a consumer-standardized `A x D` assay (e.g. standardized pollination + predator exclusion) and directly measure candidate physiological/allocation costs before naming `U_delta` as `kappa_delta`. |
| Q9 | BALANCE worldlines are prospectively defined | **PARTIAL** | Freeze shared world `S`, accessible alternative `D`, valid optimization domains, and `Delta_W = W_D* - W_S*` before focal outcome inspection. |
| Q10 | SLK quantities are transported only after identification | **PASS AS GOVERNANCE** | Do not infer `R`, `K`, `s`, or `Phi` from a BITA residual. Promote only independently identified upstream quantities. |

## Immediate pilot: manipulation qualification, not hypothesis testing

The next field execution should be a small qualification pilot whose sole purpose is to decide whether Q1–Q3 and Q6 are technically valid.

### Pilot factors

```text
A: low vs high realized corolla exsertion
D: water-defence low vs high
E_G: seed-predator excluded vs exposed
E_P: pollinator excluded vs accessible
```

All four factors are crossed, but the pilot is not powered for the biological interaction. It is powered only to detect manipulation failure and leakage.

### Validation measurements

For every treatment cell record:

```text
realized exsertion
bract water state / volume
flower damage caused by manipulation
pollinator access / visitation state
seed-predator exposure / attack evidence
flower longevity
initial ovule count where feasible
initial seed set before predation
final undamaged mature viable seed count
```

The pilot fails if changing one factor materially changes the realized level of another focal factor before the consumer response is expressed.

## Full focal design after qualification

If the pilot passes, freeze one `context_id` and one `fitness_scale_id` and run:

```text
A x D x E_G x E_P = 2 x 2 x 2 x 2 = 16 cells
```

with blocked randomization within plant / inflorescence where biologically defensible and with enough replication to estimate the highest-order interaction.

Primary quantities:

```text
Delta_AD W                      total focal trait interaction
Delta_AD W | E_G states         antagonist-allocation face
Delta_AD W | E_P states         pollinator-allocation face
A:D:E_G:E_P                     four-way separability diagnostic
m0_delta                        pollinator-independent A x D baseline
U_delta                         unallocated remainder
Delta_W = W_D* - W_S*           direct BALANCE worldline contrast
```

Interpretation rule:

```text
four-way = 0 within registered tolerance
+ selective interventions validated
+ independent remaining-channel assay agrees
=> mechanism allocation may be promoted

otherwise
=> retain partial identification
```

## Remaining-channel assay

The default independent assay is a consumer-standardized block:

```text
standardized hand pollination
+ seed-predator exclusion
+ A x D
```

Measure reproductive output together with direct candidate cost readouts such as flower longevity, tissue damage, water/biomass allocation, nectar production, and seed provisioning where feasible. A residual from the main factorial is retained as `U_delta` until this assay identifies its biological content.

## SLK handoff ceiling

A successful focal crossed experiment can strongly support G1–G5 only if the required quantities are independently identified on the same fitness scale. It does **not** by itself identify G6 accessibility, G7 invasion, G8 fixation, or G9 occupancy.

The allowed promotion chain is therefore:

```text
SCH/BALANCE: conflict and worldline ordering
BITA:        ecological allocation of the focal interaction
SLK:         transport identified L/R/K/Phi quantities
             without compressing Phi > 0 into "differentiation evolves"
```

## Current status

```text
BIOLOGICAL FIT:            STRONG
EXISTING CONFLICT EVIDENCE: STRONG
D DEFENCE MANIPULATION:    SUPPORTED
A CAUSAL MANIPULATION:     OPEN
SELECTIVE E_G:             OPEN
SELECTIVE E_P:             PARTIAL
FOUR-WAY FEASIBILITY:      OPEN
REMAINING-CHANNEL ASSAY:   OPEN

FINAL STATUS = PROVISIONALLY QUALIFIED
```

The next empirical action is therefore not a full powered experiment. It is the manipulation-selectivity pilot that can either promote `Pedicularis rex` to **EXECUTION-QUALIFIED** or reject it before costly field replication.
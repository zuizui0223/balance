# Pedicularis rex focal crossed-experiment qualification v2

## Decision

`Pedicularis rex` remains the leading shared biological platform for the BALANCE–BITA–SLK focal programme, but it is **PROVISIONALLY QUALIFIED, NOT YET EXECUTION-QUALIFIED**.

The criterion is whether one population-season can support the same-context causal sequence:

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

Published work supports two biological premises.

1. Corolla exsertion is associated with opposing functional consequences: greater exsertion is associated with increased pollination success and increased seed predation.
2. Water retained in cupulate bracts is experimentally supported as seed-herbivore defence: draining water increases seed predation, while published visitation measurements did not detect discrimination by legitimate pollinators between drained and intact flowers.

Published work therefore supports the biological premise and the D manipulation, but not the full causal allocation.

## Qualification matrix

| Gate | Requirement | Current status | Promotion rule |
|---|---|---|---|
| Q1 | `A` and `D` are manipulable as independent focal contrasts | **OPEN** | Demonstrate a validated causal manipulation of realized exsertion `A` that preserves flower viability and leaves water-defence `D` unchanged; reconfirm drainage/retention for `D`. |
| Q2 | Pollinator intervention is selective | **PARTIAL** | Use controlled pollinator access or standardized hand-pollination and show that it does not alter `A`, `D`, antagonist exposure, or candidate remaining-channel readouts. |
| Q3 | Antagonist intervention is selective | **OPEN — CRITICAL** | Establish seed-predator exclusion/exposure independently of water retention and pollinator access. Water drainage cannot serve as `E_G`; ordinary bagging that also changes pollination does not pass. |
| Q4 | One common reproductive fitness scale is available | **PASS-IN-PRINCIPLE** | Freeze `undamaged mature viable seeds per focal flower`; retain component outcomes. |
| Q5 | Pollinator-independent reproductive baseline is measurable | **PASS-IN-PRINCIPLE** | Measure reproduction under pollinator exclusion / controlled pollination rather than assuming zero; estimate `m0_delta`. |
| Q6 | Full `A x D x E_G x E_P` is feasible | **OPEN** | Pilot all 16 cells; fail if any intervention collapses another registered factor. |
| Q7 | Four-way separability is estimable | **OPEN** | Pre-register `A:D:E_G:E_P` as an identification diagnostic. |
| Q8 | Remaining joint channel has an independent assay | **OPEN** | Run a consumer-standardized `A x D` assay and direct candidate-cost measurements before naming `U_delta`. |
| Q9 | BALANCE worldlines are prospectively defined | **PARTIAL** | Freeze shared world `S`, accessible alternative `D`, optimization domains and `Delta_W = W_D* - W_S*` before outcome inspection. |
| Q10 | SLK quantities are transported only after identification | **PASS AS GOVERNANCE** | Never infer `R`, `K`, `s`, or `Phi` from a BITA residual alone. |

## Manipulation-selectivity pilot

The next field execution is a qualification pilot, not a powered test of the biological interaction.

### D — water-defence manipulation: reference implementation

Use the published drainage logic as the starting implementation:

```text
D_high = intact cupulate bract with retained rainwater / standardized refill
D_low  = drainage opening at bract base, with matched sham handling
```

Record water volume/depth repeatedly. A sham perforation/handling control is required if feasible so that tissue injury is not silently absorbed into `D`.

Promotion requires:

```text
large persistent D contrast
+ no material change in realized A
+ no detectable direct change in pollinator access mechanics
+ acceptable tissue-damage differential after sham correction.
```

### A — realized exsertion manipulation: candidate ladder

No published causal exsertion manipulation is treated as established. Test candidate methods in the following order and accept only a method that changes realized exsertion without changing D or floral viability.

```text
A1  reversible corolla-position spacer/support
    -> alter flower position relative to bract without cutting bract or corolla

A2  inert external bract-height cuff / visual-geometry sleeve
    -> only if it can alter effective exsertion while leaving water volume,
       access geometry and oviposition substrate demonstrably unchanged

A3  destructive shortening/extension manipulation
    -> last resort; reject if wound effects or floral mechanics are non-negligible
```

The target is the realized exsertion contrast, not a particular surgical method.

For every candidate measure:

```text
realized exsertion
corolla angle
opening width
nectar standing crop
flower longevity
bract water volume
visible tissue damage
pollinator handling time on validation flowers
```

A method fails Q1 if the induced exsertion contrast is accompanied by a biologically important shift in water defence, flower opening, nectar, or longevity.

### E_G — seed-predator intervention: critical feasibility ladder

Published biology makes this the hardest gate: fly and moth seed predators oviposit externally after flowers open and before ovary swelling. A generic pollinator-exclusion bag therefore cannot be called selective.

Test candidate strategies fail-closed:

```text
G1  temporally staged antagonist exclusion after a fixed pollination window
    -> acceptable only if the pollination exposure window is identical across E_G states
       and predator attack still occurs in the exposed state during the registered risk window

G2  localized physical oviposition barrier around ovary/sepal attack surfaces
    -> acceptable only if bumblebee approach, landing and floral handling are unchanged

G3  repeated antagonist removal / egg removal
    -> acceptable only if detection/removal is reliable and handling/sham effects are matched

G4  localized chemical deterrence
    -> not promotable without explicit evidence that pollinator behaviour and plant physiology
       are unaffected; default status is FAIL rather than presumed selective
```

A mesh aperture strategy that excludes small Diptera/Lepidoptera while allowing larger bumblebees is not assumed viable; body-size filtering works in the wrong direction for at least part of this consumer set.

Q3 promotion requires all of:

```text
strong reduction in oviposition/attack under E_G exclusion
+ no material change in pollinator visitation/handling under pollinator-access conditions
+ no material change in A or D
+ matched handling/sham effects
+ same registered ecological risk window across E_G states.
```

If no candidate passes, `Pedicularis rex` is rejected for full BITA mechanism allocation even if it remains useful for SCH/BALANCE.

### E_P — pollinator intervention

Two admissible routes enter the pilot:

```text
P1 natural-access route:
   pollinator accessible vs excluded, with identical timing/handling

P2 standardized-pollination route:
   controlled pollen delivery vs pollinator-independent baseline
```

P2 is preferable for the remaining-channel assay because it can standardize pollen receipt while antagonist exposure is suppressed. P1 is preferable when the target is naturally mediated pollinator allocation. They are different estimands and must not be silently mixed.

## Pilot layout

Run all nominal cells at small replication:

```text
A x D x E_G x E_P = 2 x 2 x 2 x 2 = 16 cells
```

but do not interpret the biological `A:D:E_G:E_P` term from the qualification pilot.

The pilot asks only whether the factors remain manipulable and selective.

For every cell record:

```text
realized exsertion
bract water state / volume
flower damage caused by manipulation
pollinator access / visitation state
pollinator handling time where observable
seed-predator oviposition / attack evidence
flower longevity
nectar standing crop where feasible
initial ovule count where feasible
initial seed set before predation
final undamaged mature viable seed count
```

## Pre-registered leakage diagnostics

For each manipulated factor `X`, fit validation models for every other realized factor and manipulation-sensitive covariate.

Examples:

```text
A manipulation -> realized D, water volume, opening width, nectar, longevity
D manipulation -> realized A, pollinator handling, tissue damage
E_G            -> pollinator access/handling, A, D
E_P            -> antagonist exposure, A, D
```

Do not use non-significance as proof of selectivity. Promotion requires effect-size compatibility with a prospectively registered tolerance or equivalence region plus adequate measurement precision.

Until empirical pilot variance is available, the repository does not hard-code numerical tolerances. The first pilot estimates measurement error and biologically plausible equivalence bounds without opening the target BITA interaction for confirmatory interpretation.

## Execution promotion rule

`Pedicularis rex` becomes **EXECUTION-QUALIFIED** only if:

```text
Q1 PASS
Q2 PASS
Q3 PASS
Q4 PASS
Q5 PASS
Q6 PASS
```

Q7 and Q8 then become mandatory components of the powered execution rather than optional additions.

Failure handling:

```text
Q1 failure -> seek alternative A implementation; if unresolved, reject focal system
Q2 failure -> retain only antagonist-side partial identification if valid
Q3 failure -> Pedicularis may remain SCH/BALANCE but cannot close full BITA allocation
Q6 failure -> abandon four-way interpretation; do not repair by dropping failed cells post hoc
Q8 failure -> report U_delta as unallocated remainder, not biological cost
```

## Full focal design after qualification

If promoted, freeze one `context_id` and one `fitness_scale_id` and run the 16-cell factorial with blocked randomization where defensible and enough replication to estimate the highest-order interaction.

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

Interpretation:

```text
four-way compatible with registered separability tolerance
+ selective interventions validated
+ independent remaining-channel assay agrees
=> mechanism allocation may be promoted

otherwise
=> retain partial identification
```

## Remaining-channel assay

Default independent assay:

```text
standardized hand pollination
+ validated seed-predator exclusion
+ A x D
```

Measure reproductive output with candidate direct costs such as flower longevity, tissue damage, water/biomass allocation, nectar production and seed provisioning where feasible. `U_delta` remains unlabeled until this assay supports a biological interpretation.

## SLK handoff ceiling

A successful focal crossed experiment can support G1–G5 only where the relevant quantities are independently identified on the same fitness scale. It does not by itself identify G6 accessibility, G7 invasion, G8 fixation, or G9 occupancy.

```text
SCH/BALANCE: conflict and worldline ordering
BITA:        ecological allocation of the focal interaction
SLK:         transport identified L/R/K/Phi quantities
             without compressing Phi > 0 into "differentiation evolves"
```

## Current status

```text
BIOLOGICAL FIT:             STRONG
EXISTING CONFLICT EVIDENCE: STRONG
D DEFENCE MANIPULATION:     SUPPORTED
A CAUSAL MANIPULATION:      OPEN — candidate ladder registered
SELECTIVE E_G:              OPEN — CRITICAL BOTTLENECK
SELECTIVE E_P:              PARTIAL — two routes registered
FOUR-WAY FEASIBILITY:       OPEN
REMAINING-CHANNEL ASSAY:    OPEN

FINAL STATUS = PROVISIONALLY QUALIFIED
```

The immediate decision problem is now sharp: test whether an exsertion manipulation and a truly selective seed-predator intervention exist. If E_G cannot be qualified, do not spend a full field season trying to force Pedicularis into the BITA flagship.
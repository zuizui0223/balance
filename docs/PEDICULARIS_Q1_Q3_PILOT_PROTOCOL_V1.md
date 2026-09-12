# Pedicularis rex Q1/Q3 qualification pilot v1

## Purpose

This pilot is an **engineering / identification qualification**, not a test of the biological BITA interaction.

Its only job is to decide whether `Pedicularis rex` can support the registered focal design without factor leakage:

```text
A x D x E_G x E_P
```

where:

```text
A   = low / high realized corolla exsertion
D   = low / high water-bract defence state
E_G = seed-predator excluded / exposed
E_P = pollinator excluded / accessible
```

The pilot must be completed before any powered focal interaction experiment.

---

## General fail-closed rule

A manipulation passes only if both conditions hold:

1. it creates the intended change in its own registered factor; and
2. all prespecified off-target variables remain inside prospectively frozen equivalence margins.

`P > 0.05` is not evidence of selectivity.

Equivalence margins must be frozen from measurement repeatability, untreated biological variation, and a biologically negligible-change argument **before inspecting reproductive outcomes**.

If a manipulation changes another focal factor outside its equivalence margin, that manipulation is rejected even if the downstream biological result is attractive.

---

# Stage 0 — measurement repeatability and margin freeze

Before manipulating flowers, repeat the focal measurements on untreated flowers to estimate measurement error and natural short-interval variability.

Freeze measurement definitions for:

```text
realized_exsertion_mm
bract_water_volume_or_state
corolla_aperture
flower_orientation
flower_longevity
nectar_volume
visible_manipulation_damage
pollinator_access_state
seed_predator_attack_or_oviposition_state
```

For each quantity define:

```text
measurement_error
untreated_short_interval_variation
equivalence_margin
```

No equivalence margin may be chosen after seeing treatment effects.

---

# Stage 1 — Q1 causal A-manipulation qualification

## Goal

Create two reproducible levels of realized corolla exsertion without altering the registered water-defence axis or gross floral function.

## Manipulation ladder

Test candidate methods in this order and stop at the first method that qualifies:

```text
A1  reversible external support / spacer
A2  inert collar or cuff that changes realized exsertion without entering the bract water reservoir
A3  minimal structural repositioning with sham control
```

Do not begin with irreversible cutting or tissue removal unless all reversible approaches fail; destructive alteration has a high risk of changing floral damage, longevity, water relations, or pollinator handling.

## Required groups for each candidate A method

```text
untouched control
sham-manipulated control
A_low
A_high
```

## Required validation

The candidate method must establish separation in:

```text
realized_exsertion_mm
```

while remaining equivalent for:

```text
bract_water_volume_or_state
corolla_aperture except where mechanically inseparable from the registered A definition
flower_orientation
visible tissue damage
flower longevity over the qualification interval
nectar volume where feasible
```

A method is rejected if the sham itself produces a non-negligible change in any focal validation variable.

## Q1 promotion receipt

Record:

```text
A_method_id
A_low realized distribution
A_high realized distribution
sham distribution
off-target equivalence results
photographic protocol
operator / block information
```

Q1 becomes `PASS` only after one method produces a stable A contrast with acceptable leakage.

---

# Stage 2 — Q3 selective seed-predator intervention qualification

## Goal

Manipulate seed-predator exposure independently of `A`, `D`, and pollinator access.

## Critical constraint

Water drainage / retention is the focal defence trait `D` and therefore **cannot** be reused as the antagonist intervention `E_G`.

A whole-flower bagging treatment that simultaneously excludes pollinators is also not a qualified `E_G` manipulation for the full factorial.

## Candidate E_G ladder

Test in this order:

```text
G1  stage-specific exclusion applied only during the seed-predator oviposition window
G2  localized physical oviposition barrier that leaves the pollinator-facing corolla accessible
G3  repeated direct removal / interception of seed predators with matched handling control
```

A candidate may advance only if it changes predator exposure or attack evidence while preserving pollinator access and floral state.

## Required groups for each candidate E_G method

```text
predator-exposed control
sham handling / sham barrier
predator-excluded treatment
```

## Required validation

Intended effect:

```text
seed_predator_attack_or_oviposition_state changes in the registered direction
```

Off-target equivalence:

```text
realized_exsertion_mm
bract_water_volume_or_state
corolla_aperture
flower_orientation
flower longevity
pollinator access
pollinator visitation / legitimate handling behaviour during the validation window, where observable
visible tissue damage caused by the exclusion method
```

If the barrier changes legitimate pollinator visitation or handling outside the frozen equivalence margin, Q3 fails for that method.

## Q3 promotion receipt

Record:

```text
E_G_method_id
predator exposure contrast
pollinator-access equivalence
A/D preservation
sham performance
operator / temporal block
```

Q3 becomes `PASS` only if one antagonist manipulation is both effective and selective.

---

# Stage 3 — E_P validation

The pollinator intervention is already `PARTIAL`, but it must be qualified in the same population-season used for the focal programme.

Compare the registered pollinator-access / exclusion or controlled-pollination states and verify that they preserve:

```text
A
D
E_G treatment integrity
flower damage
flower longevity
```

Pollinator exclusion must not be interpreted as zero reproduction. The later experiment must estimate the pollinator-independent baseline `m0_delta`.

---

# Stage 4 — 16-cell manipulation dry run

Only after Q1 and Q3 individually pass, instantiate all combinations:

```text
A x D x E_G x E_P = 16 cells
```

This is still a technical dry run, not the powered outcome experiment.

For every cell validate:

```text
realized A
realized D
realized E_G
realized E_P
flower damage
flower longevity
```

The key question is whether manipulations that are selective alone remain selective when combined.

## Interaction leakage audit

Fit validation models for each realized factor using all four assigned factors and their interactions.

Examples:

```text
realized_A ~ assigned_A * D * E_G * E_P + block
realized_D ~ assigned_D * A * E_G * E_P + block
E_G_validation ~ assigned_E_G * A * D * E_P + block
E_P_validation ~ assigned_E_P * A * D * E_G + block
```

These models are manipulation audits, not biological mechanism tests.

A significant or large cross-factor effect is not automatically fatal; the decision is based on whether the realized factor leaves its prospectively frozen admissible range or whether off-target variables leave their equivalence margins.

---

# Stage 5 — promotion decision

Promote `Pedicularis rex` from `PROVISIONALLY QUALIFIED` to `EXECUTION-QUALIFIED` only if:

```text
Q1 A manipulation                     PASS
Q2 selective pollinator intervention PASS
Q3 selective antagonist intervention PASS
Q4 common fitness currency           PASS
Q5 pollinator-independent baseline   FEASIBLE
Q6 all 16 cells technically feasible PASS
Q7 four-way diagnostic estimable     PASS-IN-DESIGN
Q8 remaining-channel assay feasible  PASS-IN-DESIGN
Q9 BALANCE worldlines frozen         PASS-IN-DESIGN
Q10 SLK transport governance         PASS
```

Any failure of Q1, Q2, Q3, or Q6 blocks the full BITA mechanism-allocation experiment.

---

# Remaining-channel block to prepare in parallel

Before the powered experiment, confirm feasibility of a consumer-standardized assay:

```text
A x D
+ standardized hand pollination
+ predator exclusion
```

Candidate direct readouts:

```text
flower longevity
manipulation damage
nectar production
water / biomass allocation where feasible
ovule number
seed provisioning / viable seed mass where feasible
```

The main-factorial remainder remains `U_delta` until this independent assay supports a biological label.

---

# Field data schema

Minimum flower-level columns:

```text
context_id
plant_id
inflorescence_id
flower_id
block_id
assigned_A
assigned_D
assigned_E_G
assigned_E_P
A_method_id
E_G_method_id
realized_exsertion_mm
bract_water_state
bract_water_volume
corolla_aperture
flower_orientation
visible_damage
flower_longevity
nectar_volume
pollinator_access_validated
pollinator_visits
predator_exposure_validated
predator_attack_or_oviposition
ovule_count
initial_seed_set
final_undamaged_mature_viable_seeds
notes
```

Outcome columns may be collected for logistics, but the qualification decision must be made from the registered manipulation/selectivity criteria rather than from whether the biological interaction looks promising.

---

# Stop / fallback rule

```text
Pedicularis Q1 PASS + Q3 PASS + 16-cell dry run PASS
    -> proceed to powered focal crossed experiment

Pedicularis Q1 FAIL after the registered manipulation ladder
or Q3 FAIL after the registered selective-antagonist ladder
or combined 16-cell selectivity FAIL
    -> retain Pedicularis for SCH/BALANCE where valid
    -> activate Fragaria focal-trait qualification
```

Do not weaken the BITA identification standard in order to keep Pedicularis as the flagship.
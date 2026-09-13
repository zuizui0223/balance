# Pedicularis 16-cell dry run and powered experiment plan v1

## Purpose

Separate technical qualification from biological hypothesis testing for the focal BALANCE–BITA–SLK programme.

The 16-cell dry run is **not** used to estimate the biological interaction of interest. Its purpose is to test whether the full crossed intervention architecture remains valid when all manipulations are combined.

## Registered factors

```text
A   attraction-facing exsertion contrast: low / high
D   water-bract defence contrast: low / high
E_G seed-predator state: excluded / exposed
E_P pollinator state: excluded / accessible
```

Full crossing:

```text
A x D x E_G x E_P = 16 cells
```

## Stage 1 — technical dry run

### Primary technical estimands

For each assigned factor, evaluate the realized treatment state and leakage onto the other registered factors before outcome interpretation.

Required realized-state variables:

```text
realized_exsertion
realized_bract_water_state
pollinator_access_or_handling_state
seed_predator_access_or_attack_proxy
flower_orientation
flower_opening_geometry
manipulation_damage
flower_longevity
nectar_or_reward_proxy_if feasible
```

### Fail-closed leakage rule

For each intervention X and off-target variable Y, define a prospective equivalence margin `delta_XY` before viewing the dry-run biological outcomes.

Promotion requires the confidence interval for the off-target contrast to lie wholly inside the registered equivalence interval.

```text
CI(off_target_effect_X_on_Y) subset [-delta_XY, +delta_XY]
```

A conventional non-significant difference is not evidence of selectivity.

### Cell-retention rule

Every one of the 16 cells must preserve the intended A and D contrast and the intended consumer state at the design level. A treatment combination that systematically collapses a registered contrast fails technical qualification.

Missing observations are handled separately from manipulation failure. A plant is **not** discarded merely because one or more assigned cells are missing. Preserve the randomization record and all observed cells for the hierarchical analysis unless a preregistered exclusion criterion applies.

### Dry-run sample size

The dry run is sized for treatment validation and equivalence precision, not for detection of `A:D:E_G:E_P` on fitness. Therefore no interaction p-value from this stage is promoted into the biological paper.

Replication is increased until the registered equivalence decisions are sufficiently precise or the method is rejected as technically infeasible.

## Stage 2 — powered focal experiment

Only after all technical gates pass, freeze one `context_id`, one `fitness_scale_id`, the A/D contrast definitions, consumer interventions and equivalence margins.

Primary reproductive fitness currency:

```text
undamaged mature viable seeds per focal flower
```

Retain component outcomes to diagnose pathways:

```text
pollinator visitation / controlled pollen receipt
initial ovule number
initial seed formation before predation where feasible
seed-predator attack evidence
final mature seed number
seed viability
flower longevity
candidate physiological/allocation readouts
```

## Primary model

Fit the full factorial rather than stepwise deleting higher-order terms:

```text
W ~ A * D * E_G * E_P + preregistered block/random effects
```

Use a distribution appropriate to the registered fitness variable and its dispersion/zero structure. Model choice is frozen before testing the focal contrasts after pilot dispersion information is available.

Blocked randomization within plant or inflorescence is used when feasible, with plant identity retained as a grouping factor rather than treating flowers as independent biological replicates.

### Partial-data rule

The powered analysis uses all valid observed cells. Complete-case analysis is retained only as a sensitivity analysis because requiring all 16 cells from one plant creates an avoidable attrition penalty.

The pre-dry-run working model for design calculations uses generalized least squares with compound-symmetric plant covariance. The final analysis may use a GLMM or another registered hierarchical model after the dry run identifies the outcome distribution, dispersion, zero structure, and missingness pattern.

If missingness depends on treatment, manipulation damage, consumer attack, or latent reproductive outcome, that mechanism must be represented in the final design simulation and sensitivity analysis rather than treated as random cell loss.

## Registered estimands

### Total focal trait interaction

Under the full ecological state:

```text
Delta_AD_W = W11 - W10 - W01 + W00
```

Estimate `A0`, `A1`, and `Delta_AD_W` with joint uncertainty.

### Antagonist allocation face

Compare `Delta_AD_W` across `E_G` states at each pollinator state.

The change in the A-by-D interaction induced by selective predator exclusion is the identified antagonist-mediated allocation face, conditional on intervention selectivity.

### Pollinator allocation face

Compare `Delta_AD_W` across `E_P` states at each antagonist state.

Pollinator exclusion does not define zero reproduction. Estimate the pollinator-absent `A x D` baseline explicitly as `m0_delta`.

### Four-way separability diagnostic

```text
A:D:E_G:E_P
```

is an identification diagnostic, not a nuisance interaction.

Interpretation:

```text
four_way compatible with registered separability tolerance
+ intervention selectivity validated
=> additive consumer-channel allocation remains admissible

four_way outside tolerance
=> consumer-channel allocation is state-dependent;
   retain partial identification and do not force rho/iota decomposition
```

Absence of conventional significance is not by itself a separability receipt. Use a preregistered tolerance/equivalence criterion on the four-way estimand.

## Remaining-channel assay

Run a separate consumer-standardized A x D block:

```text
standardized hand pollination
+ seed-predator exclusion
+ A x D
```

Compare its independently estimated A-by-D interaction with the unallocated remainder from the main factorial.

The remainder remains `U_delta` unless the independent assay supports a registered candidate mechanism. Do not name `U_delta` as architecture cost or physiological cost by subtraction alone.

## Power target hierarchy

Power the full experiment for the smallest estimand required for the main inferential claim, in this order:

```text
P1 four-way separability diagnostic
P2 consumer-allocation contrasts in Delta_AD_W
P3 total Delta_AD_W
```

The highest-order interaction is expected to be the limiting estimand. Main-effect power is not an acceptable substitute.

### Simulation-based power requirement

After the dry run supplies dispersion, within-plant correlation, attrition and feasible effect-scale bounds, run simulation-based power over a grid of biologically meaningful effect sizes.

Freeze:

```text
candidate n plants
flowers per plant per cell or allocation scheme
dispersion / zero inflation if present
plant-level random-effect variance
cell-specific attrition pattern
registered minimum meaningful four-way magnitude
registered four-way separability tolerance
registered minimum meaningful allocation-face magnitude
```

Choose the smallest design meeting the preregistered P1 criterion while retaining sufficient power/precision for P2. Do not compute sample size from a simple independent-cell ANOVA if the final design is blocked/hierarchical.

The current pre-dry-run envelopes are documented separately:

```text
PEDICULARIS_FOURWAY_SENSITIVITY_GRID_V1.md
PEDICULARIS_PARTIAL_DATA_POWER_ENVELOPE_V1.md
```

The complete-case envelope is a conservative feasibility bound. The partial-data hierarchical envelope is the preferred pre-dry-run approximation.

## Promotion states

```text
TECHNICALLY_QUALIFIED
= Q1/Q2/Q3 pass
+ all 16 assigned treatment combinations preserve factor states
+ leakage equivalence passes

POWER_QUALIFIED
= technically qualified
+ final dry-run-informed hierarchical simulation meets P1/P2 target

MECHANISM_ALLOCATION_ELIGIBLE
= powered experiment completed
+ selective interventions remain valid
+ separability criterion passes
+ remaining-channel assay agrees sufficiently for any biological label
```

If separability fails, the experiment still yields a strong result: mechanism allocation is context-dependent and only partially identified.

## Cross-paper handoff

```text
SCH      supplies identified conflict prerequisite where supported
BALANCE  supplies direct shared-vs-accessible worldline comparison
BITA     supplies interaction-to-mechanism allocation test
SLK      may transport independently identified L/R/K/Phi quantities
```

No dry-run or BITA residual is promoted automatically into SLK architecture cost.
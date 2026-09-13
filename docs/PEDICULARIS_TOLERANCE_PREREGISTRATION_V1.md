# Pedicularis protected-endpoint tolerance preregistration v1

## Purpose

Define raw-unit equivalence margins for Q1/Q3 manipulation selectivity before formal qualification data are inspected.

The tolerance is not a statistical artifact and is not chosen to make the pilot pass. For each protected endpoint Y, freeze three ingredients from Stage-0 untreated data and biological reasoning:

```text
ME_Y   = repeat-measurement error scale in raw units
NV_Y   = untreated short-interval natural variability scale in raw units
BN_Y   = largest biologically negligible change in raw units
```

The registered equivalence margin is

```text
delta_Y = max(ME_Y, NV_Y_floor) subject to delta_Y <= BN_Y
```

where `NV_Y_floor` is a prospectively declared fraction of untreated short-interval variation used to avoid defining a tolerance narrower than the measurement process can resolve.

If `max(ME_Y, NV_Y_floor) > BN_Y`, the endpoint is **not qualification-resolvable** under the current measurement protocol. Do not widen BN_Y after seeing treatment effects; improve the measurement protocol or reject that manipulation route.

## Endpoint classes

### Geometry endpoints

```text
realized_exsertion_mm
corolla_aperture_mm
flower_orientation_deg
```

BN must be justified from the smallest change likely to alter pollinator approach/handling or predator access in a biologically meaningful way. Measurement repeatability is assessed from repeated image/physical measurements of untreated flowers over the qualification interval.

### Water-defence endpoints

```text
bract_water_volume_uL
bract_water_state
```

For Q1, any off-target effect on D must remain comfortably below the registered low/high D contrast. A default governance rule is:

```text
delta_water <= 0.20 * registered_D_contrast
```

unless a stricter biological bound is justified. This 20% rule is a preregistration ceiling, not an empirical claim about Pedicularis.

### Floral condition endpoints

```text
flower_longevity_hours
visible_damage_score
nectar_volume_uL
```

BN is defined relative to the smallest change that could plausibly modify the common reproductive-fitness pathway. Damage uses an ordinal admissibility rule rather than pretending the score is continuous if that is not defensible.

### Pollinator endpoints for Q3

```text
pollinator_access_validated
pollinator_visitation_rate
legitimate_handling_time_or_success
```

For binary access state, any systematic loss of accessibility caused by E_G is a failure. For visitation/handling rates, use a raw or log-ratio margin justified from repeat-day variation and the smallest change that would alter pollen delivery enough to threaten channel selectivity.

### Predator-state endpoints

```text
predator_access_validated
oviposition_or_attack_rate
```

These are intended-effect endpoints for E_G, not protected off-target endpoints. Qualification requires a minimum efficacy threshold as well as selectivity. Freeze `eta_G`, the minimum acceptable reduction in predator attack/oviposition, before formal qualification.

## Direction-specific margins

Symmetric ±delta margins are allowed only when increases and decreases of the endpoint are equally harmful for identification. Otherwise register asymmetric bounds:

```text
[-delta_minus, +delta_plus]
```

Examples include nectar or longevity if only reductions threaten manipulation validity.

## Margin freeze table

Before Stage-B formal qualification, complete one row per protected endpoint:

| endpoint | raw unit | repeatability estimate | untreated short-term variation | BN rationale | registered lower bound | registered upper bound | resolvable? |
|---|---|---:|---:|---|---:|---:|---|

No row may be completed using reproductive-outcome contrasts from the formal qualification experiment.

## Multiplicity governance

Q1 or Q3 passes only if **all mandatory protected endpoints** pass their registered equivalence criteria and the intended factor achieves its minimum efficacy threshold. Do not rescue a failed endpoint by averaging it with successful endpoints.

Optional exploratory endpoints do not block qualification unless promoted to mandatory status before formal Stage-B data are opened.

## Q1-specific hierarchy

Mandatory minimum:

```text
A efficacy: realized_exsertion separation >= eta_A
D protection: bract water within registered margin
geometry protection: aperture/orientation within margin unless part of A definition
condition protection: damage and longevity within margin
```

Nectar is mandatory if Stage-A shows the manipulation could contact or compress reward structures; otherwise it may remain secondary.

## Q3-specific hierarchy

Mandatory minimum:

```text
E_G efficacy: predator attack/oviposition reduction >= eta_G
pollinator access preserved
A preserved
D preserved
damage and longevity preserved
```

Visitation/handling becomes mandatory when the E_G method is physically visible to legitimate pollinators or lies in their approach/handling path.

## Promotion rule

For endpoint Y with registered interval [L_Y, U_Y], promote equivalence only when the chosen confidence interval for the manipulation contrast is wholly contained in that interval.

```text
CI_Y subset [L_Y, U_Y]
```

The confidence level and interval method are frozen with the analysis plan. Conventional non-significance is not a substitute.

## Stop rule

If a biologically defensible BN is narrower than what the measurement protocol can resolve, do not manufacture a larger tolerance. Improve measurement precision, redesign the manipulation, or mark the system/method as not qualification-resolvable.

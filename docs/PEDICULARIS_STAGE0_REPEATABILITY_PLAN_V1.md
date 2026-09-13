# Pedicularis Stage-0 repeatability and natural-variation plan v1

## Purpose

Stage 0 exists only to make the later Q1/Q3 equivalence margins empirically resolvable in raw units before treatment outcomes are inspected.

It estimates three distinct quantities for every protected endpoint:

```text
ME = short-interval measurement error / repeatability noise
NV = untreated short-term biological variation over the qualification window
BN = prospectively justified biologically negligible change
```

ME and NV are empirical. BN is biological/governance judgement supported by measurement scale and functional interpretation. BN must not be inferred from treatment effects.

## Sampling frame

Use untreated flowers from the same population-season and developmental window intended for Q1/Q3 qualification.

Recommended initial frame:

```text
20-30 plants
1-2 focal flowers per plant
2 operators when feasible
3 measurement occasions per flower
```

This is not a fixed final n. Increase Stage-0 replication if ME or NV estimates remain too imprecise to determine whether an endpoint is qualification-resolvable.

## Timing

For morphology/state endpoints:

```text
t0      baseline measurement
+t_short repeat measurement after handling-only interval
+t_field repeat over the shortest interval matching the intended Q1/Q3 validation window
```

For dynamic endpoints such as nectar or visitation, use repeated standardized observation windows rather than pretending one snapshot has the same meaning as morphology.

## Protected endpoints

### Q1 A-manipulation protection set

```text
bract_water_volume_or_state
corolla_aperture
flower_orientation
visible_damage
flower_longevity
nectar_volume where feasible
```

### Q3 antagonist-intervention protection set

```text
realized_exsertion_mm
bract_water_volume_or_state
corolla_aperture
flower_orientation
flower_longevity
pollinator_access
pollinator_visitation_or_handling
visible_damage
```

## Estimation rules

### Measurement error ME

Estimate from repeated measurements taken close enough in time that genuine biological change is negligible relative to the measurement scale.

For continuous endpoints use the SD of paired repeat differences, reported in raw units. Keep operator identity so operator-specific bias can be checked.

For categorical/binary validation states, record disagreement probability rather than forcing an SD interpretation.

### Natural variation NV

Estimate untreated within-flower or matched-flower change across the actual qualification interval.

Do not combine between-plant heterogeneity with short-term within-unit variation when the later equivalence test is paired/blocked.

Report at minimum:

```text
paired-difference SD
median absolute change
90th percentile absolute change
```

### Biologically negligible change BN

Freeze BN separately for each endpoint before Q1/Q3 treatment effects are inspected.

BN must be written in raw units and accompanied by a short biological rationale. Examples of acceptable rationale types are:

```text
change smaller than normal handling variation and below a morphology threshold relevant to pollinator access
change too small to alter the registered D state
change below a predeclared fraction of the intended focal contrast
change below temporal variation that is functionally negligible over one flower lifetime
```

Do not justify BN by saying that a treatment difference was non-significant.

## Resolvability gate

For each endpoint define a conservative empirical floor from ME and NV. The exact summary must be preregistered; default:

```text
empirical_floor = max(ME_90_or_equivalent, NV_floor)
```

An endpoint is qualification-resolvable only if:

```text
empirical_floor < BN
```

If not, do not widen BN merely to obtain a pass. Improve the measurement protocol, shorten/standardize the interval, or reject the manipulation platform for that endpoint.

## Tolerance freeze

For a resolvable endpoint, freeze equivalence margin delta in raw units such that:

```text
empirical_floor <= delta <= BN
```

Prefer the smallest delta that remains above the measurement/natural-variation floor and can be estimated with feasible precision.

For A leakage onto D, retain the governance ceiling already registered in the tolerance document: the permitted water-state perturbation may not exceed 20% of the intended D contrast unless a stricter biologically justified BN is smaller.

## Stage-0 receipt

For every endpoint freeze:

```text
endpoint_id
unit
measurement protocol
operator protocol
repeat interval
ME estimate
NV estimate
BN rationale
BN raw value
chosen delta
qualification_resolvable true/false
required paired n for formal equivalence
```

No Q1/Q3 formal qualification begins until every mandatory protected endpoint is either resolvable with a frozen delta or explicitly declared unavailable, in which case the corresponding manipulation cannot be execution-qualified.

## Stop rules

```text
mandatory endpoint unresolved after protocol improvement
    -> Q1 or Q3 remains OPEN/FAIL

all mandatory endpoints resolvable and margins frozen
    -> proceed to Stage A mechanical screen
```

Stage 0 contains no BITA mechanism claim and no reproductive-outcome promotion.
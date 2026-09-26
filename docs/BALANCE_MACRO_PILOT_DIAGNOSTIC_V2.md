# BALANCE macro pilot diagnostic v2 — after coverage repair

## Status

This document supersedes the **current-count** portions of `BALANCE_MACRO_PILOT_DIAGNOSTIC_V1.md` while preserving V1 as the record of the initial bottleneck.

All rows remain pilot-screening candidates. No confirmatory association is estimated here.

## Current screened universe

```text
55 systems

plant_reproductive   25
animal_morphology    16
molecular_gene       14
```

Conflict status:

```text
POSITIVE                  32
NO_DEMONSTRATED_CONFLICT  11
ALIGNED_NO_CONFLICT        1
UNRESOLVED                11
```

Architecture state:

```text
SHARED_INTEGRATED                    24
REGULATORY_TEMPORAL_SEPARATION        2
SPATIAL_COMPARTMENTALIZATION          6
PARTIAL_STRUCTURAL_DIFFERENTIATION   11
SEPARATE_MODULES                      8
POLYMORPHIC                           1
UNRESOLVED                            3
```

Whole-screen structural outcome:

```text
false       32
true        19
unresolved   4
```

## Logical primary candidates before adjudication

The purely logical screen

```text
conflict_status == POSITIVE
and
structural_differentiation in {true,false}
```

now yields 31 candidates.

```text
domain                nonstructural   structural   total
plant_reproductive          8             5         13
animal_morphology           6             5         11
molecular_gene              3             4          7
TOTAL                      17            14         31
```

This substantially repairs the initial domain-by-outcome bottleneck recorded in V1.

It does **not** license a model: coverage repair deliberately searched for missing outcome classes and is therefore unsuitable as a confirmatory denominator.

## Why the repair matters

The pilot now demonstrates that the architecture codebook is capable of representing both outcomes in every broad domain.

Examples newly added to the structural side include:

### Plants

- `Pulsatilla alpina`: unisexual male flowers as modular resolution of male-female sexual conflict;
- `Cyananthus delavayi`: sexual conflict over male/female phase duration associated with gynodioecy;
- `Senna` heteranthery: differentiated feeding and pollinating stamen roles;
- `Melastoma candidum`: dimorphic stamen division of labour.

### Animals

- cichlid oral/pharyngeal jaw partition, now coded as conflict-positive at pilot level because a single-jaw system faces force/mobility and capture/processing constraints;
- fiddler-crab paired-claw specialization, recoded from a shared major-claw signal/weapon example to the more relevant feeding-versus-sexual-function module split;
- `Callinectes` crusher/cutter heterochely;
- Coleoptera forewing/hindwing functional partition.

These rows remain `SCREENED`, not `ADJUDICATED`.

## Predictor observability after repair

First-pass categories:

```text
conflict strength:
  HIGH        19
  MEDIUM       4
  UNRESOLVED  31
  NA           1

alternative accessibility:
  HIGH        24
  MEDIUM       3
  LOW          3
  UNRESOLVED  24
  NA           1

functional coupling:
  HIGH        11
  MEDIUM      23
  UNRESOLVED  21

temporal heterogeneity:
  HIGH         6
  UNRESOLVED  49

spatial heterogeneity:
  HIGH        11
  UNRESOLVED  44

alternative repertoire:
  ONE         19
  MULTIPLE     5
  UNRESOLVED  31
```

## New primary design risk — circular predictor coding

Outcome balance is no longer the main pilot failure.

The main risk is now:

```text
observed differentiation
-> coder infers "architecture was accessible"
-> H1 mechanically appears true
```

or:

```text
persistent integration
-> coder infers "functions are strongly coupled"
-> H2 mechanically appears true.
```

That is not acceptable.

The next gate is therefore an **outcome-independent predictor receipt**.

No row may become primary-model eligible merely because its predictor values look plausible.

## Revised near-term model hierarchy

### Primary candidate predictors

Retain:

```text
alternative_accessibility
functional_coupling
```

only after independent evidence receipts pass the non-circularity audit.

### Secondary / targeted subset

```text
temporal_heterogeneity
spatial_heterogeneity
alternative_repertoire
conflict_strength_proxy
```

These remain important biologically but lack adequate current coverage or harmonization.

### H5

The principle

```text
conflict != automatic differentiation
```

remains central.

A numerical conflict-strength × accessibility test is postponed until conflict strength can be harmonized without converting incomparable experiments into an arbitrary score.

## Coverage-repair stopping rule

The pilot coverage objective is now met:

```text
>=5 screened structural-differentiation candidates
in plant_reproductive and animal_morphology,
with molecular_gene also containing both outcomes.
```

Do not keep outcome-targeted searching merely to balance the table further.

The next discovery effort should return to an outcome-blind systematic sampling frame.

## Next gates

1. freeze non-circular coding rules for H1/H2;
2. attach predictor-specific evidence receipts independent of the outcome where possible;
3. double-code a pilot subset;
4. quantify coder agreement;
5. draft the outcome-blind confirmatory search frame;
6. only then decide whether a cross-domain hierarchical model is defensible or whether the primary result should be stratified by domain.

## Current conclusion

The pilot question is feasible.

The initial problem was insufficient differentiated plant/animal coverage. That has been repaired for codebook stress testing.

The scientifically harder problem is now the correct one:

> Can the proposed predictors be measured independently of the architecture state they are supposed to explain?

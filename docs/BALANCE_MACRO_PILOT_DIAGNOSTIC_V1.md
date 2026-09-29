# BALANCE macro pilot diagnostic v1

## Scope

This diagnostic summarizes the first-pass `BALANCE_MACRO_PILOT_LEDGER_V1.csv`.

The rows are **screened discovery candidates**, not adjudicated confirmatory data. No inferential model is licensed from these counts.

## First-pass universe

The pilot currently contains:

```text
49 screened systems
21 plant reproductive / attraction systems
14 animal morphology systems
14 molecular / gene-architecture systems
```

Conflict screen:

```text
POSITIVE                  25
NO_DEMONSTRATED_CONFLICT  11
ALIGNED_NO_CONFLICT        1
UNRESOLVED                12
```

Architecture state:

```text
SHARED_INTEGRATED                    25
REGULATORY_TEMPORAL_SEPARATION        2
SPATIAL_COMPARTMENTALIZATION          6
PARTIAL_STRUCTURAL_DIFFERENTIATION    5
SEPARATE_MODULES                      7
POLYMORPHIC                           1
UNRESOLVED                            3
```

Binary structural outcome across the whole screened set:

```text
false       33
true        12
unresolved   4
```

## Candidate primary subset before adjudication

Applying only the logical preconditions

```text
conflict_status == POSITIVE
and
structural_differentiation in {true,false}
```

yields 24 candidate rows.

They are **not** marked `primary_model_eligible`; every current pilot row remains `SCREENED` and `primary_model_eligible=false`.

Candidate composition:

```text
domain                shared/nonstructural   structural   total
plant_reproductive             8                 1          9
animal_morphology              7                 1          8
molecular_gene                 3                 4          7
TOTAL                         18                 6         24
```

## Main pilot failure revealed

The first-pass primary subset has a strong domain-outcome imbalance.

Structural differentiation is currently concentrated in molecular/gene systems, whereas plant and animal discovery has so far recovered mostly shared or nonstructurally partitioned systems.

Therefore the following model is **not yet licensed**:

```text
structural differentiation ~ predictors + domain
```

because architecture outcome and domain are too close to confounded in the current discovery set.

The next search round must preferentially seek:

1. independent plant systems with structural division of labour;
2. independent animal systems with serial-homolog or module specialization;
3. matched shared/integrated comparators within the same broad clades where possible.

This is targeted **coverage repair**, not outcome-conditioned inclusion into the final denominator. The confirmatory search frame must still retain all eligible screened systems.

## Predictor coverage

First-pass resolved/non-NA coverage:

```text
conflict strength proxy       16 / 49 clearly resolved + 1 medium
alternative accessibility     23 / 49 resolved
functional coupling           28 / 49 resolved
temporal heterogeneity         4 / 49 resolved
spatial heterogeneity         10 / 49 resolved
alternative repertoire        17 / 49 resolved
```

### Consequence for H1

Architecture accessibility is measurable in enough high-information cases to remain a primary pilot hypothesis, but requires independent recoding to ensure it is not inferred circularly from the observed differentiated state.

### Consequence for H2

Functional coupling also remains measurable enough for pilot development. A domain-specific coding rubric is required because molecular coupling and organismal mechanical coupling are not automatically commensurate.

### Consequence for H3

Temporal heterogeneity is missing in 45/49 first-pass rows.

Therefore H3 should remain biologically motivated but **secondary / targeted-subsample** until a dedicated temporal-regime extraction pass demonstrates adequate coverage.

It should not be forced into the first confirmatory cross-domain model merely because it was theoretically attractive.

### Consequence for H4

Alternative-repertoire count is unresolved in 32/49 rows and is highly vulnerable to study effort.

H4 remains secondary until:

- candidate-alternative search effort is standardized;
- source count / study intensity is included;
- the accessibility registry is coded independently of outcome.

### Consequence for H5

Conflict strength is too inconsistently quantified for the present interaction model.

The qualitative claim

```text
conflict != automatic differentiation
```

remains central, but a confirmatory `conflict_strength x accessibility` interaction requires a separate harmonization pass. Do not manufacture a pseudo-continuous conflict-strength score from incomparable source designs.

## Strongest current comparative axis

The most defensible near-term cross-system contrast is:

```text
given adjudicated conflict:
shared / regulatory / spatial persistence
versus
structural division of labour
```

with primary predictors:

```text
architecture accessibility
functional coupling
```

and domain/taxonomic structure treated explicitly rather than pooled away.

## Immediate search repair targets

### Plants

Prioritize repeated origins of structural division of labour such as:

- heteranthery beyond the existing *Solanum rostratum* seed;
- other floral module specialization where the two functions and ancestral/shared comparator are explicit;
- mixed/shared versus structurally partitioned reproductive architectures only when the functional conflict is independently documented.

### Animals

Prioritize:

- independent heterochelous crustacean lineages;
- feeding-module decoupling beyond the current cichlid anchor;
- serial homolog specialization where an integrated/shared comparator exists.

### Molecular systems

Do **not** keep expanding molecular examples merely because they are easy to code. The molecular stratum already supplies both shared-generalist and duplicated-specialist outcomes and should now serve mainly as a calibration stratum.

## Promotion rule

Do not fit the confirmatory macro model until all of the following hold:

1. >= 2 independently adjudicated structural-differentiation systems in each retained broad domain, preferably >= 5;
2. primary predictors are resolved for a majority of candidate primary rows;
3. predictor definitions pass non-circularity audit;
4. domain-specific sensitivity models can be fit without perfect or near-perfect separation;
5. the full screened denominator and exclusion flow are frozen.

## Current conclusion

The pilot already demonstrates feasibility of the comparative question but also reveals a design problem early enough to fix it:

> the biggest current risk is not lack of examples; it is **domain-by-outcome confounding plus uneven predictor observability**.

That is exactly what the pilot was intended to diagnose.

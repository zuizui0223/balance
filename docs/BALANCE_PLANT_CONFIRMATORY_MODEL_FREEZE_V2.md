# BALANCE plant confirmatory model freeze v2

> **Superseded before architecture coding by v3.** V2 solved the raw-category parameter-budget problem, but the pre-outcome U2+U6 predictor-support audit found only one `DISTRIBUTED` spatial-exposure dependence group. V3 retains spatial coding as a secondary axis and removes it from the primary joint fixed-effect model. See `docs/BALANCE_PLANT_CONFIRMATORY_MODEL_FREEZE_V3.md`.

## Status

Frozen before U6 independent architecture coding and before any confirmatory plant model fit.

This version supersedes the **model parameterization** in v1. It does not change:

- the four-class primary architecture response;
- the raw predictor codebook;
- the independent-coder requirement;
- the outcome-independent predictor-receipt requirement;
- the no-post-hoc-response-recoding rule.

The revision is driven by an outcome-blind parameter-budget audit.

## Why v1 was too large

The v1 joint multinomial used the raw categories:

```text
module_substrate             5 resolved levels -> 4 df
conflict_timing_geometry     5 resolved levels -> 4 df
conflict_spatial_geometry    6 resolved levels -> 5 df
intercept                                      -> 1
```

For a four-class multinomial response there are three non-reference logits.

Therefore, even **before** adding conflict family:

```text
14 columns/logit x 3 logits = 42 fixed-effect coefficients
```

The prospective conflict-positive plant surface is measured in tens of biological
dependency groups, not hundreds. A 42+ coefficient primary model would turn sparse cell
patterns into unstable coefficients.

This is a design problem visible before outcomes are coded. It is not a response to a null
or inconvenient result.

## Response remains unchanged

```text
SHARED
NONSTRUCTURAL_SEPARATION
STRUCTURAL_MODULE_DIVISION
MOSAIC
```

Raw `architecture_mode` remains archived and auditable.

## Raw predictors remain unchanged

Coders still assign the full source-level categories.

### module_substrate

```text
SINGLE_OR_CONTINUOUS
SERIAL_WITHIN_FLOWER
REPEATED_FLOWERS
PREEXISTING_SEPARATE_ORGANS
MULTILEVEL
```

### conflict_timing_geometry

```text
SIMULTANEOUS
SEQUENTIAL_WITHIN_UNIT
SEASONALLY_ALTERNATING
CONTEXT_DEPENDENT
MIXED
```

### conflict_spatial_geometry

```text
SAME_UNIT
BETWEEN_MODULES
AMONG_INDIVIDUALS
AMONG_POPULATIONS
ENVIRONMENTAL_MOSAIC
MIXED
```

The reduction happens **after** independent coding and independent predictor licensing.

## Frozen primary contrasts

### 1. Module opportunity

```text
SINGLE
  SINGLE_OR_CONTINUOUS

MODULAR
  SERIAL_WITHIN_FLOWER
  REPEATED_FLOWERS
  PREEXISTING_SEPARATE_ORGANS
  MULTILEVEL
```

Biological question:

> does having more than one independently addressable conflict-bearing unit alter routing?

### 2. Temporal exposure

```text
SIMULTANEOUS
  SIMULTANEOUS

ORDERED_OR_ALTERNATING
  SEQUENTIAL_WITHIN_UNIT
  SEASONALLY_ALTERNATING

VARIABLE_CONTEXT
  CONTEXT_DEPENDENT
  MIXED
```

This grouping does not claim that context dependence is an evolutionary time series.
It distinguishes a fixed simultaneous exposure, a consistently ordered/alternating
exposure, and an exposure whose timing changes among contexts or combines modes.

### 3. Spatial exposure

```text
SAME_UNIT
  SAME_UNIT

DISTRIBUTED
  BETWEEN_MODULES
  AMONG_INDIVIDUALS
  AMONG_POPULATIONS
  ENVIRONMENTAL_MOSAIC
  MIXED
```

Biological question:

> is conflict localized to one unit or distributed across separable biological units or
> contexts?

## Parameter budget

Main model:

```text
intercept                    1
module_opportunity2          1
temporal_exposure3           2
spatial_exposure2            1
------------------------------
columns per logit            5

5 x 3 non-reference logits = 15 fixed-effect coefficients
```

Registered interaction extensions:

```text
module x timing   7 columns/logit -> 21 coefficients
module x spatial  6 columns/logit -> 18 coefficients
```

This does not make sparse data magically informative. It removes avoidable categorical
fragmentation before outcomes are known.

## Primary model

```text
regularized Bayesian multinomial logit

architecture_class4
~ module_opportunity2
+ temporal_exposure3
+ spatial_exposure2
```

Reference response:

```text
SHARED
```

Registered priors:

```text
slope coefficients:
  Normal(0, 0.75)

non-reference intercepts:
  Normal(0, 1.5)
```

Prior sensitivity:

```text
slope coefficients:
  Normal(0, 1.5)
```

Results are reported primarily as predicted probabilities and probability contrasts, not as
a table of log-odds coefficients.

## Why conflict_family is not a primary fixed effect

Conflict family is strongly coupled to the literature universe:

- U2 is enriched for sexual interference;
- U6 is explicitly a pollen-theft / pollen-fate conflict universe;
- U1 is a broad antagonist-pollinator screen.

Adding family as another sparse categorical fixed effect would both consume degrees of
freedom and risk pretending that family and sampling frame are cleanly separable.

Instead, the following sensitivities are mandatory:

1. report response and predictor support by `conflict_family`;
2. leave one sampling universe out where at least two informative universes remain;
3. estimate within-family probability contrasts only where empirical overlap supports them;
4. do not describe a pooled contrast as family-independent when predictor support is
   segregated by family.

This is a claim ceiling, not a method for removing all confounding.

## Estimability gate

The primary model is not fit merely because all data-entry gates close.

Before fitting:

```text
>= 2 independent dependence blocks in every one of the four response classes

every primary predictor contrast has >= 2 observed levels

primary design matrix has full rank
```

For each reported probability contrast, there must be empirical support for both sides of
the contrast. Unsupported contrasts are labelled `NON_ESTIMABLE`; they are not obtained
by extrapolating into an empty cell.

If the gate fails:

```text
DO_NOT_FIT_OR_DROP_TERMS_POST_HOC
```

The response remains four-class and the result is an estimability limitation.

## Primary planned probability contrasts

1. module opportunity:

```text
P(STRUCTURAL_MODULE_DIVISION | MODULAR)
-
P(STRUCTURAL_MODULE_DIVISION | SINGLE)
```

2. temporal exposure:

```text
P(NONSTRUCTURAL_SEPARATION | ORDERED_OR_ALTERNATING)
-
P(NONSTRUCTURAL_SEPARATION | SIMULTANEOUS)
```

3. spatial exposure:

```text
P(MOSAIC | DISTRIBUTED)
-
P(MOSAIC | SAME_UNIT)
```

These are population-standardized over the observed support of the other primary predictors.

## Registered interactions

### I1 — module x timing

```text
architecture_class4
~ module_opportunity2 * temporal_exposure3
+ spatial_exposure2
```

Fit only after the main model and only where the interaction cells required for a reported
contrast have empirical support.

### I2 — module x spatial

```text
architecture_class4
~ module_opportunity2 * spatial_exposure2
+ temporal_exposure3
```

Same support rule.

Neither interaction is selected because it gives a stronger result.

## Raw-category analyses are secondary

The full raw categories remain scientifically useful for:

- support tables;
- descriptive architecture maps;
- diagnosing whether the coarse contrast hides qualitatively different systems;
- regularized secondary models when the final sample actually supports them.

They cannot replace v2 as the primary fit merely because a raw-category coefficient is
interesting.

## Claim ceiling

Even a successful v2 fit licenses comparative association within the frozen screened
literature surfaces.

It does not identify:

- evolutionary transition probabilities;
- causality of architecture origin;
- natural prevalence across angiosperms;
- theoretical `R`, `K`, `Phi`, `rho`, `xi`, or `d_B`.

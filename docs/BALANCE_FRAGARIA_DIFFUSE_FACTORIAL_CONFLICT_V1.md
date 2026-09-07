# BALANCE Fragaria diffuse factorial conflict v1

## Question

Can a shared plant display trait be pulled in opposite directions by pollinators and herbivores while the strength of each selective force depends on the ecological state of the other agent?

This is a stricter object than a simple two-gradient conflict because the agent-mediated selection coefficients are themselves context dependent.

## Primary source

Egan PA, Muola A, Parachnowitsch AL, Stenberg JA. 2021. `Pollinators and herbivores interactively shape selection on strawberry defence and attraction.` Evolution Letters 5:636-643. DOI `10.1002/evl3.262`.

Public data: Dryad DOI `10.5061/dryad.1rn8pk0vn`.

Supplementary material includes Table S2 with selection-gradient estimates underlying the mediated-selection contrasts.

## Experimental design

The study used woodland strawberry `Fragaria vesca` in a common garden.

The two selective-agent manipulations were crossed factorially:

```text
pollination
  open
  supplemental hand pollination

herbivory
  herbivore addition
  herbivore removal
```

The experiment therefore generated four treatment combinations.

Herbivory was manipulated primarily with the strawberry leaf beetle `Galerucella tenella`; herbivore-removal plots received insecticide treatment and addition plots received water controls.

The common downstream female-fitness endpoint was total fertilized seed output per plant.

## Trait coordinate

The strongest BALANCE-relevant shared trait is:

```text
z = inflorescence density
    number of flowers per unit plant volume
```

The biological interpretation is unusually clean for a pattern-level conflict:

- denser floral displays can increase attractiveness or within-inflorescence movement of pollinators;
- the same dense display can also serve as a host-location / use cue for florivorous herbivores.

Thus one visible architecture coordinate is used by a mutualist and an antagonist.

## Selection analysis

The source standardized traits and relative fitness and estimated multivariate directional selection gradients `beta`.

The fitted model included:

```text
trait effects
pollination treatment
herbivory treatment
pollination x herbivory
trait x treatment interactions
```

Differences among fitness-trait slopes were then evaluated with `emmeans::emtrends` to recover:

```text
pollinator-mediated selection | herbivores present
pollinator-mediated selection | herbivores absent
herbivore-mediated selection  | pollen limited
herbivore-mediated selection  | pollen supplemented
combined pollinator + herbivore mediated selection
```

This is important for BALANCE because the paper does not force one agent effect to be invariant to the other agent.

## Recovered conflict

For inflorescence density:

```text
pollinator-mediated selection   positive
herbivore-mediated selection    negative
```

The two agents therefore pull the same trait coordinate in opposite directions.

The source additionally reports that the agent-mediated effects are **diffuse**: selection imposed by one agent is detected in one state of the other agent and not both states.

The combined opposing effects neutralize net selection on inflorescence density in the focal experiment.

This is a high-value real-world signature of a shared coordinate maintained under opposing functional demands.

## Why this is not a direct BALANCE receipt

The experiment identifies conflict on one shared trait but does not construct and optimize an explicit differentiated architecture worldline.

It therefore does not measure:

```text
W_S*  optimized shared architecture fitness
W_D*  optimized differentiated architecture fitness
rho   = W_S* - W_D*
Phi
xi
d_B
```

The correct R-layer admission is:

```text
CONFLICT_WITHOUT_SPLITTING
```

not direct BALANCE occupancy.

## Why this does not enter the simple Q1 bivariate stratum unchanged

The existing `OPPOSING_FLORAL_SELECTION` stratum targets one bivariate within-study object:

```text
(beta_pollinator, beta_antagonist)
```

with joint uncertainty.

Fragaria is more structured. There are at least four context-specific mediated contrasts:

```text
c1 = pollinator-mediated selection | herbivores present
c2 = pollinator-mediated selection | herbivores absent
c3 = herbivore-mediated selection  | pollen limited
c4 = herbivore-mediated selection  | pollen supplemented
```

Collapsing this to one pair by choosing whichever context looks most natural would be outcome-dependent and would discard the main biological result: the effect of each selective agent depends on the other.

Therefore Fragaria is registered in a separate quantitative stratum:

```text
DIFFUSE_FACTORIAL_AGENT_SELECTION
```

## Quantitative promotion gate

The preferred quantitative object is the joint vector:

```text
c = (c1, c2, c3, c4)
```

with the full covariance matrix.

Promotion to `EFFECT_SIZE_READY` requires either:

1. exact Table S2 / model contrast estimates plus their joint covariance from the fitted model; or
2. raw-data reanalysis reproducing the published model and bootstrapping / extracting the full contrast covariance.

The following shortcuts are prohibited:

```text
choose only one convenient pollinator/herbivore contrast pair
count four contrasts as four independent studies
set covariance among contrasts to zero
infer exact numerical coefficients from Figure 1 by eye
replace common fertilized-seed fitness with visitation or herbivore damage
```

## Relationship to Gymnadenia 2015

Both studies use factorial manipulation of pollination and herbivory, but they play different quantitative roles at present.

`Gymnadenia conopsea` 2015 provides a strong opposed-agent example in which flowering-time effects were described as broadly additive and similar in strength.

`Fragaria vesca` 2021 explicitly demonstrates diffuse context dependence of the agent-mediated selection gradients.

They remain independent biological systems. Their effect vectors must not be pooled under one scalar estimand until a common multivariate representation is registered.

## Internal controls

The Fragaria experiment also helps prevent positive-only screening.

Across the other traits:

- pollinator and herbivore effects are not universally opposed;
- some agent-mediated effects appear only in one context;
- total selection can differ from the mediated components.

Therefore the BALANCE signal is trait-specific rather than a blanket property assigned to the species.

## Current status

```text
PRIMARY_SOURCE:                     PEER_REVIEWED_OPEN_ACCESS
RAW_DATA:                           PUBLIC_DRYAD
FULL_FACTORIAL_AGENT_MANIPULATION:  YES
COMMON_FEMALE_FITNESS:              YES
SAME_TRAIT_AGENT_CONFLICT:          RECOVERED
DIFFUSE_CONTEXT_DEPENDENCE:         RECOVERED
R_PATTERN:                          CONFLICT_WITHOUT_SPLITTING
SIMPLE_Q1_BIVARIATE_READY:          NO
Q1B_DIFFUSE_FACTORIAL_CANDIDATE:    YES
FULL_MULTICONTRAST_COVARIANCE:      NOT YET RECOVERED
EFFECT_SIZE_READY:                  NO
DIRECT_BALANCE_RECEIPT:             NO
```

## Claim ceiling

Appropriate:

> A full-factorial Fragaria experiment recovered context-dependent opposing pollinator- and herbivore-mediated selection on the same inflorescence-density coordinate under a common seed-fitness endpoint.

Not appropriate:

> Fragaria directly identifies the BALANCE worldline reserve or already supplies an independent scalar meta-analytic effect without further covariance recovery.

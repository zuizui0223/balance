# BALANCE quantitative synthesis contract v1

## Purpose

Turn the Chapter-2 R layer from an evidence map into quantitative synthesis **without pooling unlike biological or statistical objects**.

The current pattern ledger contains multiple useful signatures, but it deliberately spans observational floral selection, experimental evolution, molecular architecture, comparative morphology, and phylogenetic transitions. A single omnibus meta-analysis would therefore be scientifically invalid.

This contract registers separate quantitative strata before effect extraction.

Machine-readable registry:

```text
data/BALANCE_QUANTITATIVE_STRATA_V1.csv
```

## Global rules

### 1. Pattern recurrence is not an effect size

A row in `BALANCE_PATTERN_LEDGER_V1.csv` contributes to source-adjudicated recurrence at its registered claim ceiling. It does not automatically enter a quantitative pool.

### 2. Cluster is the independence unit

Multiple populations, years, traits, coefficients, or experimental lines from one study/programme are not silently counted as independent literature replications.

Dependence is handled within study by multilevel modelling, a covariance matrix, or a prespecified aggregation rule.

### 3. No covariance-by-convenience

For a contrast involving two estimates from the same plants/study,

```text
Var(a-b) = Var(a) + Var(b) - 2 Cov(a,b).
```

If `Cov(a,b)` is needed and unavailable, do one of the following:

1. recover it from the fitted model / supplementary material;
2. reanalyse raw data and bootstrap or estimate the joint covariance;
3. retain the study in the qualitative/evidence-map layer.

Do **not** set covariance to zero merely because the paper does not report it.

### 4. No coefficient-class mixing

The following are not assumed commensurate:

```text
standardized Lande-Arnold directional gradients
path coefficients
GLM link-scale coefficients
raw slopes
odds ratios
phylogenetic transition rates
architecture fitness differences
```

They may enter one quantitative stratum only after a justified common reanalysis or transformation.

### 5. Do not meta-analyse latent BALANCE parameters from unmatched studies

Cross-study pooling of the following is prohibited unless they arise from directly compatible receipts:

```text
s
K
Phi
rho
xi
d_B
```

The current literature map cannot identify those quantities by analogy.

---

# Q1 — opposing floral selection

## Biological question

Across conflict-active flowering systems, how consistently do pollinators and antagonists impose different directional selection on the **same floral trait coordinate**?

Current high-confidence registered candidates are:

```text
Dalechampia scandens      Perez-Barrales et al. 2013
Castilleja linariaefolia Cariveau et al. 2004
Pedicularis rex           Sun et al. 2016
```

A public-data reanalysis candidate is:

```text
Ipomopsis spp. / hybrids
Campbell et al. 2022
DOI 10.1086/716740
Dryad DOI 10.7280/D1KM49
```

The Ipomopsis study decomposes female seed fitness into seeds initiated during pollination and the proportion escaping seed predation. It is not pre-classified as a positive opposing-selection BALANCE pattern; raw-data reanalysis first determines whether any same trait has compatible opposing directional components.

## Preferred estimand

For study/cluster `i`, retain the bivariate directional-selection vector

```text
theta_i = (beta_P,i, beta_A,i)
```

where:

```text
beta_P = pollinator-mediated directional effect
beta_A = antagonist-mediated directional effect
```

on one biologically defined increasing trait coordinate.

A useful derived contrast is

```text
D_i = beta_P,i - beta_A,i
```

with

```text
Var(D_i)
= Var(beta_P,i)
+ Var(beta_A,i)
- 2 Cov(beta_P,i, beta_A,i).
```

The component estimates remain primary because a large `D_i` does not by itself prove opposite signs.

## Required compatibility

A quantitative Q1 contribution requires:

1. one declared floral trait coordinate within study;
2. pollinator and antagonist effects estimated for that coordinate;
3. a common downstream reproductive-fitness interpretation or a prospectively justified episodic decomposition;
4. uncertainty for both components;
5. within-study covariance, or raw data supporting joint reanalysis/bootstrap;
6. no duplicated counting of populations/years as independent papers.

## Current status

```text
registered high-confidence pattern candidates  3
public-data reanalysis candidates               1
minimum independent clusters for pooling        3
effect-size-ready clusters                       0
pooling status                                   NOT READY
```

The minimum count is a preregistered anti-fragility rule; it does not imply that three heterogeneous estimates are automatically sufficient for a stable random-effects model.

## Planned extraction order

1. recover exact coefficient definitions and uncertainty from `Dalechampia`;
2. recover the `Castilleja` path model and determine whether raw data or a common reanalysis is available;
3. recover `Pedicularis` population/model coefficient details and joint uncertainty;
4. reanalyse the public Ipomopsis dataset under the common estimand where biologically valid;
5. only then determine which subset is actually poolable.

If only two studies can be put on one scale, report them as a quantitative comparison rather than forcing a meta-analysis.

---

# Q2 — direct worldline reserve

Target:

```text
rho(e) = W_S*(e) - W_D*(e).
```

This is the strongest direct BALANCE quantity, but there are currently no empirical direct receipts in the R layer.

Eligibility requires same-context and same-fitness-scale optimized shared and accessible-alternative worldlines with compatible uncertainty.

Current status:

```text
effect-size-ready clusters  0
```

The first candidate remains the final focal Pedicularis Experiment-B route.

---

# Q3 — quantitative boundary threshold

Target:

```text
e* = context at shared -> differentiated architecture crossing.
```

The R layer now has two `BOUNDARY_CROSSING` patterns:

```text
Solanum heteranthery
S. cerevisiae GAP1/PUT4 CNV
```

but neither yields a directly comparable numeric `e*`.

Solanum is a repeated phylogenetic/natural transition; the yeast CNV source compares static and fluctuating regimes rather than a single graded scalar control axis.

Therefore:

```text
pattern boundary clusters      2
numeric threshold-ready        0
pooling status                 NOT READY
```

Do not invent a continuous threshold by numerically coding categorical environments.

---

# Q4 — hysteresis width

Target:

```text
H = e_reverse - e_forward.
```

Eligibility follows Issue #24 and requires forward/reverse architecture thresholds on the same registered control path with uncertainty.

Current status:

```text
empirical hysteresis clusters  0
```

No generic physiological memory, phylogenetic reversal, or population coexistence enters this stratum.

---

# Moderator policy

Moderators are estimated only inside a compatible stratum.

For Q1, the Pedicularis geographic study suggests an especially relevant moderator hypothesis:

```text
pollinator-mediated selection relatively consistent
+
antagonist-mediated selection geographically variable
-> conflict strength / compromise position varies primarily with antagonist pressure.
```

Candidate moderator fields include:

```text
antagonist incidence / predation pressure
pollinator guild / visitation environment
population / site
phenology
abiotic context when biologically linked
```

Do not attach moderators across fundamentally different estimands simply because all examples are called BALANCE-like.

---

# Reporting contract

Every quantitative report must state:

```text
screened pattern clusters
eligible stratum clusters
successfully extracted clusters
excluded-after-extraction clusters + reasons
effect-size definition
within-study dependence handling
heterogeneity model
moderators considered
claim ceiling
```

A failed quantitative stratum is still informative. If coefficients cannot be made commensurate, the correct result is a structured evidence map plus explicit measurement recommendations for future studies, not a synthetic number with unclear meaning.

# BALANCE Caruso floral-selection database re-screen contract v1

## Purpose

Use existing open selection databases to accelerate Chapter-2 quantitative recovery **without inheriting their estimand, pooling decisions, or biological classifications**.

Primary source universe:

```text
Caruso et al. 2019
A meta-analysis of the agents of selection on floral traits
DOI 10.1111/evo.13639
Dryad DOI 10.5061/dryad.2v8c5g0
```

Dryad provides:

```text
Exp_stud_NOTdup_Dryad.xls
Exp_stud_dup_Dryad.xlsx
```

The non-duplicated file is the source-of-truth inventory. The duplicated workbook exists to reproduce the original manuscript's pair construction and is never counted as additional evidence.

The public database contains 755 directional selection-gradient records with associated standard errors from 36 articles, 35 species and 15 families. The original paper constructed 487 same-trait / same-fitness-component treatment pairs.

## Why the original meta-analysis is not the BALANCE analysis

Caruso et al. primarily quantified the magnitude of treatment-induced changes in directional selection, including an absolute contrast of the form

```text
|beta_i - beta_j|.
```

That is appropriate for asking how strongly different agents alter selection.

BALANCE instead asks whether multiple functions or agents pull the **same trait coordinate in incompatible directions**, and later whether a shared architecture persists or loses to a differentiated alternative.

Therefore:

```text
published Caruso mean effect
!= BALANCE conflict effect
```

The public database is used as a search universe only.

---

# Stage A — immutable source inventory

Before inspecting which records look positive, freeze:

```text
source file = Exp_stud_NOTdup_Dryad.xls
source DOI
file identity / checksum when locally acquired
column mapping
row count
article count
experiment / population identifiers
```

If file bytes are acquired manually rather than programmatically, the same inventory fields apply. The scientific result must not depend on the download route.

`Exp_stud_dup_Dryad.xlsx` is tagged `DEPENDENCE_AUDIT_ONLY`.

## Canonical source registry

See:

```text
data/BALANCE_QUANT_SOURCE_REGISTRY_V1.csv
```

This also registers the broader Caruso et al. 2017 experimental-selection CSV database as a fallback search universe and public raw-data candidates for Ipomopsis and Gymnadenia.

---

# Stage B — canonical agent-pair screening schema

A source can contribute to the focal floral-conflict stratum only after it is rewritten into a source-level canonical record containing:

```text
study / experiment identity
system / taxon
one biologically defined trait coordinate
pollinator component status
second-agent biological type
second-agent identity confidence
same-trait status
fitness-component compatibility
directional relationship
raw-data availability
joint uncertainty / covariance status
screening class
```

See the seeded ledger:

```text
data/BALANCE_AGENT_PAIR_SCREENING_V1.csv
```

## Screening classes

Allowed primary classes are:

```text
OPPOSED_AGENT_PAIR
ALIGNED_AGENT_PAIR
ONE_AGENT_NULL_OR_UNRESOLVED
AGENT_IDENTITY_UNRESOLVED_CONFLICT
NON_ANTAGONIST_OTHER_BIOTIC
ABIOTIC_MODERATOR
NOT_SAME_TRAIT_OR_FITNESS_COMPONENT
DEPENDENT_DUPLICATE
SOURCE_REANALYSIS_REQUIRED
```

The class is assigned from direction and biological identity before looking at whether adding the source would improve a pooled estimate.

---

# Stage C — split Caruso's `other biotic` category

The original paper's `other biotic` category includes biologically different manipulations such as herbivory, conspecific density and heterospecific presence.

BALANCE must recover the primary paper and classify the manipulated agent explicitly:

```text
florivore / herbivore
seed predator
predator modifying pollinator behaviour
conspecific competitor
heterospecific competitor
other identified biotic factor
unresolved
```

Do not infer `antagonist` merely from the database-level label `other biotic`.

This is especially important because competitive context can alter selection without representing the shared pollinator-versus-antagonist architecture question.

---

# Stage D — directional conflict rule

For a candidate same-trait pair, preserve the signed estimates.

The focal Q1 object is eventually

```text
theta_i = (beta_P,i, beta_A,i)
```

and optionally

```text
D_i = beta_P,i - beta_A,i.
```

An `OPPOSED_AGENT_PAIR` requires biological and directional opposition; a large absolute difference is insufficient.

Examples:

```text
beta_P > 0 and beta_A < 0  -> possible opposed pair
beta_P < 0 and beta_A > 0  -> possible opposed pair
beta_P > 0 and beta_A > 0  -> aligned even if magnitudes differ greatly
one component approximately zero -> unresolved / boundary unless stronger evidence exists
```

Statistical promotion rules are applied after the source-level biological classification. The ledger should retain estimates and intervals even when signs are uncertain.

---

# Stage E — effect-size readiness

A biologically valid opposed pair is **not yet meta-analysis ready**.

Readiness additionally requires compatible uncertainty. For a derived within-study contrast:

```text
Var(D_i)
= Var(beta_P,i)
+ Var(beta_A,i)
- 2 Cov(beta_P,i,beta_A,i).
```

If covariance is unavailable:

1. recover it from the original fitted model;
2. recover raw data and jointly reanalyse/bootstrap;
3. keep the study in the evidence map.

Never replace missing covariance by zero for convenience.

Path coefficients, GLM link-scale coefficients and variance-standardized selection gradients are not silently treated as one coefficient class.

---

# Seed adjudications

The initial ledger deliberately includes mixed outcomes.

## Positive source-level conflict candidates

```text
Dalechampia scandens
Castilleja linariaefolia
Pedicularis rex
```

All are already admitted as bounded R-layer conflict patterns, but none is currently `effect_size_ready` for the common Q1 pool.

## Negative / weak boundary candidate

`Ipomopsis` Campbell et al. 2022 has public raw data and sequential pollination / seed-predation fitness components. In the published analysis, strong pollination selection on corolla width was not accompanied by detected seed-predation selection on that same trait. It is therefore a useful common-estimand boundary/control, not a pre-labelled positive conflict.

## Agent-identity unresolved conflict

`Gymnadenia conopsea` Chapurlat et al. 2019 reports three scent compounds for which pollinator-mediated and nonpollinator-mediated selection oppose one another. The public dataset contains individual morphology, scent and fitness data.

However, `nonpollinator-mediated` is not automatically equivalent to a known antagonist. The biological second agent must be recovered from the methods/results before this study enters an antagonist-specific stratum.

---

# Independence rule

The hierarchy is:

```text
article / experimental programme
  -> experiment / population / year
     -> trait
        -> treatment / coefficient
```

Multiple lower-level records can inform one multilevel effect, but they are not independent papers.

In particular:

- multiple Pedicularis populations remain one literature cluster;
- multiple scent compounds in Gymnadenia remain dependent effects within one study;
- Caruso's duplicated analysis workbook does not create new evidence;
- repeated use of one treatment record in multiple Caruso manuscript pairs must be tracked as dependence.

---

# Outputs

The re-screen produces four distinct objects:

1. **source registry** — provenance and acquisition state;
2. **row inventory** — immutable mapping from original database records;
3. **source-level screening ledger** — biological adjudication and exclusions;
4. **effect extraction table** — only records that pass biological and statistical compatibility.

Only object 4 can change `effect_size_ready_clusters` in `BALANCE_QUANTITATIVE_STRATA_V1.csv`.

## Current state

```text
Caruso metadata / database scope            VERIFIED
non-duplicated workbook identity             VERIFIED BY DRYAD LANDING PAGE
local/programmatic file ingest               PENDING
canonical source registry                    REGISTERED
canonical source-level screening seed         REGISTERED
Q1 effect-size-ready clusters                0
```

## Claim ceiling

This workflow can establish a reproducible quantitative synthesis of shared floral conflict if compatible effects are recovered. It cannot infer direct BALANCE occupancy or estimate `W_S*`, `W_D*`, `rho`, `Phi`, `xi`, or `d_B` from the selection-gradient database.

# BALANCE plant macro programme evidence map v1

## Why a programme map is needed

The plant macro programme now contains four evidence lanes with intentionally different sampling logic.

Their raw counts must not be combined into one prevalence estimate.

The correct object is a **programme map** showing what each lane contributes to identification.

Canonical executable surface:

```text
balance_domain/plant_programme.py
tests/test_plant_programme.py
```

## U1 — broad interaction specificity

Current provisional source-screened sample:

```text
20 records
13 excluded at the shared-reproductive-coordinate S0 gate
0 positive conflict
1 aligned no-conflict
5 no-demonstrated-conflict
14 unresolved (including S0 failures)
```

U1's value is specificity.

It shows that a broad herbivory-pollination literature cannot simply be renamed a functional-conflict dataset.

## U2 — mechanism-targeted sexual interference

Current source-closed review universe:

```text
22 dependency groups
8 positive conflict
2 no-demonstrated-conflict
12 unresolved
```

U2 is the first lane with a formal, outcome-blind, source-closed first-20 double-coding packet.

Its next gate is genuinely independent coder B, not further assistant-generated recoding.

## U3 — structural-positive case-control development

Current species-level case registry:

```text
6 source-resolved heteranthery cases
3 direct pollen-fate conflict cases
3 partial conflict cases
6 registered PRIMARY controls
2 adjudicated controls
4 screened controls still open
```

U3 is outcome-selected by architecture and therefore cannot estimate prevalence.

Its valid role is matched case-control development for structural division of labour.

## U4 — pollinator-prey mechanism stress test

Current high-information species series:

```text
10 species
2 direct positive conflict
5 no-demonstrated-conflict
3 unresolved
```

U4 adds an important architecture state:

```text
SIGNAL_SEPARATION
```

and demonstrates why pollinator capture/overlap alone is not equivalent to reproductive-fitness conflict.

Selfing can buffer the cost of captured pollinators, while spatial or cue separation can exist without evidence that conflict caused the architecture.

## Cross-lane result

The four lanes converge on a methodological biological point:

```text
ecological interaction
!=
shared-coordinate conflict

morphological or temporal separation
!=
proof that conflict caused the separation

review membership
!=
positive mechanism receipt
```

This is not merely a guardrail. It defines the empirical target of BALANCE macro:

> identify the conditions under which an independently demonstrated functional conflict is associated with shared, temporal, spatial, signal, or structural resolution architecture.

## What remains before a confirmatory model

The programme is not yet model-ready because:

1. U1 full-47 reconstruction is formally open;
2. U2 independent double coding has not been completed;
3. U3 has complete screened control coverage but four of six PRIMARY controls remain open;
4. U4 is a mechanism stress test, not an outcome-blind prevalence frame;
5. phylogenetic dependence has not yet been frozen across the final confirmatory species set.

The repository therefore explicitly reports:

```text
primary_model_ready = false
pooled_prevalence_estimate = null
```

until those gates close.

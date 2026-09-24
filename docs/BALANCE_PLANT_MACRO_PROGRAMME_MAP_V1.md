# BALANCE plant macro programme evidence map v1

## Why a programme map is needed

The plant macro programme contains four evidence lanes with intentionally different sampling logic.

Their raw counts must not be combined into one prevalence estimate.

The correct object is a **programme map** showing what each lane contributes to identification.

Canonical executable surface:

```text
balance_domain/plant_programme.py
tests/test_plant_programme.py
```

## U1 — broad interaction specificity

The provisional strict blind first-20 screen currently returns:

```text
20 records
0 positive conflict
1 aligned no-conflict
18 no-demonstrated-conflict
1 unresolved candidate
```

U1's value is specificity.

It shows that a broad herbivory-pollination literature cannot simply be renamed a functional-conflict dataset.

## U2 — mechanism-targeted sexual interference

Current source-closed review universe:

```text
22 dependency groups
8 strict conflict-gate positives
3 no-demonstrated-conflict
11 unresolved candidates
```

U2 is the first lane with a formal, outcome-blind, source-closed first-20 double-coding packet.

Its next gate is genuinely independent coder B, not further assistant-generated recoding.

The contrast with U1 is a measurement/specificity result, not a prevalence comparison, because the review universes use different inclusion criteria.

## U3 — structural-positive case-control development

Current species-level case/control registry:

```text
6 source-resolved heteranthery cases
6 registered PRIMARY controls
4 adjudicated controls
2 Monochoria controls still open
0 cases currently lacking a registered eligible control
16 review families: 11 body-text representatives + 2 independently resolved + 3 pending
```

U3 is outcome-selected by architecture and therefore cannot estimate prevalence.

The original `Senna surattensis` proposals were rejected because "little morphological differentiation" is not evidence of heteranthery absence. Frozen replacement searches have now recovered and adjudicated both Senna controls: `S. covesii` for `S. bicapsularis` after a VIIb audit, and `S. spectabilis` for `S. alata` after all sampled clade-II candidates failed and a clade-III SOURCE_QUALITY tie-break was closed.

The valid U3 role is matched case-control development for structural division of labour with fail-closed control eligibility.

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

weak differentiation
!=
absence of differentiation
```

This defines the empirical target of BALANCE macro:

> identify the conditions under which an independently demonstrated functional conflict is associated with shared, temporal, spatial, signal, or structural resolution architecture.

## What remains before a confirmatory model

The programme is not yet model-ready because:

1. U1 full-47 reconstruction is formally open;
2. U2 independent double coding has not been completed;
3. U3 control matching is open only for the two Monochoria cases, and three review-family representative identities remain supplement-dependent;
4. U4 is a mechanism stress test, not an outcome-blind prevalence frame;
5. phylogenetic dependence has not yet been frozen across the final confirmatory species set.

The repository therefore explicitly reports:

```text
primary_model_ready = false
pooled_prevalence_estimate = null
```

until those gates close.

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
5 no-demonstrated-conflict
14 unresolved
13 records excluded at the shared-coordinate gate
```

U1's value is specificity.

It shows that a broad herbivory-pollination literature cannot simply be renamed a functional-conflict dataset. The full review denominator is still open at 44/47 registered taxa. The three supplement-only taxa are not promoted from article-level triangulation: the located PeerJ/Figshare source tables must be ingested first, after which the deterministic first-20 frame is recomputed.

## U2 — mechanism-targeted sexual interference

Current source-closed review universe:

```text
22 dependency groups
8 strict conflict-gate positives
2 no-demonstrated-conflict
12 unresolved candidates
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
0 cases currently lacking a registered primary control
16 review families: 11 body-text representatives + 2 independently resolved + 3 pending
```

U3 is outcome-selected by architecture and therefore cannot estimate prevalence.

The original `Senna surattensis` proposals were rejected because "little morphological differentiation" is not evidence of heteranthery absence. Frozen replacement searches recovered and adjudicated both Senna controls: `S. covesii` for `S. bicapsularis` after a VIIb audit, and `S. spectabilis` for `S. alata` after all sampled clade-II candidates failed and a clade-III SOURCE_QUALITY tie-break was closed.

The valid U3 role is matched case-control development for structural division of labour with fail-closed control eligibility.

The Monochoria molecular problem now has two registered resolution levels. The original public-accession `ndhF+rbcL` surface is non-identifying: `M. australasica` and `M. cyanea` tie for both focal cases on an identical joint-site mask. A subsequent complete-plastome audit uses 68 shared single-copy CDS and 51,357 jointly comparable sites per case. On that frozen plastid-proximity surface, `M. australasica` has lower p-distance than `M. cyanea` to both `M. korsakowii` (460 versus 475 differences) and `M. vaginalis` (484 versus 501 differences). Gene-wise support also favors `M. australasica` (24 versus 14 with 30 ties; 24 versus 15 with 29 ties, respectively).

That result closes the **conditional phylogenetic-distance ranking**, not the control adjudication. It is a plastid-proximity diagnostic rather than a nuclear species-tree result. Direct species-level effective animal-pollination eligibility remains unresolved for the Monochoria candidate set; until eligibility is known, `M. cyanea` must remain available in case the closer candidate fails the ecological gate.

Among the four PASS-adjudicated U3 pairs, matched extraction currently contains eight rows. Case-side pollen-fate conflict is `POSITIVE` in 2/4 and `UNRESOLVED` in 2/4; control-side conflict is `POSITIVE` in 1/4 and `UNRESOLVED` in 3/4. No control is yet source-secure as `SHARED_INTEGRATED`; one control (`Solanum lycocarpum`) instead resolves to `AMONG_FLOWER_MODULE_DIVISION`.

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

1. U1 full-47 reconstruction is formally open; the located supplement/Figshare tables still need direct ingestion before the missing taxa and formal first-20 frame can be frozen;
2. U2 independent double coding has not been completed;
3. U3 control matching is open only for the two Monochoria cases: molecular distance ranking is frozen, but direct species-level effective animal-pollination eligibility is unresolved; three review-family representative identities also remain unresolved;
4. U3 matched pollen-fate conflict remains incomplete for `Osbeckia chinensis` and both Senna case-control pairs;
5. U4 is a mechanism stress test, not an outcome-blind prevalence frame;
6. phylogenetic dependence has not yet been frozen across the final confirmatory species set.

The repository therefore explicitly reports:

```text
primary_model_ready = false
pooled_prevalence_estimate = null
```

until those gates close.

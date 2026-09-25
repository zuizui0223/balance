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

The full 47-taxon U1 review universe is source-closed by direct Figshare reconciliation. The three Figure-4-omitted taxa are `Eichhornia crassipes`, `Nemophila menziesii`, and `Ruellia nudiflora`. All three sort after the existing twentieth taxon, so the deterministic first-20 frame is unchanged and frozen.

The existing pre-independent-coding first-20 specificity screen returns:

```text
20 records
0 positive conflict
1 aligned no-conflict
5 no-demonstrated-conflict
14 unresolved
13 records excluded at the shared-coordinate gate
```

U1's value is specificity plus a source-closed outcome-blind denominator.

It shows that broad herbivory-pollination literature cannot simply be renamed a functional-conflict dataset. Denominator reconstruction is closed; the remaining U1 gate is genuinely independent second-coder classification of the frozen first 20.

## U2 — mechanism-targeted sexual interference

Current source-closed review universe:

```text
22 dependency groups
8 strict conflict-gate positives
2 no-demonstrated-conflict
12 unresolved candidates
```

U2 has a formal, outcome-blind, source-closed first-20 double-coding packet.

Its next gate is genuinely independent coder B, not further assistant-generated recoding.

The contrast with U1 is a measurement/specificity result, not a prevalence comparison, because the review universes use different inclusion criteria.

## U3 — structural-positive case-control development

Current review and matched-control state:

```text
16 review families / 12 orders
16 / 16 family representatives source-resolved at explicit provenance levels
6 source-resolved species cases
6 registered PRIMARY controls
4 controls adjudicated PASS
2 Monochoria controls still OPEN
U3 dependence structure FROZEN
```

The inaccessible 2010 Wiley Table S1 itself remains unrecovered, with the retrieval failure preserved as an audit receipt. Representative-family coverage is nevertheless complete through body-text identities plus explicitly separated independent evidence; no Table-S1 transcription is claimed.

U3 is outcome-selected by architecture and therefore cannot estimate prevalence.

### Monochoria control selection

The original public-accession `ndhF+rbcL` surface is non-identifying: `M. australasica` and `M. cyanea` tie for both focal cases.

A subsequent complete-plastome audit uses 68 shared single-copy CDS and 51,357 jointly comparable sites per case. On that frozen plastid-proximity surface, `M. australasica` has lower p-distance than `M. cyanea` to both `M. korsakowii` (460 versus 475 differences) and `M. vaginalis` (484 versus 501 differences).

That closes the **conditional phylogenetic-distance ranking**, not the control adjudication. Direct species-level effective animal-pollination eligibility remains OPEN for both candidates.

The remaining evidence ceiling is explicit:

```text
needed:
species-level flower visitation
+ pollen transfer / stigma deposition / reproductive effectiveness
```

General buzz-pollination context and Amegilla territorial behaviour above `M. australasica` do not satisfy the gate.

### Matched pollen-fate extraction

Among the four PASS-adjudicated pairs:

```text
case conflict POSITIVE                      4 / 4
control conflict POSITIVE                   3 / 4
control conflict UNRESOLVED                 1 / 4
pairs with both conflict states resolved    3 / 4
matched_conflict_estimand_ready             false
```

Fully conflict-resolved matched pairs:

- `Solanum rostratum -> Solanum lycocarpum`
- `Senna alata -> Senna spectabilis`
- `Senna bicapsularis -> Senna covesii`

The sole remaining matched conflict measurement blocker is `Osbeckia chinensis`.

Its historical source establishes pollen extraction from poricidal anthers plus visitor-body stigma contact, but not the registered reward-removal versus export/deposition or reproductive-consequence measurement. That absence is now frozen as an evidence-ceiling receipt rather than repeatedly treated as an unsearched gap.

### Architecture result already visible

The nonheterantherous controls do not collapse into one "integrated" state:

```text
Solanum lycocarpum   conflict positive   AMONG_FLOWER_MODULE_DIVISION
Senna spectabilis   conflict positive   WITHIN_FLOWER_DIVISION_OF_LABOUR
Senna covesii       conflict positive   broader architecture UNRESOLVED
Osbeckia chinensis  conflict unresolved broader architecture UNRESOLVED
```

No control is currently source-secure as `SHARED_INTEGRATED`.

Thus the current U3 evidence already separates three biological objects:

```text
pollen-reward / gamete-transfer conflict
!=
morphological heteranthery
!=
level at which functional routing occurs
```

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

1. U1 independent double coding has not been completed, although the 47-taxon universe and first-20 reliability frame are frozen;
2. U2 independent double coding has not been completed;
3. the two Monochoria matched controls remain OPEN at the direct species-level effective-pollination eligibility gate; the conditional 68-CDS ranking is already frozen;
4. the four-pair U3 matched conflict extraction is missing only the `Osbeckia chinensis` control-side pollen-fate measurement;
5. U4 is a mechanism stress test, not an outcome-blind prevalence frame;
6. dependence for U3 is frozen, but dependence/covariance still must be frozen for whatever final confirmatory plant set survives U1/U2 coding.

The repository therefore explicitly reports:

```text
primary_model_ready = false
pooled_prevalence_estimate = null
```

until those gates close.

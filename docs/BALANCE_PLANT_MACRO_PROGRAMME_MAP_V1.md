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

It shows that broad herbivory-pollination literature cannot simply be renamed a functional-conflict dataset. Denominator reconstruction is closed. The frozen first 20 are source-ready for the independent reliability exercise, and the remaining 27 taxa now have exact review-primary study identities mapped from Figshare. Those 27 still require primary full-text/evidence retrieval before production coding.

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

The remaining uncertainty is now partially identified rather than treated as all-or-nothing. In the current four-pair matched sample, case conflict-positive fraction is fixed at 1.00, while the control fraction is bounded at 0.75-1.00 depending on the unresolved Osbeckia state. The raw case-minus-control binary-positive difference is therefore bounded at 0.00-0.25. This is a matched-sample logical bound, not a population prevalence or causal estimate. Crucially, three directly positive nonheterantherous controls already falsify binary conflict presence as a deterministic separator of heteranthery.

Measurement completion and effect estimability are now separated explicitly. If Osbeckia is ultimately POSITIVE there are zero conflict-status-discordant matched pairs; if it is NO_DEMONSTRATED_CONFLICT there is exactly one discordant pair and it is case-positive/control-negative, with no reverse discordance. Therefore a finite conditional binary conflict-presence coefficient is not estimable under either admissible completion. Osbeckia remains worth resolving for evidence completeness, quantitative strength and routing architecture—not as a route to a binary presence effect.

### Prospective matched-control expansion

A second U3 exercise prospectively froze four additional species-level case families before any prospective control conflict or routing outcome was inspected:

```text
Bixaceae        Amoreuxia wrightii
Brassicaceae    Brassica rapa
Lythraceae      Lagerstroemia indica
Malvaceae       Mollia lepidota
```

The matching-stage result is:

```text
controls CLOSED                    0 / 4
EVIDENCE_CEILING_BLOCKED           4 / 4
dependence blocks retained         4 / 4
prospective_queue_exhausted        true
```

The blockers are heterogeneous rather than one generic failure: nearest-candidate animal-pollination eligibility in Bixaceae; retained tetradynamy plus unresolved family-level closest ranking in Brassicaceae; an unranked monomorphic congener in Lythraceae; and unresolved current-species morphology plus infrageneric phylogeny in Mollia.

This is **not** a biological null and does not show that valid controls do not exist. It shows that, under the frozen predictor-blind matching rules and current public evidence, adding heteranthery-positive cases is easier than identifying defensible negative controls. The four blocked dependence units therefore remain explicit missingness rather than being replaced by more convenient distant taxa.

This changes the practical U3 strategy: do not enlarge the positive-case list merely to increase sample size. New U3 replication should enter only when new morphology, pollination or phylogenetic evidence genuinely reopens one of the frozen matching blocks.

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

A matched counterexample now makes the second separation explicit. `Senna alata`
is heterantherous and `S. spectabilis` is nonheterantherous under the frozen
fertile-stamen morphology definition, yet both have positive pollen-fate
conflict and the same source-resolved
`WITHIN_FLOWER_DIVISION_OF_LABOUR` routing state. Therefore heteranthery is
not necessary for within-flower functional division, and visible stamen
morphology does not uniquely identify routing architecture.

Combined with `S. lycocarpum`, which routes positive conflict among flower
modules, the current evidence supports a hierarchical empirical target:

```text
conflict presence / strength
-> routing level
-> morphological or floral implementation
```

These are distinct estimands and should not be collapsed into one binary
"heteranthery as conflict resolution" variable.

The mapping is now non-identifying in **both directions** on the registered
matched evidence surface:

```text
same morphology, different routing:
  nonheterantherous S. spectabilis -> WITHIN_FLOWER_DIVISION_OF_LABOUR
  nonheterantherous S. lycocarpum  -> AMONG_FLOWER_MODULE_DIVISION

same routing, different morphology:
  heterantherous S. alata          -> WITHIN_FLOWER_DIVISION_OF_LABOUR
  nonheterantherous S. spectabilis -> WITHIN_FLOWER_DIVISION_OF_LABOUR
```

Thus visible fertile-stamen morphology is neither a deterministic predictor of
routing architecture nor recoverable from routing state. The ecological object
is a three-layer state: conflict, routing and implementation.

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

1. U1 independent double coding has not been completed; separately, the 27 non-reliability-frame taxa have mapped primary-study identities but still require primary full-text/evidence retrieval before production coding;
2. U2 independent double coding has not been completed;
3. the two Monochoria matched controls remain OPEN at the direct species-level effective-pollination eligibility gate; the conditional 68-CDS ranking is already frozen;
4. the four-pair U3 matched conflict extraction is missing only the `Osbeckia chinensis` control-side pollen-fate measurement;
5. the prospectively frozen four-family U3 expansion is exhausted at the matching-stage public evidence ceiling (0/4 controls closed, 4/4 blocks retained as missingness) and must not be rescued by convenience matching;
6. U4 is a mechanism stress test, not an outcome-blind prevalence frame;
7. dependence for U3 is frozen, but dependence/covariance still must be frozen for whatever final confirmatory plant set survives U1/U2 coding.

The repository therefore explicitly reports:

```text
primary_model_ready = false
pooled_prevalence_estimate = null
```

until those gates close.

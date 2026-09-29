# BALANCE plant macro programme evidence map v1

## Why a programme map is needed

The plant macro programme contains five evidence lanes with intentionally different sampling logic: U1, U2, U3, U4, and the conflict-first U6 reconstruction.

Their raw counts must not be combined into one prevalence estimate.

The correct object is a **programme map** showing what each lane contributes to identification.

Canonical executable surface:

```text
balance_domain/plant_programme.py
tests/test_plant_programme.py
```

## U1 — broad interaction specificity

The full 47-taxon U1 review universe is source-closed by direct Figshare reconciliation.
The three Figure-4-omitted taxa are `Eichhornia crassipes`, `Nemophila menziesii`, and
`Ruellia nudiflora`; all sort after the frozen first-20 reliability frame.

The complete strict conflict source screen now returns:

```text
47 records / 47 dependency groups

POSITIVE                    0
ALIGNED_NO_CONFLICT         1
NO_DEMONSTRATED_CONFLICT   46
UNRESOLVED_CANDIDATE        0

PASS_CONFLICT_GATE          0
FAIL_CONFLICT_GATE         47
HOLD_FOR_FULL_TEXT          0
```

Architecture is not inferred in this screen.

Two earlier holds are now closed from primary-source results:

- `Brassica nigra`: the source explicitly concludes that no herbivory-pollination
  trade-off was evident;
- `Myrmecophila tibicinis`: floral size/asymmetry manipulations did not significantly
  alter male/female pollination success, and the paper concludes that florivory has little
  reproductive effect beyond direct sexual-structure consumption.

Thus U1's current empirical role is stronger and narrower: it is a complete,
interaction-defined **specificity universe** showing that generic herbivory-pollination
effects, damage-mediated pollination costs, and indirect floral changes cannot simply be
relabeled as the registered shared-coordinate conflict.

This is still a source-screen result. The frozen first 20 must complete the independent
coder reliability/adjudication exercise before U1 is confirmatory. If independent coding
changes any source-screen call, the adjudicated value supersedes this ledger.

See `docs/BALANCE_PLANT_U1_FULL47_CONFLICT_SCREEN_V1.md`.

## U2 — mechanism-targeted sexual interference

Current source-closed review universe:

```text
22 dependency groups
8 strict conflict-gate positives
14 no-demonstrated-conflict
0 unresolved candidates
```

U2 has a formal, outcome-blind, source-closed first-20 double-coding packet. The
frozen worksheet now validates 20 dependency groups × 2 blank coder rows, and all eight
current source-screen positive groups are inside that reliability frame.

Its next gate is genuinely independent coding/adjudication, not further assistant-generated
recoding.

The contrast with U1 is a measurement/specificity result, not a prevalence comparison,
because the review universes use different inclusion criteria.

See `docs/BALANCE_PLANT_U2_FULL22_CONFLICT_SCREEN_V1.md`.

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

## Frozen confirmatory estimand

The primary response is now fixed before model fitting as:

```text
SHARED
NONSTRUCTURAL_SEPARATION
STRUCTURAL_MODULE_DIVISION
MOSAIC
```

`SIGNAL_SEPARATION` is retained inside `NONSTRUCTURAL_SEPARATION`, and
`POLYMORPHIC_OR_MOSAIC` remains primary-outcome eligible even when the derived
binary structural field is unresolved. The raw nominal architecture categories
remain secondary detail.

There is no outcome-count-triggered fallback model. See
`docs/BALANCE_PLANT_CONFIRMATORY_MODEL_FREEZE_V3.md`.

## U6 — pollen-theft conflict-first recovery universe

A new architecture-blind recovery universe is registered from Hargreaves, Harder &
Johnson (2009), *Consumptive emasculation: the ecological and evolutionary consequences of
pollen theft*.

U6 is admitted by empirical pollen-theft / inefficient-transfer evidence, not by
heteranthery or any other architecture state. Reference classification is two-pass:

```text
Pass 1:
  classify anchor-review references for empirical pollen-theft evidence
  freeze included taxa/dependency groups
  architecture fields physically absent

Pass 2:
  only after Pass-1 freeze, code architecture and the three confirmatory predictors
```

U6 Pass 1 is now closed: 157/157 anchor references are classified, 33 candidate references are adjudicated, and 21 conflict-first dependency groups are frozen. Pass 2A generic source recovery is complete; the final source packet is frozen and independent coding is open. All 63 raw predictor receipt slots are also source-screened outcome-independently, but 0/21 groups are independently adjudicated. U6 remains outside the active confirmatory model until coding, agreement, adjudication and the final V3 estimability gates close.

See `docs/BALANCE_PLANT_U6_POLLEN_THEFT_UNIVERSE_PROTOCOL_V1.md`.

## What remains before the v3 primary model

The primary denominator is now explicitly restricted to outcome-blind/conflict-first
U1 + U2 + U6. U3 and U4 continue as parallel evidence lanes but do not block the primary
model.

Primary blockers:

1. **U1 independent reliability/adjudication** remains incomplete. The full 47-taxon
   source screen itself is closed at 0 positive / 0 unresolved; the production 27 are no
   longer an unsearched evidence block.
2. **U2 independent double coding** remains incomplete.
3. **U6 independent double coding** is open but still unstarted across the frozen
   21 dependency groups.
4. Every admitted row still requires three **adjudicated, outcome-independent** predictor
   receipts. The source-screen stage is already complete for all eight U2 conflict-positive
   groups and all 21 frozen U6 groups (63/63 U6 receipt slots resolved as
   outcome-independent), but neither lane has independent predictor adjudication yet.
5. The final U1/U2/U6 assembly must close cross-universe dependence and pass the
   allowlisted model-assembly contract. U3/U4 rows are rejected from this denominator.
6. Only then can model-v3 estimability be evaluated: each of the four response classes
   requires at least two independent dependence blocks; both levels of
   `module_opportunity2` and all three levels of `temporal_exposure3` require at least
   two independent blocks; and the 12-coefficient primary design matrix must be full rank.
   `spatial_exposure2` is now secondary because the pre-outcome source-screen support is
   28 SAME_UNIT versus 1 DISTRIBUTED block.

Current source-screen diagnostics do **not** pre-decide the final class support. U1/U2
currently lack a source-screened `STRUCTURAL_MODULE_DIVISION` row, while U6 architecture
remains independently uncoded. No class is imported from U3 to repair that uncertainty.

Parallel but nonblocking work:

- U3 matched/case-control measurement completion, Monochoria controls, and Osbeckia;
- U4 pollinator-prey mechanism stress tests.

The repository therefore explicitly reports:

```text
primary_model_ready = false
pooled_prevalence_estimate = null
```

The current primary statistical specification is
`docs/BALANCE_PLANT_CONFIRMATORY_MODEL_FREEZE_V3.md`.

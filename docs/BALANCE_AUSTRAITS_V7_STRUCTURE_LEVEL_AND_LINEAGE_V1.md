# AusTraits: reproductive architecture levels, source support and lineage candidates (2026-10-19)

**Status: ACTUAL PUBLIC-DATA ANALYSIS, post-open exploratory extension.** This document supplements, but does not replace, the original [prospectively frozen v7 sex-system/pollination contrast](BALANCE_AUSTRAITS_INDEPENDENT_STRUCTURAL_OPPORTUNITY_V1.md) and its [source acquisition audit](BALANCE_AUSTRAITS_V7_LIVE_READOUT_20261019.md). No new biologically sampled plants, fitness/selection experiments, phylogenies, independently dated transitions or causal origin evidence were generated.

## Verified inputs and implementation

- Source: **AusTraits v7.0.0**, DOI [10.5281/zenodo.15718081](https://doi.org/10.5281/zenodo.15718081). Exact verified source archive SHA256: `2995fb9e5eebf9271f9241b5a6c2e2cbb7b45e8eda5ce4db43c14c68f95e2f3f`.
- The six predeclared source trait names remain fixed and unchanged: `sex_type`, `flower_structural_sex_type`, `flower_perianth_fusion`, `flower_perianth_symmetry`, `pollination_syndrome`, `pollination_system`.
- Reproducible final [GitHub Action](https://github.com/zuizui0223/balance/actions/runs/39264510200): source verification, frozen source/ontology tests and full source acquisition passed. Aggregated-results-only artifact ID `12193410268`, artifact digest `sha256:8cdf7fad6cd1d9191e5b3b6ec8f6b8ecff1372591dc4bfdbe5b9bf6658b6bb53`.
- [Original independent source processor](../balance_domain/austraits_architecture_macro.py), [new hierarchy reader](../balance_domain/austraits_organizational_hierarchy.py), [new congeneric discovery reader](../balance_domain/austraits_lineage_frontier.py); corresponding regression tests freeze expected source/selection logic.
- Full public source archive was rechecked against its declared checksum. Raw mixed-license species-level trait records are **not redistributed**; output lists only aggregate source counts and genus-level candidate summaries.

## Result 1: Plant-level and flower-level reproductive architecture are distinguishable

Among **1,080** exact binomial species independently qualifying for **both** `sex_type` and `flower_structural_sex_type` on the same source name:

| Operationally coherent or unresolved organizational state | Exact source species |
| --- | ---: |
| Whole-plant hermaphroditic / bisexual flower = shared in flower | **797** |
| Monoecious / unisexual flower = sexes partitioned among flowers | **98** |
| Dioecious / unisexual flower = sexes partitioned among plants | **112** |
| Incompletely unisexual flower = retained partial state | **52** |
| Source-sex and flower-sex labels not directly concordant | **21** |
| **Total** | **1,080** |

The **1,007/1,080** matching organizational classifications are descriptive agreement between *two botanical traits*, not independently validated evolutionary functions or studies. The 52 partial/unresolved and 21 discordant states are **not** forced into one of the three levels. Inconsistency may reflect taxonomic/study context differences, not a proof of false source data.

## Result 2: Flower-level unisexuality recovers a parallel ecological association

Strictly exact raw `flower_structural_sex_type` of `bisexual` or `unisexual`, and exact `pollination_syndrome` of `insect` or `wind`, are jointly available for **425** binomial species. A further **9** flower states are only `incompletely_unisexual` and remain outside the binary comparison.

| Pollination source state | Qualified species | Unisexual-flower species | Descriptive fraction |
| --- | ---: | ---: | ---: |
| Insect | **383** | **37** | **9.66%** |
| Wind | **42** | **10** | **23.81%** |
| **Difference (wind - insect)** | | | **+14.15 percentage points** |

This is in the same descriptive direction as the original organism-level comparison (insect 183/2,495 vs wind 60/346; difference +10.01 percentage points).

**Key taxonomic restriction:** insect-labelled flower-level species occur in **349 genera**, wind-labelled species in **40 genera**, and **ZERO genera occur under both pollination states** in this specific qualified source subset. The wind/insect difference is therefore completely a **between-genus association**; it cannot be interpreted as a contrast of pollen-environment transitions within the same genus.

Genus-equal averaging changes the source-selected unisexual-flower fractions to **9.46% insect vs 22.50% wind** (difference **+13.04 points**). This does not remove common-ancestry confounding.

The separately registered *post-open* source-pair diagnostic admits **217** species with one dataset key for each trait and holds **208** with multiple source-dataset keys. **No specific `flower structural sex source -> pollination source` pairing** satisfies the frozen >=20 species and >=5 genera in **both** insect and wind arms. Source-pair qualification therefore remains `HOLD_INSUFFICIENT_COMMON_SUPPORT` even though the full descriptive contrast is numerically available.

## Result 3: Three-layer complete species yield similar source direction, still observational

An exact triplet of `sex_type × flower_structural_sex_type × pollination_syndrome` exists for **294** binomial species. Of these, **280** satisfy the strict concordant organizational states, with remaining cases retained as partial/discordant rather than silently converted.

| Strict consistent organizational contrast | Insect | Wind |
| --- | ---: | ---: |
| Qualified species | **249** | **31** |
| Structural sex organization separated across flowers or individuals | **27** | **9** |
| Source-selected fraction | **10.84%** | **29.03%** |

The raw nested difference is **+18.19 percentage points**, not independent of the other two comparisons because the source sample is nested. It is not proof that a wind-pollination environment selected for new organs or changed developmental architecture.

## Result 4: The actionable same-genus morphology frontier is unexpectedly narrow

A separately frozen candidate **screening rule** requires: exact binomial source label, one source-consistent normalized state, and **at least two distinct species in each architecture state** within the same genus. This candidate criterion is about *observed present-day variation* and cannot count the number, date, direction, independence or selection cause of evolutionary transitions.

| Focal structure layer | Qualified species | Qualifying genera | Candidate genera with >=2 species on both sides | Candidates containing BOTH source pollen states |
| --- | ---: | ---: | ---: | ---: |
| Whole-plant sexual organization (hermaphrodite vs monoecy/dioecy) | **15,936** | **1,720** | **11** | **0** |
| Flower structural sex (bisexual vs unisexual) | **1,499** | **1,386** | **0** | **0** |

The flower structural-sex archive has mainly one qualified species per genus; **zero qualifying transition candidates is a coverage result, not biological evidence of zero floral transitions**.

All eleven organism-level genus candidates are:

| Genus | Shared (hermaphroditic) species | Separated sexual-system species | Qualified exact pollen-state context |
| --- | ---: | ---: | --- |
| *Lobelia* | 6 | 6 | 5 insect, none wind |
| *Acacia* | 5 | 11 | no strict pollen-state overlap |
| *Melicope* | 9 | 4 | no strict pollen-state overlap |
| *Flindersia* | 5 | 4 | no strict pollen-state overlap |
| *Lepyrodia* | 3 | 15 | no strict pollen-state overlap |
| *Wurmbea* | 14 | 3 | 8 insect, none wind |
| *Auranticarpa* | 3 | 3 | 1 insect, none wind |
| *Grewia* | 2 | 14 | no strict pollen-state overlap |
| *Denhamia* | 12 | 2 | 4 insect, none wind |
| *Pimelea* | 2 | 11 | 10 insect, none wind |
| *Polyscias* | 6 | 2 | 1 insect, none wind |

Within *Lobelia* (qualified pollen-source subset: 1 shared + 4 separated insect records), *Wurmbea* (5 shared + 3 separated insect records) and *Denhamia* (3 shared + 1 separated insect record), different observed sexual organizations occur **among species classified under the same broad insect pollen-syndrome category**. This is a promising **specificity-control design** against explaining every sexual architecture difference by a wind-vs-insect shift. However, the exact relevant function pairs, context, phylogenetic histories and mechanism/fitness contrasts are **not measured** here.

Genus names require accepted-taxon author reconciliation and a phylogenetic-monophyly check before they become real historical replicates. The pooled AusTraits source archive may share specimen literature and related data providers across taxa; 11 selected genera are not 11 independent evolutionary origins.

## Claim freeze and next actionable biological test

1. **Supported now:** sexual organization varies among present-day taxa, and its descriptive source distribution differs by pollen-vector category in the broad archive; broad and flower-level trait views agree in sign.
2. **Also supported now:** accessible flower-level source data contain **zero** shared genera between wind and insect categories; source-specific wind common support is inadequate; direct organism-level sex-state variation under a consistent recorded insect category exists in named genera.
3. **Not established:** a given female/male or reproductive-assurance functional trade-off selected for the appearance of sexual structures; a modular architecture has positive net `W_D^*-W_S^*`; the ancestral-to-derived direction, transition counts, or heritable accessibility of new structures.
4. **Next data priority:** verify accepted species and phylogenies for **congeneric contrasts** (for instance *Lobelia*, *Wurmbea*, *Denhamia*), recover organism/flower functional-fitness studies at the same coordinate, and compare **insect-only species with differing architecture** as a negative control. Do not promote a genus to historical-origin evidence until ancestral polarity and independent trait/environment transition support are actually documented.

The central SCH–BALANCE–SLK/PAYOFF–BITA causal hypothesis remains unverified; this source-backed study **narrows exactly which structural levels and which candidate lineages could genuinely test it.**

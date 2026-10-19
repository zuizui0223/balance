# Live AusTraits v7.0.0 independent structural-opportunity screen (2026-10-19)

**PROVENANCE:** public original multi-study AusTraits archive, frozen release `7.0.0`, DOI [10.5281/zenodo.15718081](https://doi.org/10.5281/zenodo.15718081), declared checksum verified. Exact ZIP SHA256: `2995fb9e5eebf9271f9241b5a6c2e2cbb7b45e8eda5ce4db43c14c68f95e2f3f`.

Executed **actual retrieval and all-source-table scan** in [GitHub Actions run 39259657751](https://github.com/zuizui0223/balance/actions/runs/39259657751), with `validate` and `acquire-and-summarize` jobs both successful. Provenance-only artifact ID `12190055769`, artifact digest `sha256:3a803ee825bae8f1d5dd0f1c29fae4a9ec87aa75e68d956828cbdee1361b9bb0`. Raw mixed-license source records were **not redistributed**.

## Recovered source footprint (not numbers of independent biological experiments)

| Stage | Actually observed |
| --- | ---: |
| Source long-table rows scanned | **1,798,215** |
| Source rows matching the six prospectively frozen structural/opportunity traits | **46,299** |
| Distinct raw source taxon names with selected trait data | **24,492** |
| Species/taxon names with `sex_type` records | **21,687** |
| Species/taxon names with `pollination_syndrome` records | **9,079** |
| Species/taxon names with flower-specific structural sex data | **1,675** |
| Names with perianth symmetry | **1,015** |
| Names with perianth fusion | **944** |
| Names with `pollination_system` | **1,018** |

These are names present in the multi-source trait archive; they are not a GBIF/WFO taxonomic reconciliation, complete census of all angiosperms, independently sampled lineages, or evidence of active conflict.

## Strict species-first contrast: sexual organization versus pollen-transport mode

Frozen categories: one unambiguous exact binomial source `sex_type` in `{hermaphrodite,monoecious,dioecious}`, and one exact raw `pollination_syndrome` in `{insect,wind}`. All other coded sexual organizations and mixed pollination labels are not silently included; their source rows are counted and left outside this estimand.

| Category | Source-qualified species | Genus count | Monoecious | Dioecious | Hermaphrodite | Sex separated / species |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| INSECT | **2,495** | **504** | 78 | 105 | 2,312 | **0.07335** |
| WIND | **346** | **106** | 30 | 30 | 286 | **0.17341** |
| **Total** | **2,841** | **603 distinct genera** | 108 | 135 | 2,598 | **0.08553** |

**Unadjusted difference (wind minus insect): +0.10006 = 10.006 percentage points.** The raw selected-sample risk ratio of sex-separated organization is approximately `0.17341 / 0.07335 = 2.36`, but neither ratio nor difference is a phylogenetically adjusted evolutionary effect.

### Common-support failure is itself an important result

Only **7 genera** contain both pollen-mode categories, out of **603 distinct genera** represented in the strict species comparison. The documented equally weighted within-genus mean difference is **0.0** for those seven genera. These seven overlap genera were not a matched randomized sample, and the zero aggregate does not prove zero causal effect: within-genus ecology is nearly unrepresented. The apparent 10-percentage-point global difference could reflect lineage sorting, taxonomic coverage and source selection rather than current wind-versus-insect trade-off-mediated differentiation.

This is not a contradiction: a between-lineage correlation can be strong while **within-lineage variation needed to separate adaptation from ancestry is almost absent**. This directly motivates phylogenetic/repeated-transition designs instead of fitting a naive species-independent model or retrospectively expanding source labels to obtain an answer.

## Post-open source/cohort and within-genus diagnostic (separate from frozen main contrast)

A second full-release checksum-verified replay ([GitHub Actions run 39260914506](https://github.com/zuizui0223/balance/actions/runs/39260914506), artifact ID `12191945610`, SHA256 `9a2e73bf8695778b15d4ad696c62152b39649d71b1b0da1934ffdef8297a6024`) reproduced the original **1,798,215 / 46,299 / 24,492 / 2,841** source figures and the same archive SHA256. It did **not** change the main outcome definition. The source-stratified results below were introduced after observing that main source comparison and must **not** be presented as preregistered confirmatory results.

**Study provenance:** `Sjostrom_2006` supplies **20,832 of 27,014 `sex_type` source records**. In `pollination_syndrome`, `White_2020` contributes **7,892 of 13,440** and `Draper_2023` **4,109 of 13,440**. These record contributions are heavily unbalanced and may share botanical source lineages.

Of the **2,841** primary source-qualified exact species:
- **1,720** have exactly one contributing source dataset key for each of the two traits;
- **1,121** have multiple contributing dataset keys for at least one trait, so they are deliberately excluded from the post-open *source-cohort* sensitivity, though retained under the frozen main exact-state definition.
- The dominant single-key source pairings are `Sjostrom_2006 -> White_2020` (**819** species) and `Sjostrom_2006 -> Draper_2023` (**751** species). These are database-source pairings, **not 1,570 independent selection experiments**.

| Pollination data source in single-key cohort | Insect-only qualified species | Wind-only qualified species | Separated-sex fraction: insect | Separated-sex fraction: wind | Difference, percentage points |
| --- | ---: | ---: | ---: | ---: | ---: |
| `Draper_2023` | **667** | **94** | **2.70%** | **14.89%** | **+12.19** |
| `White_2020` | **821** | **0** | **1.58%** | not estimable | HOLD |

The direction of the wind/insect raw association **persists within the qualified Draper pollen-source stratum**. This reduces one simple source-composition concern but still does **not** adjust for ancestry, geographic sampling, or the particular sex-system source study contributing most records. `White_2020` has no eligible strict wind arm in this filtered sample and therefore cannot provide an independent cross-mode contrast; it must not be counted as replication of the Draper effect.

A post-open within-genus sign audit finds **0 positive, 0 negative, 7 exactly zero** differences among the seven genera represented under both pollen modes. This should be understood as **nearly complete lack of taxonomic common support**, not as experimental evidence that pollination cannot select on sexual organization. The seven genera may be stable in the present data because sex architecture is inherited at deeper phylogenetic scales or because coverage is incomplete.

## Data-semantic safeguard

The source reports 1,982 *flower_structural_sex_type* records from 1,675 taxon names, with 1,414 `bisexual`, 449 `unisexual` and 119 `incompletely_unisexual` **records**. Those record counts are not percentages of independent species or distinct evolutionary origins.

These traits must never be conflated:
- `sex_type` = species reproductive-sex system;
- `flower_structural_sex_type` = condition of a flower, not a species sexual system;
- `flower_perianth_fusion` = raw morphological fusion (values between 0 and 1 in source records), not the ecological release coefficient `s`;
- `pollination_syndrome` = annotated pollen-transport opportunity, not an intervention-based selection gradient.

The longer-term SCH–BALANCE–SLK/PAYOFF–BITA question still requires independently measured shared-trait conflict, feasible common-fitness alternative architectures, direct structural cost, heritable accessibility and historical origin.

## Status and next evidence gate

1. **Acquisition / provenance** — PASS. The full v7 archive was actually downloaded; source checksums and trait extraction were audited.
2. **Independent source-denominator expansion** — PASS for structural *opportunity*: 24,492 named taxa with relevant floral/sex/pollination information. Not a complete macro structural-modularity phenotype.
3. **Descriptive ecological association** — PASS only at source-stratified species level; raw wind/insect difference observed. No phylogenetic correction or causal trait interpretation.
4. **Within-genus / repeated-history identifiability** — HOLD: only seven genera share the two source-defined pollen modes.
5. **Functional-conflict-caused structural origin** — NOT TESTED: no measured conflict strength or dated independent structural transitions in the present source.

**Publication ceiling:** valid new independently acquired *morphology/opportunity* baseline with an instructive taxonomy/positivity limit, not a positive empirical validation of trade-off-driven new trait architecture. The main BITA/SCH manuscripts and BALANCE V4 confirmatory files remain untouched.

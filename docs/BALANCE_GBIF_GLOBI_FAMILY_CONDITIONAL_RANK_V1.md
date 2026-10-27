# GBIF–GloBI: exact within-family documentation-rank separation in an independently sampled species panel

**STATUS: REAL PUBLIC DATA; EXPLORATORY POST-OPEN ASSOCIATION. NOT a causal observation-effort effect, natural interaction frequency or direct structural BALANCE fitness result.**

## A nontrivial pattern in the original 48-species panel

The frozen GBIF panel selected four accepted taxa per deliberately chosen family (12 families), **before retrieving GloBI outcomes**. Original direct GBIF occurrence/search source counts were obtained for all 48 species on October 24, 2026, with archived original URLs and batch Git hashes. GloBI interactions were recorded five days earlier. GBIF indexed 20,131 occurrences in total, of which 13,049 had coordinates.

Among the five families with both GloBI *verbatim target-name documented* and *undocumented* species, the documented plants always occupy the **highest GBIF indexed occurrence ranks within their respective family**:

| Family | Documented species out of 4 | Documented ordinal GBIF occurrence ranks |
| --- | ---: | --- |
| Brassicaceae | 2 | #1 and #2 |
| Ericaceae | 1 | #1 |
| Fabaceae | 3 | #1, #2 and #3 |
| Rosaceae | 1 | #1 |
| Rubiaceae | 1 | #1 |

Within those five mixed-status families, there are 16 documented-versus-undocumented species pairs, and **all 16 pairwise count comparisons favor the GloBI-documented taxon**. Ranking instead by georeferenced GBIF occurrences preserves all 16/16 comparisons. The seven remaining families are not omitted: all their four sampled species share the same GloBI label, so they provide no *conditional within-family* information.

## An exact conditional reference distribution, not a randomized experiment

To transparently quantify the extremeness of that source pattern, hold each family's four original species, their GBIF occurrence ranks and the observed number k of GloBI-documented names fixed. Under the *unverified hypothetical null* that documentation labels are exchangeable among four species within each family, there are

    choose(4,2) × choose(4,1) × choose(4,3) × choose(4,1) × choose(4,1)
      = 6 × 4 × 4 × 4 × 4 = 1,536

joint conditional label assignments.

The observed rank statistic attains its theoretical maximum: 16/16 pairwise concordant, corresponding to **exactly one** of 1,536 assignments. This gives a **one-sided conditional reference probability of 1/1,536 = 0.000651**, or a **two-sided doubled-tail reference of 0.001302**. The georeferenced-index sensitivity yields exactly the same rank outcome.

**This analysis was formulated after looking at the data.** It is exploratory and not a preregistered confirmation. GloBI labels were not assigned by randomization; within-family exchangeability may be violated by genus, evolutionary lineage, region, collector effort, taxonomic naming and source ingestion. The 12 families themselves were deliberately selected, not randomly sampled among angiosperms. Therefore the exact permutation reference is a useful description of source-rank extremeness **under an explicit conditional null**, not a randomized causal p-value or globally generalizable ecological evidence.

## The taxonomic identifier sensitivity changes the conclusion's scope

Only **2 of the 16 name-documented taxa** have GloBI target identifiers directly matching their original GBIF species taxon key. Replacing the weak name-only flag with that stronger direct-key match creates a very different evidence surface:

| Recording criterion | Qualifying species | Informative within-family strata | Concordant pairs | Right-tail conditional reference |
| --- | ---: | ---: | ---: | ---: |
| Literal exact plant target-name | 16/48 | 5 | 16/16 | 0.000651 |
| Direct original GBIF species taxon-key match | **2/48** | 2 | **3/6** | **0.625** |

For direct keys, the doubled-tail reference is 1.0. This is not evidence that the first association was numerically false; it shows that its **taxonomic certainty is weaker** than would be required to interpret GloBI labels as independently author-resolved species-level ecological interactions. Key match also does not independently verify vouchers or taxonomic authorship.

The issue was already anticipated by the previous source-selected four-plant GloBI audit: a name-only query for **Solanum rostratum** returned **Solanum angustifolium** rows because distinct historical author-qualified rostratum concepts are present in botanical nomenclature. A database row labeled a familiar species name need not match the ecological taxon that an experiment actually studied.

## Independent data and reproducibility

The new analysis consumes exactly the original, already merged datasets, **without new species selection, exclusions or fabricated observations**:

- Frozen source-selected GBIF species list, selected before GloBI.
- Unaltered GloBI target-name/key source-coverage table, October 19.
- The original 12 GBIF source batches, containing all 96 occurrence/search and georeferenced count response texts, October 24.
- Source manifest with Git blob checks and original taxon-key and occurrence-count validation.

The previously implemented GBIF occurrence source auditor authenticates the original rows **before** this analysis reads their detection labels. Each analysis enumerates all conditional placements of label within the five informative families (1,536 assignments). When counts tie, a documented-versus-undocumented pair contributes half a concordance; GBIF key gives only deterministic display order, not artificial rank evidence.

New files:
- balance_domain/gbif_globi_family_exact_rank.py — original-source family-conditional exact enumeration and independent coordinates/key-identity sensitivities.
- data/BALANCE_GBIF_GLOBI_FAMILY_CONDITIONAL_RANK_FREEZE_V1.json — immutable source numbers, no-conflict caveats and alternative identifier support.
- scripts/audit_gbif_globi_family_exact_rank.py — creates a new source-SHA256 JSON receipt, refusing overwrites.
- tests/test_gbif_globi_family_exact_rank.py — full 48-species source check, exact 1/1,536 and strict-key 10/16 reference, source identity and artificial tied-rank tests.

Reproduce from a clean repo:

    python scripts/audit_gbif_globi_family_exact_rank.py --out /path/to/new_rank_receipt.json

## Biological meaning and next empirical step

**New defensible data finding:** Within the specific selected plant families, documentation in two independent public databases is highly uneven: taxa with GloBI *name-matched* relationships invariably have higher GBIF indexed occurrence counts than name-undocumented taxa in the mixed families. This reinforces that **a missing indexed relationship must not be coded as a negative pollinator or floral antagonist state**.

**Still not demonstrated:** that GBIF indexed records represent independent observer visits, that observational effort causally determines GloBI coverage, that GloBI rows are taxonomically voucher-correct, that a plant has any or no true ecological interactions, or that pollinator/antagonist competition imposes opposing selection gradients on the same floral morphology.

The next biologically informative test requires a **broader, outcome-independent, author-validated species denominator** with an observation/detection model and independent controlled reproductive function-pair tests. This result belongs as a *source-bias and identification section* of a future macro BALANCE study, not as new strict BALANCE worldline evidence.

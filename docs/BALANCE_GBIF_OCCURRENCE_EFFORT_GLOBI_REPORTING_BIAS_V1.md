# Independent GBIF occurrence effort versus GloBI documentation

**Status: REAL public data**, fetched 2026-10-24 and joined to the frozen 2026-10-19 GloBI source. This is a documentation-bias analysis, NOT empirical same-trait ecological conflict or a structural BALANCE result.

## Objective

The outcome-independent GBIF 12-family, 48-species panel (merged PR #247) yielded only 16 species with exact plant-target name matches among GloBI interactions. We ask whether species with documented GloBI relationships also have more indexed GBIF occurrence records, a proxy for public observational effort.

The original 48 species selected independently of GloBI records, family, taxon keys and row positions are ALL retained. Families were deliberately chosen and are **not** a representative angiosperm sampling frame.

## New real public API source

For all 48 frozen GBIF taxon keys we obtained TWO official GBIF occurrence/search JSON count queries:

- https://api.gbif.org/v1/occurrence/search?taxonKey=KEY&limit=0
- https://api.gbif.org/v1/occurrence/search?taxonKey=KEY&hasCoordinate=true&limit=0

All **96 query response texts** are archived in 12 four-species GBIF source JSON batches under data/external/gbif/2026-10-24/. Their Git blob hashes, original query URLs, selected species identities and counts are version-locked by data/BALANCE_GBIF_OCCURRENCE_EFFORT_48_SOURCE_MANIFEST_V1.json.

Source limitations: GBIF occurrence/search includes indexed records under the key, potentially infraspecific taxa; records are not independently verified specimen/observer-effort days, abundance, plant fitness or complete ecological sampling. API indices update over time. Text was obtained through a public content reader, not a byte-for-byte original HTTP archive. GloBI and GBIF snapshots are separated by five days.

**Major field distinction:** every selected taxonomy record previously had GBIF species/search numOccurrences=0, yet actual occurrence/search finds indexed occurrences for **45 of 48 species**. Never interpret the taxonomy-search field as a valid absence or a field-effort measurement.

## Quantitative source-observed association

| Measure | Original panel |
|---|---:|
| Selected species | **48**, in 12 selected families/orders |
| Total GBIF occurrence-search records | **20,131** |
| Of these with coordinates | **13,049** |
| Species with at least one GBIF occurrence | **45** |
| GloBI exact target-name documentation | **16 species** |
| No exact GloBI target-name record | **32 species** |
| Species with no GloBI record but WITH GBIF occurrences | **29** |

| Focal source group | Number of selected species | Median GBIF occurrence count | Median georeferenced count |
|---|---:|---:|---:|
| GloBI name-match documented | **16** | **701** | **442.5** |
| No exact-name GloBI relationship | **32** | **6.5** | **2.5** |

Thus, GloBI documentation is substantially concentrated among species with higher indexed GBIF occurrence counts in this **originally species-first** sample.

Five of the twelve families have both GloBI-documented and undocumented species: Fabaceae, Rosaceae, Rubiaceae, Brassicaceae and Ericaceae. In **all five**, documented species have a higher within-family median GBIF occurrence count. A descriptive within-family top-two vs bottom-two split shows **11/24** upper-half species vs **5/24** lower-half species documented in GloBI. Among the five mixed-documentation families only, the split is **7/10 versus 1/10**. These are post-open descriptive contrasts: family randomization, phylogenetic independence and observation/reporting comparability are NOT established. No p-value, causal detection mechanism or population estimate is inferred.

For illustration, *Solanum asperolanatum* has **4,244** indexed GBIF occurrences (2,372 with coordinates) and 103 archived GloBI relationship rows; *Oryza barthii* has **4,551** occurrences (3,719 with coordinates) and 9 GloBI rows. These are data-documentation counts, not ecological interactor frequencies or selection strengths.

## Ecological inference

A missing GloBI relation may reflect taxonomy, data-provider extraction and study effort, even where GBIF has occurrence records. The presence of an interaction label (e.g. pollinates, eats, visitsFlowersOf) does not identify a conflict between opposite floral trait optima. A biological conflict-prevalence analysis treating no GloBI association as a true negative would confound observation effort and taxonomic coverage with ecological state.

Source record counts may be correlated because widespread, conspicuous or economically important species attract more independent recording effort in both databases. The observed association does **not** prove that adding one GBIF occurrence causes GloBI to add an interaction, or that rare species experience fewer biotic interactions.

## Correct next macroecological target

Keep three outcomes in separate evidence layers:
1. GBIF occurrence-record coverage and coordinates (indexed exposure/study-effort proxy, unknown detection probability).
2. Public biotic interaction opportunities (GloBI verbatim relations, source and target orientation, accepted-taxon concepts and source-study evidence).
3. Actual directly tested opposing reproductive fitness components under a shared morphological trait coordinate, plus separately observed functional routing and accessible net alternative architecture.

In a larger preregistered species-first sample, fit a proper detection/effort layer before estimating ecological conflict prevalence. Include common-source/study and phylogenetic dependence; a record with no GloBI relation is UNKNOWN, not NO CONFLICT. Other interaction datasets and primary experiments are needed for the functional biological claim.

## Reproduction and strict ceiling

Original public text snapshots: data/external/gbif/2026-10-24/occurrence_effort_batch_01.json through occurrence_effort_batch_12.json.

Contract: data/BALANCE_GBIF_OCCURRENCE_EFFORT_48_SOURCE_MANIFEST_V1.json.

Auditor: balance_domain/gbif_occurrence_effort.py.

Runner: scripts/audit_gbif_occurrence_effort.py.

Source regression tests: tests/test_gbif_occurrence_effort.py.

Run pytest on the test file and run the auditor with --out-json and --out-csv pointing to new nonexisting paths. It outputs the full 48-species source-joined table, family ranks, original source SHA256 and explicit missingness/causality ceilings.

**No new independent floral fitness study, trade-off experiment, direct conflict load L, source-specific architecture cost K, net W_D versus W_S, phylogenetic selection analysis, or strict BALANCE occupancy is created by this public database linkage.**

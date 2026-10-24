# An outcome-blind botanical pilot: what public interactions actually cover

**Status: REAL PUBLIC DATA acquired from GBIF and GloBI on 2026-10-19. This is a 12-family cross-order convenience panel, NOT a representative random sample of all angiosperms. No new plant fitness experiment or strict structural BALANCE occupancy was measured.**

## Research question and selection

Previous BALANCE screens collected published cases in which interacting functions were already of ecological interest. Those examples are valuable positive mechanistic evidence but cannot represent the denominator of all flowering plants.

Here the protocol froze an outcome-independent GBIF taxonomic sample **before checking GloBI for the selected taxa**: 12 families each from a distinct angiosperm order, one predetermined GBIF accepted-species search page per family, and a second fixed SHA256 ranking choosing 4 accepted species names per page. All 48 names were selected without reference to pollination, herbivory, or prior conflict results, and no missing species was replaced with a known positive one. The family choices are convenience cross-order strata, not a random family sample.

Original official GBIF JSON and GloBI CSV bytes are archived under data/external/gbif/2026-10-19/ and data/external/globi/2026-10-19/. The source selection contract, original source family counts/offsets, selected taxa with authorship and GBIF keys, full retrieved interaction rows and source receipts are committed. Source workflow: https://github.com/zuizui0223/balance/actions/runs/39221661954.

## Actual 48-species source coverage

| Family, four species each | Species with at least one exact target-name GloBI row | Exact-name rows |
| --- | ---: | ---: |
| Asteraceae | 0 | 0 |
| Fabaceae | 3 | 5 |
| Orchidaceae | 0 | 0 |
| Poaceae | 4 | 39 |
| Lamiaceae | 0 | 0 |
| Rosaceae | 1 | 1 |
| Solanaceae | 4 | 125 |
| Rubiaceae | 1 | 2 |
| Ranunculaceae | 0 | 0 |
| Brassicaceae | 2 | 8 |
| Ericaceae | 1 | 8 |
| Myrtaceae | 0 | 0 |
| **Total: 12 families, 48 species** | **16** | **188** |

All 48 GloBI official API queries succeeded. The 32 species without a literal target-name match are **undocumented in this particular returned response**, NOT species without real pollinators, herbivores or other biotic interactions.

The downloaded GloBI source files contain 230 rows total: 188 exact target-name rows and 42 target-taxonomy mismatch rows, all 42 from the query on Solanum asperolanatum. These rejected rows are preserved in the original CSV and are not reassigned to the queried taxon.

### Extreme source concentration

A single sampled species, **Solanum asperolanatum**, contributed **103 of the 188 exact-name relationship rows (54.8%)**, including 80 rows with the original GloBI interaction label "eats". Four sampled Solanaceae species contributed 125 of the 188 exact-name rows.

Across all 48 sampled species, 90 rows were labelled "eats"; only **two** were labelled "visitsFlowersOf", both with **Hormathophylla longicaulis** as the plant target, and **none** were labelled "pollinates". These are literal source database categories, NOT ecological field rates or causal flower-visitation/fitness observations. They do not imply that the sampled species are rarely pollinated or that Solanaceae suffer greater natural herbivory.

### Name agreement is not author-level taxonomy

Of 188 exact target-name records, only **88** carry a matching external taxon key in the form GBIF:sampled_key. They are concentrated in just **two sampled species**:

- Solanum asperolanatum: 87 of its 103 exact-name rows have an exactly matching GBIF key;
- Ptilagrostis porteri: 1 key-matched row.

The other **100** records use external identifiers from other taxonomic systems (e.g. Catalogue of Life, Wikidata), generic unmatched names, or other naming namespaces. This does not make them false observations: they simply require an independent taxonomic concept and authorship crosswalk before combining with GBIF species traits or phylogeny. An exact GBIF key itself is also an index association, not independent confirmation of an experiment or plant reproductive fitness.

The GBIF species/search field numOccurrences was 0 for each selected GBIF taxonomy record. **This is not an independently verified GBIF occurrence-search count and does not establish that the plants have no GBIF observations.** Future work must obtain actual occurrence/effort through the GBIF occurrence API rather than interpreting taxonomy index metadata as sampling effort.

## What this changes for ecological inference

The first independently sourced plant association database demonstrates a major **measurement/coverage constraint** on a future macroecology of floral conflict:

1. Having a recorded visitor or consumer is an **interaction opportunity**, not evidence that two functions favor opposed states of the same floral structure.
2. Lack of a record is a source-data non-detection, not an experimentally demonstrated ecological absence.
3. A genus/family source taxon or a generic "interactsWith"/"pathogenOf" label is not necessarily a species-specific reproductive fitness effect.
4. The 48 selected names sample a breadth of taxa but are still conditional on 12 chosen families, source API name matching and the GloBI provider's heterogeneous literature coverage.
5. Any study claiming species-level conflict prevalence from GloBI alone would conflate network-reporting effort, taxonomic matching and actual biotic exposure.

A direct BALANCE claim additionally requires a demonstrated common floral trait coordinate, measured opposing fitness gradients, functional organization and a separately viable differentiated structural architecture on the same net fitness scale. None is available from a public association list.

## Next data acquisition for publishable ecology

Preserve this initial 48-species denominator and **supplement** it rather than replacing poorly documented taxa. Add an independently versioned species-first GBIF occurrence-effort layer; validate taxon author concepts across GloBI, GBIF, Catalogue of Life and Wikidata. Add independent specialized floral visitation datasets beyond GloBI, then map function pairs: pollinator attraction, floral herbivory, nectar robbery, pollen consumption, male/female interference, and their experimentally demonstrated or untested trait conflicts.

A later biological test must measure a species-by-function-pair-by-structure-by-ecological-context outcome, retaining actual direct negative tests and NOT-TESTED records and phylogenetic dependence. No current frequency of true opposing selective demands is estimated.

## Reproduce the source analysis

Canonical:
- data/BALANCE_GBIF_SPECIES_FIRST_CROSS_ORDER_PANEL_V1.json — pre-interaction family frame and seed.
- data/BALANCE_GBIF_SPECIES_FIRST_SELECTED_V1.json — selected 48 GBIF accepted species.
- data/BALANCE_GBIF_GLOBI_SPECIES_FIRST_READOUT_V1.json — all 48 GloBI search outputs with coverage/hold statuses.
- data/external/gbif/2026-10-19/species_first_*.json and data/external/globi/2026-10-19/species_first_*.csv — actual original downloaded public data.
- balance_domain/gbif_species_first_coverage.py — independently rederive sample from GBIF pages and verify GloBI source SHA256, exact target-name counts and directly matching GBIF taxon identifiers.
- scripts/audit_gbif_species_first_coverage.py — new JSON plus complete 48-species CSV, no overwrite.
- tests/test_gbif_species_first_coverage.py — actual downloaded public source regression tests.
- tests/test_gbif_species_first_acquisition.py — synthetic outcome-blind design and source failure tests.

Run: python scripts/audit_gbif_species_first_coverage.py --out-json /path/to/result.json --out-csv /path/to/species_table.csv

**Claim ceiling: public relationship-documentation coverage and taxonomic-source uncertainty, NOT a newly observed fitness conflict, global pollinator guild rate, true absence, or structural BALANCE direct biological occupancy.**

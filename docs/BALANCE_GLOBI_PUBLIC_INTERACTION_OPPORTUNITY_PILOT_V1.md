# First independent public interaction database pilot: GloBI, four plant taxa

**Status: ACTUALLY ACQUIRED public Global Biotic Interactions records (snapshot 2026-10-19), not another extraction of the BALANCE source-positive studies. This is data coverage and taxonomic-integrity evidence only, NOT direct source-identified functional conflict, fitness components, ecological prevalence or structural BALANCE occupancy.**

## Why this matters

The four *Polemonium / Narcissus / Solanum / Ipomopsis* source-overlap cases in BALANCE's literature synthesis are useful biological hypothesis generators, but they were selected precisely because publications investigated interesting reproductive functions. Such literature-derived rows cannot form an outcome-blind estimate of macroecological conflict prevalence.

GloBI provides an **independent interaction association database** with a public API (https://www.globalbioticinteractions.org/how-to), so we performed an exploratory snapshot acquisition for the four cases before attempting a species-first large-scale sampling frame.

Queries were made on 2026-10-19 using the public endpoint:

    https://api.globalbioticinteractions.org/interaction.csv?targetTaxon=SPECIES&limit=500

Raw textual CSV responses are now archived **exactly as returned by the content-extraction service** under data/external/globi/2026-10-19/. Each file's Git blob SHA1 is recorded in the manifest; the analysis script additionally emits a raw text SHA256. These are versioned **response-text snapshots**, not the original HTTP byte sequence or a versioned release of GloBI. The GloBI website warns that live per-species query results can change between requests; there is no claim of an immutable network generation process.

## Actual source record audit

| Queried focal botanical name | API relationship rows | Rows with EXACT target-side species name | Discarded from the strict focal target set |
|---|---:|---:|---:|
| Polemonium viscosum | 30 | **28** | 2 |
| Narcissus assoanus | 2 | **2** | 0 |
| Solanum rostratum | 96 | **0 — taxonomic HOLD** | 96 |
| Ipomopsis aggregata | 126 | **66** | 60 |
| **Total** | **254** | **96** | **158** |

These numbers are the actual archived public API text rows in the four source-selected queries, not independent studies, individuals or population frequencies. The 158 rejected/mismatched rows are **kept in the raw audit**, never silently assigned to the queried species.

### GloBI reported association types, with correct scope

- Polemonium exact target side: **7 database "pollinates" relations, 2 "visitsFlowersOf"**, plus broader "interactsWith", host/pathogen and adjacent categories. Taxon labels in those relations can be generic taxa (e.g. Apoidea or Bombus), not independently verified species-level pollinator vouchers.
- Narcissus exact target side: **1 "visits", 1 "pathogenOf"**. This does not mean Narcissus has only two ecological interactions in nature.
- Ipomopsis exact target side: **8 "pollinates", 16 "visitsFlowersOf"**; additional recorded "interactsWith", "eats", etc. One query record using Ipomopsis as the **source** rather than the **target** would be falsely added by an either-side string match. The strict target-side count is 66, not 67.
- Solanum query: **96 raw rows are ALL attributed to the different target label "Solanum angustifolium"**, not to the literal requested target "Solanum rostratum".

The third issue is not an ordinary misspelling. The Kew Plants of the World Online backbone distinguishes the **accepted focal Solanum rostratum Dunal** from a homonymous/historical **Solanum rostratum L'Hér. ex Dunal**, which POWO treats as a synonym of **Solanum angustifolium Mill.** These distinct authorships cannot be reconstructed from the author-free GloBI target name column. See:

- focal Solanum rostratum Dunal: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:820804-1
- different historical name Solanum rostratum L'Hér. ex Dunal: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:820803-1
- accepted Solanum angustifolium Mill.: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:818253-1

The correct GloBI interpretation for the focal S. rostratum Dunal is **TAXON_NAME/HOMONYM_UNRESOLVED**, **not** "96 observations of S. rostratum" and **not** "zero true ecological interactions of S. rostratum".

## What this DOES and DOES NOT prove about ecology

**Directly shown by this newly acquired database snapshot:** public plant–agent association records are unevenly documented and a name-only join would mix unrelated taxonomic concepts. Some retrieved associations have explicit pollination or flower visitation labels. The key ant attack on Polemonium demonstrated by Galen & Cuba (2001) is not recovered as an independent directly typed ant-predation record in this initial API response, illustrating coverage bias in one snapshot, not an absence of ants in nature.

**Not identified from interaction associations:** opposing trait optima, causal costs of visitation/ant attack, an evolutionary trade-off, morphological division of labour, seed fitness, total network completeness, species interaction richness, or the BALANCE net structural W_D-W_S ranking. Even a row labelled "pollinates" is not a verified treatment-effect experiment on reproductive success. An unspecific "interactsWith" row is especially unsuited to a conflict claim.

## Required next macroecological data acquisition route

1. **Freeze an outcome-blind species-first denominator** (e.g. a reproducible, stratified GBIF taxonomic/occurrence sample). Do not choose all species because GloBI has a pollinator or interesting conflict record.
2. Retrieve *both taxonomic directions*, keeping query term, exact authorship, accepted name/taxon IDs, source vs target orientation and a source-ID crosswalk from a versioned taxonomic backbone.
3. Snapshot raw public API records and exact study IDs if available, avoiding duplicate broad taxon names as independent pollinator species; retain empty records and unknown coverage, with study effort.
4. Build a separate **biotic interaction opportunity** layer (recorded pollination, florivory, herbivory, nectar robbing or other taxa) without inferring direct conflict.
5. Only in a second source-independent layer extract raw direct opposing-selection/interference experiments and architecture observations on the same trait and fitness scale. Separate potential and naturally realized conflict, and retain properly designed negative, not measured, and unresolved tests.
6. Include species/phylogenetic dependence and original experiment plant/flower sampling units; report coverage/missingness before modelling interspecific generality.

The current four were **source selected** and thus are useful only as a taxonomic/API validation fixture, not a sampled population for comparing pollinator-versus-ant network prevalence.

## Executable reproducibility

- data/external/globi/2026-10-19/*.csv — four archived live GloBI API text responses; **254 unmodified API relationship rows**.
- data/BALANCE_GLOBI_OPPORTUNITY_SOURCE_SNAPSHOT_V1.json — per-species original query URL, Git blob identity, exact counts, author-homonym HOLD, GloBI release/coverage limitations.
- balance_domain/globi_opportunity.py — exact target-side species qualification, original CSV schema and Git blob checks, verbatim interaction-type counts, source side-join protection and fail-closed Solanum homonym.
- scripts/audit_globi_opportunity_pilot.py — read-only, no-overwrite summary with Git blob and SHA256 provenance.
- tests/test_globi_opportunity.py — tests from ACTUALLY ACQUIRED public GloBI response texts, verifying 254 raw/96 strict/158 unmatched, author-name ambiguity, non-specified higher-rank source taxa and exclusion of a fake SCH/BALANCE finding.

Run:

    python scripts/audit_globi_opportunity_pilot.py --out /path/to/new_globi_receipt.json

External sources: GloBI API how-to https://www.globalbioticinteractions.org/how-to ; Kew POWO links above; original Polemonium bee/ant experimental finding https://doi.org/10.1111/j.0014-3820.2001.tb01313.x .

**Publication and inference ceiling:** the GloBI snapshot is independent public BIOTIC ASSOCIATION data, not yet a new independently quantified functional-conflict dataset or a valid sample for a globally representative biological selection result. The ecological hypotheses in BALANCE remain unproved at a population/macro level until an outcome-blind sampling frame and direct reproductive experiments are obtained.

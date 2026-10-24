# Independent cross-species structural-opportunity audit: AusTraits v7.0.0

**Date:** 2026-10-19. **Status:** prospectively frozen acquisition and comparison protocol; biological outcome not interpreted until the exact v7 source is acquired and checked.

## Why this is necessary

The previous [source-screened U2 and plant-pilot comparison](BALANCE_SOURCE_STRATIFIED_CONFLICT_ARCHITECTURE_COMPARISON_V1.md) recovers meaningful counterexamples to deterministic conflict-to-modularity reasoning, but the plant cases were intentionally **selected for interesting biological functions or structures**. They cannot be used to estimate the distribution of trait architecture in flowering plants. This audit begins from a **pre-existing independent multi-species trait archive**, without selecting species because they have a positive experimental conflict or an unusual structure.

External ecological motivation and sources:
- AusTraits public dataset, version **v7.0.0**, Zenodo record versions API https://zenodo.org/api/records/3568418/versions.
- [Island repository's 2026-07 source-backed pilot](https://github.com/zuizui0223/island/blob/main/docs/experiments/free_bulk_trait_source_pilot.md) already recovered >1.7 million source records, with independent flower sex, floral symmetry, and pollination categories. The existing proven, checksum-audited fetcher is pinned to [island immutable commit 2a1fd059](https://github.com/zuizui0223/island/blob/2a1fd0591bf31a3aea2cd217cbe8e76886490eb0/src/island_v2/fetch_austraits_bulk.py). BALANCE copies that exact source fetch implementation under `balance_domain/island_austraits_fetch.py`.
- New flower trait source options include eFLOWER, and eFLOWER_Dun_2022 for flower-level sexual morphology, but **neither is a source of a measured ecological fitness trade-off**.

## Frozen source selection / value contract

Select a Zenodo release with version **exactly 7.0.0**, not simply whichever release is newest. Stop with HOLD unless exactly one release matches. Obtain its plain-text ZIP and verify the author-declared checksum **before reading trait values**. Record the archive SHA-256 and source DOI. Do not use a manually curated list of 'successful specialization' taxa.

The six exact source trait-name targets are frozen **before opening their joint distribution**:

```text
sex_type
flower_structural_sex_type
flower_perianth_fusion
flower_perianth_symmetry
pollination_syndrome
pollination_system
```

Rows remain identifiable by `taxon_name`, `trait_name`, `trait_value`, `trait_unit`, `dataset_key`, and version-linked `source_record_id`. Store manifest and aggregated readout only; do not redistribute the full mixed-license AusTraits records. The raw archive is discarded after checksum verification and analysis.

**Source code for this audit:** `balance_domain/austraits_architecture_macro.py` and `scripts/run_austraits_architecture_macro.py`. The live run is under `.github/workflows/austraits-independent-architecture.yml` and uploads its verified output to a time-limited GitHub Actions artifact.

## Main descriptive screen and honest construct limits

The primary target is **structural opportunity**, not a proven selectively evolved module. `sex_type` is the species-level sexual system; `flower_structural_sex_type` is flower-level morphology; `flower_perianth_fusion` is morphological integration only in a descriptive botanical sense, *not* identified ecological multifunctional integration. Never substitute `sex_type` for male-female interference strength or `flower_perianth_fusion` for BITA's architecture cost.

For source-verbatim values, use only an exact binomial (two tokens) and an unambiguous single normalized category per species. Exclude and count multi-label conflict and unmapped values. No fuzzy synonym joins, no genus-level state imputation, no undocumented pollination-syndrome conversion. Preserve dataset provenance and differing source semantics; a pair of joined species traits is not an independent experimental replication.

### Prespecified ecological-opportunity contrast

Among species with an exact, singly coded `sex_type` and `pollination_syndrome`, compare the **observed separation of reproductive sex organs at plant organization levels** across raw `wind` versus raw `insect`:

| Raw sex_type | Descriptive organizational category |
| --- | --- |
| hermaphrodite | `SHARED_SEX_SYSTEM` |
| monoecious | `SEX_SEPARATED_AMONG_FLOWERS` |
| dioecious | `SEX_SEPARATED_AMONG_INDIVIDUALS` |

Other forms (gynodioecy, andromonoecy etc.) are retained in the raw coverage counts and excluded from this narrow contrast, **not** assumed absent or undifferentiated. Pollination values are exactly `wind` or `insect`; labels such as "bee", "bird", "insect wind" or "self" are not silently pooled.

The descriptive estimand is the difference in the proportion with non-hermaphrodite organizational states between `wind` and `insect`. It is reported only if **each raw pollen-mode arm has >=20 exact species and >=5 genera**. Otherwise return HOLD. The script additionally counts genera with both modes and reports their mean within-genus difference only as a descriptive diagnostic, never a species-independent causal estimator or phylogenetic correction.

The primary comparison is **not** a test of trade-off-induced new structures. Even a strong organizational association would still need independent SCH conflict evidence, BALANCE common-fitness-scale architecture alternatives, SLK/PAYOFF genetic accessibility, and historical origin ordering.

## Counterfactuals and future link

If large source-trait coverage is achieved, the next legitimate operation is to take **the independent source denominator** and overlay verified SCH source-specific conflict status, retaining unmeasured taxa as unmeasured. Then test for replicated **function-pair-specific** structural opportunity while stratifying taxonomy, source/country/study coverage and exposure. No causal evolutionary interpretation can be made without transitions and historical control cases.

If the source does not furnish enough exact cross-trait overlap, that is a *real null feasibility result* which precludes a pooled macro model. Do not redefine categories or lower support thresholds after reading results just to obtain a statistic.

## Execution, provenance, limits

```bash
pytest -q tests/test_austraits_architecture_macro.py
python scripts/run_austraits_architecture_macro.py --out-dir /tmp/balance-austraits-v7
```

Only source-acquisition summary JSONs are retained:
- `austraits_structural_opportunity_manifest.json`
- `austraits_structural_opportunity_readout.json`

The current confirmed causal-inference ceiling does not change: structural sex and pollination associations are **neither** opposing trait optima **nor** measured `Phi=R-K`, `eta`, or historical modularization. The [BITA integrated causal programme](https://github.com/zuizui0223/bita/pull/362) remains the place where these separate evidence layers eventually meet.

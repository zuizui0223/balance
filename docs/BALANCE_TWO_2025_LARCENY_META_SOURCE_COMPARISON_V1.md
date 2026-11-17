# Two independent 2025 floral-larceny meta-analyses: original-data cross-audit

**Date:** 2026-11-17. Exploratory original-source quality and linkage audit, not a new meta-analysis or new biological experiment. Do NOT use these data as direct BALANCE specialization or structural fitness evidence.

## Public original sources

| Study | Primary publication | Original source | Source size |
|---|---|---|---|
| Zhong et al., Plant Diversity (2025) | [DOI 10.1016/j.pld.2024.12.004](https://doi.org/10.1016/j.pld.2024.12.004) | [Figshare original data/code](https://figshare.com/s/99df84fe5c473dc85d85), author share, item 27129204 | **776 effects, 153 papers, 120 plant species** |
| Leal et al., Ecology (2025) | [DOI 10.1002/ecy.70036](https://doi.org/10.1002/ecy.70036) | [Zenodo original data/code](https://doi.org/10.5281/zenodo.14773082) | **267 effects, 69 study IDs, 60 plant species** |

Original Zhong workbook SHA256: 6554409f22b09156ee1c2a35ee2547eb5ae28c4a25934b9c639d8a19ea7fe9b4.

Original Leal ZIP SHA256: 3f6e9b5b55ad8090f41f62faeb2f306c6700a9beb274ac6467106ebab9573c2d. Nested CSV complete_hedges.csv SHA256: 4ecd656251f778189d8c13f3608ba99f4de942656fecfe6f2edc8d2509a3d2cb. Original R source SHA256: 9d60311b102cf27c234f9d6c63eeae602c91768950466e7579ed3a03f0488013. Each downloaded original is checked in dedicated GitHub Actions, and source-relative data never silently changed.

## Finding 1: The archived Leal effect-size metric is ROM rather than standardized mean difference

Leal's published source is named complete_hedges.csv and some code/metadata refer to Hedges' g. **Its R code uses the metafor escalc("ROM", ...) measure (log of mean ratio)**, not the standardized Hedges' g estimator. The published yi field matches ln(mean_larcenist/mean_control) for **264 of 267** rows (absolute tolerance 0.000001). Three archived yi values differ, all with the sign exactly reversed against the supplied input means:

| Source sample ID | Source study | Status |
|---|---|---|
| 79 | Fumero-Caban and Melendez-Ackerman 2013 | yi sign opposite to calculated ROM |
| 88 | Gelvez-Zuninga et al. 2016 | yi sign opposite to calculated ROM |
| 178 | Souza et al. 2019 | yi sign opposite to calculated ROM |

Additionally, **7 of 267 source vi values** differ from the standard delta-method ROM sampling variance based on reported group SD, mean and N. Sample IDs **56, 79, 81, 83, 84, 88, 178**. These discrepancies may reflect orientation coding or preprocessing not carried into the archived input fields. They are **not established publication errors**. The original results are retained without any correction, and the whole published meta model has NOT been independently refitted or invalidated.

## Finding 2: Overlap and exposure-route coding matter

Conservatively normalizing first-author surname, year, and botanical binomial yields **45 candidate overlapping paper×species sources** between the two archives. **Two candidate keys collide** and are explicitly unresolved. Matching on those fields does **not** establish that two effect sizes use the same source DOI, treatment, population or time. Manual matching must use original DOI, treatment contrast, guild and response.

Among those 45 provisional overlaps, **six** have differing robber/theft type sets:

| Botanical source | Candidate author-year | Zhong category | Leal category |
|---|---|---|---|
| Alpinia kwangsiensis | Deng 2004 | robber | thief |
| Alpinia roxburghii | Deng 2015 | robber | thief |
| Impatiens oxyanthera | Li 2021 | robber | thief |
| Ipomopsis aggregata | Richman 2018 | robber + thief | robber |
| Jacaranda caroba | Quinalha 2017 | robber | thief |
| Oreocallis grandiflora | Hazlehurst 2016 | robber | thief |

**Do not call these errors before primary-source adjudication.** Two published papers can use different operational robbery/thievery definitions, may select different behavioral subcases, and same first-author-year-plant does not certify identical effect contrast. In particular, the Alpinia 2015 squirrel interaction is described with both 'nectar robbery' and 'nectar theft' language in passages of the original article.

## Finding 3: Within-original-study contrasts are extremely sparse

Zhong: only **3 paper×species** groups have both robber and thief categories; **5 paper×species×outcome** groups have both. Leal: **1 study×plant** with both source types; **1 study×plant×metric**, namely Zhang et al. 2014 Corydalis ambigua **visitation**. This is NOT a seed/fitness within-study route contrast. Therefore mean robber/theft fitness differences in the two published meta-analyses mostly derive from different combinations of original studies.

This audit does not pool 776+267 effects as 1043 independent tests. Original meta effects may repeat the same original study and plant, their errors are dependent, and even the two author meta-analyses share primary publications.

## Biological interpretation and BALANCE novelty ceiling

Zhong already published outcome-stage differences, and Leal already published route-specific average patterns. New BALANCE work must not rediscover these claims. The most defensible extension is a **registered cross-study study-conditional model** testing whether *operationally verified access route × pollen saturation × visit efficacy × floral injury* predict the transfer of a reward cost into actual pollen delivery, fruit initiation and viable seeds.

Before that model:
1. Re-read the six discordant source papers, confirm exact feeding geometry (corolla hole vs natural entrance), nectar removal, pollen contact and damage.
2. Reconcile three yi and seven vi deviations with the original Leal preprocessing or source paper before recomputing an effect.
3. Link duplicated original studies by DOI, plant species, original treatment and endpoint, retain uncertain records as unresolved.
4. Harmonize seed set denominators (per ovule, per sampled mature fruit, per plant) and true maternal or site clustering.
5. Use study-level out-of-sample validation; no nominal p-value from pooled non-independent effect rows.

Strict BALANCE conflict load L, differentiation cost K, Phi and optimized shared vs differentiated structural fitness remain unmeasured. Original frozen V4, 21 U6 source taxa, 42 independent architecture coding slots and SLK are unchanged.

## Inspectable source replay

Run the official original-data workflow in GitHub Actions: [.github/workflows/leal-2025-ecology-source.yml](../.github/workflows/leal-2025-ecology-source.yml). It downloads the Zenodo originals and Zhong Figshare original, verifies source-level MD5/SHA256, runs the source-gated tests, and exports CROSS_META_READOUT.json as an Actions artifact. Local command:

    BALANCE_TWO_META_ZHONG=/path/to/Zhong.xlsx BALANCE_TWO_META_LEAL=/path/to/Leal.zip python -m pytest -q tests/test_two_larceny_meta_sources.py
    python scripts/audit_two_larceny_meta_sources.py --zhong-original /path/to/Zhong.xlsx --leal-original-zip /path/to/Leal.zip --out /tmp/cross_meta.json

Draft stacked PR only. No merge and no direct architectural fitness promotion.

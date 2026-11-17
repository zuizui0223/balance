# Five-stage source identity audit: Corydalis 2018 versus Gentiana 2020

**2026-11-17. One new audit of an existing meta-analysis, NO new biological study or confirmatory causal result.** Parent [source stage inventory](BALANCE_LARCENY_2025_STAGE_MATCHING_V1.md), official 2025 meta [Zhong et al.](https://doi.org/10.1016/j.pld.2024.12.004), authors' original [Figshare data and code](https://figshare.com/s/99df84fe5c473dc85d85) (CC BY 4.0).

## Why this audit

The authors' original **776-effect, 153-paper, 120-species** table contains only two paper×species sources with the same **five named response classes**: nectar volume, legitimate visits, pollen deposition, fruit set and seed set. The parent inventory establishes their identities. Here we look at **the actual 47 effects** in their two paper×species groups, rather than interpreting co-reporting as a causal pathway.

| Source paper and plant | Meta ref-ID | 5-stage effects by endpoint (nectar/visit/pollen/fruit/seed) | Other effects | Five-stage records |
|---|---:|---|---:|---:|
| [Heiling et al. 2018, *Corydalis caseana*](https://doi.org/10.1111/oik.05440) | 29 | 1 / 1 / 3 / 2 / 2 | 2 | 11 |
| Zhang et al. 2020, *Gentiana straminea* (full original publication identity **unverified**) | 101 | 4 / 2 / 4 / 4 / 4 | 18 | 36 |

**Both have ZERO experiment-level classifications common to all five stages**: in Heiling 2018, nectar and visits are labelled individual-flower while fruit and seed are whole-plant; pollen has both levels. In the Gentiana extraction, nectar and pollen deposition are individual-flower while visit rate, fruit and seed are whole-plant. These are broad **original meta-table labels**, not proof about all field observation identities. Absence of a common recorded level means a naive same-grain five-stage panel cannot be constructed. Original experiment and treatment/cohort identifiers are **not present** in these 776-effect rows.

## Why assigning row order makes false results

If someone simply links all stage effects from one paper, the possible **Cartesian products of published endpoint effects**, *not actual ecological paths*, are:

- Corydalis: `1 × 1 × 3 × 2 × 2 = 12` hypothetical five-stage combinations.
- Gentiana: `4 × 2 × 4 × 4 × 4 = 512` hypothetical five-stage combinations.

Within fruit vs seed alone:
- Corydalis: **2×2=4 arbitrary combinations**; `yi_seed − yi_fruit` ranges **−0.19139 to +0.23418**, with **2 positive and 2 negative**. The inferred direction **flips depending on fabricated pairing**.
- Gentiana: **4×4=16 arbitrary combinations**, `yi_seed − yi_fruit` ranges **−0.42831 to −0.23910**, all **16 negative**. This is a **pairing-independent ordering of the available numbers**, not 16 replications or a matched causal stage contrast.
- In Gentiana, every recorded nectar-volume and pollen-deposition effect is negative; every visit-rate and fruit-set effect is positive; every seed-set effect is negative. This is genuinely interesting **mixed-stage source description**, but original treatment identity and sampling populations are not identified.

Both groups therefore have **0 verified full matched cohorts** in the *meta-only dataset*, but 0 is **missing evidence, not a measured zero effect**. Neither a mediation coefficient nor any p-value is warranted. Outcome effects share original source studies and may share contrasts; the between-endpoint covariance is unavailable.

## Independent primary-source verification and prior art

**Heiling et al. 2018**: Original primary paper [DOI 10.1111/oik.05440](https://doi.org/10.1111/oik.05440), primary raw data [Dryad DOI 10.5061/dryad.bh6hs70](https://doi.org/10.5061/dryad.bh6hs70) with workbook **Heiling.et.al.Oikos.2018.data.xlsx** publicly listed, CC0. The paper *already* tests three explanations for neutral outcomes: **pollinator non-discrimination**, **legitimate-pollinator prevalence** relative to robbers, and **pollen saturation even in unvisited stigmas**. These mechanisms therefore **cannot be billed as new discoveries by BALANCE**. The paper's differently staged experiments and the published meta `yi` fields are not automatically linked observations. In this audit the original Dryad workbook is **listed/identified but not independently downloaded/validated**.

**Gentiana original 2020 source**: The meta file describes a source as *The Effects of Pollinators, Nectar Robbers and Abiotic Environment on Reproductive Ecology of Three Alpine Species in Alpine Meadows on the Qinghai-Tibet Plateau*, citation shorthand **Zhang et al., 2020**; the effect rows identify *Gentiana straminea*. A uniquely matching primary-publication DOI or source original data has **not been independently verified**. Some adjacent literature on Gentiana reproductive ecology belongs to other studies from 2005–2007 and **must not be substituted**. Treat ref 101 as **PUBLICATION_SOURCE_VERIFICATION_PENDING**, rather than assign an invented journal or DOI. The apparent repeated four effects across several endpoints must not be assumed to be four matched cohorts or dates.

## What can be called a result now

1. The true global evidence denominator is still 153 papers / 120 species / 776 effects, and the 5-stage co-report denominator is 2 papers.
2. In **0/2** co-report papers is there a shared experiment-level category across all five stages; this is a *data-architecture limitation*, not proof of ecological disconnection.
3. Corydalis stage contrasts are **pairing-sensitive**; Gentiana's fruit versus seed direction is **numerically pairing-invariant** but **not experimentally linked**.
4. At least one proposed physiological mechanism — pollen saturation and non-discriminating pollinators in Corydalis — is already directly developed in prior research. Novelty must come from **prospectively defined across-study conditional prediction** or experimentally linked stage losses, not rediscovery of the pathway labels.

## Next admissibility gates for an actual macro model

Obtain the exact original Heiling workbook; link each original study's **year, site, floral cohort, treatment/control and endpoint definition** to the 2025 meta-effect IDs. Trace the true Zhang 2020 primary bibliographic source before inferring anything about its treatment number, date or manipulation. Create a joint analysis table **only for verified same-treatment pairs**; retain ambiguous assignments as `UNRESOLVED`. Reserve source-independent followout programmes for external validation, and compare pollen-limited versus saturated systems only with justified source-defined scales and covariances.

**No impact** on original U6 21 source admissions, 42 unopened A/B coder rows, V4 confirmatory model/outcomes, or SLK manuscript. No strict BALANCE `L/K/Phi/W_S*/W_D*` has been estimated.

## Reproduce against the official 2025 source

```bash
BALANCE_LARCENY_2025_ORIGINAL=/path/to/ORIGINAL_776_META_EFFECTS.xlsx \
  python -m pytest -q tests/test_larceny_two_five_stage_sources.py

python scripts/audit_larceny_two_five_stage_sources.py \
  --original-meta /path/to/ORIGINAL_776_META_EFFECTS.xlsx \
  --out /tmp/BALANCE_TWO_FIVE_STAGE_SOURCES.json
```

Exactly pinned original XLSX SHA256: `6554409f22b09156ee1c2a35ee2547eb5ae28c4a25934b9c639d8a19ea7fe9b4`; refuse changed data or publication/stage identifiers. New workflow replays the audit from the **actual private-share Figshare ZIP** and archives the source-bound JSON. Keep PR draft/unmerged.

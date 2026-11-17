# Heiling 2018: true treatment identity for seed effects, not fabricated five-stage mediation

**2026-11-17 / source-bound exploratory provenance analysis.** This reconciles the existing 2025 floral-larceny meta workbook with **published 2018 original-paper treatment summaries**. It is not a new trial or evolutionary result.

## Original sources and accessibility

- Heiling, J. M. et al. (2018), *Oikos*, [Why are some plant–nectar robber interactions commensalisms?](https://doi.org/10.1111/oik.05440). An author-posted full article is publicly available: https://jacobmheiling.weebly.com/uploads/2/6/1/1/26112358/heiling_et_al-2018-oikos_vol127_issue11.pdf
- Published raw original dataset: [Dryad 10.5061/dryad.bh6hs70](https://doi.org/10.5061/dryad.bh6hs70). Official public REST metadata is verified: version **9716**, single XLSX file **41496**, filename `Heiling.et.al.Oikos.2018.data.xlsx`, size **122,150 bytes**, registered MD5 `31e7e67fa98c5ffb7b4b133686191b90` (CC0).
- In the current GitHub Actions environment, unauthenticated source download **did not succeed**: the published browser file-stream endpoint returned **HTTP 403**, REST file-download endpoint **HTTP 401**. Both outcomes are source logged in [the recovery workflow](https://github.com/zuizui0223/balance/actions/runs/44061818575). **No original Dryad XLSX was read** in this specific audit; no fabricated original plant records, treatment assignments or sample covariance.
- Independent comparison source: the Zhong et al. (2025) [Plant Diversity meta-analysis](https://doi.org/10.1016/j.pld.2024.12.004), original [Figshare archive](https://figshare.com/s/99df84fe5c473dc85d85). Its downloaded, unchanged effects workbook is validated at SHA256 `6554409f22b09156ee1c2a35ee2547eb5ae28c4a25934b9c639d8a19ea7fe9b4`.

## What the primary experimental paper actually did

A **single 2015 experimental programme at Kebler Pass** followed plants in three assigned groups: **control (no robbery), PR (one-time artificial robbery), CR (artificial robbery every day)**, with **five plants per group and 15 plants total**. Authors say plants were *haphazardly assigned*, **not independently verified randomized**. Each plant contributed selected flowers from five lateral racemes, about 10–20% of flowers. They measured pollen receipt, proportion fruit set and mean seed set per raceme, modeling plant as a random effect when subsampling racemes. Reported overall treatment tests were not significant (pollen receipt p=0.11, fruit p=0.36, seeds p=0.83). The unrelated flower visitation and single-visit pollen saturation experiments are **not the same fifteen plant units** and cannot be joined by row number.

## Original means versus source meta ln response ratios

| Source quantity | Control | PR | CR |
|---|---:|---:|---:|
| Paper mean seeds per raceme | 7.56 | 6.73 | 8.65 |
| Original published fruit-set proportion | 0.74 | 0.73 | 0.83 |
| Pollen receipt (published square-root-transformed mean) | 24.83 | 28.16 | 28.54 |

2025 meta source effect identities (original ref-ID **29**, *Corydalis caseana*):

| Potential treatment block from **original meta row order** | Pollen effect ID/lnRR | Fruit effect ID/lnRR | Seed effect ID/lnRR |
|---|---|---|---|
| PR candidate | 254 / +0.19549 | 255 / −0.09949 | **256 / −0.116296** |
| CR candidate | 257 / +0.18981 | 258 / +0.07510 | **259 / +0.134688** |

**Exact robust result:** `ln(6.73/7.56) = −0.11629604653480505` matches source meta ID **256** to the floating-point limit, and `ln(8.65/7.56) = +0.13468813075234634` similarly matches **ID 259**. Swapping the two treatment labels does **not** yield the matches. Thus the identity of these **seed-source effects** is supported by independent article-summary arithmetic.

**Important unresolved point:** the source meta fruit lnRR values (−0.09949 and +0.07510) **do not** match ratios of rounded published fruit means (`ln(.73/.74)=-0.01361`, `ln(.83/.74)=+0.11498`). Source meta pollen values also cannot be reconstructed by ratios of reported **square-root-transformed** means without knowing the original pre-transformation data and exact variance treatment. Row-adjacent pollen and fruit effects have plausible PR and CR labels but **their original experimental treatment identities and outcome denominators remain unverified** without 2018 raw XLSX. This is a data lineage difference, not an established error in the 2018 paper or 2025 meta-analysis.

For illustration only, joining these contiguous meta blocks gives `yi_seed − yi_fruit = −0.01681` (PR candidate) and `+0.05959` (CR candidate); opposite signs, with **unknown within-plant covariance**. These are not two independent ecological studies, not identified causal stage effects, not original source-assured treatment pairs, and not a valid multivariate mixed-effects statistical test.

## What is new and what is prior art

This audit **rescues a limited but verified treatment mapping** which was invisible in the 2025 meta's generic `experiment_level` label and rules out a naive fully paired five-stage analysis. It does **not** discover Heiling's original three mechanisms: the 2018 paper already tested pollinator non-discrimination, legitimate/robber prevalence and pollen saturation. In a new macro model, these can be **predefined candidate moderators**, not claimed original findings.

An admissible follow-up: recover the Dryad original XLSX via authorized download, inspect sheets and plant/raceme/treatment keys, verify all 3 response variables within the same experimental programme and each meta effect computation, and only then estimate correlated fruit/seed contrasts. The unrelated visits and nectar saturation experiments require separate units even if from the same paper. No strict BALANCE \(L\), \(K\), \(\Phi\), \(W_D^*-W_S^*\) comparison has been obtained.

## Replay

```bash
BALANCE_LARCENY_2025_ORIGINAL=/path/to/ORIGINAL_776_META_EFFECTS.xlsx \
  python -m pytest -q tests/test_heiling_2018_paper_treatment_map.py

python scripts/audit_heiling_2018_paper_treatment_map.py \
  --source /path/to/ORIGINAL_776_META_EFFECTS.xlsx \
  --out /tmp/heiling_2018_paper_meta_identity.json
```

The frozen paper means are explicitly **manuscript summaries**, not invented raw plants. The read-only script checks original Figshare XLSX SHA256, ID/endpoint mapping, seed mean ratio identity and treatment-overstatement guards. Source-only branch PR #267 remains **draft/unmerged** on `main`; 21 U6 taxa, 42 independent A/B coder forms, sealed V4 outcomes and SLK manuscript are untouched.

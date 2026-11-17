# Source-level guild and reproductive endpoint gate: Leal 2025 samples 56, 87, 88

**17 November 2026. Independent original 2016 primary-paper audit; no new biological studies, no re-fit of published mixed/phylogenetic meta models.** This is a deliberately strict source-quality investigation of original published Leal et al. (2025) effect rows.

## Authoritative source provenance

- Cuevas & Rosas-Guerrero (2016), *Plant Biology*, [DOI 10.1111/plb.12311](https://doi.org/10.1111/plb.12311), original [author-deposited publisher PDF](https://rosasguerrerolab.com/wp-content/uploads/2023/07/16-cuevas.pdf), SHA256 `216750e6c649d8472420e54f272c5448caab875e59aab51603fd5b5e9afb5cdf`. Fig. 4 visually inspected at printed page 12.
- Gélvez-Zúñiga et al. (2016), *Revista Mexicana de Biodiversidad*, [DOI 10.1016/j.rmb.2016.09.004](https://doi.org/10.1016/j.rmb.2016.09.004), original [journal-hosted PDF](https://revista.ib.unam.mx/index.php/bio/article/download/1353/1382/6582), SHA256 `1e8ef9017756cacd5f893cef6e42abe2669cd0baf7ea506999324c9f386b0a0a`; [SciELO source HTML](https://www.scielo.org.mx/scielo.php?pid=S1870-34532016000401352&script=sci_arttext), SHA256 `cec6de206cdf17cf65311ff78558478a4597fbd2cb119818a31b12ee60705489`.
- Leal et al. (2025), *Ecology* [10.1002/ecy.70036](https://doi.org/10.1002/ecy.70036), original [Zenodo](https://doi.org/10.5281/zenodo.14773082), original ZIP SHA256 `3f6e9b5b55ad8090f41f62faeb2f306c6700a9beb274ac6467106ebab9573c2d`.
- Zhong et al. (2025), *Plant Diversity* [10.1016/j.pld.2024.12.004](https://doi.org/10.1016/j.pld.2024.12.004), original [Figshare](https://figshare.com/s/99df84fe5c473dc85d85), XLSX SHA256 `6554409f22b09156ee1c2a35ee2547eb5ae28c4a25934b9c639d8a19ea7fe9b4`.

The new workflow requires **all four independently re-downloaded original sources**, verifies PDF/ZIP/XLSX SHA256 plus the official Zenodo MD5, and runs exact source-linked tests without modifying either published meta CSV/XLSX. Source PDFs may carry publisher copyright; link to original sources for manuscript distribution rather than reproduce full articles.

## First independent issue: Salvia source sample 56 — apparent robber visitation, not verified pollinator service

**Leal sample 56** (`Cuevas&Guerrero_2016`) archives `sp_plant=Salvia_gesnerifolia`, metric `visitation`, mean `0.21` in robbed flowers versus `0.07` in unrobbed flowers, `n=7` in each column, `yi=+1.098612289`.

The actual original paper studies ***Salvia gesneriflora***, so the published meta label **gesnerifolia** does not match the primary binomial. The original February 2014 video experiment filmed **seven plants (nine–17 flowers per plant), 44 h / 204 flowers**. The same seven plants contribute both robbed and unrobbed flowers, so `n=7` is **not 7 independently randomized plants per treatment**.

Fig. 4 separately plots legitimate hummingbird ***Eugenes fulgens***, secondary robber ***Bombus ephippiatus*** and primary robber ***Diglossa baritula***. Visually, the approximate Fig. 4 points for **D. baritula** are ~0.21 versus 0.07 visits/flower/hour; legitimate ***E. fulgens*** is ~0.19 versus 0.10, *not the same comparison*. **Leal 56 numerically fingerprints the primary robber's visitation rate**. The author figure has no embedded machine-readable treatment mean table, so the exact numeric source extraction is **a strong candidate, not a verified digital record**. Do not count 56 as confirmed legitimate pollinator service without a published original extraction sheet.

The primary source reports **no statistically significant hummingbird discrimination** (chi-square p=0.276), and a roughly eightfold difference in nectar availability (robbed vs unrobbed). Primary robber `D. baritula` difference is also nonsignificant at p=0.083. These are prior published findings and do NOT certify ecological no effect, equivalence or causality.

The 2025 Zhong original workbook contains this same Cuevas 2016 original publication correctly as ***Salvia gesneriflora*** ref-ID 13, with source IDs **501–506**; row **506** is visitation rate with `yi=+0.67756245` and `pollinator_type=bird`. The figure's hummingbird points have an approximately similar ratio, but **both hummingbird and D. baritula are birds**, and the original 2025 extraction ledger does not confirm which bird supplied row 506. Thus there may be **different visitor guild definitions for the two paper-level visitation effects**, and they **must not be silently paired** as identical effects. Previous 45 provisional overlap candidates + verified Fumero and Gélvez + Souza source candidates = at least 48; the independently verified *Salvia* same primary study is one further candidate **(at least 49 original-paper correspondences)**, NOT 49 DOI-and-treatment-verified effect pairs.

Additional original source-quality question: the Leal 56 archived `vi=0.058309` agrees with **swapping the two archived SD columns**; the plotted Fig. 4 bars may represent uncertainty, but **the paper caption does not specify these numbers as group SD**, so original SD-vs-SE is not resolved. Group covariance is unavailable.

## Second issue: Collaea sample 87 — floral abortion coded as favorable female fitness

The original *Collaea cipoensis* study measured **flower abortion ratios**, not final viable seeds or plant fecundity. Leal **sample 87** (`sp_plant=Collaea_speciosa`, metric `female`) archives robbed 0.38 versus intact 0.22, producing `yi=ln(0.38/0.22)=+0.546543706`.

The original 2016 paper reports **0.38 ±0.061 SE** in robbed versus **0.22 ±0.057 SE** in intact flowers, in **44 plants** with **570 damaged and 716 intact flowers**. Its maternal-plant random-intercept GLMM reports **F(1,80)=2.6, p=0.11** — **not a significant effect**. Higher abortion is a *loss* of reproductive potential, not positive female fitness. Therefore `+0.54654` is an abortion-rate ratio, not evidence of a positive female fitness effect. **Do not simply negate `yi`**: even the illustrative non-abortion proportion ratio, **ln(0.62/0.78)=−0.229574**, is mathematically distinct from `−0.546544` and not measured fruit or viable seed set.

Archived `n_larcenist=570` and `n_control=716` are **flowers**, not independent maternal plants. The archived SD columns are close to `published SE × sqrt(number of flowers)` (0.061√570 ≈1.456; 0.057√716 ≈1.525), but this arithmetic correspondence does not establish correct plant-clustered sampling variance. The original did not randomize 570 plants against 716 separate plants.

## Third issue: Collaea sample 88 — original visits decrease but archive orientation is reversed

The same *Collaea cipoensis* paper reports **hummingbird visits 3.44 ±1.05 SE (N44)** in robbed flowers versus **17.11 ±2.70 SE (N237)** intact (original Wilcoxon p<0.0001 for observed visitation). Thus the direct observed robbed-versus-intact log ratio is **ln(3.44/17.11)=−1.6041916**. Leal's sample **88** archives `yi=+1.6041916`, the exact opposite orientation. The earlier SD-column discrepancy was independently traced to the original SEs and N. Different original flower counts are not independent maternal plant counts, and the natural robbing exposure contrast remains observational.

Thus the 2016 paper's **two purported positive meta-response signs** represent a higher *abortion* rate and a reversed *legitimate hummingbird visitation* log ratio, respectively. These are two distinct response-definition issues, not proof of fraud or invalidity of the overall Leal published ecological meta-analysis.

## Exploratory sensitivity only: remove unclear endpoint rows, NO refit

Using *original unchanged* archived Leal `yi,vi` values, one may compare simple summaries, not the author's study/phylogeny random-effects model:

| Metric | Full archived effects | Source-defined exclusion sensitivity |
|---|---:|---:|
| Robbers × female: effect rows | 130 | 129 (exclude abortion-source 87) |
| Robbers × female: source-study-equal mean lnRR | −0.19576 | −0.21432 |
| Robbers × visitation: effects | 44 | 42 (exclude robber-guild candidate 56 and sign-misoriented 88) |
| Robbers × visitation: source-study-equal mean lnRR | −0.11980 | −0.31596 |
| Robbers × visitation: raw inverse-`vi` weighted mean lnRR | −0.26172 | −0.26491 |

A purely **hypothetical** reorientation of 88 (replace its `yi` with the original observed negative ln ratio) changes the descriptive source-study equal mean from −0.11980 to −0.30853, but the original author analysis is not refitted and the unverified source covariance and other likely endpoint differences remain. **No meta-analytic p-values, conditional causal parameters, or generalized reversal claim can be inferred from these sensitivity summaries.**

## Unresolved original source records

The previous seven SD transposition cases were 56, 79, 81, 83, 84, 88, 178. Sample 178 was source-adjudicated as *Jacaranda caroba* floral scent rather than nectar in PR #269. Sample 88 was independently source-linked to *Collaea* original visitation, while the present audit adds its abortion companion sample 87. Sample 56 can now be mapped to the exact original author's visitor figure and botanical species but its **group SD-vs-SE interpretation and original row digitization remain unresolved**. The full original Fumero & Meléndez-Ackerman 2013 tables for samples **79/81/83/84 are still not acquired**, and the sign rationale for 79 remains unresolved. Their original paper abstract is accessible but not a substitute for exact original raw contrast/sampling units.

## Why this matters for a BALANCE macro research question

A larger comparative study must separate **resource depletion** (nectar), **cue alteration** (scent/visual injury), **robber behavior**, **legitimate visitor service**, **pollen transfer**, **abortion/fruit initiation** and **viable seeds**. A source-level positive log effect on abortion should not be counted as improved female fitness, and an increase in robber's own visits should not be interpreted as improved pollinator visitation.

Neither this audit nor the 2025 meta authors identify net differentiated-versus-shared fitness, `L`, `K`, `Phi`, optimized `W_D^*−W_S^*`, or independent evolved structural architecture gain. This is **a source-data eligibility gate**, not novel confirmation of a biological mechanism already present in these original papers.

Replay with `python scripts/audit_leal_2016_visitor_abortion_gate.py --leal-zip ... --zhong-xlsx ... --cuevas-original ... --gelvez-original ... --out ...` after source download; source-bound GitHub Actions workflow runs 8 regression checks. No original U6 21-taxon sources, blinded independent architecture coders (42), V4 frozen outputs, SLK manifesto or main branch modified. Keep new stacked branch **draft/unmerged**.

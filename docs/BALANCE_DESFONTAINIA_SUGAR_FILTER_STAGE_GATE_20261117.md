# BALANCE — Desfontainia source-script sugar filter and exposure/fitness stages (2026-11-17)

**Exploratory original-source audit, one species, one study. Not a randomized nectar-robbery effect, plant fitness equivalence, or structural BALANCE occupancy.**

## Original sources and provenance

Valdivia & Orellana (2026), *Ecology and Evolution* [10.1002/ece3.73933](https://doi.org/10.1002/ece3.73933). The March 6, 2026 Zenodo submission [10.5281/zenodo.18895003](https://doi.org/10.5281/zenodo.18895003) includes a workbook MD5 `e7e59a06cc3eb7aed636620a85a1ea98` and author R script MD5 `9fd405c399ecad9c3fe54d1cd70b21c0`; both were independently read as exact source bytes. The final publication's Data Availability Statement points to [10.5281/zenodo.20469376](https://doi.org/10.5281/zenodo.20469376), which **has now been independently verified as a distinct and updated final-paper code deposit**. Do not treat the March prepublication script as the code controlling the published paper.

## Final-paper source version verified — correction to preliminary audit

The final article's DOI [10.5281/zenodo.20469376](https://doi.org/10.5281/zenodo.20469376) is **public and accessible**. An independent source-authenticated GitHub Actions retrieval verified that its raw XLSX has the **same MD5** `e7e59a06cc3eb7aed636620a85a1ea98`, whereas its updated R code has MD5 `8e72799d10773c70a77089bd7efc4fab` (different from the March-submission code). The **final R code explicitly filters positive measured sugar only**, not `nectar_ul >= 5`; it constructs 9 paired shrubs and is consistent with the published t≈−2.13, p≈0.066. It also uses `geepack::geeglm` for its GEE models, whereas the March-submission R used different model implementations. Thus the earlier source-script mismatch is a **historical version difference**, **not an error in the final deposited script**. No published numeric sugar result needs retraction on this basis.

The remaining question is solely whether the measurements from low-volume flowers are adequately supported by the stated approximate refractometer-volume limit, not whether the final data/code can reproduce the nine-shrub statistic. Source receipts: [GitHub original and final record reconciliation](https://github.com/zuizui0223/balance/actions/runs/43904198046).

## Historical March-submission source-code discrepancy

The submitted original R script reads the nectar sheet, applies `filter(nectar_ul >= 5, !is.na(sugar_pct), sugar_pct > 0)`, summarizes sugar concentrations at the shrub × pierced/undamaged level, and performs `t.test(..., paired=TRUE)`.

Against its exact deposited workbook, **only four naturally pierced flowers from three shrubs** pass this 5-µL volume condition; **only one shrub** has a matching undamaged sugar measurement at the same threshold. Thus the submitted filter would leave *one valid paired shrub*: a paired t-test is unestimable.

Without the >=5 µL gate, keeping actual positive measured nectar and positive sugar observations, the nine paired shrubs precisely reproduce the published sugar result: pierced 5.03889% w/w versus undamaged 13.91852%, t(8)=−2.12931, two-sided p=0.065864. This reproduces the original reported ~2.76-fold difference and p=.066, **but not the source script's stated filter**. It suggests a mismatch in the documented threshold/code, not evidence of data fabrication or a proven wrong result. The suitability of measuring sub-5 µL sugar concentrations requires instrument/protocol clarification.

Post-open flower-volume threshold sensitivity, **not independent confirmatory tests**:

| Minimum qualifying flower volume | Paired shrubs | Exploratory t / p |
|---|---:|---|
| Positive nectar (>0 µL) | 9 | −2.129 / .0659 |
| ≥0.5 µL | 9 | −2.129 / .0659 |
| ≥1 µL | 6 | −1.381 / .2258 |
| ≥2 µL | 4 | −0.936 / .4183 |
| ≥3 µL | 4 | −0.935 / .4186 |
| ≥5 µL (original script) | 1 | not estimable |

These changing p-values mostly reflect reduced and selectively observed support; they do not show a dose-response.

## Distinguish event occurrence, conditional reward difference, and downstream reproduction

The independent 100-shrub × 10-flower incidence survey records **165/1000 pierced flowers (16.5%)**, with **43/100 shrubs** having any pierced flower. An exploratory **shrub-unit** 20,000-draw bootstrap of the sample piercing rate has percentile 95% range **11.6–21.8%** (seed 20261117). A binomial interval treating 1000 flowers as independent is narrower because it ignores clustering.

The separate 40-shrub, deliberately balanced (five pierced/five undamaged per shrub) nectar sample shows conditional standing nectar means **0.4810 versus 4.4489 µL**, i.e. ~89.2% less in selected pierced flowers. The *selected* 50:50 sample is **not** evidence of 50% piercing in the population, and a conditional 89.2% difference is **not** a population-wide 89.2% reward collapse.

The paper states the nectar and seed treatments were sampled from the **same 40 shrubs**, but **different individual flowers**. Shrub-level mean nectar deficit (undamaged minus pierced) versus naturally pierced-minus-protected mature seed difference has Spearman **ρ=+0.1381**, asymptotic p=.3956, shrub-paired bootstrap 95% **[−.202,+.462]** (10,000 draws, seed 20261117). This provides **no resolved positive cross-stage association, no absence-of-mediation proof and no same-flower mediation estimate**. Selection of already-robbed open flowers and tape-protected unopened buds further obstructs causal attribution.

## Claim ceiling and remaining scientific work

A non-significant sugar comparison cannot establish unchanged nectar composition, especially when only 9/40 shrubs contribute and original script says the filter should instead yield 1/40. A non-significant seed contrast likewise cannot certify no reproductive cost or equivalent fitness. No `L`, `R`, `K`, `Phi`, optimized shared/differentiated worldlines, evolutionary architecture costs, or heritable origins are measured.

**Next empirical gate:** verify final-paper source-version identity and refractometer reliability below 5 µL; then prospectively assign comparable same-age flowers within independent shrubs to sham, standardized nectar removal and physical damage, and follow *the same flowers* from visitor contact/pollen receipt to mature seeds. Maintain plant rather than flower-level independent units.

The attached workflow re-downloads the archival source and audits the reported n=9 versus source-script n=1 denominator. This entire exploration leaves the original U6 21-group source admissions, 42 blinded architecture coder slots, frozen V4 outcomes and active manuscripts untouched. No scientific claim is promoted automatically.
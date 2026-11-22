# BALANCE — two Solanum pollen paths, denominator audit, and original Zenodo data gate

**2026-11-22 | Original 2025 publication read; publication-source quantitative re-expression only until Zenodo source files and original 15 trials are authenticated.**

## What biological evidence is genuinely independent here?

Vasquez-Castro, Morel, Garcia-Simpson & Vallejo-Marín (2025), *Journal of Pollination Ecology* 39:246–260, [DOI 10.26786/1920-7603(2025)836](https://doi.org/10.26786/1920-7603(2025)836), [open journal article](https://www.pollinationecology.org/index.php/jpe/article/view/836).

The design exposed a donor flower to one *Bombus terrestris* worker followed by up to **four** pollen-blocked recipient flowers, and measured the donor's remaining pollen, falling grains caught under the donor, bee pollen basket, terminal body load, and four recipient stigmas. Exactly **15 completed donor-to-four-recipient trials**: *Solanum dulcamara* n=9, *S. rostratum* n=6; **60 stigmas nested in 15 trials**, not 60 independent experiments. Bees came from two source colonies. The source did not measure pollen lost on the ground or air after the bee left the donor, and held all experimental flowers at a fixed 90-degree orientation. It did **not** genotype fathered progeny or measure seed set.

The source's original DATA AVAILABILITY STATEMENT explicitly identifies the original deposit [Zenodo record 17102653](https://zenodo.org/records/17102653). We found that locator rather than presuming the previously inaccessible Dryad datasets were the only source. The repository script `scripts/audit_vasquez_2025_zenodo.py` attempts the official Zenodo API and validates file byte sizes/checksums/CSV schemas; its GitHub workflow reports retrieval failures as **HOLD**, not new empirical tests.

## Fate percentages: clearly separate two denominators

Original author per-trial compartments, then group mean proportions:

```
C = grains remaining in donor anthers
D = grains falling on ground under donor
F = grains in bee's corbiculae
G = grains remaining on bee body
H = H1 + H2 + H3 + H4, deposited on four recipient stigmas

Measured reconstruction A = C + D + F + G + H
Measured donor removal B = D + F + G + H
PTE = 100 * H/B, NOT 100 * H/A.
```

The sums are **bookkeeping over measured compartments**, not proof that every pollen grain physically produced in the flower was recovered, because other in-flight/ground losses were not measured. Moreover, the author reports percentages averaged across trials: the product of marginal group mean percentages is not the per-trial mean `E[(B/A)*(H/B)]`.

| Original reported value | *S. rostratum* n=6 | *S. dulcamara* n=9 |
|---|---:|---:|
| Donor pollen removed as % of *measured A* | 13.55% | 37.77% |
| Ground D/B | **62.99%** | 19.07% |
| Basket F/B | 27.65% | **65.92%** |
| Terminal body G/B | 8.54% | 14.01% |
| Four recipient stigmas H/B = PTE | 0.86% | 1.00% |

For the within-removed-pollen compartment accounting, the published mean percentages sum to 100.04% for *S. rostratum* and 100.00% for *S. dulcamara* (rounded). This is a numerical sanity check of the author figure and prose, **not an additional empirical replication**.

Original authors report significant species differences for ground (Z=3.66, p=.001) and corbicula (Z=−2.535, p=.011), but not terminal body (p=.760) or stigma PTE (p=.221). **Nonsignificant PTE difference is not statistical equivalence.** The two source species contrast includes numerous differences besides architecture (species, background flower size, pollen production, etc); no within-species arrangement randomization occurred.

### A potentially misleading conclusion from the published PTE label

Both conditional PTE values are roughly **1% of removed pollen**, but the source-measured percentage *removed* differs by a factor of about **2.79** (37.77/13.55). Therefore similar *removed-pollen-conditioned* transfer fractions do **not** imply equal overall donor pollen delivered from **total measured production**.

For intuition only, multiplying published rounded group means gives:
- *S. rostratum*: `(13.55/100)*(0.86/100)*100 ≈ 0.11653%` of measured produced inventory on the four stigmas;
- *S. dulcamara*: `(37.77/100)*(1.00/100)*100 ≈ 0.37770%`;
- Descriptive product ratio ≈ **3.24**, distinct from the two species' conditional PTE ratio ≈ 1.16.

**THIS IS NOT a newly observed species effect or a 3.24× estimated contrast.** It is the **product of two rounded species sample means**, rather than the necessary `mean(H_i/A_i)` calculated jointly on the **15 trial-level observed pairs**. Within-species covariance between removal and delivery may change the true result materially. Do not report a p-value or confidence interval for this proxy; even the sign is not formally established by the source products alone.

The *actual* trial-level scientifically interesting estimand is `H_i/A_i` (fraction measured produced to four stigmas), with source unit one donor/bee trial. Compare `H_i/B_i` and `B_i/A_i` in the same donor trials to evaluate whether the similarity of conditional PTE masks a change in the end-to-end source outcome. This is a testable, nontrivial difference from the literal bookkeeping identity.

## Recipient sequence is an exposure window, not a fitness measure

The published negative-binomial mixed model describes recipient-stigma pollen decreasing with recipient sequence position. Its reported slope is **−0.339 ± 0.098** per position (p<.001). The conditional per-recipient carryover ratio is `exp(-.339)=0.7125`. Extending the same fitted decay beyond the four measured recipients to **20 modelled recipients** implies the first four account for about 74.3% of modeled first-20 deposition; the complementary 25.7% is **a model extrapolation**, not measured extra recipient pollen. Original species×recipient position AIC difference is 1.8; prefer the simpler source model but **do not assert equivalent species decay**.

A source-recipient stigma grain is not automatically fertilization; viable genetic paternity, reproduction and an optimized alternative floral architecture cost remain unmeasured.

## Connection to BALANCE's earlier authentic bee trial PR #279

[Wilkins et al. (2022), PR #279](https://github.com/zuizui0223/balance/pull/279) experimentally **joined versus freed anthers in the same species *S. elaeagnifolium*** with *Bombus impatiens*, and our original-data reanalysis verified an architecture×bee-head-width association with pollen left on the bee's body versus pollen in the bee's corbiculae. It **did not establish a direct difference between body/basket and stigma/basket interaction slopes** (same-bee HC3 direct p=.334). This is a within-flower manipulation with a different bee, plant species, and treatment from the 2025 donor/recipient sequence experiment. No numerical treatment effect should be pooled across these studies as one common parameter.

The 2025 published study adds a second original plant–pollinator programme and **quantifies the ground-loss channel** absent from Wilkins 2022. Together they motivate a sharper explicit hypothesis:

> Two differently structured flowers can route pollen differently among ground, corbicula, bee body and recipient stigma. Neither comparable conditional PTE nor a mechanical source-release advantage guarantees similar *total produced pollen delivered* or fathered offspring.

This is a **positive observed source-stage phenomenon** paired with an *untested causal architecture explanation*. Both are within Solanum and share research context, not independent deep evolutionary origins. No legitimate new V4 architecture coder response is inferred from this cross-paper comparison.

## What must pass before claiming an original reanalysis?

1. Public Zenodo record 17102653 API responds; verify title, file names, archive sizes, MD5/SHA source content.
2. Inspect real CSV fields for one-donor/bee trial ID, species, C/D/F/G and H1–H4 in the **same experimental unit**. If table has long recipient rows, join only by verified trial identity and never multiply donor source measurements by 4.
3. Preserve missingness and trial denominator: at most 15 completed donor trials unless original source explicitly includes additional independently completed units.
4. Refit one **predeclared** trial-level estimand: `H_i/A_i` and `H_i/B_i` with correct source denominator and a trial-level nonparametric interval; keep colony identity if observed. No denominator-selected p-value after seeing results.
5. Treat within-donor four recipient deposits as nested when modelling recipient order; block by trial and ideally bee if repeat identification is available.
6. Only then say a real raw-data result was reproduced, and still avoid genetically assigned paternity, seed fitness and causal between-species architecture claims.

## Reproduce

```bash
python - <<'PY'
from balance_domain.vasquez_2025_pollen_fates import build_source_pollen_fates
from pprint import pprint
pprint(build_source_pollen_fates())
PY
python -m scripts.audit_vasquez_2025_zenodo
python -m scripts.audit_vasquez_2025_zenodo --online --out /tmp/vasquez-zenodo-source-only.json
pytest -q tests/test_vasquez_2025_source_and_zenodo.py
```

The branch-specific `.github/workflows/vasquez-2025-zenodo-audit.yml` attempts genuine network retrieval from GitHub's runner and uploads **only the file identities, hashes, row counts and column names**, never raw experimental records. This makes success/failure of the source-data recovery inspectable, without claiming actual trial-level effects before scientific joins can be verified.

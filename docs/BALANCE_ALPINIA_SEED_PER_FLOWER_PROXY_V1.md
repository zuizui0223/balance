# ALPINIA — fruit-stage loss translated to a conditional seed-per-flower index

**2026-11-17, post-open source-only exploratory analysis.** One biological plant species (*Alpinia roxburghii*), one published field programme. This is **NOT measured total plant seed output**, a randomized nectar-only causal effect, a multi-study meta-analysis, or a direct BALANCE architecture-value certificate.

## Original and source units

Deng et al. (2015), *PLOS ONE*, https://doi.org/10.1371/journal.pone.0144585, official supplement S2, https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0144585.s002&type=supplementary . Original DOC SHA256 `d3f659090ed0d581e34a45c03e7879e5fb107796f23ea078548be041621880ee`. The source-authenticated 16-cell year × compass direction × robbery-status table is frozen in `data/external/alpinia_2015/S2_EXTRACTED_16_CELLS.csv` (SHA256 `ad52b6ca136b63b9dd049ec01993636869c5e16635c4e2e6b77e96f741ab374c`).

There are 34,076 source flowers; only 1,695 fruits were actually sampled for seed counts, out of 12,175 recorded fruits. The **unit of data availability is 16 published aggregate cells**; flowers, fruits, direction cells, or years are not independent study programmes.

## Conditional, descriptive extrapolation

For natural robbed versus guarded unrobbed plots, define:

`F_t = observed mature fruits / recorded flowers`

`M_t = seeds counted in sampled mature fruits / sampled mature fruits`

`I_t = F_t * M_t` = **proxy seeds per original flower, ONLY IF the sampled fruit mean equals the full fruit-population mean within that treatment/context**.

| Original source component | Robbed | Guarded unrobbed |
| --- | ---: | ---: |
| Fruits / flowers | 5,174 / 17,231 | 7,001 / 16,845 |
| Observed fruit-set fraction | 0.300273 | 0.415613 |
| Seeds / sampled fruits | 25,502 / 881 | 24,159 / 814 |
| Mean seeds per **sampled** fruit | 28.9467 | 29.6794 |
| **Sampled fruits as fraction of all fruits** | **17.03%** | **11.63%** |
| **Seed-per-flower index, conditional** | **8.6919** | **12.3351** |

Composite robbed/guarded index ratio is **0.704645**, or a **29.535% lower proxy**. This is a derived product, **not measured total seeds per flower**. The fruit-set ratio is **0.722482**; sampled seed-per-fruit ratio is **0.975312**. Therefore the observed lower proxy arises mainly from recorded fruit formation, not from sampled fruits having fewer seeds.

Year-level proxy indices and ratios (same source and assumption): 2005 **6.7894 vs 11.1190, ratio 0.610611 (−38.939%)**; 2007 **10.8869 vs 13.9914, ratio 0.778115 (−22.188%)**. **All eight** year×compass-direction source strata also have robbed proxy lower; equal-stratum proxy ratio **0.711468** versus original-flower-weighted overall ratio **0.704645**. This is a stability description across one programme, **not eight biological replications or an exact sign test**.

## Break-even and missing-fruit sensitivity

**If fruit formation fractions were fixed**, the robbed flowers would need mean seeds per mature fruit at least **1.384118 times** those of guarded flowers (about **38.4% higher**) to achieve the same average seed per original flower. The observed sampled ratio is **0.975312** (about 2.5% lower).

The source directly samples only **17.0%** of robbed fruits and **11.6%** of guarded fruits for seed counts. It does not identify the unsampled-fruit mean. Let `b_R` and `b_U` be true whole-fruit seed means divided by the respective observed sample means; the corrected conditional index ratio would be `0.704645 * (b_R/b_U)`. A reversal requires `b_R/b_U >= 1.41915`. In a symmetric sensitivity scenario where each true whole-fruit mean can differ from its sampled value by at most `e` in either direction, **opposite-direction ±17.326% deviations** are enough to erase the ratio deficit. This is a hypothetical bias threshold, not an estimate of actual sampling bias.

| Hypothetical deviation of *each* true mean from sampled mean | Plausible index ratio band under this assumption | Is ratio < 1 guaranteed within this band? |
|---|---|---|
| ±15% | 0.5208–0.9533 | Yes |
| ±20% | 0.4698–1.0570 | **No** |

Year-specific sensitivity threshold: **±24.18%** (2005) and **±12.48%** (2007). Thus a single pooled index number can hide differing fragility across years. Selection of sampled fruits could depend on fruit size, damage, maturity, location or maternal identity. Their availability is not characterized by S2; **do not assume missing completely at random**.

## Cross-reading the published article

The article discusses an estimated **12.22% potential seed loss**, using its reported fruit-set and “seed set” percentages. S2 explicitly contains **seeds / number of sampled fruits**, not a measured *ovule denominator*. The **29.5% figure above is a different, explicit ratio-of-products estimand under representativeness assumptions**, so it neither reproduces nor invalidates the paper's original analysis. The true full-fruit seed means and a jointly valid cluster uncertainty model remain unavailable in S2.

There is also no pure-nectar manipulation contrast: natural striped-squirrel visits involved floral damage (including styles), while guarded plots prevent squirrel access and may alter pollinator visits. The article's observed fluorescent tracer patterns do not estimate genetic male parentage. No `L`, `R`, `K`, `Phi`, `W_S*` or `W_D*` has been estimated.

## BALANCE role

This adds a *testable stage-specific scenario*: if pollen transfer, intact floral structures and legitimate visitation affect the **probability of fruit initiation**, relatively stable seed numbers among **sampled surviving fruits** need not imply stable seed production per original flower. In a new controlled study, record flowers → fruits → ALL mature seeds for the same maternal plants and randomize independent floral damage and nectar removal components, retaining visits, pollen fates and direct seed viability; register viable shared and differentiated architectures separately if a strict BALANCE worldline is the aim.

A cross-study test must not pool this inferred ratio with Desfontainia 40-shrub paired seed differences, Campanula pollen limitation, Zurich fruits, or apple richness/visitation RMSE as though they estimate one evolutionary effect size.

## Reproduction and guardrails

```bash
python -m pytest -q tests/test_alpinia_original_stage.py tests/test_alpinia_seed_proxy.py
python scripts/audit_alpinia_seed_proxy.py --original-doc /path/to/pone.0144585.s002.doc --output /tmp/ALPINIA_SEED_PROXY.json
```

The source SHA256, 16-cell denominator, 8 source strata, seed-sampling fraction, break-even ratio, hypothetical sensitivity bands and explicit claim guard fields are checked. The original U6 21 taxa, independent architecture coding 42 A/B slots, frozen V4 responses and active SLK manuscript are unchanged.

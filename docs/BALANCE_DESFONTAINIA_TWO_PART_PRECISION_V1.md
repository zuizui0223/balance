# Desfontainia original 40 shrubs: two-part seed production and no-equivalence precision gate

**2026-11-16; post-publication, exploratory, source-authenticated; NOT new confirmatory ecology, no causal nectar-robbery effect or BALANCE worldline.**

## Question

Valdivia & Orellana (2026), *Ecology and Evolution*, [DOI 10.1002/ece3.73933](https://doi.org/10.1002/ece3.73933), report pronounced nectar depletion in naturally perforated flowers but no statistically detected decline in seed production. Does the original 40-shrub treatment table demonstrate that the downstream seed effect is *small*, and is the reported mean seed count sufficient to describe reproductive response?

The earlier BALANCE source audit established three distinct 40-shrub outcomes (`-P-R`, `+P-R`, `+P+R`), a paired seed contrast of **+5.225 seeds** (`+P+R - +P-R`) with paired t 95% confidence interval **[-12.850, +23.300]**, plus substantial nectar depletion on *other* flowers. The current audit is a subsequent planned robustness/precision check of **the same data**, not another biological replicate. Source archive [Zenodo 10.5281/zenodo.18895003](https://doi.org/10.5281/zenodo.18895003), original XLSX MD5 `e7e59a06cc3eb7aed636620a85a1ea98`. Numeric readout has a separately frozen JSON digest-bound to the original source through the inherited MD5 validator.

## New measured quantities (40 paired shrubs, one treatment flower per shrub)

| Descriptive endpoint | Protected `+P-R` | Naturally pierced `+P+R` |
| --- | ---: | ---: |
| Flowers with nonzero mature-seed count | 32/40 (80.0%) | 28/40 (70.0%) |
| Mean seeds restricted to nonzero flowers | 32.65625 | 44.78571 |
| Mean seeds including zero flowers | 26.125 | 31.350 |

The presence difference (`pierced - protected`) is **-0.10**, paired-shrub 20,000-resample percentile range **[-0.30, +0.10]**; discordant pairs are 10 protected-only seed producers versus 6 pierced-only, exact two-sided symmetry reference **p = 0.4545**. The two-sided paired sign reference for seed number is **19 positive versus 19 negative, 2 ties, p = 1**; median paired difference **0**, mean **+5.225**. These are exploratory descriptive reference tests, not randomized treatment-assignment p-values; a null result does not prove no harm or equivalence.

### Descriptive arithmetic, NOT a biological mechanism or unique decomposition

Define success frequency `p_j=P(seeds>0)` and mean seed output among positive flowers `m_j=E(seeds|seeds>0)` for observed treatment label `j`:

`E(Y_j) = p_j * m_j`.

At a **chosen reference ordering** (the protected positive-flower mean for prevalence change and naturally pierced success probability for magnitude change), the observed mean difference decomposes exactly as

`(p_pierced-p_protected) * m_protected = -3.265625 seeds` and

`p_pierced * (m_pierced-m_protected) = +8.490625 seeds`;

sum `+5.225 seeds`. With 20,000 fixed-seed paired-shrub resamples, the descriptive 95% percentile ranges are **[-10.23,+3.11]** and **[-4.57,+22.45]**, respectively. The conditional positive-only seed mean difference is **+12.1295 seeds**, bootstrap range **[-6.66,+31.37]**. These parts are not identified causal pathways. Conditioning on seed success selects post-exposure outcomes. Different valid decomposition reference orders assign different magnitudes to the parts; neither estimates compensation or biological buffering.

### Explicit practical-equivalence audit

The paired seed difference has 90% Student-t confidence interval **[-9.8313,+20.2813] seeds** (df 39). Standard α=.05 TOST equivalence requires this entire 90% interval to lie strictly inside *scientifically predeclared* bounds ([Lakens 2017](https://doi.org/10.1177/1948550617697177)). This is **post-open sensitivity**, not a preregistered equivalence test. For illustrative symmetric margins relative to the observed 26.125-seed protected mean:

| Assumed smallest effect of interest, symmetric | Half-width | Does 90% CI fit? |
| --- | ---: | --- |
| 10% | 2.6125 seeds | No |
| 20% | 5.2250 seeds | No |
| 50% | 13.0625 seeds | No |

The *minimum symmetric half-width* that would contain this particular observed 90% interval is **just over 20.2813 seeds**, **77.63% of the protected mean**. **This is NOT evidence that a ~78% change would be biologically negligible; it quantifies how uninformative the current contrast is for small-effect claims.** The 95% interval still permits a 12.85-seed *reduction*, ~49% of the protected average; even formal equivalence of this observed association would not identify the causal robbery effect given the selection/handling differences.

The paired 95% bootstrap range for whole-flower mean difference is **[-11.825,+22.60] seeds**. Omitting any single shrub leaves a mean difference ranging **+2.513 to +8.615 seeds**. These are retrospective influence descriptions, not robustness of a causally interpretable effect. No single-shrub deletion repairs the original confounding.

## Critical experimental-identity ceiling

- `+P+R` sampled **already-open, naturally robbed** flowers; `+P-R` sampled **unopened buds protected with red-ink masking tape**. The same-shrub pairing does not randomize floral stage, visitor history, baseline quality, or treatment handling.
- Nectar observations are on other flowers. Neither plant-level nectar means nor flower-level nectar measurements can be treated as mediator observations for the three seed-fitness flowers.
- A robustly nonzero resource *association* alongside an imprecise, partly nonrandomized downstream reproductive *comparison* is not direct evidence that a fitness effect is buffered or that any structural architecture is profitable.
- No functional conflict load `L`, recovered gain `R`, differentiated structural cost `K`, `Phi`, male mating success, inherited architectural novelty, or optimized `W_S*`/`W_D*` was observed.
- These are **one study and one species**, not 40 independent evolutionary trials and not a new case for an RMSE synthesis.

## Next decisive study design (not executed here)

Randomize **comparable same-stage flowers within independent maternal plants** to sham, standardized nectar removal, and corolla damage (ideally orthogonal treatments), retaining natural-visitor access contrasts and pollinator-exclusion controls where feasible. Follow *the same flowers* through nectar recovery, visitor contact, pollen delivery, seed presence, mature viable seed count and (if possible) paternity. Prespecify an ecologically meaningful seed/fertilization equivalence margin before analyzing outcomes, and pilot the among-shrub variance rather than transplanting the current confounded 56.5-seed paired SD as a guaranteed design variance. Only an independent matched performance/cost comparison of viable shared and differentiated structures can identify strict BALANCE occupancy.

## Reproduce

```sh
BALANCE_DESFONTAINIA_SOURCE=/path/to/'Raw Data Desfontainia fulgens.xlsx' python -m pytest -q tests/test_desfontainia_two_part_precision.py
python scripts/audit_desfontainia_two_part_precision.py --source /path/to/'Raw Data Desfontainia fulgens.xlsx' --out /tmp/new-desfontainia-two-part.json
```

Tests cover exact 40-shrub original numbers, paired identity/dependence, arithmetic reconstruction, sign and discordance references, zero-difference synthetic equivalence, negative/corrupted source rejection and strict limits on causal/evolutionary claims. The current repository's original 21 U6 taxa, 42 unstarted A/B architecture coders and frozen V4 outcomes remain unopened.

# Desfontainia 2026: resource depletion is not an identified architecture fitness penalty

**Status (2026-11-15):** independent original-source, post-publication descriptive reanalysis of **one biological study and 40 shrubs**. This is not a new ecological replication of the Zurich/Campanula/apple visitor composition estimand, a causal equivalence test, a historical selection test, or a direct BALANCE `W_D* - W_S*` experiment.

## Traceable originals

- Valdivia & Orellana (2026), *Ecology and Evolution*, DOI [10.1002/ece3.73933](https://doi.org/10.1002/ece3.73933).
- Original publicly archived six-worksheet XLSX and R source: [Zenodo 10.5281/zenodo.18895003](https://doi.org/10.5281/zenodo.18895003). Original XLSX verified against independently published MD5 `e7e59a06cc3eb7aed636620a85a1ea98`. The complete workbook stays in the immutable Actions source artifact; analysis and result JSON here are text-based. The 2026-03 submitted R script is **not** treated as the exact script of the June 2026 published GEE analysis.

## Three separate biological estimands

- **Proximate resource**: 40 shrubs, five pierced and five undamaged flowers per shrub (400 original rows). Of these, **34 flower-level nectar values are missing** (14 pierced, 20 undamaged). Missing values are excluded from respective within-shrub means, **not** recoded as zero. All 40 shrubs have usable paired means, but the missing within-plant flowers could bias those means. Across paired shrub means, pierced flowers hold `0.4810 µL` versus `4.4489 µL` for undamaged flowers, ratio `0.1081` (89.2% less). Paired pierced-minus-undamaged difference `−3.968 µL`, two-sided Student t95 `[−5.451, −2.485] µL`; paired 20,000 resamples `[−5.438, −2.589] µL`. **Pierced status was not randomized**, so this is a strong source-observed association, not a pure causal nectar-removal treatment effect.
- **Female reproductive outcome under pollinator access**: 40 shrubs contributed **one different flower for each of three treatments**. The published original records contain mean mature seeds: `−P−R = 5.175`, `+P−R = 26.125`, `+P+R = 31.350` per flower. The within-shrub `+P+R minus +P−R` mean difference is **+5.225 seeds**, parametric paired t95 `[−12.850, +23.300]`, fixed-seed 20,000 paired-shrub bootstrap95 `[−12.275, +22.400]`. 19 shrubs increase, 19 decrease, 2 tie. Seed-present counts are 2/40, 32/40 and 28/40 respectively. The presence contrast for robbing-with-pollinators is −0.10, paired bootstrap95 `[−0.30, +0.10]`. **Failure to detect a decrease is not proof of equivalence or zero seed cost**: the negative end of the seed-count t interval reaches ~49% of the protected-pollinator mean.
- **Pollinator dependence**: the `+P−R minus −P−R` paired mean is `+20.95` seeds, t95 `[+8.81,+33.09]`, consistent with strong female seed dependence on pollinator access in this system. This is not the cost of maintaining a structural morphology.

## Source design audit: what these contrasts do not identify

The original paper states `−P−R` is a **bagged unopened bud**; `+P−R` is an **unopened bud with red-ink-colored masking tape around the corolla base**; `+P+R` is a **naturally open flower already showing a bumblebee-perforated corolla**. The last is **not an otherwise comparable randomized bud allocated to robbery**. Treatment bundles differ in developmental stage, visitor exposure, handling and selection; ink/tape effects are unverified. There is no `−P+R` fourth factorial cell. Consequently:

1. The original observed seed contrasts remain useful as published ecological evidence, but cannot isolate **the causal effect of robbery** from exposure/flower-selection/handling confounding.
2. The resource survey and seed treatment records involve different flowers even when shrubs overlap; no individual-flower `nectar -> pollinator behavior -> seed` mediating causal path is observed.
3. Nectar resource loss and female reproductive change are **different outcomes with different exposure definitions**; a significant nectar contrast paired with a nonsignificant seed contrast does **not** test their difference statistically, quantify a buffer parameter, or prove adaptive compensation.
4. The original Zenodo March R script uses **glmmTMB mixed models** with `(1|plant)` for the two-part seed endpoints. The published June paper reports **GEE Wald tests** for this inference. They are distinct estimators, and one cannot claim exact published p-value reproduction from the archived R script alone.
5. Male siring fitness, architecture costs (`K`), recoverable conflict (`R`), different gene/structural architectures, and matched optimized `W_S*`, `W_D*` remain absent. Strict BALANCE occupancy cannot be inferred.

## Legitimate scientific use

This is a **separate independent research programme** showing an observed large reward depletion with uncertain (not proved neutral) female seed response. It is a reason to model the pathway `reward removal -> effective pollinator service -> male/female reproductive fitness` at the correct biological stage and to require an explicit downstream fitness receipt before classifying resource loss as shared-axis conflict. It is **not** a fourth study in the previous common-guild-composition RMSE denominator; no effect size is pooled.

## Reproduce

```bash
BALANCE_DESFONTAINIA_SOURCE=/path/to/'Raw Data Desfontainia fulgens.xlsx' python -m pytest -q tests/test_desfontainia_fitness_gate.py
python scripts/audit_desfontainia_fitness_gate.py --source /path/to/'Raw Data Desfontainia fulgens.xlsx' --out /tmp/independent-desfontainia-receipt.json
```

Auditor is dependency-free and parses exact `sheet3`/`sheet6` of the original hash-gated OOXML workbook without silently imputing missing values. It fails on wrong source digest, unexpected headers, malformed/duplicate shrub identities, invalid seed counts or missing original study denominators. Original U6 21 taxa, U2/U6 blind A/B coder sheets, and V4 frozen outcomes are not read, edited or populated.
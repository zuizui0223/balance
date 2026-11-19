# U6 visitor-order polarity × pollen-stage source identity (2026-11-19)

**Status: source-only, post-open exploratory reconciliation, no biological fit.**

This is an extension of BALANCE draft PR #273, based on main. It explicitly **reuses the three already sourced temporal-order records from unmerged PR #252** (`audit/u6-preoutcome-taxonomy-20261021`, source ledger `data/BALANCE_U6_SEQUENTIAL_VISITOR_ORDER_SOURCE_V1.csv`, upstream blob SHA `6df7e18e73ca4401aff675970fac95865015d89d`). It is **not a second independent validation of those original studies**, and no frozen U6 admission, source predictor or architecture response is changed.

## The focal error to avoid

The primary V4 timing predictor collapses `SEQUENTIAL_WITHIN_UNIT` into `ORDERED_OR_ALTERNATING`. That coding describes temporal exposure geometry; it does **not** mean the conflict is resolved and does not automatically identify an adaptive timing program.

The only three U6 sequential groups have two mechanistically distinct visitor orders:

| Original group | Source-side visitor sequence | Original admission evidence tag | Current measured fitness ceiling |
| --- | --- | --- | --- |
| *Clusia arrudae* | Honeybees remove pollen **before** effective native resin-bees visit | `DIRECT_REMOVAL_FITNESS_COST` | Honeybee visit frequencies correlate negatively with seeds, plus strong pollen-carrier depletion; **no randomized flower-structure comparison** |
| *Crescentia alata* | Social bees rob pollen **before** bats visit | `DIRECT_POLLEN_ROBBING_NO_POLLINATION` | Anther dehiscence/theft relationship across four trees; **40% estimate refers to nectar**, not pollen; seed/paternity fitness is not reported in this source receipt |
| *Tolmiea menziesii* | Effective fungus-gnat visits commonly **precede** later pollen-collecting syrphids and bumblebees | `DIRECT_POLLEN_ROBBING_NO_POLLINATION` | Visitor phenology and pollination role; **no matched theft-specific seed/paternity loss** |

Primary sources:
- do Carmo et al. 2004, [Biotropica DOI 10.1111/j.1744-7429.2004.tb00329.x](https://doi.org/10.1111/j.1744-7429.2004.tb00329.x) (ca 99% pollen removal and post-honeybee effective-bee loads less than 0.1%).
- Martínez del Río & Bullock 1990, [Botanical Sciences DOI 10.17129/botsci.1377](https://doi.org/10.17129/botsci.1377) (four-tree anther dehiscence association; ca 40% **nectar** removal).
- Goldblatt et al. 2004, [Plant Systematics and Evolution DOI 10.1007/s00606-003-0067-1](https://doi.org/10.1007/s00606-003-0067-1) (fungus-gnat, syrphid, bumblebee visitor order; early-visited male flowers still possess a residual pollen stock unless otherwise measured).

The source-documented relative visitor order is not a measurement of **the fraction of viable gametes exported before later visitors**. An early effective visitor may remove only a fraction of donor pollen; a later thief can then prevent export by subsequent legitimate visitors. Similarly, deposition on a recipient stigma followed by removal is a distinct pathway from donor pollen theft.

## Exact source-support audit: 21/3/1

- **21** original frozen U6 groups, 3 `SEQUENTIAL_WITHIN_UNIT`, and 18 `SIMULTANEOUS`.
- Within the three sequential groups, **2** are theft-before-first-effective-visitor and **1** is effective-visitor-before-later-theft.
- **Only 1 of the 3**, *Clusia*, bears the original admission tag referring to a plant fitness endpoint. Even this is not a matched randomized causal fitness effect or a full architecture-cost comparison.
- The three source-side groups are distinct admission references, but their heterogeneous biological endpoints are not an effect-size meta-analysis.
- The three post-open stage mismatch/bundled-flower flags in PR #273 concern **other** U6 groups; they do not fill missing comparable reproductive effects in the sequential stratum.

## Three leave-one-source ordered-group checks

| Source-side scenario | U6 ordered groups | Theft → legitimate | Legitimate → later theft | Ordered groups with original fitness-admission tag | 5-column V4 design rank |
| --- | ---:| ---:| ---:| ---:| ---:|
| Full frozen 3 | 3 | 2 | 1 | 1 | 5/5 |
| Drop *Clusia* | 2 | 1 | 1 | **0** | 5/5 |
| Drop *Crescentia* | 2 | 1 | 1 | 1 | 5/5 |
| Drop *Tolmiea* | 2 | 2 | **0** | 1 | 5/5 |

The original U6 two-ordered-group **marginal predictor-support** threshold still passes after any one of the three ordered groups is removed, and rank remains full. But an independent *within-polarity* comparison fails in the full and every deletion scenario because effective-first/later-theft has only one source (or none).

The stronger cross-universe G1 predictor common-support gate remains blocked by the frozen U2 `SINGLE+SIMULTANEOUS = 1` cell in every scenario. These source distinctions do **not** change the registered V4 model, its two directional predictions or existing priors.

## Hypothesis worth genuinely testing

**Stage-dependent future-opportunity hypothesis:** The direct effect of irreversible pollen removal on realized male reproduction depends on how many effective pollen-export opportunities remain **after** the removal, and how much viable pollen remains at each opportunity. Merely knowing that a legitimate visitor came first is inadequate.

For a new matched sequence experiment, record:
1. A common pollen cohort, floral age, available source-pollen stock, and baseline natural pollen depletion.
2. Explicit `legitimate -> thief` and `thief -> legitimate` randomized orders **with equal visitor identities, numbers, time gaps and opportunity counts**, and controls with no thief.
3. Pollen removed by each visitor and residual donor pollen *before and after* each visit, including any regeneration or delayed anther release.
4. Recipient stigma deposition plus viable siring/seed-fitness outcomes linked to the same flowers or families, with independent plants as the replication unit.
5. Distinct developmental floral programming manipulation, if the evolutionary routing hypothesis rather than visitor-access sequence is the intended estimand.

Observed pollen-carrier load and seed-count associations from separate flowers/studies cannot be multiplied into a lineage-fitness or structural `L/K/Phi` value. Until these matched measurements exist, the stage-dependent hypothesis is a falsifiable proposal, not an established ecological result.

## Reproduce / protection

```bash
python scripts/audit_u6_temporal_polarity_bridge.py
python -m pytest -q tests/test_u6_temporal_polarity_bridge.py
```

The code checks the three original DOIs and groups against the frozen U6 evidence receipts; validates all 21 U6 source group identities; confirms all 3 original `SEQUENTIAL_WITHIN_UNIT` codes; verifies each original source admission tag and fixed prior-stage reviewer flags; and recalculates rank/support under every single-group removal. It rejects contradictory source coding, fabricated A/B architecture returns, and selective deletion of a hard case. No independent new experimental outcomes, architecture labels, V4 fitted coefficients, or primary publications were produced.

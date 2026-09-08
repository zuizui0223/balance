# BALANCE Trifolium factorial negative control v1

## Purpose

Register `Trifolium repens` (Santangelo, Thompson & Johnson 2018) as a design-matched quantitative negative control for the Chapter-2 diffuse-factorial R layer.

This source is valuable because it satisfies the experimental-design side of the Q1B contract but does **not** recover a same-trait pollinator-versus-herbivore opposing-selection pattern.

## Source

Santangelo JS, Thompson KA, Johnson MTJ. 2018. `Herbivores and plant defenses affect selection on plant reproductive traits more strongly than pollinators.` Journal of Evolutionary Biology. DOI `10.1111/jeb.13392`.

Public data/code:

- Dryad DOI `10.5061/dryad.h6qg003`;
- author repository `James-S-Santangelo/HPS_Herbivore-Pollinator-Selection`;
- reproducible R script `scripts/Santangelo-Thompson-Johnson_Evolution_2018.R`;
- cleaned experimental data and treatment-specific selection datasets under `data-clean/`;
- published selection-gradient and p-value CSV tables under `tables/`.

## Experimental design

The common-garden experiment crossed:

```text
chemical defence / HCN
x
pollination treatment
x
herbivory treatment
```

across 50 clonal genotypes of white clover.

Thus it is close to the factorial architecture needed for quantitative Chapter-2 screening and is a stronger negative control than a study lacking agent manipulations.

## Reproducible selection construction

The public R script reconstructs treatment-specific selection gradients and then defines agent-mediated differences as:

```text
HerbMedSel = Gradient.HerbAmb - Gradient.HerbRed
PollMedSel = Gradient.PollOp  - Gradient.PollSupp
DefMedSel  = Gradient.Cyan    - Gradient.Acyan
```

The analysis therefore preserves signed agent-mediated selection rather than only absolute effect magnitudes.

## Why it is not a positive Q1B replication

The source-level result is not a single same-trait opposing pollinator/herbivore pair.

The paper and public model tables show:

- pollinators did not independently alter selection on the measured traits overall;
- pollination modified flowering-time selection only conditional on HCN state;
- herbivores weakened selection for increased inflorescence production;
- herbivore effects on flower-size traits were also HCN dependent;
- the strongest pollination and herbivory selection modifications therefore occur on different trait/modifier combinations.

In the published multivariate model:

```text
Pollination : flowering date          p ~= 0.838
Herbivory   : inflorescence number    p ~= 0.000103
HCN x Pollination x flowering date    p ~= 0.0132
HCN x Herbivory x banner width        p ~= 0.0137
HCN x Herbivory x banner height       p ~= 0.0465
```

These results support a strong statement that the factorial experiment contains real agent-dependent selection, while failing the narrower same-trait opposing-agent admission rule.

## Registered screening state

```text
screening_class = FACTORIAL_NO_SAME_TRAIT_OPPOSITION
pattern_promotion_status = NO_POSITIVE_PROMOTION
effect_size_status = NEGATIVE_CONTROL_REANALYSIS_READY
```

`NEGATIVE_CONTROL_REANALYSIS_READY` means that the public data and reproducible models are sufficient to rerun the registered analysis as a negative/control case. It does **not** mean that the study is an effect-size-ready positive conflict receipt.

## Q1B role

For `DIFFUSE_FACTORIAL_AGENT_SELECTION`:

```text
positive registered pattern candidates = 1  # Fragaria
reanalysis negative/control candidates = 1  # Trifolium
effect-size-ready positive clusters     = 0
```

The Trifolium source must never increase the positive numerator unless a preregistered same-trait agent contrast is independently recovered from the data.

## Independence and modifier safeguards

- HCN-positive and HCN-negative plants are modifier strata within one experiment, not independent studies.
- Multiple traits are dependent outcomes within one study, not independent literature replications.
- Herbivory and pollination contrasts are not pooled across different traits merely because both are non-zero.
- HCN-dependent effects are retained as moderator structure rather than cherry-picked as separate positive examples.

## Relation to Fragaria

`Fragaria vesca` remains the current positive diffuse-factorial conflict candidate because the same trait (`inflorescence_density`) has pollinator- and herbivore-mediated effects of opposite sign in a common-fitness factorial design.

`Trifolium repens` supplies the complementary falsification/control case: a similarly rich factorial manipulation does not automatically yield that same-trait conflict signature.

## Claim ceiling

This negative control says nothing directly about `W_S*`, `W_D*`, `rho`, `Phi`, `xi`, `d_B`, a BALANCE critical threshold, or natural prevalence.

It strengthens the R-layer inference by showing that the screening rule can reject a high-quality factorial study rather than classifying every pollination-by-herbivory experiment as positive.

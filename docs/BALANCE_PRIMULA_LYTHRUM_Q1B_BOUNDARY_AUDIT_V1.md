# BALANCE Primula / Lythrum quantitative-boundary audit v1

## Purpose

This audit asks whether two strict multi-agent floral-selection programmes can be counted as additional positive replications of the registered `DIFFUSE_FACTORIAL_AGENT_SELECTION` (Q1B) estimand after the first effect-size-ready `Fragaria vesca` receipt.

The answer is **no for two different reasons**.

- `Primula farinosa` contains a strong experimentally identified pollinator-versus-grazer conflict on one floral-display coordinate, but the coordinate is a genetically based discrete long/short scape morph and the source estimand is relative morph fitness rather than a continuous standardized selection-gradient vector.
- `Lythrum salicaria` uses a highly relevant pollination-by-damage design and standardized selection analysis, but the source does not recover pollinator-mediated selection on the registered traits and does not recover a pollination-by-damage interaction in selection.

These studies therefore improve the quantitative programme by defining two different boundaries around Q1B rather than by inflating its positive numerator.

## Primula farinosa — strict biological conflict but a different estimand

Primary source:

- Ågren J, Hellström F, Toräng P, Ehrlén J. 2013. `Mutualists and antagonists drive among-population variation in selection and evolution of floral display in a perennial herb.` PNAS. DOI `10.1073/pnas.1301421110`.

The source combines long-term observations with field experiments. The focal display coordinate is a genetically based scape dimorphism:

```text
long scape
short scape
```

The experiment manipulates the intensity of mutualist and antagonist interactions and identifies opposite directions of selection:

```text
pollinator-mediated selection -> long scape

 grazer-mediated selection     -> short scape
```

The source further shows that spatial variation in the relative strength of these interactions explains among-population variation in relative fitness and is associated with morph-frequency evolution.

This is a high-information real-world selection mosaic. It should not be downgraded to `UNRESOLVED` in a biological sense merely because it is not a continuous beta study.

However, it is not compatible with the current Q1B estimand:

```text
(P | H present,
 P | H absent,
 H | P limited,
 H | P supplemented)
```

on one continuous standardized trait coordinate.

The Primula source instead targets a discrete genetically defined contrast. Converting the long-versus-short relative-fitness contrast into a pseudo-continuous beta would change the estimand. Counting four field sites or repeated years as independent studies would also create pseudoreplication.

The registered action is therefore a separate reserve stratum:

```text
DISCRETE_MORPH_AGENT_SELECTION
```

with one current programme and zero effect-size-ready pooled receipts.

## Lythrum salicaria — design-matched negative control

Primary source:

- Thomsen CJM, Sargent RD. 2017. `Evidence that a herbivore tolerance response affects selection on floral traits and inflorescence architecture in purple loosestrife (Lythrum salicaria).` Annals of Botany. DOI `10.1093/aob/mcx026`.

The experiment combines simulated apical-meristem damage with pollen supplementation and estimates standardized trait-selection gradients using relative total seed production.

The most relevant reported linear-selection results are:

| trait | herbivory-mediated change in direct selection | pollinator-mediated `delta beta` | pollination x damage x trait |
|---|---:|---:|---:|
| number of inflorescences | `+0.27 +/- 0.10` | `-0.01 +/- 0.05` | `-0.12 +/- 0.12` |
| inflorescence height | `+0.11 +/- 0.11` | `0.00 +/- 0.06` | `+0.11 +/- 0.13` |
| flowering start | `+0.25 +/- 0.10` | `-0.07 +/- 0.06` | `+0.01 +/- 0.12` |

The biological conclusion is not that the experiment lacked selection. Simulated herbivory changed direct selection strongly enough to favour earlier flowering and weaken selection for more inflorescences.

The quantitative boundary is narrower:

```text
pollinator-mediated selection on the registered traits: not detected
pollination x damage x trait interaction:              not detected
```

Thus Lythrum is valuable precisely because it is a design-near control in which the multi-agent experiment does **not** yield a same-trait diffuse opposing Q1B signal.

It is registered as:

```text
FACTORIAL_NO_DIFFUSE_SAME_TRAIT_CONFLICT
```

and must not increase either the positive Q1B numerator or the effect-size-ready numerator.

## Why these two boundaries matter

The three current factorial programmes now play distinct roles:

```text
Fragaria     positive diffuse-factorial conflict
             + effect-size-ready joint covariance

Trifolium    factorial design-matched negative control
             + public raw data / code

Lythrum      near-factorial source-reported negative control
             + herbivory-mediated selection but no pollinator-mediated Q1B pair
```

Primula is intentionally outside that vector because its discrete-morph estimand is different:

```text
Primula      strong opposing-agent morph-selection mosaic
             + separate discrete-morph quantitative stratum
```

This separation prevents three common errors:

1. **positive-only screening** — factorial experiments without an opposing signal are retained;
2. **estimand conversion by convenience** — a discrete genetic morph contrast is not renamed a continuous beta;
3. **replication inflation** — sites, years, traits or morph classes are not counted as independent studies.

## Quantitative bookkeeping after this audit

### `DIFFUSE_FACTORIAL_AGENT_SELECTION`

```text
positive registered clusters          = 1  (Fragaria)
design-matched control/reanalysis      = 2  (Trifolium, Lythrum)
effect-size-ready positive clusters    = 1  (Fragaria)
minimum independent positives to pool  = 3
pooling                                = NOT READY
```

### `DISCRETE_MORPH_AGENT_SELECTION`

```text
registered programmes                  = 1  (Primula farinosa)
effect-size-ready clusters             = 0
minimum independent clusters to pool   = 3
pooling                                = NOT READY
```

## Claim ceiling

Appropriate:

> Strict multi-agent experiments occupy more than one quantitative regime. Fragaria supplies a context-dependent continuous-trait factorial conflict with joint uncertainty; Primula supplies a strong discrete genetic morph selection mosaic; Trifolium and Lythrum show that factorial or near-factorial multi-agent designs do not automatically produce same-trait opposing selection.

Not appropriate:

> The four programmes are four exchangeable estimates of one universal pollinator-versus-antagonist effect size.

None of these studies identifies direct BALANCE `W_S*`, `W_D*`, `rho`, `Phi`, `xi`, or `d_B`.

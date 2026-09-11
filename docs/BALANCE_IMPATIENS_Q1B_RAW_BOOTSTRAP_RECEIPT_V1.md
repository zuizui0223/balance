# BALANCE Impatiens Q1B raw-bootstrap receipt v1

## Result

`Impatiens capensis` is the second independent positive effect-size-ready cluster in the registered `DIFFUSE_FACTORIAL_AGENT_SELECTION` (Q1B) stratum.

```text
positive effect-size-ready Q1B clusters = 2
minimum independent positives to pool   = 3
pooling                                  = NOT READY
```

This is an R-layer quantitative selection-pattern receipt. It is not direct BALANCE occupancy and does not identify `W_S*`, `W_D*`, `rho`, `Phi`, `xi`, or `d_B`.

## Source and frozen analysis

Primary study: Soper Gorden & Adler 2018, DOI `10.1002/ajb2.1182`.
Public Dryad archive: `10.5061/dryad.0j96d17`.

The analysis was frozen before the Q1B result was opened:

- use the randomized factorial experiment;
- restrict `Robbing == N` so the registered Q1B design is Pollination × Florivory;
- common reproductive component = `Average_CH_Fruits_Per_Day`;
- predeclared traits = `Early_Season_Flower_Redness` and `Early_Season_Condensed_Tannins`;
- nuisance covariate = `Date_of_First_CH_Flower`;
- all predeclared traits must be retained;
- no post hoc trait choice is allowed;
- estimate the four treatment-cell selection slopes and obtain their joint uncertainty by stratified raw-plant bootstrap.

The frozen implementation is `scripts/run_impatiens_q1b_reanalysis.py`. The first execution used 2,000 bootstrap replicates and seed `20260909`.

## Data support

Complete-case no-robbing sample:

```text
N = 85
open pollination, florivory absent       19
open pollination, florivory present      23
supplemented pollination, florivory absent 23
supplemented pollination, florivory present 20
```

The joint covariance is therefore estimated from raw-data resampling rather than by setting unreported covariances to zero.

## Registered result

The machine receipt is `data/BALANCE_IMPATIENS_Q1B_RECEIPT_V1.json` and has state

`JOINT_MULTICONTRAST_READY`.

For early-season condensed tannins, the registered mediated contrasts were:

```text
P | florivory present      -0.2404 ± 0.2789
P | florivory absent       -0.4164 ± 0.2868
H | open pollination        0.0196 ± 0.3019
H | supplemented           -0.1564 ± 0.2582
```

For early-season flower redness:

```text
P | florivory present       0.4827 ± 0.4062
P | florivory absent        0.0145 ± 0.3942
H | open pollination        0.4544 ± 0.5155
H | supplemented           -0.0139 ± 0.2284
```

Here `P` and `H` denote the registered pollinator- and florivory-mediated treatment contrasts; signs must be interpreted with the registered treatment-difference convention rather than as standalone biological labels.

Both predeclared traits satisfy the preregistered point-pattern opposition rule in at least one factorial context. The confidence intervals are broad and individually overlap zero, so this is not reported as a strong single-system significance result. Its promotion is based on the registered Q1B requirements: a positive same-trait factorial pattern plus a complete dependent multicontrast effect and joint uncertainty from raw bootstrap.

## Why this is effect-size ready

The receipt provides, for every predeclared trait:

1. the four treatment-specific selection slopes;
2. all four registered mediated contrasts;
3. bootstrap uncertainty for every contrast;
4. the full 4×4 covariance matrix of the mediated contrast vector;
5. one independent biological study cluster.

It therefore satisfies the `JOINT_MULTICONTRAST_READY` route in `BALANCE_FACTORIAL_SELECTION_RECEIPT_V1.md`.

## Pooling gate

This changes only the positive effect-ready numerator:

```text
Fragaria vesca     effect-size-ready positive
Impatiens capensis effect-size-ready positive
----------------------------------------------
current positive effect-ready clusters = 2
required before first pool             = 3
```

Gymnadenia conopsea 2015 remains the leading third candidate but is not counted until its joint covariance is identified through reported factorial sufficient statistics or a valid raw-data/joint-model route.

# Peucedanum longitudinal mosaic — Chapter 2 observational evidence v1

## Question

Does the Peucedanum source series repeatedly place floral sex allocation on the same antagonist-pressure axis, or is the 2025 HL--HC sign reversal an isolated operational result?

This is an **observational longitudinal-concordance** question. It is not a direct `W_S*` versus `W_D*` BALANCE test.

## Layer 1 — 2021 population and temporal pressure mosaic

Kudo & Shibata (2021), DOI `10.1002/ece3.7468`, followed nine populations over 2017--2019.

Published results include:

```text
flowering time -> seed predation
GLMM estimate = -0.803
SE = 0.110
z = -7.29
p < 0.0001
```

and, across populations and years,

```text
predation risk vs proportion of male flowers
r^2 = 0.64
p < 0.0001.
```

The source also contains a within-population temporal check at HC: earlier flowering in 2018 was associated with 59% predation versus 29% in 2019 when flowering occurred at its usual time.

Thus the early/late environmental ordering is not merely a between-population label: predation intensity also changes through time within one population.

## Layer 2 — later mechanistic / fitness source

Dryad DOI `10.5061/dryad.w3r2280v5` registers the follow-up dataset used to examine male-biased flower production under intensive predispersal seed predation.

Its registered source interpretation is directionally consistent with the 2021 mosaic:

- early-snowmelt populations experience intensive predation;
- predator oviposition is associated with more perfect flowers and taller inflorescences, whereas male flower number is not the positive oviposition target;
- male-biased allocation is advantageous under high predation through female-damage reduction while floral display / male function is retained.

This layer is retained as corroboration and is **not counted as an independent study simply because it has a separate dataset DOI**.

## Layer 3 — 2025 selection reversal

Kudo & Shibata (2025), DOI `10.1111/1365-2745.70130`, directly estimates selection across the ordered contexts

```text
HA -> HL -> HC -> KD -> HD.
```

For final fruit-set selection gradient on perfect-flower production:

```text
HA  -0.035
HL  -0.029
HC  +0.034
KD  +0.008
HD  +0.026.
```

The sign therefore changes between HL and HC. Selection differentials and female-gain shape place their threshold in the same coarse bracket in the separate critical-definition analysis.

## Registered longitudinal result

The Chapter-2 classifier requires all of the following:

```text
1. later flowering predicts lower predation;
2. high-predation populations track toward greater male allocation;
3. direct selection on perfect-flower production changes from negative on the early/high-predation side to positive on the later/lower-predation side.
```

Current published-source readout:

```text
LONGITUDINAL_MOSAIC_CONCORDANT
```

Implementation:

```text
balance_domain/longitudinal_mosaic.py
empirical/peucedanum/PEUCEDANUM_LONGITUDINAL_MOSAIC_INPUT_V1.json
```

## What this adds to Chapter 2

The result is stronger than a single 2025 coefficient sign change. It shows a temporally extended chain in the same biological system:

```text
phenology shifts antagonist pressure
        ->
sex allocation tracks that pressure
        ->
fitness selection on perfect-flower production reverses across the same broad environmental ordering.
```

This supports the existence of a persistent **selection mosaic / critical region** worth testing with the BALANCE worldline framework.

## Claim ceiling

Do not interpret this receipt as:

- three independent studies;
- a causal SCH conflict-load receipt `L`;
- an observed shared-world optimum `W_S*`;
- an observed differentiated-world optimum `W_D*`;
- architecture cost `K`;
- direct BALANCE occupancy;
- historical differentiation.

The strongest statement is:

```text
A multi-year, multi-source observational Peucedanum series is directionally concordant with one recurrent phenology--predation--sex-allocation selection mosaic; the causal two-worldline BALANCE test remains unexecuted.
```

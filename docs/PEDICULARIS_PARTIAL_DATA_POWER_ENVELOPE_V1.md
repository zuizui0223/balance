# Pedicularis partial-data power envelope v1

## Purpose

Replace the deliberately conservative complete-case power envelope with a partial-data hierarchical approximation that retains plants with incomplete subsets of the 16 factorial cells.

The design remains:

```text
A x D x E_G x E_P = 2 x 2 x 2 x 2
```

and the primary power-limiting estimand remains the `A:D:E_G:E_P` four-way contrast.

## Working model

For the subset of cells observed within plant `i`, use the working covariance

```text
V_i = sigma_e^2 I + sigma_plant^2 J.
```

Generalized least-squares information is accumulated over all observed cells rather than discarding an entire plant after one missing cell.

This is still a Gaussian design scaffold. It is not the final seed-count GLMM. Its role is to quantify how much of the previous sample-size inflation was caused by the complete-case rule itself.

## Pre-dry-run envelope

For a standardized four-way signed contrast `effect / residual SD`, alpha=0.05 and target power=0.80, the balanced no-missing benchmark remains:

| four-way / residual SD | plants |
|---:|---:|
| 0.50 | 503 |
| 0.75 | 224 |
| 1.00 | 126 |
| 1.25 | 81 |
| 1.50 | 56 |
| 2.00 | 32 |

Under independent cell attrition, the partial-data GLS approximation gives the following expected-information thresholds when `plant SD = residual SD`:

| four-way / residual SD | 0% attrition | 5% attrition | 10% attrition |
|---:|---:|---:|---:|
| 0.50 | 503 | 531 | 563 |
| 0.75 | 224 | 236 | 250 |
| 1.00 | 126 | 133 | 141 |
| 1.25 | 81 | 85 | 90 |
| 1.50 | 56 | 59 | 63 |
| 2.00 | 32 | 34 | 36 |

These are design-envelope calculations, not effect predictions for `Pedicularis rex`.

## Main conclusion

The previous complete-case penalty was mostly an analysis artifact. At 5% cell attrition, requiring all 16 observations would retain only about `0.95^16 = 0.44` of plants and inflate a 1-SD design from about 126 complete plants to roughly 286 assigned plants. Retaining partial observations reduces the corresponding expected-information requirement to about 133 assigned plants under this working model.

Therefore the main design recommendation changes from:

```text
protect complete 16-cell plants at almost any cost
```

to:

```text
preserve randomized cell assignment,
record realized treatment states,
retain partial observations,
and fit the registered hierarchical model.
```

## Important limits

The envelope assumes:

- missingness is independent of the latent outcome after registered treatment/block information;
- plant covariance is adequately represented by a random intercept at the design stage;
- the fitness-scale approximation is Gaussian;
- all 16 fixed-effect columns remain identifiable in the realized design;
- no treatment-dependent attrition or structural zero process is present.

The dry run must test these assumptions. If attrition depends on A, D, consumer treatment, manipulation damage, or latent reproductive failure, final power must be recalculated under that missingness mechanism.

## Promotion rule

Do not freeze the powered experiment from this envelope alone.

After the dry run, replace placeholder values with:

```text
observed cell-specific attrition
plant-level variance / within-plant correlation
outcome dispersion and zero structure
feasible flowers per plant
minimum meaningful four-way tolerance/effect
minimum meaningful consumer-allocation contrast
```

Then fit the final simulation to the analysis model intended for the paper. `POWER_QUALIFIED` is granted only when the final design meets the preregistered P1/P2 targets.

## Practical implication

If the minimum biologically meaningful four-way magnitude is near 1 residual SD, a design around 130--150 plants may be plausible under modest random cell loss. If the target is only 0.5 residual SD, the design remains on the order of 500+ plants and is probably unsuitable for the proposed intensive 16-cell field architecture without either repeated seasons/populations or a different experimental allocation.

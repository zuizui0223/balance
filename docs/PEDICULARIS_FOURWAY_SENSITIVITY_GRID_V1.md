# Pedicularis four-way sensitivity grid v1

## Purpose

Provide a pre-dry-run feasibility envelope for the `A:D:E_G:E_P` four-way estimand under the current complete-plant simulation scaffold.

This is not a final sample-size calculation. It is a diagnostic to reveal when the registered design becomes implausibly large before field execution.

## Assumptions used for the provisional grid

The current scaffold treats each plant as contributing one observation to every one of the 16 factorial cells and discards a plant from the four-way contrast if any one cell is lost.

For a balanced 2^4 contrast with residual SD `sigma`, the signed four-way contrast has approximate SD `4 sigma`. Using a two-sided alpha of 0.05 and target power 0.80, the approximate complete-plant requirement is:

```text
n_complete ~= ((1.96 + 0.842) * 4 / (four_way_effect / sigma))^2
```

If per-cell attrition is `a` and complete-case retention is required, a plant survives all sixteen cells with probability:

```text
p_complete = (1-a)^16
```

and the assigned-plant requirement is approximately `n_complete / p_complete`.

## Sensitivity grid

| four-way effect / residual SD | per-cell attrition | complete-plant probability | complete plants for ~80% power | assigned plants under complete-case rule |
|---:|---:|---:|---:|---:|
| 0.50 | 0% | 1.00 | 503 | 503 |
| 0.50 | 2% | 0.72 | 503 | 695 |
| 0.50 | 5% | 0.44 | 503 | 1142 |
| 0.50 | 10% | 0.19 | 503 | 2711 |
| 0.75 | 0% | 1.00 | 224 | 224 |
| 0.75 | 2% | 0.72 | 224 | 309 |
| 0.75 | 5% | 0.44 | 224 | 508 |
| 0.75 | 10% | 0.19 | 224 | 1205 |
| 1.00 | 0% | 1.00 | 126 | 126 |
| 1.00 | 2% | 0.72 | 126 | 174 |
| 1.00 | 5% | 0.44 | 126 | 286 |
| 1.00 | 10% | 0.19 | 126 | 678 |
| 1.25 | 0% | 1.00 | 81 | 81 |
| 1.25 | 2% | 0.72 | 81 | 112 |
| 1.25 | 5% | 0.44 | 81 | 183 |
| 1.25 | 10% | 0.19 | 81 | 434 |
| 1.50 | 0% | 1.00 | 56 | 56 |
| 1.50 | 2% | 0.72 | 56 | 78 |
| 1.50 | 5% | 0.44 | 56 | 127 |
| 1.50 | 10% | 0.19 | 56 | 302 |
| 2.00 | 0% | 1.00 | 32 | 32 |
| 2.00 | 2% | 0.72 | 32 | 44 |
| 2.00 | 5% | 0.44 | 32 | 72 |
| 2.00 | 10% | 0.19 | 32 | 170 |

## Immediate design implication

The dominant feasibility risk is not only the biological effect size. It is the current **complete-case requirement across all 16 cells**. Even 5% cell-level attrition retains only about 44% of plants as complete sixteen-cell blocks.

Therefore the current scaffold should be treated as a conservative upper-bound diagnostic rather than the final power engine.

## Registered next step

After the technical dry run, replace the complete-case scaffold with a hierarchical model simulation that:

- retains partially observed plants when the missingness mechanism is admissible;
- represents the actual number of flowers per plant and per cell;
- includes plant and, if needed, inflorescence random effects;
- uses the registered count/binomial distribution for viable-seed output;
- propagates observed dispersion and zero inflation;
- evaluates both detection of material non-separability and equivalence to the registered separability tolerance.

Do not commit to hundreds of plants solely because the complete-case approximation is large. First determine whether cell attrition and within-plant covariance actually support a more efficient hierarchical design.

## Provisional feasibility interpretation

Until dry-run estimates exist:

```text
four-way <= 0.5 residual SD  -> likely impractical under complete-case design
four-way ~ 1.0 residual SD  -> roughly 126 complete plants before attrition
four-way ~ 1.5 residual SD  -> roughly 56 complete plants before attrition
four-way ~ 2.0 residual SD  -> roughly 32 complete plants before attrition
```

These are design-sensitivity numbers, not biological predictions about Pedicularis.

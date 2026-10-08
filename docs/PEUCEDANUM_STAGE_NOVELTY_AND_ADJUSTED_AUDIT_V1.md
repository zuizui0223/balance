# Peucedanum stage contrast: source novelty and sensitivity audit (2026-10-08)

## Scientific ownership — avoid rediscovering the source result

Kudo & Shibata (2025), *Journal of Ecology*, DOI 10.1111/1365-2745.70130,
**already study** selection on perfect- and male-flower production across
pollination, oviposition/fruit predation, female fitness, and local phenology.
The authors report that predator moths prefer plants with many perfect flowers
and fewer male flowers, and that seed predation contributes to a shift in local
selection direction. Thus neither "seed predators alter floral gender
selection" nor "initial versus final fruit success has different trait slopes"
is a new BALANCE discovery. The source is not an independent confirmation
dataset for claims it originally established.

This extension is strictly **auditing robustness and source dependence** of
an existing ecological finding; it is not a new demonstration of architectural
differentiation, resource cost K, recoverable load R, hysteresis, or BALANCE
occupancy.

## Source and exploratory provenance

HUSCAP DOI 10.14943/hu95572, exact normalized source CSV SHA256
`ed6bf4c5301309283ca2e3d2033fdab1e253d46ed94bbba5fde1f3ee43281dbc`.
685 records, 19 observed plot-year cells; 2021 HA has no final fruit
outcomes. Original published-table numerical reproduction remains
`R1_NOT_FULLY_REPRODUCED` (Issue #215).

The unadjusted within-cell, complete-pair weighted regression using perfect
flower fraction shows four **descriptive** changes of slope sign (HA2020,
HC2020, HA2022, HD2021) among 18 analysable plot-year cells. Their paired HC3
z statistics are all smaller than 1.96 in absolute magnitude. There is no
statistically established sign reversal from these descriptive checks.

## Size-adjusted sensitivity model

Instead of comparing separate regression coefficients on different samples,
the outcome is exactly the individual paired change in observed fruit rates:

`D_i = FinalFruitN_i/HflowerN_i - InitialFruitN_i/HflowerN_i`.

Within each plot-year, fit weighted least squares with perfect-flower-count
weights and HC3 heteroskedasticity-consistent uncertainty:

- **primary alternative to a shared predictor denominator:**
  `D_i ~ standardized(log1p(MflowerN_i)) + standardized(log(HflowerN_i)) + standardized(Height_i)`;
- **sensitivity predictor:** replace the male-count term with standardized
  `HflowerN_i/(HflowerN_i+MflowerN_i)` while retaining the size controls;
- retain observed count reversals (FinalFruitN > InitialFruitN) for the
  **nonnested paired-rate** outcome only; repeat excluding those 3 rows
  without claiming they are source errors;
- test all plot-year cells, not only sign flips. Report nominal normal
  approximation HC3 p-values plus BH-adjusted q-values **within each of the
  four exploratory variants**, explicitly not a preregistered multiplicity
  decision over all prior model explorations.

Source-global complete-pair-plus-height support is 608 rows. Exclusion of
the 3 nonnested count reversals leaves 605 rows. Eighteen cells have data
support; 2023 HD has essentially zero paired-rate variation, so 17 yield
nondegenerate exploratory p-values. These counts are validated as code
contracts but do not imply independent replicates.

## Computed exploratory observations, pending standalone workflow receipt

In the primary male-count variant, the smallest nominal p-value was ~0.0139
in HC2020, but the smallest BH q-value across 17 nondegenerate cells was
~0.2367. In the perfect-fraction adjusted sensitivity, the smallest q was
~0.1742. **No cell survives a 0.05 BH screen**, and the earlier four visual
sign reversals cannot be promoted as supported trait-selection reversals.

HC2023 is a particularly important uncertainty caution. The **unadjusted**
perfect-fraction slope on its raw fraction scale was -0.321637 ± 0.0689
(HC3). Its predictor SD was 0.16705, so the comparable per-SD contrast is
approximately -0.05373 ± 0.0115, **not -0.3216 per SD**. The
size-adjusted per-SD coefficient is -0.03769 ± 0.04539 (nominal p~0.4063).
This reflects both some attenuation and a substantial loss of precision.
Never compare the raw-scale and standardized coefficients directly.

These p/q diagnostics are not independent tests of the previously explored
model landscape, nor do they correct for within-plot-year nonrandomness,
year-level population dependence or unmeasured fitness/resource allocation.

## Auxiliary predator egg association — not a causal mediation result

A **separate exploratory** pooled WLS with plot-year fixed intercepts,
log perfect flower count, log1p male flower count, and flower height showed
an inverse association between `log1p(OvipN)` and `D`. A male-by-egg
interaction was not supported in a preliminary calculation. Egg counts are
post-flowering measurements and cannot be randomized from these records;
their association with fruit loss is expected from the predator biology and
does not independently identify an adaptive switching mechanism.

No numeric egg model is treated as a confirmatory result or introduced into
the existing source-analysis coefficient table without its own reviewed code,
uncertainty, and temporal assumptions.

## Next ecological decision

Do not open a standalone "stage selection reverses because of predation"
paper: that is both substantially covered by the source authors and not
robustly established by the present additional within-cell fit.

Keep this extension as a reproducibility / robustness appendix to the
BALANCE comparative ecology programme. A genuinely new mechanism would
require an intervention or cross-system predictive restriction that separates
a structural shared/differentiated architecture's causal fitness payoff from
the already-observed floral allocation selection mosaic.

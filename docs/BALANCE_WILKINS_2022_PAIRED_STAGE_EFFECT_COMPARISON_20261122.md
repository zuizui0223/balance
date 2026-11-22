# Wilkins 2022: formally paired destination-stage contrasts

**2026-11-22 | Source-locked exploratory analysis, completed after PR #279's
published-model reproduction and first two endpoint sensitivity analyses.**

## The statistical problem

The earlier real-data analysis demonstrated an architecture×bee-head-width
interaction for `log(BodyPollen / CorbiculaPollen)` on a **bee-equal-weighted**
scale (59 bees; beta +3.175, HC3 p=.00593), but did not detect the corresponding
size interaction for `log(StigmaPollen)` or
`log(StigmaPollen / BodyPollen)` when fitted separately.

**Comparing a significant p-value to a nonsignificant p-value is not a
statistical comparison of their underlying effects.** Furthermore, both
stage outcomes were recorded for the *same bees*: covariance matters. An
adequate next analysis therefore tests the direct stage contrast on the
same observational scale, with the same bees, predictors and model
specification.

## Frozen direct biological question

Under altered *Solanum elaeagnifolium* anther arrangement, is the bee-size
dependency observed for **terminal body/basket** pollen allocation
statistically different from that observed for **stigma/basket** pollen
allocation, when both are estimated from the same bee trial?

This is a pollen-destination question, **not** identification of paternity
fitness or true transfer efficiency. Original trial allocation alternated,
bee size was observed, and three colonies/source plants were not completely
independent or available for full source-plant blocking.

## Same-bee, same-design algebra and covariance (pre-run contract)

Use the source-authenticated publisher CSV (same SHA-256 as previous PR #279),
exactly 59 complete `BeeID` trials, each with observed positive stigma,
body and basket pollen, treatment and head width. Let:

```
B_i = log(BodyPollen_i / CorbiculaPollen_i)
S_i = log(StigmaPollen_i / BodyPollen_i)
T_i = log(StigmaPollen_i / CorbiculaPollen_i) = B_i + S_i
```

This *identity is not a newly discovered ecological mechanism*; its only
purpose is to keep the **same bee** and correct cross-endpoint covariance
when comparing the effects. For each response `B` and `S`, fit the same
one-row-per-bee model with:

- Treatment Sham (free) vs Cone (joined);
- continuous HeadWidth (centered once on the full 59-bee mean);
- colony fixed intercepts;
- either with original mean-centered observed VisitTime (conditional
  analysis, potentially adjusted for a post-treatment quantity), or
  without VisitTime (sensitivity).
- Treatment×HeadWidth, expressed per mm as the free−joined size slope.

All models use 59 observations, the same model matrix and no grain-count
weight. The fixed-effects estimator is ordinary least squares.

For the two independent outcomes `(B,S)`, compute **HC3** covariance
including the paired within-bee product of residuals. When the design is
shared, the directly estimated `T` coefficient is the sum of the two
outcome coefficients; compute its standard error from their **joint**
covariance, not the sum of two independently estimated variances.

The primary direct cross-endpoint comparison is:

```
delta = beta(B) - beta(T) = -beta(S)
```

This tests whether the architecture×size coefficient for body relative to
basket differs from that for stigma relative to basket. Its apparent
simplicity is the exact within-bee dependency, not a claim of evolutionary
mechanism or causal mediation.

A secondary **2-df omnibus** tests whether all three destination-specific
log-count effects have equal size×architecture slopes by a Wald test of
`beta(B)=beta(S)=0` using their 2×2 HC3 covariance. It tests for
*some destination heterogeneity*, not a specific causal step or difference
between pollen-carrying body and recipient stigma.

Regression anchors: when VisitTime is controlled, the independent direct
models must reproduce the previously verified
`beta(B)=+3.17546609` and `beta(S)=−2.78571840` (and their HC3 interval
bounds) within a prespecified 0.002 absolute tolerance. If not, **fail**:
do not select a preferred implementation by p-value.

All p-values and intervals are *bee-row* approximate HC3 results. They are
not colony-population-robust with three original colonies. Conditioning on
post-treatment observed VisitTime creates a different estimand from the
unadjusted model. Observed stigmatic grains are not genetically verified
male fitness, and neither `BodyPollen` nor `StigmaPollen` is
a fully tracked pollen reservoir.

## Outcome interpretation gate before inspecting results

- If the **direct** `delta` interval excludes zero in both fixed models,
  report a within-study stage-differential association, but **not**
  proof that the visitor's grooming mediates or causes it.
- If `delta` intervals include zero, report **insufficient evidence
  that the head-width/architecture effects on body/basket and stigma/basket
  differ**, even if one individual-stage coefficient is positive and
  significant while another is not. Do not claim transfer decoupling
  as an established causal finding.
- If the omnibus detects heterogeneity but the direct `delta`
  does not, report only *some unequal destination slopes*, which may
  arise entirely from body-versus-basket allocation.
- Do not select a model by its p-value, impute seven missing noncollector
  bees, or treat the three original colonies as three independent
  evolutionary origins.

## Execution and deliverables

```bash
Rscript scripts/check_wilkins_2022_paired_stage_contrasts.R \
  ORIGINAL_PUBLISHER_CSV /tmp/wilkins-paired-stage
```

The original-source authenticated
`.github/workflows/wilkins-2022-architecture-reanalysis.yml`
runs this script only after the original 37 published tests and earlier
sensitivity checks. The new readout comprises:

- `paired_stage_effect_contrasts.csv`: four direct and derived
  same-bee headwidth-slope contrasts × two fixed models;
- `paired_stage_omnibus.csv`: 2-df HC3 omnibus on the two independent ratios;
- `paired_stage_inference_scope.csv`: source hash and restricted claim ceiling.

No U2/U6/V4 original blinded architectural outcomes, main manuscripts,
source-admission counts or hypothesized structural net fitness are changed.


## Actual authenticated result (2026-11-22)

The source-authenticated R workflow
[run #45017971832](https://github.com/zuizui0223/balance/actions/runs/45017971832)
completed successfully. The original five-model comparison again reproduced
37 published Type II tests, maximum absolute chi-square discrepancy 0.00169969.
The paired model recovered the previously verified individual response
coefficients and their HC3 intervals to eight decimals (a cross-implementation
regression check, not an independent study).

### Within-bee direct stage contrast: measured versus unmeasured

The **same 59 bees and full joint endpoint covariance** yielded these
exploratory size×architecture interaction coefficients (free−joined per
head-width mm), adjusted for observed visit time and colony intercepts:

| Same-bee observed log outcome | Beta | Approx. HC3 95% CI | Approx. p |
|---|---:|---:|---:|
| Terminal body / corbicula pollen | +3.1755 | [+0.9549, +5.3960] | 0.00593 |
| Stigma / corbicula pollen | +0.3897 | [−4.2595, +5.0390] | 0.8671 |
| **Direct effect difference:** body/basket minus stigma/basket | **+2.7857** | **[−2.9474, +8.5188]** | **0.3341** |

The **directly tested effect difference is NOT distinguishable from zero**.
It equals the negative of the independently fitted stigma/body effect as a
mathematical identity on the same log scale, and the paired covariance
calculation reproduces the expected interval. Therefore a strong
body/basket slope and an individually nonsignificant stigma/basket slope
**do not establish biological decoupling between terminal carrying and
stigma transfer**. No extra causal step is newly identified by this
algebraic check.

### Omnibus destination heterogeneity

The direct 2-df joint HC3 Wald test of equal source architecture×head-width
slopes across all three pollen destinations is:

| Fixed model | 2-df joint Wald χ² | Asymptotic p |
|---|---:|---:|
| Adjusted for observed visit time | **9.4435** | **0.00890** |
| Without visit-time adjustment | **7.8035** | **0.02021** |

This is **positive within-study statistical evidence that at least one
destination-specific log-pollen effect differs from another**; it may be
driven predominantly by the verified body/basket interaction. The omnibus
test does not establish which pair differs, and the direct body-vs-stigma
destination contrast above is not supported. The underlying response
ratios are calculated from the *same bee pollen inventory*, so the joint
two-dimensional test is not three independent outcome replications. These
are exploratory post-open checks on the original population of 59 bees
from only three colonies, not cross-population p-values.

The machine-readable exact model output is
[`results/wilkins_2022/PAIRED_DESTINATION_CONTRASTS_20261122.json`](../results/wilkins_2022/PAIRED_DESTINATION_CONTRASTS_20261122.json);
the actual GitHub Actions artifact
`wilkins-2022-architecture-model-replay` ID `14752347567`
(SHA-256 `3ea5ea51fdca69e8c808c449f31e4a2624fb53b466d2bd83e52d4dc467e9a690`)
contains the derived original-source stage contrasts, omnibus test and
provenance. The artifact expires in December 2026.

### Biological claim ceiling

What this adds: **the structure×visitor size relation varies across
measured pollen destinations in the original experiment**. What remains
unidentified: a specific loss of pollen transfer between body and stigma,
a causal grooming or temporal mediation pathway, actual fathered offspring,
pollen viability, source-plant hierarchy and the net architectural cost or
BALANCE `Phi`. The original source's alternating architecture allocation
and bee/plant/colony dependence also limit causal generalization.

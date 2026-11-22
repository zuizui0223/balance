# BALANCE: anther architecture, bee size and pollen destination

## What was recovered

The original publisher CSV and R code for **Wilkins, Mayberry, Vallejo-Marín & Russell (2022)**, [DOI 10.1007/s00442-022-05246-0](https://doi.org/10.1007/s00442-022-05246-0), were downloaded from the journal's [supplementary materials](https://link.springer.com/article/10.1007/s00442-022-05246-0#Sec15) and authenticated by byte counts and SHA-256. This is an original-data analysis of **60 bee trials**, not another transcription-only literature record. The source receipt and row-audit JSON are stored alongside this report.

The experiment manipulated naturally free anthers of *Solanum elaeagnifolium* into glued cones and compared them with free anthers receiving sham glue. Architecture assignment alternated; *Bombus impatiens* body size was observed. One bee foraged on four flowers per trial, with anthers and stigmas pooled separately. The same flowers served as donors and recipients. The dataset contains 28 free-anther and 32 joined-anther trials from three colonies, after seven of the 67 recruited bees failed to collect basket pollen and were excluded. The archive cannot recover outcomes for those seven bees. Source plants numbered eight; individual plant contributions are not identified in the CSV.

Anther counts are missing in three joined-anther trials; one of these also lacks head width. Thus the anther model has **57 complete bees** and other models involving head width have **59**. Descriptive basket, body and stigma results use all **60**. Four flowers, individual pollen grains, and multiple outcomes from a bee do not add independent experimental units.

## Verified pollen accounting changes the endpoint definition

Every row satisfies the following identities in the published CSV:

| Archived field | Verified contents | Biological scope |
|---|---|---|
| `BodyPollen` | Head + thorax + abdomen grains | Pollen remaining on the bee outside its baskets at the end of the trial |
| `PollinatingPollen` | `BodyPollen + StigmaPollen` | A composite of terminal body pollen and pollen already deposited on stigmas |
| `TotalPollen` | `PollinatingPollen + CorbiculaPollen` | Composite plus basket pollen; not initial pollen production or a complete flower mass balance |

The author R code uses `PollinatingPollen` for the reported nonbasket amount and allocation fraction. Those models include stigma grains in their response, so they cannot be treated as independent body-only corroboration of stigma receipt. The final stigma model instead uses the separate `BodyPollen` covariate. This distinction motivates two fixed endpoint-definition sensitivities: replacing the composite count with body-only count, and replacing composite-versus-basket counts with body-only-versus-basket counts. All other formula components remain the same.

## Arithmetic reproduced from the authentic rows

Values below are equal-bee-weighted means. Counts are per trial; anther and stigma counts pool the four flowers. Uncertainties and endpoint-specific denominators are available in the row audit.

| Outcome | Free anthers | Joined anthers |
|---|---:|---:|
| Bees in archive | 28 | 32 |
| Pollen remaining in anthers | 252,900 (n=28) | 383,540 (n=29) |
| Basket pollen | 211,697 | 163,949 |
| Terminal body-only pollen | 33,945 | 20,968 |
| Stigma pollen | 3,933 | 3,220 |
| Mean body-only / (body-only + basket) fraction | 14.603% | 15.451% |
| Mean published composite / (composite + basket) fraction | 16.030% | 17.857% |

The count summaries reproduce the corresponding Table 1 means (body-only is the sum of its three body-part columns). Mean fractions average each bee's fraction; they are not fractions of pooled counts. These arithmetic differences have no inferential significance classification by themselves. Initial pollen was measured in separate controls, so subtracting one common initial mean from every trial is not an individually observed release measurement.

## Model replay fixed before fitting

The [implementation plan](superpowers/plans/2026-11-21-wilkins-reanalysis.md) fixes all seven models before their fit results are inspected. Five reproduce the author's archived formulas; two change only the composite endpoint definition. All Gaussian responses use the natural logarithm, maximum likelihood and the archived colony random intercept. Both allocation models use two-column binomial counts and nested colony/bee random intercepts, retaining the bee-level overdispersion term. Pollen grains are not interpreted as independent biological replicates.

The script exports all coefficient estimates, their covariance-based contrasts, Type II Wald tests, model sample counts, optimizer status, Hessian status and random-effect variances. It compares **37 archived Type II chi-square values** with a prespecified numerical tolerance of `0.005 + 0.005 * abs(published_chisq)`. Compatibility within this tolerance is a numerical replay check, not proof of model assumptions or an independent biological replication.

Conditional free-minus-joined contrasts use common head-width support and its pooled type-7 25th/75th percentiles, pooled mean handling time, and pooled median terminal body pollen for the stigma model. Their intervals use the full fixed-effect covariance. These grid values probe the same conditional model; they do not define selected small/large categories or an optimized morphology. Because handling time and terminal pollen are measured after treatment, adjusted contrasts are not total causal architecture effects.

The first actual-engine run exposed numerical failures in four Gaussian fits: one invalid Hessian and three nonfinite fixed-effect covariance matrices. A deterministic retry divides head width by 3 and handling time by 100. This is a positive change of measurement units, preserving every model column's hypothesis space, response, observation, family and random-effect term. The retry is triggered only by numerical diagnostics, never by p-values or agreement with the paper. Coefficients and their full covariance are converted back to millimetres and seconds, and all original/retry attempts are exported. Independent checks against native model predictions verified that this conversion preserves estimates and standard errors.

## Recomputed model findings

The [verified GitHub Actions replay](https://github.com/zuizui0223/balance/actions/runs/44914763307), using R 4.5.2 / glmmTMB 1.1.15.2 / car 3.1.5 / TMB 1.9.25, recovered **all 37 archived Type II tests** within the prespecified tolerance (largest absolute chi-square discrepancy **0.00170**). Seven final fits had successful optimizer status, positive-definite Hessians and finite positive-definite fixed-effect covariance matrices. The source/retry history contains 11 attempts. These are numerical checks; they do not reproduce all residual diagnostics or establish distributional assumptions. Several fitted colony variances are near zero, and there are only three colonies.

The complete derived output is committed under [`results/wilkins_2022`](../results/wilkins_2022), with [runtime/workflow and file hashes](../results/wilkins_2022/REPLAY_RECEIPT.json), [all tests](../results/wilkins_2022/model_tests.csv), [coefficients](../results/wilkins_2022/model_coefficients.csv), [conditional contrasts](../results/wilkins_2022/conditional_contrasts.csv), and [all fitting attempts](../results/wilkins_2022/model_attempts.csv). A separate local R 4.5.0 / glmmTMB 1.1.11 check agreed; it emitted a TMB patch-version warning, so the reported results here use the separately verified GitHub environment and its artifact bytes.

The two endpoint-definition sensitivities yield the following architecture-by-head-width terms. Every term below has one degree of freedom and uses 59 bees.

| Response | Recomputed chi-square | Recomputed p | Analysis class |
|---|---:|---:|---|
| Log composite pollen amount: body + stigma | 4.1480 | 0.04168 | Published-model replay |
| Log body-only pollen amount | 2.9668 | 0.08499 | Endpoint-definition sensitivity |
| Composite-versus-basket allocation | 13.1118 | 0.000293 | Published-model replay |
| Body-only-versus-basket allocation | 13.2182 | 0.000277 | Endpoint-definition sensitivity |

**The allocation interaction persists after removing stigma grains from the numerator.** It therefore does not depend on that particular composite definition. For absolute pollen amount, the body-only interaction is less precisely supported at the conventional 0.05 threshold. This difference between p-values is not a formal test that the two endpoint effects differ, and it should not be called disappearance of an effect.

For the body-only allocation model, the following odds ratios compare **free with joined** anthers at two prespecified sizes. Here the odds concern body-only versus basket pollen. They are conditional model estimates, not ratios of the raw group means or pollen-deposition probabilities.

| Head width | Free / joined allocation odds ratio | 95% Wald interval |
|---|---:|---:|
| 3.334 mm (25th percentile within common support) | 0.647 | 0.417–1.002 |
| 3.620 mm (75th percentile within common support) | 1.581 | 1.018–2.456 |

Handling time is fixed at the pooled mean of 168.10185 seconds. Point estimates reverse direction across these sizes; the lower-size interval includes equal odds. The observed interaction supports size-dependent allocation, not superiority of one architecture for every bee.

### Stigma receipt is a different result

The stigma architecture-by-head-width test is **p=0.49192**. Thus the allocation-size result must not be relabeled a demonstrated architecture-by-size interaction in actual stigma receipt. Instead, the source stigma model has an architecture-by-terminal-body-load interaction (**chi-square=5.2986, p=0.02134**).

| Slope of log stigma pollen versus log terminal body pollen | Estimate | 95% Wald interval |
|---|---:|---:|
| Joined anthers | −0.844 | −1.843 to 0.155 |
| Free anthers | +0.596 | −0.114 to 1.306 |
| Free minus joined slope | +1.440 | 0.214 to 2.665 |

The slope difference is supported even though each individual slope's interval spans zero. These are conditional associations with pollen remaining after foraging/grooming, not causal effects of experimentally assigned body load. They agree with Figure 6a's direction and contradict the reversed direction in the Results prose. No seed production, donor identity or paternity was measured.

## Source discrepancies and interpretation

The published Results prose describes the architecture-by-body-load stigma response in the opposite direction to Figure 6a and the supplied coefficient table; the replay above adjudicates the fitted direction. The supplement also displays identical coefficient/SE/z entries in Tables S1 and S4 despite different omnibus tests. Recomputed coefficients show that those repeated cells track the allocation-share model rather than the anther model; neither duplicated table was used as coefficient ground truth. The [2023 correction](https://doi.org/10.1007/s00442-023-05413-x) concerns Figure 1's legend, not these model results.

This live-bee manipulation is a direct bridge to the artificial-vibration anther experiment in PR #277. The previously reported mechanical increase in release from joined anthers does not identify what a freely moving bee will collect or deposit. Observed pollen destination additionally depends on the bee and its behavior. The learning experiment in PR #278 is a separate intervention; none of these papers identifies a training-by-architecture interaction across experiments.

For BALANCE, this tests how floral structure and the interacting organism jointly affect functional outcomes within one species. It does not turn joined/free architecture into feeding-versus-pollinating anther specialization, identify evolutionary transitions, or measure maintenance cost, genetic paternity, seed fitness or net shared-versus-differentiated architecture fitness. Frozen U2/U6/V4 admissions and human coding remain unchanged.

## Reproduce

```bash
python -m scripts.audit_solanum_bee_architecture \
  --source-dir /tmp/balance-wilkins-source --download \
  --out /tmp/balance-wilkins-results/source_audit.json

Rscript scripts/replay_wilkins_2022_architecture.R \
  /tmp/balance-wilkins-source/442_2022_5246_MOESM3_ESM.csv \
  /tmp/balance-wilkins-results

python -m pytest -q tests/test_solanum_bee_architecture.py
```

The R dependencies are `glmmTMB`, `car`, `digest` and `lme4`; runtime/package versions are captured in `session_info.txt`. The dedicated GitHub Actions workflow performs the download, authentication and model replay and retains derived outputs, including diagnostics if any model fails. Full publisher article/code copies are not included in the repository.

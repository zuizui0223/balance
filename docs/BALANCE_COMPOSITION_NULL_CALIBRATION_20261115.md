# BALANCE: interaction composition prediction — independent null/influence audit

**2026-11-15. Original-data, post-open exploratory sensitivity analysis. Not a new confirmatory study.**

## Provenance, no promotion

This is an extension of the independent-source programmes already frozen in the stacked BALANCE PRs #260–261:

- Zurich: [Reji Chacko et al., EnviDat](https://doi.org/10.16904/envidat.676), 24 gardens with 4 phytometer species; exact original EnviDat archive SHA256 `b1ea0dc54d0c6e33bfacb44d7285377ec3e113807cc945fc2dfbfcc3e534bcc9`. Original survey frame: 670 actual capture windows, 5,794 individual flower visitors; 27 records without matching survey-exposure timestamps retained in source audit but not silently inserted into the primary rates.
- Apple: [Mallinger & Gratton, Dryad](https://doi.org/10.5061/dryad.t75c4), original *fruitsetbees.xlsx* MD5 `5445fb585421e6d9b1f5b5869342bbb4`, 47 orchard-years, 11 bee-missing 2011 records never imputed, 36 complete orchard-years and **21 independent orchard identities** across 2012–13.

Only one original Zurich research programme and one apple research programme enter this new audit. Campanula remains separately source-audited in PR #259; no pooled effect size is calculated. No independent U6 coder fields, V4 preregistration, biological admissions, architecture fitness outcomes, or publication manuscripts are modified.

## Estimands and methods

The *Zurich* comparison uses the same published-source, same-outcome, same-24-garden response and visitor types as the original PR #260. The baseline OLS model includes the intercept and log1p visitors per observer-hour. The expanded model adds the source-identified guild shares with the largest guild omitted as the compositional reference. Predictions are genuine held-out one-garden OLS refits, checked algebraically against the `residual / (1-h)` identity.

For each of 20,000 draws under a fixed seed (987654), we construct two **diagnostic null references** from the total-only fitted values and residuals: (a) jointly permute garden residual indices across all four species, preserving their shared-garden block alignment; (b) jointly flip residual signs per garden across all four species. Both recompute the full change in held-out RMSE. The familywise reference compares each observed improvement to the *maximum gain among four species* for each draw. Neither reference is an exact randomization test: group composition and gardens were not assigned at random; residual exchangeability/symmetry may fail and environmental confounding remains.

Separately, 20,000 paired garden bootstrap resamples operate on **already held-out squared errors**, to show whether observed cross-garden predictive improvement is dominated by a few gardens. Those percentiles are *not* CIs from refitting the model on independently bootstrapped original gardens and do not license a population-level significance statement. Both a model-null reference and a distributional stability diagnostic are reported precisely because they address different questions.

For *apple*, each orchard, including its repeated year when present, is excluded jointly during model fitting. The baseline contains year indicator, frost fraction and log1p total measured bee abundance. The extension adds wild-bee share and log1p observed bee richness. We resample 21 orchard-level **held-out loss pairs**, never all 36 orchard-years as independent points. Results also retain year-only (no frost), 2012 frost-only and 2013-only contrasts as nonexchangeable sensitivities. Bee abundance is not equivalent to actual per-flower visitation.

## Empirical Zurich result: four species are not four independent studies

| Species | Added-guild RMSE gain | Approx. residual-permutation four-species max reference | Approx. sign-flip four-species max reference | Paired held-out-garden bootstrap 95% range | Gardens improved |
| --- | ---: | ---: | ---: | ---: | ---: |
| *Daucus carota* | **+19.395%** | **0.00745** | **0.01470** | **−23.24% to +36.44%** | 11/24 |
| *Raphanus sativus* | −0.103% | 0.51172 | 0.64602 | −14.33% to +10.05% | 12/24 |
| *Onobrychis viciifolia* | −5.074% | 0.96415 | 0.88361 | −16.10% to +3.26% | 10/24 |
| *Symphytum officinale* | +6.415% | 0.14069 | 0.26169 | −14.01% to +18.46% | 11/24 |

All four taxa occur in the **same 24 gardens** and share sampling environments; the familywise calibration uses the same residual-index/sign draw across taxa. Under the two declared residual-null assumptions, carrot has an unusually large improvement, but neither null makes visitor-guild causation or a selected floral structure identifiable.

**Influence sensitivity:** the single garden `19` supplies approximately **85.05% of carrot's net reduction in held-out squared error** (other gardens include offsetting negative contributions). Excluding that garden and refitting the remaining 23-garden analysis reduces carrot gain to **+4.08%**; post hoc, its one-species residual-permutation right-tail reference becomes approximately **0.067**, and its sign-flip reference **0.058**. This exclusion is *post-outcome diagnostic*, not a new admission, unregistered definitive test or source error. The separately already-registered 24 leave-one-garden refit comparisons all retained a positive carot response (range +4.08% to +24.49%). There is no contradiction between direction stability and an extreme-dependent magnitude.

## Empirical apple result: year/frost adjustments and one-orchard leverage

| Orchard-heldout model | Added wild share + richness RMSE gain | Paired orchard bootstrap 95% range |
| --- | ---: | ---: |
| 2012–13 year + frost | +6.763% | **−18.32% to +18.67%** |
| 2012–13 year only | +9.091% | −19.38% to +24.75% |
| 2012 frost-adjusted | +19.188% | −23.07% to +39.13% |
| 2013 only | −7.336% | −17.82% to +1.12% |

Only **12/21 orchard units** improve under the primary model. Orchard `20` accounts for approximately **75.19% of the net reduction in orchard-heldout squared error**. Leave-one-orchard-out loss contribution is not an estimate of orchard-level causal influence, and its single-site accounting includes offsetting losses from other orchards. The usual test of a positive predictive gain is not robust to genuine orchard-to-orchard variability: paired held-out-loss resampling crosses zero by a wide margin. The model extension includes both wild share and richness, so the improvement cannot be attributed to composition alone; in the original PR #261 wild share by itself gave only +0.62% in the pooled year/frost model.

## What the data actually support

1. A *localized* garden-level compositional prediction signal is present in carrot under the declared linear reference models; it is much smaller after removing one influential garden. The other three phytometers do not reproduce the signal under four-species correction.
2. An exploratory composite wild-share-plus-richness gain is present in apple under several context adjustments but is uncertain across independent orchard identities, includes an additional *richness* predictor, and reverses in the 2013-only model.
3. These data do **not** establish a general biological rule that composition always outpredicts total exposure, or that pollen thieves selected evolutionary floral module division. They are not same-scale meta-analysis effect sizes.
4. **Priority next test:** independently selected source studies with a *common reproductive response* and direct measurements of visitor role (pollen receipt/export, stigma pollen loss, flowering exposure timing), plus a negative/control stratum chosen before outcomes, and independently verified taxonomic identities.
5. A strict BALANCE receipt still needs same-context `L>0` and a matched shared-versus-viable-differentiated architecture comparison `W_D* - W_S* <0` with joint fitness uncertainty. None of the two datasets supplies this.

## Reproduction

```bash
python -m pip install 'numpy==2.3.5' 'pytest>=8,<10'
BALANCE_ZURICH_ORIGINAL_ARCHIVE=/path/to/original.zip \
BALANCE_APPLE_ORIGINAL=/path/to/fruitsetbees.xlsx \
python -m pytest -q tests/test_zurich_composition_null.py tests/test_apple_cv_uncertainty.py
python scripts/audit_zurich_composition_null.py --source /path/to/original.zip --out /tmp/zurich_null_v1.json --draws 20000 --seed 987654
python scripts/audit_apple_cv_uncertainty.py --source /path/to/fruitsetbees.xlsx --out /tmp/apple_uncertainty_v1.json --draws 20000 --seed 20261115
```

All original workbook/ZIP bytes are acquired in the GitHub Actions source workflow, verified with SHA256/MD5, and retained in the non-manuscript source artifact. Source-backed JSON outputs are frozen in `data/` for exact re-auditing. Do not use exploratory source notes or model outputs to fill the original independent architecture coder slots.

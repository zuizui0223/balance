# BALANCE: independent published *Solanum* buzz-to-pollen source mechanism (2026-11-20)

## Executive boundary

**This is a source-only readout of the original authors' experimental model fits, not a new raw-data regression, original ecological effect estimate, genotype-based paternal fitness measurement or V4 confirmatory architecture result.** It supplies independent *research-programme* evidence for the physical process of progressive pollen dispensing under repeated pollinator behaviour. It is **NOT an independent species or evolutionary origin**: *Solanum rostratum* is already the focal species in BALANCE's registered U3 *Solanum* matched block.

Original article: Vallejo-Marín, M. & Lundgren, A. [doi:10.1111/1365-2435.70189](https://doi.org/10.1111/1365-2435.70189), *Functional Ecology*, online 6 October 2025; 2026 volume 40(2):476–485. The separately published Dryad data archive is [doi:10.5061/dryad.kkwh70sh4](https://doi.org/10.5061/dryad.kkwh70sh4), released September 22, 2025.

## What the original experiment measured

The paper includes **80 flower-level trials**, **2,101 individual buzzes**, **13 bumblebee individuals**, all from **one colony**. Because each bee contributed repeated flowers and each flower contained many buzzes, there are **not 2,101 independent flower trials or evolutionary replicated outcomes**. The authors' mixed model used `(1|BeeID)`; colony-to-colony variability is unmeasured.

The experiment directly relates time spent sonication-buzzing by *Bombus terrestris* to pollen remaining in *Solanum rostratum* anthers. Published original fits of an exponential remaining-pollen model are:

```
P_remaining(t) = A0 * exp(-r * buzzing_seconds).
```

| Published fitted model | A0 available pollen | r per buzzing second | Source-reported half-life |
|---|---:|---:|---:|
| Nonlinear, Table 1 Model 1 | 403,314 grains | 0.027 | 25.2 s |
| Log-linear, bee random intercept | **352,284 grains (Table 1)** | 0.036 | 19.2 s |

**Original article inconsistency:** The Results prose gives **352,384** for the bee-mixed fit's A0, whereas Table 1 says **352,284**. The 100-grain discrepancy is retained explicitly and not silently repaired or resolved by missing original raw files. When rounded r=0.027 is inserted in ln(2)/r, the implied half-life is 25.67 seconds rather than the paper-reported 25.2 seconds; this is consistent with published coefficient rounding but is not independently adjudicated. For r=0.036, the implied half-life is 19.25 seconds.

The authors also modeled the fraction of total pollen that was initially **available** for removal. With two *different fixed denominators* (mean control pollen or maximum pollen seen in visited flowers), Table 1 gives **a=0.955** versus **a=0.537**. These do not constitute the lower and upper bounds of a sampling confidence interval and should not be used to claim an experimentally identified species-wide range.

## Quantitative predictions implied by published models (not re-estimated coefficients)

The exact deterministic calculation uses `released(t)/A0 = 1-exp(-r*t)`; fractions refer to **initially available source pollen**, not all produced pollen or successfully fertilizing pollen.

| Fixed cumulative buzzing time | Published nonlinear r=0.027 | Published bee-mixed r=0.036 |
|---:|---:|---:|
| 0.748 s (paper mean single-buzz duration) | 2.00% | 2.66% |
| 5 s | 12.63% | 16.47% |
| 10 s | 23.66% | 30.23% |
| 20 s | 41.73% | 51.32% |
| 30 s | 55.51% | 66.04% |

The 0.748-second calculations describe a **hypothetical buzz of exactly mean length**; nonlinear functions of a mean do not equal means of heterogeneous buzz-level responses. These rows are re-expressions of the authors' fitted functions, not new original measurements, replicates or independent biological tests.

Actual pollen removal may depend on amplitude, coupling, bee behaviour and current accessibility; the authors noted acoustic signals do **not directly measure vibration amplitude transmitted to the anther**. The single-colony design cannot establish cross-colony invariance of the release law.

### Critical portability check: a constant removal fraction per *visit* is inadequate

The observed **total buzzing duration per flower trial** ranged from **0.542 to 69.277 seconds**. Inserting those two original observed times into the *authors' published conditional source-release functions* yields:

| Fitted function | Conditional release at 0.542 seconds | Conditional release at 69.277 seconds |
|---|---:|---:|
| Nonlinear `r=0.027` | 1.45% of initially available donor pollen | 84.60% |
| Bee-intercept `r=0.036` | 1.93% | 91.74% |

These are **conditional fitted-model predictions at two observed trial times**, *not actual minimum and maximum removal outcomes*, not observed per-visit means and not evidence that the original model predicts every bee equally accurately. Nevertheless, the original study's observed duration support covers a large variation in cumulative sonication, so the `alpha=0.3` fixed-proportional visit model used in BALANCE PR #274 as a **toy scenario** is not a portable description of these trials.

The more source-consistent mechanical operation is `alpha(B)=1-exp(-r*B)` for cumulative buzzing time `B`, conditional on the original published r and available pollen `A0`. This does **not** identify the quality-weighted late contribution `q` or plant genetic paternity. Buzz events and bee visitation numbers have different biological and statistical denominators.

## Relation to Clarkia and BALANCE mechanisms

- [Kay et al. (2020)](https://doi.org/10.1098/rspb.2020.2593) on *Clarkia* (BALANCE PR #275) provides **anther developmental schedule / morphological manipulation** and bee pollen transport observations, but neither an independent thief-before/after randomized visit order nor genotype-verified paternal fitness. Raw Dryad CSV acquisition is currently blocked by public API 401 and file-stream 403; source-manifest's listed greenhouse CSV is missing.
- [Vallejo-Marín & Lundgren](https://doi.org/10.1111/1365-2435.70189) on *S. rostratum* provides **pollinator-driven mechanical release** of donor pollen as a function of buzzing duration. It directly connects an animal behaviour with a source resource-distribution mechanism, but does not measure pollen transported to a recipient stigma, viable offspring paternity or new structural-module cost.
- BALANCE PR #274 posits a **three-way order × programmed release × theft** mechanism and relative late-cohort reproductive efficacy `q`. The *Solanum* data estimate a **physical source rate `r`**, not `q` or the thief loss parameter `b`. Inserting published `r` into another model is a prospective source-informed design assumption, **not a measured cross-paper fit or validation of `q>1-b`**.
- Earlier BALANCE U3 sources already use **the same species** for heteranthery routing. This new paper can contribute a different proximal measurement to a *mechanism inventory*, but it **cannot add another independent taxon/transition to U3 or V4**. It does not replace the independently frozen A/B outcome coding.

Scientific synthesis worth pursuing: the **temporal control of pollen availability has two mechanistically separable clocks** — plant-scheduled dehiscence and bee-induced vibration exposure — with no proof that they have equivalent effects on realized male reproductive fitness. A controlled experiment must vary both clocks and independently track donor pollen availability, recipient stigma deposition and genotype-verified male paternity.

## Reproduction, input and output constraints

```bash
python scripts/audit_solanum_buzz_source.py
python -m pytest -q tests/test_solanum_buzz_source.py
```

This reads only the versioned **published-source JSON receipt** and recomputes the analytical exponential curve for prespecified cumulative buzz durations. Regression tests protect all 80/13/2101 dependence counts, both source-reported rates, pollen mass accounting, table/prose discrepancy and zero claims of added evolved taxon, genetic paternity or raw-source reanalysis.

**Raw source:** the relevant Dryad archive lists `FE_bee_release_mdat_20250701.csv` with `SampleID`, `buzz.number`, `buzz.duration`, `BeeID` and `est.pollen`. This audit has *not retrieved the actual CSV*, inspected its identities or rerun the original nonlinear mixed model. Any future original-row reanalysis must verify `est.pollen` stage and `SampleID` versus `BeeID` dependency, avoid bee-level train/test leakage, and document whether `r` and `a` are jointly identifiable after sample-size and colony adjustments.

**Ceiling:** source-backed mechanistic link between visitor behaviour and anther pollen loss only; no direct BALANCE/C1 architectural worldline or demonstrated selection for additional floral modules.

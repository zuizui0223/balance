# Dalechampia tracer source: from a per-block screen to design-based inference

**Status: PROSPECTIVE randomization inference method, NOT a real 13CO2 experiment. No isotope field observations or reproductive fitness results are available.**

## A real experimental limitation that the source screen alone cannot resolve

The previous [independent-mother isotope source screen](DALECHAMPIA_BRACT_13C_SOURCE_DISCRIMINATION_V1.md) required a three-arm matched greenhouse block:
- independent maternal plant receiving SHAM_UNLABELLED;
- independent maternal plant receiving BRACT_13CO2_PULSE;
- independent maternal plant receiving FRUIT_LEAK_MIMIC.

Bract-targeted 13CO2 must be physically isolated from fruit gas, and a fruit-exposure mimic tests whether leaked gas could instead explain seed enrichment. A plant-label shared between arms is invalid because carbon could migrate to other blossoms on the same mother. In addition, an exposure-matched leak mimic is NOT automatically matched for physiological CO2 assimilation: uptake/dose-response calibration and isotope mass balance are still required.

**A per-block numeric screen PASS is not inferential evidence.** If each small block must have a favorable seed isotope result, selecting only blocks that PASS is a form of post-outcome selection and makes treatment p-values uninterpretable. The next layer must therefore analyze *all* registered randomized blocks, whether or not their isotope values look favorable.

## Primary randomized treatment-regime contrast

For one independently randomized maternal plant per arm and block, define seed atom-% excess (APE) within that particular plant as:

  APE_i = seed atom-% 13C after chase − its own measured, pretreatment background atom-% 13C

For each complete three-arm block j, the registered *primary statistical contrast* is:

  d_j = APE_{bract pulse, j} − APE_{fruit leak mimic, j}

The observed average d_j is the estimated **between-label-regime seed APE difference**, not a source-specific carbon mixing proportion or mature-seed fitness response. The sham provides secondary contrasts to the unlabelled background but is not used to cherry-pick blocks.

Under the *sharp null* that the two regimes have identical individual plant outcomes, **valid exchangeable randomized assignment within each block**, no cross-mother tracer contamination/interference, and a fixed sham identity, the two labeled-arm assignments can be swapped without changing the null distribution. There are exactly **2^n** sign assignments for n independently randomized blocks. We use a two-sided sign-flip permutation test on the sum of the matched d_j, with *all* source blocks and no outcome-dependent exclusions. This is a design-based null test, not a large-sample seed-level t-test.

Independent methodological reference: [Permutation tests for experimental data, Experimental Economics (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10066020/). For localized photosynthetic organ tracer leakage as a real physical risk, see [Kölling et al. 2013, Plant Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC4177546/), in which deliberate chamber leakage labelled untargeted leaves.

### Minimum possible two-sided p-value is a hard design constraint

The most extreme possible two-sided exact p for n nonzero aligned pair differences is 2 / 2^n. This is the combinatorial resolution of the randomized design, NOT statistical power.

| Independent three-arm blocks | Distinct maternal plants | Smallest exact two-sided p | p <= 0.05 even possible? |
| ---: | ---: | ---: | --- |
| 3 | 9 | 0.250000 | No |
| 4 | 12 | 0.125000 | No |
| 5 | 15 | 0.062500 | No |
| **6** | **18** | **0.031250** | **Yes** |
| 8 | 24 | 0.0078125 | Yes |
| 12 | 36 | 0.0004883 | Yes |

Therefore **at least six source-complete three-arm blocks, or 18 independent maternal plants, are required for any possible two-sided 5% exact randomization rejection.** Six does **not** guarantee useful biological power. If the true bract-versus-fruit-mimic seed enrichment contrast is noisy or small, substantially more blocks will be needed. The variance of isotope APE treatment contrasts is **not measured** in the 2015 seed-mass experiment; source seed-mass variances cannot be substituted for isotope assay/biological heterogeneity to calculate an honest 80% tracer power estimate.

In the artificial synthetic test where every one of six paired differences is the same positive nonzero number, exact two-sided p = 2/64 = **0.03125**. That is a software regression fixture, **not an observed Dalechampia experiment**.

## Analysis contract: no block selection after opening outcome data

For all future isotope records:
1. Verify a genuinely dated pre-outcome allocation/calibration and secure physical independent greenhouse/pot plants, randomizing the three arms within greenhouse/time/phenology blocks.
2. Record pre/post stage-matched seed APE with separately propagated laboratory and background analytical uncertainty. Verify source chamber gas and fruit leak/ambient tracer monitoring, and prospectively calibrated physical QC.
3. Keep **every complete randomized block**, including blocks with small, negative or zero enrichment, and blocks whose per-block isotope screening result is a numeric HOLD. If physical quality failures undermine source attribution, report that as a separate inference limitation; **do not remove the failed block to obtain a smaller p-value**.
4. Test the B versus F regime difference with the registered **two-sided** sum-of-pairs sign-flip statistic; present sham comparisons as descriptive secondary contrasts. A positive source-screen and a statistically distinguishable B–F treatment response remain **unverified** as source-local carbon transport until independent fruit CO2 uptake monotonicity, chamber isolation and isotope mass-balance are demonstrated.

A protocol cannot be genuinely preregistered by writing an SHA256 into a JSON field after the measurements exist. The code calls the plan SELF_DECLARED unless independently archived pre-outcome records and calibration are available.

### Exact versus Monte Carlo randomization

For up to a registered 16 complete blocks, enumerate the entire 2^n sharp-null support. With larger n, a deterministic Monte Carlo sign-flip calculation is used with a pre-frozen RNG seed, a plus-one randomization correction and a reported Monte Carlo standard error. Its p is **approximate**, not labeled an exact p. It does not become a source-identification or reproductive-fitness result.

The exact test concerns **a difference between randomized treatments in seed APE**, not an atom fraction of carbon supplied by the bract. There is no effect-size confidence interval in this version, and p-values do not characterize uncertainty about how much bract-derived carbon entered the developing seed. A separate well-calibrated carbon-mixing model and isotope recovery data would be necessary for source fraction claims.

## Reproducibility and zero invented biology

The implementation is standard-library-only:

- balance_domain/dalechampia_tracer_randomization.py — finite-sample exact and seeded Monte Carlo sign-flip randomization, all-block arm contrasts, source-screen status kept separate from statistical inclusion, and combinatorial resolution.
- scripts/analyze_dalechampia_13c_block_randomization.py — hashes the original calibration, pre-outcome inference plan and measurement CSV; refuses overwrites and cannot verify historical registration by itself.
- data/DALECHAMPIA_13C_BLOCK_RANDOMIZATION_TEMPLATE_V1.json — intentionally NOT_FROZEN, unusable until actual independent prior study registration/calibration.
- data/DALECHAMPIA_13C_EXACT_RANDOMIZATION_RESOLUTION_V1.json — **pure combinatorial p-value resolution**, not biological evidence or modeled effect size.
- tests/test_dalechampia_tracer_randomization.py — explicitly synthetic 3, 5, 6, 8 and 17-block cases, exact p-value floor, chance simulations, no exclusion of failed per-block assays, reuse of maternal plants rejected, invalid pre-outcome plan blocked and noncausal claim ceilings.

The current project contains **zero real Dalechampia bract-isotope treatment observations**. The original Pélabon et al. 2015 data are useful for photosynthetic physiology and seed-mass experimental-unit covariance, but cannot estimate the isotope-specific B versus F outcome, independent-isotope plant variation or a carbon fraction.

## What would be publishable?

**C1 — transport:** an independently physically validated source-localized bract 13CO2 labelling experiment with leakage/fruit direct uptake controls and statistically replicated positive isotope transport evidence. Treatment-regime randomization p is only one component.

**C2 — functional benefit:** separately manipulate bract-only photosynthesis while preserving fruit illumination, closure and microclimate; follow **mature viable seed output**. An isotope tracer effect by itself does not establish benefit.

**C3 — structural BALANCE:** independently compare net reproductive fitness of **genuinely different accessible floral architectures**, with separately identified functional conflict L, within the *same ecological context*. Neither a carbon label nor its p-value identifies L, architecture cost K, or net W_S/W_D.

This methodological result closes a purely statistical design loophole in the previous tracer source-gate; it is **not** evidence of evolutionary persistence, functional cost trade-off, causal pathway activation or a new biological system.

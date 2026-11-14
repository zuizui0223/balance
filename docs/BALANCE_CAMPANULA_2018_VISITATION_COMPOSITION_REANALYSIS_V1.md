# Campanula: visitor composition beyond total visitation

Date: 2026-11-14. Status: completed local numerical analysis of actual public original data; post-publication exploratory reanalysis within ONE existing U6 plant taxon, not a new 23-species macro sample, causal test, structural BALANCE receipt or V4 outcome.

## Source and provenance

Koski et al. 2018, DOI https://doi.org/10.1098/rspb.2018.0635. Original dataset DOI https://doi.org/10.5061/dryad.5nj81nf, archived by Dryad/Zenodo at https://zenodo.org/records/4969330, CC0.

The actual workbook was retrieved in source workflow https://github.com/zuizui0223/balance/actions/runs/43594488308, artifact 14112899485. Published MD5 2d26307743e8a22384781854b8f2f33b matched the downloaded bytes. Workbook SHA256 b81b77248b75330049e1ddd8ae026db127f838e979620a0415a5addb9a7e8f27. Artifact ZIP SHA256 9b555ce2b7636897004d55c03348733d7f67bf4c559f89dfe830a6110e3079d2 was independently verified after connector download into the analysis runtime.

The first worksheet A1:AH24 was read with artifact_tool. Seven original columns are exported unchanged in value to data/external/campanula_2018/population23.csv. The canonical LF CSV SHA256 is b66ec8c1471ddfe08bcfca990cb907eadcf0898f7bef45f9fdc28257a4135cde. All 23 unique population rows are retained; no missing/low-visitation population is substituted. Original workbook and source receipt are preserved in the source artifact.

## Question and estimands

Does community composition add information on pollen limitation beyond total visits? Models use sqrt(archived PL), matching the paper's response transformation. The original regression uses log(rate+0.1) for each of three visitor groups. New models compare log(total visits+0.1) alone with the same total plus Megachile and small-bee fractions; bumblebee fraction is the reference. This is not a randomized replacement of pollinators. The paper's result was known before analysis; no independent preregistration claim.

## Actual population results

| Model | n | R2 | AICc | Leave-one-population-out RMSE |
|---|---:|---:|---:|---:|
| Intercept only | 23 | 0 | -1.558 | 0.22128 |
| Total visits only | 23 | 0.10351 | -1.408 | 0.21340 |
| Total + visitor composition | 23 | 0.47933 | -7.639 | 0.18309 |
| Three group-specific log rates | 23 | 0.62965 | -15.474 | 0.15560 |

AICc includes residual variance as an estimated parameter. The new composition model improves AICc by 6.232 and reduces internal LOO RMSE by 14.206% versus total visits alone. All transformations are fixed, not tuned per favorable outcome. LOO errors were independently recomputed with explicit numpy least-squares fits and agreed with the PRESS formula to numerical precision. This is internal interpolation-oriented validation, not a held-out spatial or taxonomic prediction test.

The original standardized slopes reproduce the published rounded directions/magnitudes: bumblebee -0.53346; Megachile -0.39168; small bee +0.47147; R2=0.62965. This is numerical reanalysis of the same data, not an independent biological replication. The recalculated Megachile ordinary P is approximately .040, whereas the figure prints .03; no claim of exact reproduction of every printed statistic is made.

In the composition model the small-bee fraction slope is +0.75866 per unit fraction on the sqrt(PL) scale, HC3 95% interval [0.26504,1.25229]. At fixed total visits and Megachile fraction, this represents substitution relative to bumblebee visits, NOT a general effect of adding small bees. A 0.10 substitution corresponds to +0.07587 sqrt(PL), not a percentage loss of seed fitness. The slope remains positive in all 23 leave-one-population-out refits. The ordinary nested F comparison is F(2,19)=6.8573, P=.005729, exploratory and not multiplicity-adjusted.

## Sensitivities retained, not filtered

Adding linear latitude and longitude gives a small-fraction slope +0.73192, HC3 95% [0.12981,1.33404]. Using untransformed archived PL gives +0.57144, HC3 [0.18031,0.96258]. With both untransformed PL and geography, the slope is +0.46531; the ordinary 95% interval [-0.09661,1.02723] includes zero, while HC3 [0.11592,0.81469] does not. Therefore direction is stable across specified fits, but inference is sensitive to scale/covariance assumptions. Geography-adjusted composition LOO RMSE is 0.21124, versus 0.22240 for geography-adjusted total only; adding geography to composition does not improve its internal prediction over the simpler composition fit. Linear geography does not remove all spatial dependence.

The paper says three negative PL values were bounded to zero. The original archived sheet contains two zeros (PA_27 and TN_19). We preserve the archive exactly rather than fabricate a third zero or attempt to recover unavailable negative values. Archived PL is used on its native documented scale; no seed-count back-transformation is licensed.

## Stage-mechanism insight and a nonindependence check

The archived population-level depletion columns are deterministic rescalings of each visitor group's rate, because per-visit efficiencies and sex-phase proportions are fixed across populations:

- Bumble depletion = rate x 2453.731798;
- Megachile depletion = rate x 6624.45192326;
- Small-bee depletion = rate x 4160.27457095.

The maximum absolute residual in all 23 rows was less than 6e-11. These columns cannot be claimed as an independent population-level confirmation of pollen removal. They are biologically motivated derived indices, not measured conflict load L or net architecture margin Phi.

Separate single-visit raw seed records contain 31/54/33 flowers for bumblebees/Megachile/small bees, with arithmetic mean seed counts 11.516/7.241/3.030 and zero-seed counts 10/25/21. These are unadjusted descriptions, not the paper's site-adjusted estimates, not paired pollen fates, and not necessarily independent maternal plants. Pollen-deposition and pollen-removal samples are separate; no per-flower transfer efficiency is reconstructed by joining them.

The ecological implication supported here is that visitor identity/composition matters beyond aggregate interaction frequency. The proposed BALANCE bridge remains a hypothesis: community-dependent demand and pollen fate may affect the opportunity for temporal/spatial routing. These data do not compare shared and differentiated viable architectures or identify the cost of floral modularization.

## Reproduction

Install numpy, scipy, statsmodels, pytest. Run:

    python -m pytest -q tests/test_campanula_2018_visitation.py
    python scripts/analyze_campanula_2018_visitation.py --out-dir /tmp/new-campanula-results

The command refuses an existing output directory and any modified CSV checksum. Both outcome scales and all specified geography sensitivities are emitted. Local focused tests: 10 passed. Full repository CI status must be checked on the final remote commit separately. All 21 original U6 taxa, 42 independent coder slots, original outcomes and active manuscripts remain unmodified.

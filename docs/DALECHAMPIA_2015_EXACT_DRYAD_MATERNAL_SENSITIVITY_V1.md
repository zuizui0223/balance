# Dalechampia 2015 — original Dryad, maternal pairing and source gas physiology

**Status:** Exact original raw bytes recovered through a source-hash-gated GitHub Actions workflow; seed and gas data are independent experimental lanes. This is an exploratory sensitivity analysis, **not** reproduction of the published mixed-effects specification or a structural BALANCE result.

## Original source and integrity

- Article: [Pélabon et al. (2015), Functional Ecology](https://doi.org/10.1111/1365-2435.12427).
- Data DOI: [10.5061/dryad.nb675](https://doi.org/10.5061/dryad.nb675), archived version 11209.
- Seed file `Pelabon et al FE file 1.txt`: **84,562 bytes**, MD5 `0d64b8a35835bfd23e0feab9276026bb`.
- Gas file `Pelabon et al FE file 2.txt`: **4,821 bytes**, MD5 `4b06aa5894f0c3ff361ee225a1f81ee5`.

The files were retrieved from the official Dryad API by the workflow `.github/workflows/dalechampia-2015-original-dryad-recovery.yml` and authenticated against these immutable identities. The seed file uses **Latin-1 and decimal commas**, whereas the gas file uses decimal points. Source parser drift is rejected rather than silently imputed or repaired.

## Biological units actually present

| Original file | Source rows | Biologically independent support |
|---|---:|---|
| Seed file | 1,221 observations, **1 missing seed mass** | **37 mothers** with at least one recorded seed, 142 blossoms |
| Gas file | 60 rows (including original paired bract-removal gas measurements and leaves) | **6 gas-assay plants** |

The 2015 greenhouse experiment randomized blossoms within **39 plants**; two plants produced no seeds. The original source states that 33 plants completed all four treatments and bract-removal treatment was missing in four plants. Data-derived missing mass = 1 in the original cut arm; thus 1,220 observed weights reproduce the published seed totals by treatment. **Do not treat 1,220 seeds as independent plants**.

Source-reported treatment seed numbers among observed weights: bag 317, cut 295, cut-control 317, intact control 291. Exactly **117 mass values are below 20 mg** (bag 33, cut 25, cut-control 39, intact 20), numerically matching the paper's aborted-seed counts. This **does not independently verify the author's morphological abortion classification**: the paper also examined the seed coat, embryo and endosperm. Report all-seed and 20-mg-cutoff analyses separately.

## Independent original-source gas calculation

The original gas source stores the paired intact-minus-bract-removed `GPPnett` in native units and the measured intact bract area `Area_Leaf.1`. Dividing `GPPnett` by the recorded bract area recovers the reported area-based rates.

| Stage | Recomputed mean gross photosynthesis (μmol m⁻² s⁻¹) |
|---|---:|
| White bracts | 0.424414 |
| Green bracts | 1.469282 |

There are **12 bract measurements per stage, from 6 individual plants**. Pairing green-minus-white plant means gives **+1.044868 μmol m⁻² s⁻¹**; a deterministic 10,000-resample plant-level percentile bootstrap gives approximately **[+0.766, +1.328]**. The exact source's published rounded means were 0.42 and 1.47, so this is an *independent source arithmetic replay with cluster-aware descriptive uncertainty*. Neither the original gas mixed-effects model nor its model-selection AIC has been reproduced here.

**Crucial:** these 6 gas-assay plants are **not** the 37 mothers contributing measured seed masses. The magnitude of the green-white physiological difference cannot be mapped directly to an individual seed-mass effect or carbon-allocation pathway. `13C` labeling would be required to trace carbon into seeds.

## Maternal-pair seed-mass sensitivity (unadjusted exploratory)

For each mother × treatment, average mass within each independently treated blossom, then average the blossom means within the maternal plant. Compare each treatment to intact control **only among mothers with both arms measured**. Resample paired mothers with replacement (10,000 deterministic replicates) to characterize uncertainty. This is not the original mixed model: it does not adjust for peduncle diameter and does not fit the source's random-effects residual structure.

| Treatment minus intact (mg) | All measured seed masses: paired mothers, estimate (bootstrap 95%) | Numeric ≥20 mg proxy: paired mothers, estimate (bootstrap 95%) |
|---|---|---|
| Entire-blossom foil cover | 34 mothers; −1.976 (−4.201, +0.331) | 30 mothers; −1.754 (−3.545, +0.028) |
| Bracts removed | 34 mothers; −1.256 (−3.626, +0.866) | 31 mothers; −0.013 (−1.787, +1.682) |
| Bract-edge cutting control | 34 mothers; −0.176 (−2.951, +2.620) | 31 mothers; +0.130 (−2.207, +2.443) |

The narrower, original **published** 2015 treatment coefficients were based on a mixed-effects model with maternal random effects and a peduncle covariate. These raw maternal-pair summaries answer a **different estimand**: they are not failures to reproduce the original model, not tests of publication error, and not new preregistered confirmatory inferences. The source controls treatment/randomization at the blossom level, but our post-hoc restriction to observed mother pairs and numeric threshold can induce outcome-dependent selection. All bootstrap intervals are conditional on included pairs and ignore uncertainty about missing seed masses and abortion morphology.

## Causal limitation and next hypothesis

The original `bag` treatment covered the **entire blossom** with perforated aluminium foil, not merely the photosynthetic surface of the bracts. `cut` removed the bracts and may alter enclosure, predation protection and temperature. There is no foil-handling or fruit-light control matched to the specific bract light intervention.

Supported ecological findings:

1. Green bracts have higher gross photosynthetic performance than white bracts on the sampled six plants (same-plant physiological evidence).
2. Randomized postpollination manipulations of the **blossom/retained-bract package** affected early seed development in the original published mixed-model analysis. Our independent paired-plant descriptive analysis provides a wider uncertainty perspective.

Not demonstrated: isolation of a bract-only carbon pathway to seeds, mature whole-plant reproductive fitness, a shared versus net-differentiated **structural architecture** comparison, `L`, `K`, `Phi`, `rho`, or structural BALANCE occupancy. The 2012 resin and 2013 natural selection studies are different contexts and **must not** be numerically pooled with 2015.

**New preregistrable test:** after source-valid handling pilots, manipulate local bract light independently of fruit irradiance with optical and microclimatic controls; measure labelled carbon in developing seeds, reproductive outcomes to maturity, and protection/temperature. If bract-specific suppression cannot be accomplished without covering the fruits, the carbon-specific causal claim remains HOLD.

## Reproduction

```bash
python -m pytest -q tests/test_retrieve_dalechampia_2015_dryad_bytes.py \
  tests/test_dalechampia_method_scope.py \
  tests/test_dalechampia_raw_sensitivity.py

# Runs as an isolated GitHub Actions job with network access:
python scripts/retrieve_dalechampia_2015_dryad_bytes.py \
  --source-dir /path/to/authenticated_original_files \
  --out /path/to/recovery_receipt.json

# Only if both original source identities and source-parser checks passed:
python -m scripts.analyze_dalechampia_2015_raw_maternal_sensitivity \
  --contract data/DALECHAMPIA_POSTANTHESIS_METHOD_AND_DRYAD_V2.json \
  --seed-file '/path/to/Pelabon et al FE file 1.txt' \
  --gas-file '/path/to/Pelabon et al FE file 2.txt' \
  --out /path/to/source_specific_sensitivity.json
```

The source files are CC0 Dryad material and are retained as short-lived GitHub Actions artifacts, not silently copied into the repository's committed biological dataset registry. Source-level receipts include SHA256s and explicit biological claim ceilings.

# Dalechampia 2015: whole-blossom shading, mechanism identification, and exact Dryad recovery (v2)

**Status:** PRIMARY-METHOD-CORRECTED / ORIGINAL PUBLIC DRYAD METADATA VERIFIED / SOURCE FILE BYTES NOT YET IMPORTED / NO NEW FIT / NO STRUCTURAL BALANCE.

This is a scientific **qualification and forward-reanalysis plan**, not a reversal of the paper's observed reproductive effect. It supplements, does not overwrite, the original source-reported numerical record at `data/DALECHAMPIA_TEMPORAL_BRACT_SOURCE_V1.json`.

## 1. Correction that matters for causal interpretation

Pélabon et al. (2015), *Functional Ecology*, DOI [10.1111/1365-2435.12427](https://doi.org/10.1111/1365-2435.12427), state in **Experimental Design** that the treatment called "shaded bracts" enclosed **the entire hand-pollinated blossom between two aluminium-foil sheets with ventilation holes**. Both bracts and the inner blossom/fruit therefore experienced a modified light environment; foil may also modify temperature, humidity or CO2 boundary conditions.

That treatment is **not** a bract-only selective photosynthesis intervention. The historical mean-seed-mass reduction of 2.03 ± 0.32 mg (source reported SE; 4-week endpoint) is a **whole-blossom foil-shading package effect**. It does not identify the causal magnitude attributable specifically to carbon fixed by the bracts. The original Discussion explicitly notes fruit photosynthesis, a bract respiratory demand under shading, and foil microclimate as explanations that are not fully separable.

The other randomized arms were:

| Original code | What actually happened | What does it identify? |
|---|---|---|
| `cont` | No post-pollination bract manipulation | Common reference |
| `cut` | **Both upper and lower bracts removed** near the attachment | Whole bract removal package: no bract photosynthesis **and** loss of physical protection, altered exposure, possible wound/handling |
| `cutcont` | **Bract edges trimmed ~1 mm** | Cutting/handling control only; does not equalize physical protection loss after full removal |
| `bag` | **Entire blossom foil shaded** | Whole-blossom light plus foil/microclimate package; fruit and bract light not separately controlled |

All blossoms were hand-pollinated, with the male subinflorescence removed during the female phase before these treatments. Thus male reproductive fitness was not estimated. Seed mass was weighed **four weeks after pollination, before final dispersal maturity**.

Original paper source: [full Methods and Results](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/1365-2435.12427).

The direction and numerical magnitude of the reported 2015 package contrasts remain valid. They support a **post-pollination value of retaining the bract-bearing blossom / avoiding the study's specific manipulations**. Direct gas-exchange observations independently support photosynthesis by green bracts, but **do not quantify its isolated causal contribution to seed mass** in the same treatment contrast.

## 2. Raw-data recovery: a new opportunity

The article explicitly deposits raw data in [Dryad 10.5061/dryad.nb675](https://doi.org/10.5061/dryad.nb675). The verified public **metadata**, version ID **11209**, describe these exact 2 files:

| Dryad file ID | File | Size (bytes) | Official MD5 |
|---|---|---:|---|
| 46163 | `Pelabon et al FE file 1.txt` | 84,562 | `0d64b8a35835bfd23e0feab9276026bb` |
| 46164 | `Pelabon et al FE file 2.txt` | 4,821 | `4b06aa5894f0c3ff361ee225a1f81ee5` |

Source: [Dryad dataset](https://datadryad.org/dataset/doi:10.5061/dryad.nb675), [file list via Dryad API](https://datadryad.org/api/v2/versions/11209/files).

**File 1** contains the individual-seed observations, mother `FemaleID`, father `MaleID`, blossom `crossID`, `treatcode`, `seedID`, seed mass, date, peduncle diameter and harvest timing. **File 2** contains repeated blossom gas exchange, with plant ID, colour, replicate, bract removal state, respiration, assimilation, GPP and GPPnett.

This unlocks a plausible **within-original-study** reanalysis, avoiding the earlier cross-paper collage. However, **the actual text file bytes were not acquired in this implementation**; the public file-stream returned an access challenge. The MD5 and sizes were retrieved from official metadata, not recalculated on local original files. No paper mixed model was re-fitted and no biological significance was newly tested.

### Biological unit and missingness rules

- **Plant** is the maternal clustering unit, not each weighed seed.
- **Blossom** `crossID` is the randomized post-pollination treatment unit within mother.
- **Seed** `seedID` is a nested measurement unit, and repeated seeds from one blossom are dependent.
- The paper reports **1,220 seeds total**, with **117 morphologically assigned abortions**; per-arm counts are recorded in the V2 contract. An analytical threshold such as mass below 20 mg cannot stand in for the authors' morphological abortion decision.
- The deposited file may omit failed blossoms, contain only mass-analyzed seeds or have missing values. Source checksum validation and field/row conservation come *before* deciding whether the deposited rows reproduce original mixed-model denominators.
- The reported means and SEs use mixed models, including a maternal-plant random effect and peduncle diameter adjustment. A simple seed-level t-test or post-hoc seed bootstrap would be pseudoreplication.

## 3. Executable prefit audit

`balance_domain/dalechampia_method_scope.py` and
`scripts/probe_dalechampia_2015_dryad.py` provide two strict levels:

**Level M — original methods plus Dryad metadata.** Requires only the frozen V2 JSON, verifies the literal original treatment targets, seed-count and abortion-count anchors, both Dryad file identities, and that bract-carbon/structural BALANCE were never promoted. Returns `raw_file_bytes_verified=false` and `raw_reanalysis_executed=false`.

**Level D — byte-perfect original data checks (future, not executed here).** Requires both files at exactly the official sizes and MD5s. Checks documented columns, the four treatment labels, seed nesting within blossom and plant, and gas-exchange plant/replicate support. Only after successful byte verification can the **independent model implementation** and original R/nlme specifications be recovered and compared to published coefficients. Raw row support may differ from publication totals due to exclusions; do **not** impute to force agreement.

Examples:

```bash
# Metadata-only: executed by tests; no source data claimed
python scripts/probe_dalechampia_2015_dryad.py \
  --out /path/to/method-receipt.json

# After obtaining both original public files (currently unexecuted):
python scripts/probe_dalechampia_2015_dryad.py \
  --seed-file "/path/to/Pelabon et al FE file 1.txt" \
  --gas-file "/path/to/Pelabon et al FE file 2.txt" \
  --out /path/to/raw-source-verification.json
```

The output includes SHA256 digests of **actual** bytes only if imported, never a guessed hash. Even a byte-perfect raw receipt is **not** a fitted treatment effect, carbon mechanism, new biological cluster or structural S-vs-D architecture worldline.

Regression guards: `python -m pytest -q tests/test_dalechampia_method_scope.py`.

## 4. Ecologically decisive follow-up: isolate the photosynthetic channel

There are at least four competing hypotheses for the four-week maternal seed-mass package effects:

| Proposed process | Main competing mechanism | Distinguishing intervention (prospective) |
|---|---|---|
| **Bract-local photosynthetic subsidy** | Same bract fixes carbon that reaches the seeds | Suppress *only bract* CO2 assimilation after anthesis while holding bract physical closure, fruit light, bract/fruit temperature, humidity and handling equal; trace labelled `13C` if claiming carbon import |
| Fruit/seed-coat photosynthesis | Whole-blossom foil reduces light reaching fruit | Independently suppress fruit illumination, with bract light and integrity unchanged |
| Protective benefit of retained bracts | Removal changes seed protection and exposure | Compare functionally protective versus nonprotective bract regimes, with measured bract photosynthesis and local microclimate controlled |
| Foil/microclimate/handling stress | Whole-blossom foil introduces heat/humidity/light covariation | Compare matched *spectrally and thermally qualified* light-transparent/opaque shams with logged microclimate and gas exchange |

**Feasibility first:** bracts close around developing fruit. Independent bract versus fruit illumination may be **physically impossible** without damaging architecture. Before the full experiment, test external and internal photon flux, CO2 exchange, closure integrity, handling damage, and temperature/humidity cross-effects. If selective intervention fails, retain a **mixed whole-blossom package effect** and do not call a source-specific carbon mechanism.

The 2015 source collected four-week seed mass rather than eventual germination or full mature viable seeds. A true fitness-stage test must independently measure later mature-seed number, mass and viability, including developmental timing and attrition.

## 5. BALANCE interpretation and stop rule

The empirical possibility opened by 2015 is **temporal functional reuse**: a display organ can have a measured benefit during a later life-history stage. This is not direct evidence that its two early functions conflict within the same matched causal experiment, nor that a distinct structural architecture would lose in net fitness.

The separate 2013 observed bract size-selection conflict and 2012 resin cost assay **must not** be algebraically stitched to 2015 seed mass to manufacture `L, K, rho, Phi` or `Delta_W`. These remain different studies and estimands.

Stop promotion if any of the following remain absent:
- independently verified source files/row genealogy for raw reanalysis;
- true bract-specific selective photosynthesis perturbation with valid handling/sham;
- cross-stage reproductive outcomes on an equivalent fitness scale;
- matched net structural architecture S/D worldlines and independently inherited positive SCH `L`.

No new field experiment was executed, and the existing `Dalechampia_scandens_mexico` biological cluster count remains unchanged.

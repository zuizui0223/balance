# Dalechampia: prospectively identify post-anthesis carbon reuse

**Status: proposed experiment and empirical-variance-based design sizing. No new field method measurements, tracer observations, seed outcomes or structural BALANCE receipts.**

## Core ecological question

Can the *same* pollinator-advertising organ acquire a second useful function after pollination, and does that later function help maintain the organ despite conflicting selection during flowering?

Pélabon et al. 2015 (https://doi.org/10.1111/1365-2435.12427) describe D. scandens bracts changing from white/open to green/closed around fruits over roughly 10 days. Their greenhouse study used whole-blossom aluminium foil and whole-bract removal; **neither isolated bract-only photosynthesis** from fruit light, closure, physical protection, humidity or temperature. Independent gas assays supported green-bract carbon fixation, but did not trace bract-derived carbon into seeds.

Our subsequent exact original-data source audit found 1103 numeric >=20-mg seeds nested in 132 blossoms and 36 maternal plants. The source-verified nested random-effect analysis estimated mother variance 15.190, blossom variance 14.500 and residual seed variance 3.809 mg², with same-blossom seed correlation 0.886. These variance components are relevant to experimental design, **not evidence for a functional carbon effect or differentiated-architecture cost**.

## Three non-interchangeable questions

**C1 — Where does new carbon go?** A bract-local, source-isolated 13CO2 pulse chase could test whether isotopic excess first appears in green bracts and subsequently in developing seed tissue. A positive isotope signal is source-identifying **only if** fruit/interior gas exposure, chamber leakage, unlabeled baselines, isotope recovery and instrument detection are qualified. A positive bract-to-seed label alone **does not quantify seed fitness or natural selection**.

**C2 — Does that carbon pathway increase reproductive performance?** After a genuinely bract-local photosynthesis perturbation with matched fruit illumination, protection, temperature, humidity and handling, compare mature **viable** seed output against a randomized optical sham. The historical 2015 whole-blossom foil package is not a qualifying C2 intervention.

**C3 — Is maintaining an integrated structural architecture fitter than a viable different structural architecture?** This strict BALANCE question additionally needs a same-context, independently accessible structural alternative, its measured net male-plus-female fitness, and an independently established SCH conflict L. C1/C2 do **not** automatically answer C3.

## Stage 0: physically test bract-selective optics BEFORE seed outcomes

Because bracts close over fruits, a cover on the bract surface can change fruit PAR. Installing sensors inside the closed bracts can itself alter closure or fruit physiology. Optical intervention feasibility is unknown.

Use **two independently assigned blossoms within every maternal plant**:
- OPTICAL_SHAM — matched installation/materials with nominally transmitted light;
- BRACT_LOCAL_OPTICAL_ATTEMPT — the desired selective attenuation of the green bracts, while preserving fruit light and bract integrity.

Record before/after **bract PAR**, **fruit/interior PAR**, fruit temperature and relative humidity, time since treatment, intact physical closure and any visible handling damage. Sham and targeted blossoms must be measured at matched times on the same mother. Evaluate targeted after/before photon ratios **relative to the contemporaneous paired sham**; also screen sham stability, fruit-temperature/humidity drifts and all tissue injuries.

The following thresholds must be justified from **independent pre-outcome instrument calibration**, not from the fertility results: minimum bract photon reduction; maximum fruit photon change relative to sham; sham light stability; maximum thermal/humidity change; time matching; minimum independent maternal blocks. **There are no fabricated "universally acceptable" thresholds in this repository.**

The executable scope check is balance_domain/dalechampia_bract_isolation.py, used by scripts/evaluate_dalechampia_bract_isolation.py with:
- data/DALECHAMPIA_BRACT_ISOLATION_THRESHOLDS_TEMPLATE_V1.json — intentionally NOT_FROZEN, invalid until true calibration;
- data/DALECHAMPIA_BRACT_ISOLATION_METHOD_ONLY_TEMPLATE_V1.csv — an exact header excluding reproductive or isotope outcomes.

The script requires all registered maternal pairs and rejects duplicate assignments, allocation-hash mismatch, nonphysical numeric inputs and outcome-contaminated fields. A single registered plant failing fruit PAR/handling/closure invalidates a blanket method pass; failures cannot be removed post hoc. Outputs are either **METHOD_SELECTIVITY_HOLD** or **METHOD_PROFILE_PASS_NOT_CARBON_CAUSAL_OR_FITNESS**. Even PASS verifies only physical compatibility for the supplied numbers, **not** retrospective timing of calibration, genuine random allocation, carbon flow, seed performance or BALANCE.

A feasible light manipulation must also show physiological reduction of **actual bract CO2 assimilation**, not merely lower PAR; that downstream qualification is separate.

### Stage 0 stop rule

If a selectively isolated light intervention cannot be achieved without altering fruit irradiance, fruit temperature, closure or damage, **do not run a full seed experiment described as bract-specific**. A whole-blossom effect may still be an ecological package effect, but cannot be promoted to bract carbon causality.

## Stage 1: spatially isolated 13CO2 tracing (a different gate)

With the proper permissions and instrument setup, compare source-local pulses on exterior green bracts to identical unlabeled/sham chambers. Where physically possible without injury, include a fruit-directed positive control. Track isotope atom-% excess in bract, non-target fruit atmosphere, surrounding chamber atmosphere and later reproductive tissues at prospectively set chase times. Measure and bound **off-target 13CO2 leakage** before using seed enrichment to attribute the carbon's source.

*Carbon detected in a seed after source-isolated bract labeling* supports movement, not that the transferred carbon was necessary for mature viable seed development. Leaky or inaccessible source chambers imply **SOURCE_ATTRIBUTION_HOLD**, even with positive seed enrichment. A precise direct carbon-contribution claim ultimately also needs isotope recovery/mass-balance, not an atom-% ratio in isolation.

Methodology:
- Plant 13CO2 pulse-chase review (2016): https://pmc.ncbi.nlm.nih.gov/articles/PMC5041120/
- Localized photosynthetic tissue pulse labelling and chamber control, Kagawa et al. (2005): https://doi.org/10.1111/j.1365-3040.2005.01343.x
- Chamber leakage and allocation methods for fruiting coffee (2025): https://doi.org/10.3389/fpls.2025.1618182

These establish methodological precedents **not** successful bract compartmentation in Dalechampia.

## Stage 2: functional seed-performance experiment, conditional on selectivity

Randomize at the blossom level within independent maternal plants. Fix treatment stage, pollination time and pollen donor; verify bract integrity and sham-equivalent light, CO2, fruit temperature/humidity, protected status and plant resource condition. Primary endpoint should be **mature viable seed** success and optionally subsequent germination, not automatically the four-week seed weight measured in 2015.

Predefine treatment of abortions/missing blossoms. Do not convert a numeric seed-mass cutoff after treatment into an independent morphological abortion classification. Store mothers, blossoms and individual seeds hierarchically; because blossoms on one mother may share carbon, even a within-mother two-arm design requires a *no-interference* sensitivity. Analyze plant/blossom hierarchical allocation, not individual seeds as replicate plants.

## Sample size — source-variance scenarios, NOT future field power

From the existing authenticated nested covariance fit:
- maternal variation 15.190316 mg²;
- **blossom variation 14.499685 mg²**;
- residual seed variation 3.808892 mg².

For a **balanced two-arm paired-mother design** with b independently treated blossoms per arm per mother, s usable measured seeds per blossom and n independently randomized mothers, a simplified normal planning standard error (mg) is:

**SE = sqrt[2 × (14.499685 + 3.808892/s) / (n × b)].**

The common mother intercept cancels only under the assumed pairing, no interference, identical treatment variances and independent conditional blossom effects. We have **not** established these assumptions for the proposed experiment; the original late foil response is **not a measured bract-local effect**. All outcomes are hypothetical 4-week seed-mass-like units, **not mature whole-plant fitness or 13C isotope-enrichment power**.

| Assumed response difference, mg | Blossoms per arm/mother | Usable seeds per blossom | Approx. independent mothers needed for 80% normal-approx power |
| --- | ---: | ---: | ---: |
| 0.5 | 1 | 8 | **941** |
| 1.0 | 1 | 8 | **236** |
| 1.83 | 1 | 8 | **71** |
| 1.83 | 2 | 8 | **36** |
| 3.0 | 2 | 8 | **14** |

The illustrative **1.83 mg** magnitude resembles the source's *whole-blossom foil package coefficient*, **not** a predicted bract photosynthetic contribution. The species can produce at most **9 seeds per blossom**, making eight *usable* seeds optimistic. Blended effective sample sizes from 1000+ individual seeds are inappropriate when source within-blossom dependence is 0.886.

The machine-readable six-scenario input is data/DALECHAMPIA_BRACT_ISOLATION_POWER_SCENARIOS_V1.json. The source-linked planner is balance_domain/dalechampia_paired_design_power.py and scripts/plan_dalechampia_bract_pilot.py. It outputs SHA256 checksums and explicitly labels the normal sample size as hypothetical. It does **not** claim achieved power for a field study.

## Reproduction

Run a method-only pilot **only after replacing the invalid threshold template with a genuinely calibrated and dated prospective contract**:

    python scripts/evaluate_dalechampia_bract_isolation.py --thresholds frozen_calibration.json --measurements outcome_free_methods.csv --out method_receipt.json

Run source-variance-based hypothetical replication planning now:

    python scripts/plan_dalechampia_bract_pilot.py --out source_power_scenarios.json

Synthetic regression tests:

    python -m pytest -q tests/test_dalechampia_bract_isolation.py tests/test_dalechampia_paired_design_power.py

No *Dalechampia* tissue-specific optical intervention, stage-isolated 13C pulse, labeled seed, seed-fitness outcome, novel independent cluster or strict structural BALANCE data have been generated here.

**Publication direction:** a prospective paper can test whether temporal functional reuse contributes to floral organ maintenance. The strongest first advance is establishing an *actual separable bract-derived carbon route*, then its causal reproductive consequence. Only a separate net structural-architecture comparison could turn it into a direct BALANCE middle-world receipt.

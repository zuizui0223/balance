# BALANCE — Solanum mechanical gate: architecture, vibrations, pollen release (2026-11-20)

## Main newly integrated result (original published empirical evidence, NOT a new experiment)

**A flower-architecture manipulation can change mechanical transmission without consistently changing how much pollen is released.** This statement is demonstrated *within one original 2022 experiment on three Solanum species*; it is not a new meta-analytic effect estimate or a BALANCE structural-fitness result.

### Direct 2022 intervention: *Evolution* 76:931–945

Vallejo-Marín, Pereira Nunes & Russell (2022), DOI [10.1111/evo.14485](https://doi.org/10.1111/evo.14485), original [Dryad doi:10.5061/dryad.s1rn8pk9p](https://doi.org/10.5061/dryad.s1rn8pk9p).

The authors applied standardized bee-like vibrations and compared **experimentally joined versus free anthers**, including a paired, randomized treatment order on the same flowers. The original manuscript reports **240 buzz records across 3 species**, with original mixed models accounting for accession, plant and/or flower dependence rather than 240 independent flowers. The published effect estimates have **different units on two outcome stages**:

| Species, baseline arrangement | Joined−free distal-anther RMS velocity (mm/s; original EMM) | Joined−free sqrt(pollen grains/buzz; original EMM) | Original pollen conclusion |
|---|---:|---:|---|
| *S. elaeagnifolium*; loose | +110.0 ± 8.93 | +48.2 ± 9.38 | **increased**, p<0.0001 |
| *S. sisymbriifolium*; loose | +116.4 ± 6.88 | +38.3 ± 7.18 | **increased**, p<0.0001 |
| *S. pyracanthos*; naturally compact but not attached | +63.3 ± 8.58 | −12.3 ± 8.91 (joined−free table coefficient) | **not detectably different**, p=0.169 |

All three original velocity contrasts were significant at p<0.0001; species×treatment interaction for pollen release was significant at p<0.001. **Non-significance in the third species is not zero effect or equivalence.** The original prose reports an absolute +12.3 on a free-minus-joined contrast; the table encodes −12.332 on the joined-minus-free scale. These are equivalent directional conventions, not a discovered discrepancy.

The published fitted model's *joined* effect on the reference species, and species-specific interactions, allow exact re-expression:
```text
DISTAL RMS velocity, joined−free:
  S. pyracanthos       = +63.273 mm/s
  S. elaeagnifolium    = +63.273 + 46.774 = +110.047 mm/s
  S. sisymbriifolium   = +63.273 + 53.146 = +116.419 mm/s

SQRT pollen grains per buzz, joined−free:
  S. pyracanthos       = −12.332
  S. elaeagnifolium    = −12.332 + 60.545 = +48.213
  S. sisymbriifolium   = −12.332 + 50.645 = +38.313
```
These are **linear combinations of published original regression coefficients**, not independently fitted effects. The approximate original source narrative is 1,500–2,300 additional pollen grains in the *two loose-anther species*; it is not correct to square the EMM contrasts to back-calculate raw grain differences.

### Independent controlled-mechanics source 2026: *Journal of Experimental Biology*

Vallejo-Marín, Magitteri & Jafferis (2026), [doi:10.1242/jeb.253005](https://doi.org/10.1242/jeb.253005), published online August 28 2026; [Dryad doi:10.5061/dryad.wstqjq328](https://doi.org/10.5061/dryad.wstqjq328). The focal species **is again *S. pyracanthos***.

- Original authors varied three input RMS amplitude levels × 0/2/4 harmonics while keeping the fundamental frequency at **300 Hz**.
- RMS acceleration at the shaker (and separately at a distal anther) predicted pollen release. The input and distal responses were only weakly correlated; flowers alter the transferred mechanical signal.
- Harmonic content did **not** have a detectable pollen release effect *under the tested input levels and frequency*. This is **not an equivalence trial** across all frequencies or any proof that harmonic structure can never matter.
- The source dataset exposes real sample / plant / accession / vibration-realisation fields; **the CSV was not retrieved or re-fitted in this audit**, so numerical effects, sample sizes and mediation path coefficients are unreported here.
- A data-specific Zenodo mirror of the Dryad CSV was **not** identified in the currently surfaced Zenodo records: 21456450 contains signal files, 21456451 contains related source code, but not the `bmdat_dryad_20260720.csv` table. These Zenodo records are **associated software/signals, not an independent replication or a substitute for the Dryad original numerical table**.

### Earlier real-bee behavior 2025: *Functional Ecology*

Vallejo-Marín & Lundgren (2025 online, 2026 print), [doi:10.1111/1365-2435.70189](https://doi.org/10.1111/1365-2435.70189), [Dryad doi:10.5061/dryad.kkwh70sh4](https://doi.org/10.5061/dryad.kkwh70sh4). In *S. rostratum* (80 flower trials, 13 bees from one colony, 2,101 buzzes nested), original fits associated cumulative buzz duration with diminishing source pollen. Estimated release was 0.027 or 0.036 of available pollen per buzzing second under different author models. Those rates cannot be silently used as a common species-wide law: the 2025 study measured time, while the 2026 *S. pyracanthos* experiment manipulated RMS acceleration. This programme was already audited in BALANCE [PR #276](https://github.com/zuizui0223/balance/pull/276); it is **reused, not independently reanalysed**.

## The biologically important within-species triangulation

**Same *Solanum pyracanthos* species; different, independent research programmes:**

1. In 2022, experimentally *joining* its already closely adjacent anthers **improved distal vibration velocity** but did **not show a statistically detectable increase in pollen released**.
2. In 2026, experimentally increasing the **vibration acceleration stimulus** did affect pollen removed; harmonics at the tested fixed fundamental frequency did not detectably alter release.

This is **not a logical contradiction** and does not prove the mechanism is saturation, pore geometry, baseline limited pollen supply, or loss of transmission at a specific point. Differences include the manipulation, measurement units (**velocity mm/s vs acceleration m s−2**), mechanical geometry, stimulus range, treatment context, donor pollen baseline and repeat structure. In particular, an across-paper product of mechanical and pollen coefficients would be an *invalid causal mediation estimate*.

The useful question is now more precise:

> Under what *pre-existing arrangement* and *external vibration amplitude* does structural attachment of anthers translate an input mechanical gain into extra available pollen?

This already goes beyond the simplistic claim that two anthers fused together always yield better pollen release. It also differs from the current U3 question of whether heteranthery morphology equals functional routing. Neither source measures the net fitness benefit of evolving an extra structural organ.

## A confirmable future experiment (not a claim of results)

Use a jointly controlled design with two baseline architectures (*S. pyracanthos* compact, *S. elaeagnifolium* loose) × experimentally joined/free anther treatments × at least three *predeclared* input vibration RMS levels, all while holding stimulus duration, total available donor pollen calibration and harmonic content fixed. **Randomize joined/free within flower where reversible, or within plant/flower blocks with independent plant replication**. Independently measure input vibration amplitude, distal-anther transmitted amplitude, source released pollen (grain counts and fraction of available stock), temporal decay and recipient pollen deposition. Measure flower age, plant identity, stimulus replication, and pore opening rather than assuming all are controlled.

Register separate endpoints and hypotheses **before seeing new data**:

- **H1 / mechanical transmission:** joined versus free raises distal vibration under identical input.
- **H2 / pollen consequence:** the joined−free effect on source pollen release is stronger in naturally loose than compact baseline architecture, after plant-level clustering.
- **H3 / interaction with input:** the joined×input RMS interaction tests whether structural gain matters preferentially at some vibration levels; sign is not fixed as it depends on transmission and pollen-availability limits.
- **H4 / source-stage alternative:** test measured distal acceleration, pore state and available-pollen baseline as possible effect moderators. **Do not claim natural mediation without an intervention or causal identification plan that distinguishes pathway-specific effects.**

The structural evolutionary fitness comparison remains a distinct **unmeasured** downstream requirement: genotype-confirmed donor siring, recipient fitness, net construction/maintenance cost `K`, optimized accessible shared-vs-separated alternatives, and repeated environmental contexts. Positive source pollen release by itself is not a BALANCE `Phi>0` or a historical transition.

## Source independence and replication ceiling

There are **three source papers**, but they share researchers, Solanum phylogenetic context, some plant taxa, and a measurement literature. The 2022 experiment has **3 species**, the 2025 experiment *S. rostratum* and the 2026 experiment repeats *S. pyracanthos*: **four different species total**, not independent clade-level evolutionary origins. *S. rostratum* already appears in the BALANCE U3 matched-pair dependence block. None of this alters the 21 frozen U6 conflict-first groups, U2 structure, the 42 still-blinded architecture coder slots, or V4 primary denominator.

The source-data streams needed for fully independent numerical synthesis remain Dryad original files `pollen_20220314.csv` / `mdat_20220314.csv` (2022); `FE_bee_release_mdat_20250701.csv` (2025); and `bmdat_dryad_20260720.csv` (2026). Dryad downloads were found to require authentication or block uncredentialed file-stream access in prior BALANCE PR #275; no raw files are asserted as downloaded, and no imaginary rows are created.

## Reproduce

```bash
python scripts/audit_solanum_mechanical_gate.py
python -m pytest -q tests/test_solanum_mechanical_gate.py
```

The code verifies every published 2022 original Table 2/3 contrast algebraically, enforces three stage-paired species and exact published p-reports, checks author programme identity and known dependency overlaps, and prohibits a numerical 2026 effect not present in the inspected public abstract. All results are **original-source positive/negative-evidence reconciliations**, not a new fit, meta-analysis or direct BALANCE structural advantage.

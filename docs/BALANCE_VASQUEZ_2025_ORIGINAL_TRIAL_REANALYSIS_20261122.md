# Vasquez-Castro (2025): authentic original-trial reanalysis — registered scope

**Study source**: [Vasquez-Castro et al. (2025)](https://doi.org/10.26786/1920-7603(2025)836), *Journal of Pollination Ecology*. The publisher's data statement links [Zenodo 17102653](https://zenodo.org/records/17102653).

## Original data now recovered and authenticated

Official Zenodo API access and source-file checksums succeeded in GitHub Actions [#45029750235](https://github.com/zuizui0223/balance/actions/runs/45029750235):
- `data.csv`, **3965 bytes**, SHA256 `484ed52ac611dbc6dc1831320a6c54d314492e9830823edd8934690c35205b79`, MD5 `d06dc42f897004e8eb6bd113a0e39bac`.
- `README.txt`, 1174 bytes, SHA256 `7ffc4a4d3fcfe7df2ac11eec8c5b99af9bb774a759301604f3985ced51a5ec40`.
- Source CSV is **60 recipient observations**, each with 10 named columns: `trial_number,bee_hive,bee_ID,flower_sp,recipient,duration_visit,pollen_stigma,donor_released,donor_remaining,donor_total`. The README says 61 rows/11 columns: 61 counts a header plus 60 data rows; 11 columns does **not** match the CSV's actual 10, and the README describes only 10. Do not invent an eleventh field.
- Exactly **15 donor-bee trials**, with four recipients each, unique original bee IDs, *S. dulcamara* n=9 and *S. rostratum* n=6. Original hives: B1 = 5/5 trials (*dulcamara*/*rostratum*); B2 = 4/1. Each trial repeats exactly the same source-pollen stock values across four recipients.
- Critical raw-data limitation: Zenodo files **do not include ground-falling grains D, bee basket grains F, or terminal body grains G**. Those published pollen-fate contrasts cannot be independently re-estimated from this public data record; retain their original-paper reported source evidence only.

The Zenodo item is linked to the **2024 preprint DOI 10.1101/2024.09.01.610688**, whereas the eventual journal article is published in 2025. The published journal paper itself identifies this exact record. Both provenance identifiers must be retained and never substituted for one another.

## Confirmed original 15-trial source-to-stigma result

Use exactly one row per authenticated donor-bee trial, and sum recipient stigma grains `H_i` across the four nested rows. Take `B_i=donor_released`, `C_i=donor_remaining`, and `A_i=donor_total`, checking `A_i≈B_i+C_i` within original numerical precision. Report **both** `100*H_i/B_i` (conditional PTE) and `100*H_i/A_i` (full measured source throughput), as species means of **individual trial ratios**.

The [original-source GitHub Actions run #45030158810](https://github.com/zuizui0223/balance/actions/runs/45030158810) produced the following **actual**, not synthetic values, independently preserving every individual trial before aggregation:

| Trial-averaged measure | *S. rostratum* n=6 | *S. dulcamara* n=9 | Dulcamara−rostratum |
|---|---:|---:|---:|
| Released / measured donor production, % | **13.5470** | **37.7680** | **+24.2210 pp** |
| Four stigmas / released pollen (PTE), % | **0.86108** | **1.00070** | **+0.13962 pp** |
| **Four stigmas / measured donor production, %** | **0.06496** | **0.31375** | **+0.24879 pp** |

Predefined descriptive 20,000-draw species-stratified **trial-bootstrap** percentile 95% intervals for dulcamara−rostratum: **[+11.3533,+37.1422] pp** for released percent; **[−0.7782,+0.9185] pp** for PTE; **[+0.1236,+0.4130] pp** for total-source throughput. These intervals **assume trial exchangeability within species**, do not account for just 2 source hives or source-plant sampling, and do **not** license a causal morphological or fitness inference.

The actual donor-sourced throughput ratio `0.31375/0.06496≈4.83` differs from an earlier **product of rounded species means** `(37.77×1.00)/(13.55×0.86)≈3.24`. The original difference is expected because `mean(released_fraction×PTE_fraction)` is generally not `mean(released_fraction)×mean(PTE_fraction)`; data-driven within-species covariance matters. This algebra itself is not a new evolved mechanism. One must not relabel conditional PTE as the full fraction of total source pollen eventually delivered.

## Additional post-open tests locked before execution

The following **additional** checks are post-open and designed to probe two distinct limitations, not to produce independent evolutionary replications or select only significant results.

### A. Hive dependence and single-trial influence

Use the already authenticated 15 donor trial data, one observation per donor. Because B2 has only **one rostratum trial**, within-B2 species contrasts cannot give meaningful precision. Report **both** within-hive point estimates without significance claims and the number/range of leave-one-original-trial-out full-source throughput differences (15 deletions). In particular the B1 comparison is balanced at **five donor trials of each species**, and is a useful *single-hive* direction check, **not a second independently replicated pollen experiment**.

Implementation: `scripts/check_vasquez_2025_hive_dependency.py`. Output only derived summary `hive_dependency.json`, not trial raw data, person/bee-specific observations or new p values.

### B. Replay the published recipient-order mixed model

The 2025 paper reports a negative binomial (`nbinom2`) mixed model of stigma grain count per recipient, with:
- recipient index 1–4 (numeric),
- species (dulcamara as reference),
- `log(duration_visit)`,
- `log(donor_released)`,
- random intercept `(1|trial_number)`.

Fit **only** the two alternatives stated in the paper, additive and species×recipient interaction, on **60 recipient measurements nested within 15 donor trials**. Report coefficient/SE for recipient order and species, AIC of both published variants, optimizer convergence, positive-definite Hessian and trial random variance. For comparison, original reported recipient-order slope −0.339 ±0.098, species *rostratum* log contrast −0.954 ±0.310 and AIC additive 794.8 vs interaction 796.6. Reproduced numerical values are compared with fixed published anchors, **not forced to equality** or used to choose a new model. The original paper's additive specification is the principal source model. Failed convergence, source-model disagreement and potentially overfitted 15-trial random effects must remain visible.

Implementation: `scripts/replay_vasquez_2025_recipient_curve.R`, using the *exact original Zenodo SHA* and glmmTMB. Outputs original-source-only model coefficients and fit diagnostics, without raw CSV redistribution.

## Hard scientific limit for BALANCE

The public data have **no direct ground-fate/basket/body columns**, **no randomized flower-architecture intervention**, **no genetic pollen fatherhood**, and **no seed fitness**. Two species are not two randomized architectures, two source bee colonies are not a broad sample of pollination systems, and the 15 donor trials (not 60 stigmas) are the main source throughput unit.

This original-data result supports an **ecologically interesting denominator-dependent pattern**: two species have similarly low percentage of *removed* pollen reaching measured stigmas, but differ strongly in the fraction of their **total measured source pollen delivered**. The flower-structural or grooming mechanism is a hypothesis until the full compartments and treatment controls are simultaneously measured. The source cannot be promoted to the frozen U2/U6/V4 architecture classes or to a BALANCE `Phi`/structural cost estimate.

Both additional tests were fixed by the code and this document prior to evaluating their result outputs; they are **not** pre-field-study confirmatory preregistrations.

## Results from the same authenticated source: hive and recipient-order checks

**Both additional analyses have now been executed** from the genuine Zenodo
`data.csv` (SHA256 `484ed52ac611dbc6dc1831320a6c54d314492e9830823edd8934690c35205b79`)
in GitHub Actions [#45030511028](https://github.com/zuizui0223/balance/actions/runs/45030511028).
They are **post-open sensitivity and original-paper reproduction**, not new
independent biological experiments.

### Original 15-trial species difference within each observed bee hive

| Source hive | Original donor trials: dulcamara / rostratum | Source production → 4 stigmas: dulcamara minus rostratum (percentage points) |
|---|---:|---:|
| B1 | 5 / 5 | **+0.28169** |
| B2 | 4 / **1** | **+0.21943** |

Both within-hive point contrasts are positive. B1 is a useful **balanced
within-one-hive** sensitivity. B2 has one rostratum trial and does **not**
provide a replicated species effect within that hive. There are only
**two colonies** total; neither within-hive contrast identifies
species-versus-flower-architecture causality or population-level
colony-robust uncertainty.

Deleting each of the **15 unique donor trials** one at a time leaves
the full-source-throughput species contrast positive in **15/15** cases;
the differences lie between **+0.17783 and +0.27038 percentage points**.
This is *single-trial influence stability*, not 15 independently
replicated hypothesis tests or an external validation.

Machine-readable source-run results:
[`results/vasquez_2025/ORIGINAL_HIVE_AND_TRIAL_INFLUENCE_20261122.json`](../results/vasquez_2025/ORIGINAL_HIVE_AND_TRIAL_INFLUENCE_20261122.json).

### Original paper's negative-binomial recipient model is recovered

Using 60 recipient measurements, each in one of 15 donor-trial random
intercept groups, the authors' original predeclared additive
`glmmTMB` negative-binomial (`nbinom2`, log link) model was
**re-executed on the original exact 2025 public records**.

| Published-model term | Replayed log coefficient | SE | Replayed p |
|---|---:|---:|---:|
| Recipient order (1–4) | **−0.339172** | 0.097607 | 0.000511 |
| *S. rostratum* relative to *S. dulcamara* | **−0.953824** | 0.309527 | 0.002059 |
| log(visit duration) | +0.264634 | 0.110311 | 0.016440 |
| log(donor source pollen released) | +0.154850 | 0.159068 | 0.330314 |

The log recipient-order slope implies a conditional per-next-flower
multiplicative deposition factor of
`exp(−0.339172) ≈ 0.7124`, not a constant number of grains
on each new stigma. The donor source pollen-release coefficient is
**not statistically detected** in this particular fitted model and must
not be recoded as zero or equivalence.

The re-run reproduced the paper's AIC:
**794.806984** (additive) versus **796.616746** (species × recipient
interaction), `ΔAIC=1.809762`. The manuscript rounded these to
794.8 and 796.6. This is a strong **technical replication of the authors'
original models**, and by definition **not independent confirmation from a
new biological sample**.

The source-verified log and coefficient artifact was retained as GitHub
Actions artifact **14757542712**, ZIP SHA256
`392765f8aefb76bf2d558f64745efbc0a21d8997420bb8d7580cb6aaa65d082e`.
Detailed machine-readable transcription:
[`results/vasquez_2025/ORIGINAL_RECIPIENT_NBINOM_REPLAY_20261122.json`](../results/vasquez_2025/ORIGINAL_RECIPIENT_NBINOM_REPLAY_20261122.json).
These results use the two alternative models reported by the authors, with
no after-results model search.

### What does this add to BALANCE?

For the two observed plant species, similarly small **removed-pollen
conditioned PTE** is compatible with substantially different
**produced-to-recipient delivery**. The original 15-trial data show a
approximately **4.83-fold** ratio of mean `H_i/A_i` between species,
not the approximate **3.24-fold** product-of-rounded-group-means shortcut.
This source-conditional difference is not driven by a single donor
trial and has the same sign within both sampled hives, but B2's
species comparison is too sparse to generalize.

The more specific ecological hypothesis is that **source pollen
accessibility/removal is one bottleneck, whereas successful recipient
delivery conditional on removal is another**. Observational contrasts
of two *Solanum* species do not identify the respective contributions
of anther morphology, bee handling or grooming, ground loss, or sexual
fitness. Ground/basket/body channels are not in this actual Zenodo CSV,
so any claims about the specific source-fate channel remain anchored
to the original published article only. No paternity, seed production,
optimization of structural alternatives or frozen BALANCE V4
architectural coding was performed.

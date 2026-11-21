# BALANCE: bee learning separates pollen acquisition from pollen delivery (2026-11-20)

**Evidence status: one original published experimental research programme, not a new dataset reanalysis.**

Original-source and input-provenance review updated **2026-11-21**.

## Independently sourced empirical test of dual-function routing

Mayberry, Naumer, Novinger, McCart, Wilkins, Muse, Ashman & Russell (2024), *Behavioral Ecology* 35(6):arae083, DOI [10.1093/beheco/arae083](https://doi.org/10.1093/beheco/arae083); Dryad [10.5061/dryad.gtht76hwk](https://doi.org/10.5061/dryad.gtht76hwk). The original research is **one programme**, not four independently evolved floral solutions.

The experiment paired **initially flower-naive** with **experienced** pollen-foraging *Bombus impatiens* worker bees on four fresh flower species. The Methods report **81 workers from seven colonies**, with at least three colonies represented per plant species. Each bee was tested twice on the **same flower species**, with a roughly **24-hour gap** and the *naive* condition **always before** the experienced condition. Each test array contained 20 flowers. The experienced trials matched the preceding naive trials' number of bee visits. Pollen in **one bee's corbicula** and pollen deposited on **pooled stigmas from visited flowers** were counted after each trial. Thus the observational grain of the published pollen endpoints is the **bee trial**, paired by `ColonyID/BeeID`; visit counts and individual stigmas are not independent replication.

Figure 5 captions total **78 naive and 80 experienced trials**, which do not establish the number of complete pairs or either model's complete-case sample. The three missing naive videos described in the Methods concern behavioral measurements; they do not establish which pollen measurements were missing. One floral-complexity score per species also leaves complexity confounded with the other differences between those species.

Important fixed-order limitation: experience is confounded with elapsed time, second-day testing and any accompanying physiological change. The test order was not randomized. Source findings are credible within-bee experimental comparisons but do not separately identify training from period/carryover effects in the way a randomized training-vs-sham trial would.

## Original primary statistical results (not fitted by BALANCE)

| Original outcome | Original source statistic | Interpretation |
|---|---|---|
| Bee pollen collection in corbicula, experience effect | 22% overall higher collection; GLMM χ²(1)=9.81, **p=0.0017** | Positive bee-reward acquisition response |
| Collection per unit time | +24% overall (published result) | More efficient collection; not a measured plant fitness effect |
| Species×experience on collection | χ²(3)=0.30, **p=0.961** | No detected source-level evidence of differential experience effect on basket collection between four flower types |
| Stigma pollen deposition, author-reported experience term | χ²(1)=0.02, **p=0.893** | Type III term in an interacting model; reference coding and averaging contrast not independently verified; not an equivalence test |
| Species×experience on stigma deposition | χ²(3)=13.31, **p=0.0040** | **Clear published statistical evidence of heterogeneous response among these four flower types** |
| Motor routine×species×experience on stigma deposition | χ²(2)=19.70, **p=0.00005** | Reported with the other terms in the same stigma GLMM; not independent model-level corroboration |

Original Results pp. 6 and 8 give the following experience-associated changes **per visit**. In the author-hosted journal PDF, **Figure 5** is the experience boxplot and **Figure 4** is the motor-routine plot; the prose transposes these figure references.

| Plant species | Modified floral complexity index | Basket pollen change | Stigma pollen change |
|---|---:|---:|---:|
| *Phacelia campanularia* | 1.876 | +17% | +18% |
| *Exacum affine* | 2.126 | +19% | +28% |
| *Solanum elaeagnifolium* | 2.276 | +26% | −49% |
| *Erythranthe guttata* | 2.925 | +27% | −6% |

The original paper explicitly says that **all four individual species-level stigma differences were not statistically significant**; their individual p-values are not reported in this passage. The basket changes are point estimates without individual significance classifications in that passage. The nonsignificant experience term and significant species×experience term test different hypotheses; neither determines the significance of every individual species contrast. With interactions present, a Type III main-effect test should not be described as a verified species-averaged contrast without checking coding and the model matrix.

**Source arithmetic discrepancy:** the Results print **χ²(2)=7.69, p=0.0056** for the motor-routine main effect on stigma deposition. The chi-square tail at the printed statistic and two degrees of freedom is **0.0213864**; at one degree of freedom it is **0.0055528**. The receipt retains all printed values and flags the inconsistency. Both tail probabilities are below 0.05, but the source does not establish which element should be corrected. These are arithmetic checks of the printed triplet, not replacement biological tests. The three-way interaction above is a separate reported term and is numerically consistent.

It would be misleading to present this as “experienced bees do not affect pollination” *in every species* or as four independent demonstrations of evolutionary change. It would also be incorrect to equate counts on stigmas with viable seeds, to infer donor paternity from pooled stigma grains, or to identify the full costs of pollinator pollen harvesting.

## Source identity and availability

The Dryad landing page lists a trial-level summary file:

`AnalysisData_All-Trials-Summary-Data_20_8-4-2024.csv`

Documented columns include `BeeID`, `ColonyID`, `Species`, `Treatment`, `NumVisits`, `CorbPolperVis`, `StigPolperVis`, `CorbPol`, `StigPol`, and `TimeTotal`. It additionally lists flower-handling trace files split by species and a naive-bee efficiency file. The source's README denotes *Erythranthe guttata* with both `ERGU` and `MIGU`; the machine analysis normalizes that **exact documented alias only**.

**No original row-level CSV was retrieved in this ChatGPT environment.** On 2026-11-21 the [official file metadata](https://datadryad.org/api/v2/files/3536167) was retrieved successfully and supplied an independent identity for the expected bytes:

| Archive identity | Value |
|---|---|
| File / version | 3536167 / 321573 |
| Byte count | 27774 |
| SHA-256 | `4abb4300cfe5202058dd51003c5910e65c8c6cb774cd8b8100e8d5563b1433cb` |

The public file-stream still returned HTTP 403 through both web and direct runtime access. This is metadata retrieval, not row-level data recovery. The published original p-values and species summaries remain **transcriptions of the paper**, not newly estimated coefficients.

The optional helper computes within-bee descriptive log1p changes from a supplied CSV and separately reports its provenance. **A file path, official-looking filename or compatible schema does not establish original data.** Only bytes matching the independently pinned archive SHA-256 and size receive verified-original status. Synthetic or modified files remain unverified candidates, even under the official filename, and their results are kept out of the original-data analysis field.

Pairing uses `(ColonyID, BeeID)` with a one-species-per-bee check. The helper rejects duplicate treatments, missing-identity markers, cross-species pairs, unmatched visit counts, counts outside the source protocol's 1–70 range, invalid values and absent files. Bees with only one trial are counted and excluded from paired summaries. Missing or invalid endpoint values fail the file explicitly: this small helper does not yet implement endpoint-specific missing-data analysis. It should not be used to infer attrition from the source figure counts.

The helper **does not compute a p-value**, treatment-effect causal estimate or original mixed-model refit. Original inferential replication would need the actual trial-level data, colony-level effects, observed species groups, and GLMM distribution/link/fitting specifications. Test fixtures are entirely synthetic and never enter the original published evidence summary.

Reproduce:

```bash
python -m scripts.audit_bee_learning_dual_function
python -m pytest -q tests/test_bee_learning_dual_function.py

# Only when the genuine Dryad CSV is locally present:
python -m scripts.audit_bee_learning_dual_function --csv /path/to/original/AnalysisData_All-Trials-Summary-Data_20_8-4-2024.csv
```

## Biological connection to prior Solanum experiments

*S. elaeagnifolium* appears in both Mayberry et al. (2024) and the **2022 joined-anther manipulation** already studied in BALANCE PR #277. The 2022 experiment found that joining naturally loose anthers increased distal vibration and source pollen release in this species. The 2024 bee-learning experiment found that experienced bees collected a greater amount of pollen in their corbiculae for this species (+26% point estimate) while stigmatic pollen deposition was lower (−49% point estimate, not individually significant).

These are **independent experiments, but not interchangeable interventions, measurements or evolutionary replicates**. Nothing establishes that anther joining caused the bee learning response, or that extra pollen collected by the bee directly caused reduced pollen deposition. Both nonetheless make a sharp, experimentally testable **cross-stage interaction hypothesis**:

> Anther attachment may alter the amount of pollen made accessible, while bee handling skill alters what fraction of obtained pollen goes to a reward basket versus a recipient stigma; the resulting trade-off depends on their interaction and species-specific floral morphology.

### New experiment to distinguish this from period effects and pure mechanics

Use the same plant species *S. elaeagnifolium* with an **independently randomized bee-training vs sham-training** condition, followed by a matched test time in which **joined versus free anther configurations** are randomized within donor plant/flower blocks. Measure (1) mechanically released source grains under matched vibration, (2) pollen corbiculae on a single bee, (3) **conspecific stigma deposition** in a standardized recipient array, and ideally (4) paternal genotype assignment. Include matched no-bee/bee-naive controls; use multi-colony replication with bee ID, plant and accession as hierarchical sources, not pooled pollen counts as independent flowers.

Primary biological estimands:

```
delta_collection = log(mean basket pollen per visit | trained, joined)
                   - log(mean basket pollen per visit | sham, joined)
                   - same trained-sham log difference under free anthers

delta_deposition = same 2x2 difference-in-differences
                   for stigma pollen receipt per visit
```

To test whether the two endpoints respond differently, predefine and estimate `delta_deposition - delta_collection` on compatible scales, retaining their within-bee covariance and reporting uncertainty. One endpoint passing a significance threshold while the other does not is not a test of their difference. A nondetection without sufficient precision also does not establish equivalence. A positive effect in pollen release or basket collection is **not by itself a BALANCE architecture-fitness benefit**; neither new flower-organ cost `K`, optimized shared-vs-differentiated net fitness, historical selection nor `Phi` are identified.

## Evidence grade

- **Demonstrated in published experiment:** pollen basket acquisition increases overall; stigma deposition has a significant species-by-experience interaction.
- **Not established:** zero experience effect on stigma pollen everywhere; any individually significant stigma contrast; a formal cross-endpoint effect difference; absence of recipient fitness loss; source-pollen deprivation as the exclusive mechanism; causal effect of motor skills separated from the trial-period order; phylogenetic generality; net benefits/costs of flower architecture.
- **Current computational result:** source-check and future real-data paired-analysis workflow, **zero newly fitted biological effects**, 0 new original data rows, 0 changed U2/U6/V4 admissions and 0 independent human A/B architecture outcomes.

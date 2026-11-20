# BALANCE: bee learning separates pollen acquisition from pollen delivery (2026-11-20)

**Evidence status: one original published experimental research programme, not a new dataset reanalysis.**

## Independently sourced empirical test of dual-function routing

Mayberry, Naumer, Novinger, McCart, Wilkins, Muse, Ashman & Russell (2024), *Behavioral Ecology* 35(6):arae083, DOI [10.1093/beheco/arae083](https://doi.org/10.1093/beheco/arae083); Dryad [10.5061/dryad.gtht76hwk](https://doi.org/10.5061/dryad.gtht76hwk). The original research is **one programme**, not four independently evolved floral solutions.

The experiment paired **initially flower-naive** with **experienced** pollen-foraging *Bombus impatiens* worker bees on four fresh flower species. Each bee was tested twice on the **same flower species**, with a roughly **24-hour gap** and the *naive* condition **always before** the experienced condition. Each test array contained 20 flowers. At least three bee colonies were represented in each plant-species group. The experienced trials matched the preceding naive trials' number of bee visits. Pollen in **one bee's corbicula** and pollen deposited on **pooled stigmas from visited flowers** were counted after each trial. Thus the observational grain of the published pollen endpoints is the **bee trial**, paired by `ColonyID/BeeID`; visit counts and individual stigmas are not independent replication.

Important fixed-order limitation: experience is confounded with elapsed time, second-day testing and any accompanying physiological change. The test order was not randomized. Source findings are credible within-bee experimental comparisons but do not separately identify training from period/carryover effects in the way a randomized training-vs-sham trial would.

## Original primary statistical results (not fitted by BALANCE)

| Original outcome | Original source statistic | Interpretation |
|---|---|---|
| Bee pollen collection in corbicula, experience effect | 22% overall higher collection; GLMM χ²(1)=9.81, **p=0.0017** | Positive bee-reward acquisition response |
| Collection per unit time | +24% overall (published result) | More efficient collection; not a measured plant fitness effect |
| Species×experience on collection | χ²(3)=0.30, **p=0.961** | No detected source-level evidence of differential experience effect on basket collection between four flower types |
| Stigma pollen deposition, global experience effect | χ²(1)=0.02, **p=0.893** | **Nondetection, not demonstrated equality or absence of plant effects** |
| Species×experience on stigma deposition | χ²(3)=13.31, **p=0.0040** | **Clear published statistical evidence of heterogeneous response among these four flower types** |
| Motor routine×species×experience on stigma deposition | χ²(2)=19.70, **p=0.00005** | Additional complex interaction in a different model; not an independently replicated causal mechanism |

Original paper Fig. 4 species-level point estimates for experience-associated changes **per visit**:

| Plant species | Modified floral complexity index | Basket pollen change | Stigma pollen change |
|---|---:|---:|---:|
| *Phacelia campanularia* | 1.876 | +17% | +18% |
| *Exacum affine* | 2.126 | +19% | +28% |
| *Solanum elaeagnifolium* | 2.276 | +26% | −49% |
| *Erythranthe guttata* | 2.925 | +27% | −6% |

The original paper explicitly says that **individual species-level stigma differences were not statistically significant**. The **global stigma main-effect null and the species×experience interaction are not contradictory**: an overall average can hide different response directions; an interaction is not evidence that every species contrast individually passes a hypothesis test.

It would be misleading to present this as “experienced bees do not affect pollination” *in every species* or as four independent demonstrations of evolutionary change. It would also be incorrect to equate counts on stigmas with viable seeds, to infer donor paternity from pooled stigma grains, or to identify the full costs of pollinator pollen harvesting.

## Source identity and availability

The Dryad landing page lists a trial-level summary file:

`AnalysisData_All-Trials-Summary-Data_20_8-4-2024.csv`

Documented columns include `BeeID`, `ColonyID`, `Species`, `Treatment`, `NumVisits`, `CorbPolperVis`, `StigPolperVis`, `CorbPol`, `StigPol`, and `TimeTotal`. It additionally lists flower-handling trace files split by species and a naive-bee efficiency file. The source's README denotes *Erythranthe guttata* with both `ERGU` and `MIGU`; the machine analysis normalizes that **exact documented alias only**.

**No original row-level CSV was retrieved in this ChatGPT environment.** The public Dryad file-stream returned 403 here; earlier BALANCE Dryad API checks had 401. We avoid additional repeated blocked-network attempts. The published original p-values and species summaries are therefore **transcriptions of the paper**, not newly estimated coefficients.

After source bytes are legitimately available, the optional helper can compute within-bee paired descriptive log1p changes for basket pollen per visit and stigma pollen per visit, using the canonical `(ColonyID, BeeID, Species)` identity. It rejects duplicate treatments, pairing across species, unmatched paired visit counts, invalid values and missing source files; missing one-side bees are explicitly excluded rather than silently paired across other individuals.

The helper **does not compute a p-value**, treatment-effect causal estimate or original mixed-model refit. Original inferential replication would need the actual trial-level data, colony-level effects, observed species groups, and GLMM distribution/link/fitting specifications. Test fixtures are entirely synthetic and never enter the original published evidence summary.

Reproduce:

```bash
python scripts/audit_bee_learning_dual_function.py
pytest -q tests/test_bee_learning_dual_function.py

# Only when the genuine Dryad CSV is locally present:
python scripts/audit_bee_learning_dual_function.py --csv /path/to/original/AnalysisData_All-Trials-Summary-Data_20_8-4-2024.csv
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

The key empirical falsifier is whether anther configuration×training significantly changes pollen deposition while pollen collection shows a different response. If not, the hypothesized transfer bottleneck is unsupported for that condition. A positive effect in pollen release or basket collection is **not by itself a BALANCE architecture-fitness benefit**; neither new flower-organ cost `K`, optimized shared-vs-differentiated net fitness, historical selection nor `Phi` are identified.

## Evidence grade

- **Demonstrated in published experiment:** pollen basket acquisition increases overall; stigma deposition has a significant species-by-experience interaction.
- **Not established:** zero experience effect on stigma pollen everywhere; per-species effect significance; absence of recipient fitness loss; source-pollen deprivation as the exclusive mechanism; causal effect of motor skills separated from the trial-period order; phylogenetic generality; net benefits/costs of flower architecture.
- **Current computational result:** source-check and future real-data paired-analysis workflow, **zero newly fitted biological effects**, 0 new original data rows, 0 changed U2/U6/V4 admissions and 0 independent human A/B architecture outcomes.

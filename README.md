# BALANCE — persistence inside the compromise domain

`balance` is the middle-world theory between [`sch`](https://github.com/zuizui0223/sch) conflict identification and [`slk`](https://github.com/zuizui0223/slk) architecture value/evolutionary transport. [`bita`](https://github.com/zuizui0223/bita) is an orthogonal mechanism-identification layer rather than the owner of the architecture-value boundary.

## Independent species-first floral substrate expansion (2026-10-19)

[AusTraits v7.0.0 source-independent architecture/opportunity contract](docs/BALANCE_AUSTRAITS_INDEPENDENT_STRUCTURAL_OPPORTUNITY_V1.md) and its [verified 1.8-million-row live readout](docs/BALANCE_AUSTRAITS_V7_LIVE_READOUT_20261019.md) and [sex-structure hierarchy plus eleven candidate genera](docs/BALANCE_AUSTRAITS_V7_STRUCTURE_LEVEL_AND_LINEAGE_V1.md) and the [Wurmbea resource/selfing/sexual-history causal test handoff](docs/BALANCE_WURMBEA_FOCAL_CAUSAL_BRIDGE_20261019.md) document an external, checksum-verified public floral trait source and exact species-level coding **without selecting taxa because a functional trade-off or modular morphology has been reported**. It compares observed sexual-system organization with independently source-coded wind/insect pollination, with strict attrition and genus-support requirements, but never treats trait co-occurrence as SCH conflict, SLK structural cost, or historical modularization. The live acquisition runs as a separate GitHub Action; BALANCE V4 outcome files and the current manuscripts remain unchanged.

## Programme structure

```text
SCH
shared trait coordinate
-> is there a real functional conflict, and what is its load L?

BALANCE
conflict is real, but differentiation still does not pay
-> how broad, deep, resilient, connected, and persistent is this compromise domain?

SLK
architecture value and evolutionary transport
-> Phi = R-K -> accessibility -> invasion -> fixation -> occupancy

BITA (orthogonal)
trait interaction -> identified set -> mechanism allocation
```

The value hierarchy is therefore

```text
SCH -> BALANCE -> SLK
conflict -> persistent compromise -> architecture value and realization
```

while BITA asks a different question: what ecological mechanism is identified by a measured trait interaction?

## BALANCE as a middle world

SCH and SLK supply the two theoretical boundaries.

```text
SCH-facing certificate
L > 0
= a real shared-axis conflict exists

SLK-facing architecture-value certificate
Phi = R-K > 0
= recoverable benefit exceeds extra architecture cost
```

BALANCE is their sandwiched intersection:

```text
L > 0
and
Phi < 0.
```

Under the registered quadratic bridge only,

```text
R = sL,  s in [0,1],
Phi = sL-K.
```

`R=sL` is not a universal identity for arbitrary landscapes.

On a common fitness scale define

```text
rho = K-R
xi  = L / (L+rho)
d_B = min(L,rho).
```

Inside BALANCE, `0 < xi < 1`. `xi -> 0` approaches the SCH-facing no-conflict boundary, `xi -> 1` approaches the SLK-facing architecture-value boundary, and `d_B` measures two-sided depth inside the middle world.

See `docs/MIDDLE_WORLD_DEFINITION.md`, `docs/THEORY_OWNERSHIP_CLOSURE_V1.md`, and `balance_domain/world.py`.

## Direct empirical two-worldline route

BALANCE does **not** require the decomposed `R,K` representation before it can be tested.

If the two worldlines can be optimized on one matched reproductive-fitness scale, define

```text
W_S*(e) = optimized shared-coordinate fitness
W_D*(e) = optimized differentiated-accessible fitness
Delta_W(e) = W_D*(e)-W_S*(e).
```

Then a direct middle-world receipt is

```text
L(e) > 0
and
Delta_W(e) < 0.
```

This makes BALANCE logically independent: SCH supplies evidence that the shared world is genuinely conflicted, BALANCE compares the optimized worldlines, and SLK supplies the architecture-value decomposition

```text
Delta_W = Phi = R-K
```

when the direct and decomposed descriptions share a valid bridge. Under the registered quadratic bridge this becomes

```text
Delta_W = sL-K.
```

BITA does not own this decomposition. BITA separately asks what a measured `A x D` interaction identifies about ecological channel allocation. A bridge residual is retained as a diagnostic mismatch rather than automatically assigned to a BITA mechanism or an SLK cost.

See `docs/TWO_WORLDLINE_CONCORDANCE.md`, `balance_domain/worldlines.py`, and `balance_domain/worldline_path.py`.

## Static domain

Let

```text
L(e) = shared-coordinate conflict / compromise load
R(e) = recoverable conflict loss for the registered differentiated architecture
K(e) = added architecture cost
Phi(e) = R(e)-K(e)
```

Then

```text
L = 0              no identified shared-axis conflict
L > 0, Phi < 0     BALANCE domain
Phi = 0            architecture-value critical surface
Phi > 0            positive global architecture margin
```

For the registered quadratic bridge `R=sL`,

```text
0 < L < K/s
```

is the BALANCE-only region when `s>0`.

## BALANCE estimands

This repository studies properties of the *interior* of that region rather than either boundary alone:

```text
xi                        position between SCH- and SLK-facing boundaries
d_B                       two-sided depth inside BALANCE
q = R/K                   dimensionless proximity to the architecture crossing
rho = K-R                 critical reserve
W_e                       environmental width of BALANCE occupancy
A_rho                     integrated reserve across environment
N_B                       number of connected BALANCE intervals
N_0                       number of Phi=0 crossings
```

## Coordinates, algebraic consequences, and testable restrictions

BALANCE deliberately separates **coordinate algebra** from **scientific results**.

The following are bookkeeping consequences of the registered definitions/bridge and are
**not claimed as novel theoretical discoveries**:

- the static sandwich `L>0` and `Phi<0`;
- under the quadratic bridge, `0<L<K/s`;
- the interior coordinates `rho=K-R`, `xi=L/(L+rho)`, and `d_B=min(L,rho)`;
- under `R=sL`, the equal-margin point `L=rho=K/(1+s)` with `xi=1/2`;
- the width ratio `1/s` and positive affine-scale invariance.

Their role is to provide a common measurement coordinate, not to manufacture a result
from two linear inequalities.

The scientifically testable layer begins where additional empirical structure is imposed:

1. **Direct worldline identification.** Matched estimates of `W_S*` and `W_D*` can identify
   persistent compromise without first identifying `R` and `K`.

2. **Bridge concordance.** When direct and decomposed routes are both measured, the registered
   bridge predicts `Delta_W=R-K` (or `Delta_W=sL-K` under the quadratic bridge). Residual
   mismatch is a model-audit target.

3. **Cross-context restrictions.** Registered monotonicity, affine-envelope, or switching-cost
   assumptions imply no-reentry, bounded threat switching, endpoint certificates, or
   duration-dependent hysteresis. Those restrictions can be rejected by data.

4. **Comparative ecology.** Among independently adjudicated conflict-positive systems, the
   macro programme tests whether pre-existing module structure and the temporal/spatial
   geometry of competing demands predict shared persistence versus temporal, spatial,
   signal, or structural separation. These associations are not implied by the coordinate
   identities above.

See `theory/MIDDLE_WORLD_RESULTS_V1.md`,
`docs/ALGEBRA_EMPIRICAL_CLAIM_BOUNDARY_V1.md`, `docs/BALANCE_MACRO_PROGRAMME_V1.md`, and
`docs/BALANCE_PLANT_CONFIRMATORY_MODEL_FREEZE_V4.md`.

### Plant confirmatory contract

Current programme state can be reproduced with:

```bash
python scripts/report_plant_v4_readiness.py
```

This reports the machine-complete preparation, remaining U2/U6 human coding/adjudication
gates, pre-outcome V4 design status, and the fail-closed standalone-paper reactivation gate.

After genuine human returns close the assembly gates, the frozen CmdStan execution entrypoint is:

```bash
python scripts/run_plant_v4_cmdstan.py --cmdstan-dir /path/to/cmdstan
```

The runner uses the preregistered sampling/diagnostic contract in
`data/BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json` and refuses posterior decisions
when convergence diagnostics fail.

The flowering-plant confirmatory lane has a frozen four-class primary response:

```text
SHARED
NONSTRUCTURAL_SEPARATION
STRUCTURAL_MODULE_DIVISION
MOSAIC
```

Entry requires independently adjudicated, outcome-independent receipts for
`module_substrate`, `conflict_timing_geometry`, and
`conflict_spatial_geometry`. The raw three-axis coding is retained, but the current V4 routing fit is restricted to the two conflict-focused universes U2 and U6, uses universe-specific multinomial intercepts, and estimates common preregistered `module_opportunity2` and `temporal_exposure3` slopes. `spatial_exposure2` is secondary because the architecture-blind source-support audit found 28 SAME_UNIT versus 1 DISTRIBUTED block. U1 remains the external broad-interaction specificity test rather than entering the V4 routing denominator.
The binary structural outcome is secondary, and there is no significance- or
outcome-sparsity-triggered switch of the primary estimand.

## Empirical claim levels

BALANCE separates two empirical levels.

```text
FUNCTIONAL_STATE_MIDDLE_WORLD
second functional state/axis is experimentally enabled or disabled
but the structural architecture itself is not removed or costed

STRUCTURAL_ARCHITECTURE_MIDDLE_WORLD
repeatable structural/performance difference is established
and matched architecture/maintenance cost is on the same fitness scale
```

For `Pedicularis rex`, the current water retained/drained intervention belongs first to the **functional-state** level. It does not by itself establish a structural-architecture middle world because the cupulate bract architecture is still present.

The empirical gate is tracked in issue #3 and `empirical/BALANCE_EXECUTION_RECOVERY_LEDGER_V1.csv`.

## Current observational anchor: Peucedanum

Published `Peucedanum multivittatum` results provide an external critical-region anchor. Three operational definitions—final fruit-set selection gradient, selection differential, and female-gain shape—each cross their threshold between the same ordered contexts `HL` and `HC`.

Registered result:

```text
SAME_COARSE_CRITICAL_BRACKET = HL--HC.
```

This does **not** establish `L`, `W_S*`, `W_D*`, or the common architecture boundary. It shows only that multiple operational definitions concordantly locate one observational transition region; because they come from the same Peucedanum observational programme, they are not independent biological replications.

See `docs/PEUCEDANUM_CRITICAL_REGION_ANCHOR_V1.md` and `empirical/peucedanum/PEUCEDANUM_CRITICAL_DEFINITIONS_V1.json`.

## Separation from sister repositories

- **SCH owns** conflict identification and, when admissible, export of a fitness-scale conflict load `L`.
- **BALANCE owns** direct ordering of shared and differentiated-accessible worldlines and the geometry, depth, reserve, topology, and persistence of the region `L>0, Phi<0`.
- **SLK owns** the architecture-value object `Phi=R-K`, the quadratic bridge `R=sL`, and the subsequent accessibility → invasion → fixation → occupancy hierarchy.
- **BITA owns** `trait interaction != ecological mechanism`, identified sets, partial identification, selective interventions, separability diagnostics, and mechanism allocation.

The programme therefore says:

```text
SCH:      conflict exists.
BALANCE:  the shared world still outranks the differentiated-accessible world.
SLK:      when Phi crosses zero, global value changes; realization still has further gates.
BITA:     a trait interaction does not identify its ecological mechanism without extra information.
```

Do not claim historical trait splitting from this repository without independent historical evidence.

## Current status

Implemented with regression guards:

- static BALANCE path analysis,
- critical reserve and topology,
- switching-cost hysteresis,
- middle-world certificate,
- middle-world position `xi`,
- two-sided depth `d_B`,
- deepest-point geometry,
- direct shared-vs-differentiated worldline comparison,
- direct empirical worldline-path mapping,
- direct-versus-decomposed bridge concordance checks,
- same-critical-point versus parallel-critical-points classification,
- bounded cross-repository receipts that preserve uncertainty,
- Peucedanum multi-definition critical-region fixture,
- explicit functional-state versus structural-architecture claim ceiling.

Canonical public fields and state labels now use neutral `architecture_*` terminology. Deprecated `bita_*` properties and legacy state accessors remain read-only compatibility aliases; they no longer define scientific ownership of the `Phi=0` boundary.

## Literature-synthesis milestone

**Mechanism-specific ecological contrast (2026-10-19):** independently assembled flowering-plant review screens now expose **two species present under different functional-pair tests**. *Mimulus aurantiacus* and *Ipomopsis aggregata* each have **NO_DEMONSTRATED_CONFLICT** for the herbivory–pollination coordinate within the U1 source review while their distinct U2 original sexual-interference studies have **POSITIVE conflict evidence**. The U1 review covers 47 plant taxa (0 registered conflict-positive under a strict shared-axis rule), U2 covers 22 species (8 conflict-positive), and the combined 69 source rows contain **67 distinct recorded dependency groups**. In the eight U2 positives, **4 have shared integrated morphology, 3 temporal/spatial separation, 1 polymorphic/mosaic**; 9 U2 non-positive records have complex morphologies despite no demonstrated interference in their original cited study. **The review samples are intentionally non-exchangeable, not independently double-adjudicated, and the same-species source pairs differ in focal functions and study contexts**. This is a source-screen ecological specificity counterexample—not a global prevalence estimate, a same-season within-species switch, a fitted structural differentiation model or a direct BALANCE worldline. See `docs/BALANCE_PLANT_CROSS_FRAME_FUNCTION_PAIR_SPECIFICITY_V1.md` and `balance_domain/plant_cross_frame_conflict.py`.



The manuscript programme places literature-pattern recovery before final direct validation. The source-adjudicated pattern ledger contains 17 independent biological clusters, including 9 middle-regime signatures. A strict Q1B quantitative layer has three independent effect-size-ready positive-admitted systems (`Fragaria vesca`, `Impatiens capensis`, and `Gymnadenia conopsea` 2015), alongside two design-matched negative controls and explicit estimand/attribution boundaries.

Because positive Q1B admission requires the preregistered same-coordinate conflict pattern, the three-cluster random-effects result is interpreted as a **conditional positive-case summary of magnitude and heterogeneity**. It is not an unbiased design-wide meta-analytic mean and its sign is not an independent test of recurrence. Recurrence is supported by recovery of the registered pattern in three independent biological systems; the matched negative controls show that comparable factorial designs do not inevitably produce the pattern.

**Structural source-eligibility audit (2026-10-14):** a new fail-closed five-system primary-source check (Pedicularis, Solanum, Dalechampia, coGFP, and Salmonella) explicitly distinguishes morphology, functional-state effects, fluorescence selection, and maternal seed costs from a matched *net structural-architecture* fitness test. All five candidates currently HOLD at this stricter source gate; none adds an independent biological cluster or a direct BALANCE worldline. See `docs/BALANCE_STRUCTURAL_WORLDLINE_SOURCE_GATE_V1.md`, `data/BALANCE_STRUCTURAL_WORLDLINE_SOURCE_AUDIT_V1.json`, and `scripts/audit_structural_worldline_sources.py`.

**Ecological stage-reuse anchor (2026-10-14):** an exact-source reported-effect audit of *Dalechampia scandens* shows a **post-anthesis reproductive benefit of retaining greenable bracts**: bract removal / **whole-blossom foil shading** in a 2015 hand-pollinated greenhouse experiment reduced four-week seed mass by 1.34 ± 0.32 / 2.03 ± 0.32 mg per seed (source SE). Its 2013 wild bract-size conflict and 2012 resin-production cost results remain **separate biological contexts**, not a combined architecture-worldline experiment. This supports an experimentally observed *staged functional reuse* mechanism worth testing but not structural BALANCE occupancy or a newly independent cluster. See `docs/DALECHAMPIA_TEMPORAL_BRACT_REUSE_V1.md`, `data/DALECHAMPIA_TEMPORAL_BRACT_SOURCE_V1.json`, and `balance_domain/dalechampia_temporal.py`.

**Original source-method clarification (2026-10-15):** the 2015 treatment historically called `shaded bracts` wrapped the **entire pollinated blossom in perforated aluminium foil**, not the bracts alone. Its observed early seed-mass effect is a total treatment-package contrast and cannot isolate bract photosynthesis from fruit illumination or foil/microclimate effects. Original seed-level and blossom gas-exchange text files are publicly catalogued as [Dryad 10.5061/dryad.nb675](https://doi.org/10.5061/dryad.nb675), and their exact metadata/digests and safe reanalysis preflight are in `docs/DALECHAMPIA_2015_WHOLE_BLOSSOM_SHADE_DRYAD_GATE_V2.md`. The raw bytes were **not downloaded or re-fitted** in this amendment.


**Exact original Dryad replay (2026-10-15):** the 2015 *Dalechampia* source files (seed records and blossom gas exchange) have now been recovered from official Dryad and independently MD5/SHA256 verified through GitHub Actions. The authenticated seed file contains **1,221 rows/1 missing mass**, 142 blossoms nested within 37 mothers; the gas experiment contains 6 independent plants. A new distinct analysis recovers green-versus-white **area-based bract photosynthesis** (1.469 vs 0.424 μmol m⁻² s⁻¹, six-plant paired difference ≈ +1.045) and explores within-mother paired early seed-mass contrasts under two reported-abortion proxy choices. This is **not** original mixed-model reproduction, a bract-specific carbon transfer experiment or structural BALANCE evidence. Full source receipts, limitations and reproducible code: `docs/DALECHAMPIA_2015_EXACT_DRYAD_MATERNAL_SENSITIVITY_V1.md`, `data/DALECHAMPIA_2015_EXACT_DRYAD_SENSITIVITY_FREEZE_V1.json` and `.github/workflows/dalechampia-2015-original-dryad-recovery.yml`.

**Blossom-level uncertainty recheck (2026-10-16):** authenticated 2015 *Dalechampia* seed records now also support an alternative regression that treats **one experimentally assigned blossom as one observation**, controls for mother fixed effects and peduncle diameter, and clusters uncertainty by mother. On the numeric ≥20 mg subset (1,103 seeds/132 blossoms/36 mothers), whole-blossom foil cover has a negative estimate (−1.841 mg) but a mother-cluster-robust 95% interval [−3.862,+0.179] mg; bract removal similarly has [−3.298,+0.981] mg. Sensitivity to the seed-mass inclusion criterion and optional seedset covariate is reported for **all four variants**, not selected post hoc. This is **not** a reconstruction or refutation of the published mother-random mixed model, and does not identify a bract-specific carbon mechanism. See `docs/DALECHAMPIA_2015_BLOSSOM_CLUSTERED_SENSITIVITY_V1.md` and the registered source-hash-gated workflow.

**Published mixed-model numerical audit (2026-10-16):** the authenticated *Dalechampia* 2015 seed file was refitted under modern R **nlme**, following all six original source Table-2 maternal-random model formulas (ML AIC, REML coefficients) and a separate treatment-specific residual-variance model. All six absolute AICs remained about **147–154 units higher** than the published figures (e.g. **6152.41 versus 6005.72** for peduncle + treatment), although modern R nlme and independently computed Python MixedLM AICs agree within numerical tolerance. The printed treatment SEs and the *relative* improvement from residual heteroscedasticity were approximately recovered. This is a **proven numerical reproduction gap under stated reconstructed assumptions**, not evidence of a publication error, nor a structural BALANCE result. Original 2015 R script and exact historical preprocessing remain unrecovered; see `docs/DALECHAMPIA_2015_PUBLISHED_NLME_REPRODUCTION_V1.md` and `data/DALECHAMPIA_2015_PUBLISHED_NLME_REPLAY_VERIFIED_V1.json`.

**Nested experimental-unit sensitivity (2026-10-16):** Original 2015 *Dalechampia* records have now also been refitted in source-validated R nlme with **random mother and nested blossom intercepts** on the same 1,103 numeric-eligible seeds. Compared with mother-only, the nested random structure sharply improves AIC (**5135.56 vs 6152.41**) and identifies very strong modeled dependence between seeds of the same manipulated blossom (**ICC 0.886**). It changes whole-blossom foil SE **0.318 → 0.991 mg**, bract-removal SE **0.323 → 1.000 mg**, while effect point estimates remain similar; all three nested normal 95% Wald intervals span zero. This is **posthoc experimental-unit covariance evidence**, not a biological replication, error verdict on original author code, bract-carbon causation or architecture BALANCE occupancy. See `docs/DALECHAMPIA_2015_NESTED_BLOSSOM_COVARIANCE_V1.md` and the verified source-readout JSON.

**Prospective mechanism programme (2026-10-17):** Because post-anthesis *Dalechampia* bracts close around developing fruits, a bract-targeted optical cover can also shade the fruit and change microclimate. New method-only, mother-paired **bract-versus-fruit photon selectivity** screening and a source-variance-anchored **hypothetical independent-plant design planner** define what a genuine bract-carbon test would require. Example (normal approximation, unknown new effect): for an *assumed* 1.83-mg response difference, one blossom per arm and eight usable seeds per blossom would require approximately **71 independent mothers** for 80% nominal power; two blossoms per arm would require **36**. The assumed difference is the magnitude of a historical **whole-blossom foil** estimate, *not* a bract-specific effect. If fruit PAR, temperature, humidity or physical protection changes with the method, the bract-only causal claim is held. Prospective source-local **13CO2** uptake/seed transfer would require independent leakage controls and is not evidence of fitness by itself. See `docs/DALECHAMPIA_BRACT_CARBON_ISOLATION_FIELD_PROGRAMME_V1.md`. No new biological outcomes or direct structural BALANCE receipt were generated.

**Prospective isotope source-discrimination gate (2026-10-17):** a ^13CO2-labelled *Dalechampia* bract and an unlabelled sham must be placed on **different independent maternal plants**; labeled photosynthate can otherwise travel to the same plant's control blossoms. The Stage-1 screen now requires **three-plant randomized blocks** (unlabelled sham, bract-local pulse, and positive fruit-leak-exposure mimic), direct bract/fruit/ambient gas-exposure monitoring, bract- and seed-tissue ^13C atom-percent excess above pretreatment background, and assay uncertainties propagated from both background and post measurements. It rejects source signatures explainable by a leaking fruit control, poor source gas containment, plant crossover, assay noise or mismatched stage. The calibration templates are deliberately invalid/unfrozen until a genuinely dated external protocol and real isotope measurements exist; even a numeric screen PASS is **not a proven causal carbon source, mature-seed fitness, or structural BALANCE state**. See `docs/DALECHAMPIA_BRACT_13C_SOURCE_DISCRIMINATION_V1.md`, `balance_domain/dalechampia_tracer_source.py` and `scripts/evaluate_dalechampia_bract_13c_source.py`.

**Exact tracer randomization design constraint (2026-10-18):** the three-distinct-mother per-block *Dalechampia* ^13CO₂ assay can perform method/QC screening with three blocks, but a **two-sided 5% exact matched-block sign-flip randomization test requires at least six independently randomized complete blocks (18 maternal plants)** even to *permit* significance: n=3/4/5 min exact p=.25/.125/.0625; n=6 p=.03125. This is the finite assignment-support floor, **not biological 80% power**. A distinct blocked randomization module computes B-vs-fruit-leak-mimic seed-^13C APE contrasts across **ALL preassigned blocks**, including source-screen HOLD blocks, so isotope-positive blocks cannot be selected post hoc to inflate significance. The randomized test only tests an isotope treatment-regime difference; it does not verify organ-specific carbon assimilation, tracer mass balance, seed-fitness improvement, or structural BALANCE. See `docs/DALECHAMPIA_13C_BLOCK_RANDOMIZATION_INFERENCE_V1.md`, `balance_domain/dalechampia_tracer_randomization.py` and `data/DALECHAMPIA_13C_EXACT_RANDOMIZATION_RESOLUTION_V1.json`.

**Species-level conflict multiplex (2026-10-19):** complete U2 sexual-interference **22-species** and plant macro **29-row/28-dependency-group** original source-screen frames overlap in **4 species**, across 51 source rows and 46 distinct dependency groups. In *Polemonium viscosum*, independent original experiments identify **self-versus-outcross pollen interference** (24-h self precedence reduced compatible pollen germination **32%** and seed production **40% in one year**, while in another year pollen germination inhibition did not lead to detected seed loss) with temporally/spatially separated pollen-stigma function **and** a distinct bee-attraction-versus-ant-defense corolla-shape trade-off, observed in a **shared integrated corolla** (genetic length/flare rA=0.70; narrow tubes reduce ants but decrease pollen receipt and seeds). *Narcissus assoanus* provides a second principle: forced self/cross interference reduced seed set in glasshouse tests (20% simultaneous, 60% prior self) but did **not** produce detected male or female field costs, with long-style protandry and short-style herkogamy as distinct avoidance strategies. *Solanum rostratum* and *Ipomopsis aggregata* likewise show function-pair/era-dependent source states. Thus a species does NOT have one ecology-wide binary conflict or architecture state: code taxon × tested function pair × shared anatomical coordinate × ecological exposure. **This is qualitative source-linked positive biology, not independent adjudication, numerical pooled fitness, unbiased macro prevalence, or structural BALANCE occupancy.** See `docs/BALANCE_PLANT_CONFLICT_MULTIPLEX_ECOLOGY_V1.md` and `balance_domain/plant_conflict_multiplex.py`.

**First independent interaction-database acquisition (2026-10-19):** four existing BALANCE focal plant names were queried in the public Global Biotic Interactions (GloBI) API and the **254 actual returned relationship rows** archived under `data/external/globi/2026-10-19/`. Only **96 rows** match the *literal requested plant on the target side*; **158 do not**, requiring taxonomic/source orientation checks. *Polemonium viscosum*: 30 returned/28 exact target; *Narcissus assoanus*: 2/2; *Ipomopsis aggregata*: 126/66. Most importantly, **all 96 rows returned for query *Solanum rostratum* refer to *Solanum angustifolium***: POWO distinguishes accepted *Solanum rostratum Dunal* from a different-authorship *S. rostratum L'Hér. ex Dunal* name synonymous with *S. angustifolium*. That target is **TAXONOMIC_HOLD**, neither 96 authenticated *S. rostratum Dunal* interactions nor proof of ecological zero. GloBI relation labels can be broad-rank, nontested and duplicated; a `pollinates` or `visitsFlowersOf` record is an *interaction opportunity*, **not a demonstrated shared-axis fitness conflict**, ecological prevalence or strict BALANCE occupancy. An outcome-blind, species-first denominator must precede confirmatory macro inference. See `docs/BALANCE_GLOBI_PUBLIC_INTERACTION_OPPORTUNITY_PILOT_V1.md`, `balance_domain/globi_opportunity.py`, and source snapshot manifest.

**Actual species-first public interaction database result (2026-10-19):** a precommitted SHA256 species sample across 12 accepted angiosperm families/orders has now been acquired from **official GBIF taxonomic pages**, yielding **48 accepted plant species selected before GloBI lookup**, with **48/48 GloBI queries completed** and original source responses committed. **16/48 species** have at least one exact TARGET-side matching GloBI association (**188 exact-name rows**) while **32/48** lack matching recorded relationships in this snapshot (**NOT ecological absences**). Coverage is severely concentrated: *Solanum asperolanatum* contributes **103/188** rows, only **2 source rows labelled flower visitation** (both *Hormathophylla longicaulis*) and **0 labelled pollinates** for these specific 48 names. Only **88/188** exact-name rows have a directly identical original **GBIF species key**, with another 100 requiring independent author-level concept crosswalk. This is genuine independently acquired *interaction-documentation opportunity* and data-bias evidence, **NOT direct same-axis fitness trade-offs or structural BALANCE**; the 12 family strata are convenience-chosen, not a globally representative random flora. Source report: `docs/BALANCE_GBIF_GLOBI_SPECIES_FIRST_COVERAGE_V1.md`; exact source files, manifests, fail-closed reauditor and 48-species export are committed on the same programme.

The literature synthesis still has zero matched direct shared-versus-differentiated worldline receipts. Therefore the remaining empirical task is the same-context, common-fitness-scale comparison of `W_S*` and `W_D*` with joint uncertainty. That empirical gap does not prevent the theoretical ownership structure from being closed.

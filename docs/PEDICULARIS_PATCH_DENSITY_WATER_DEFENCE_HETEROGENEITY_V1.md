# Pedicularis rex: patch-density moderation of water-defence function

**Status:** literature-triangulated, prospective experiment design; **no jointly observed treatment × patch-density response data** and **no causal density effect**.

## Why this is not a fourth paper repeating the same result

Three published results address *different* components of the same system, in different field contexts:

1. **Xia, Sun & Liu (2013)**, *Biology Letters*, DOI 10.1098/rsbl.2013.0387: sparse patches of *P. rex* had higher seed/fruit predation and lower final seed set, in both surveyed years; no corresponding density difference in pollination rate or initial reproductive success was detected. In their 2011 survey sparse patches had **less than 2** flowering plants m⁻², dense patches **more than 5** m⁻². Patch size and density also interacted in seed predation, so density is not a universal causal label. **Density was observed, not randomized.**
2. **Sun & Huang (2015)**, *AoB PLANTS*, DOI 10.1093/aobpla/plv019: bract drainage (by physical basal perforation) increased seed predation in **five of six** populations, and the paper reported a site-by-treatment interaction for predation. This identifies a combined water-removal/perforation intervention; its water-only mechanism requires the separate B0 qualification protocol. These six treatment populations are **not** a paired 2013 density-randomization experiment.
3. **Sun, Armbruster & Huang (2016)**, *Annals of Botany*, DOI 10.1093/aob/mcw097: floral relative exsertion was positively associated with both stigma pollen receipt and seed predation. The index `(flower_length-bract_height)/flower_length` is an anatomical composite, **not** direct water-to-oviposition-site clearance.

### The key literature-induced support gap: 2015 deliberately avoided sparse patches

Sun & Huang (2015) did not merely fail to include a density covariate: its Methods explicitly say the authors **tagged and sampled from dense patches in every population to reduce confounding from the Xia et al. (2013) density-dependent predation result**. The Methods sampled 40–60 inflorescences from 20 **dense** subplots per population and drained 20–30 inflorescences in each of six populations. Therefore no *within-study randomized wet-versus-drained contrast in sparse patches* is available for source-based reweighting, and 2015 cannot answer the proposed sparse-versus-dense water-treatment heterogeneity question.

In 2015, `site × treatment` was statistically detected for **seed predation** (Table 2: χ²=36.782, df=5, p<0.0001), but **not** for final viable seed set (χ²=4.913, df=5, p=0.4265). The paper reports water-drainage-related seed predation increases in five of six sites. Site heterogeneity alone does not establish a density gradient: those experimental sites were sampled from dense patches, and site also includes climate, antagonist community and other contextual differences.

This is a sharper empirical gap than simply noting three papers on the same organism. The required unobserved cells are *water-manipulated, method-qualified sparse patches*, with within-patch randomization and adequate independent patch replication. It is also a stronger novelty check: do not claim the 2015 seed predation effect or 2013 component Allee effect as newly discovered.

The **open question** is whether the causal payoff of an already existing water-bearing bract defence varies systematically with predator encounter context, and **at what biological stage**: encounter, oviposition given encounter, or seed damage after verified deposition. The three source papers motivate the question; they have not jointly estimated its causal contrasts.

## Registered ecological alternatives and discriminating predictions

| Mechanism | Predator approach events per focal plant-hour | Verified egg deposition given standardized encounter opportunity | Fitness advantage of refilled wet versus dry |
| --- | --- | --- | --- |
| H_encounter (density dilution/concentration) | Density strongly modifies attack opportunity; water might also cue approach | Physical water exclusion approximately invariant across patch-density contexts under equalized predator exposure | May vary because each plant faces different total attack exposure, not because barrier efficacy changed |
| H_access (density-dependent barrier usage/behaviour) | Cannot uniquely explain response | **Water × density** interaction persists under a verified standardized oviposition opportunity and matched target clearance | May vary even after accounting for encounter opportunity |
| H_cue (olfactory/visual/microclimate orientation) | Water changes approach/landing behaviour | Differences may vanish with standardized close exposure, or persist if cue affects oviposition decision | Varies with predator behaviour or community context |
| H_post (post-deposition defence) | No particular difference required | No particular difference required | Damage/viable seeds differ **after** verified egg deposition |
| H_null or context heterogeneity | No robust effect | No robust effect | No reproducible treatment heterogeneity after blocking, repeated contexts and power |

A treatment-by-density interaction in **final seed number alone** cannot allocate these pathways. The chain of approach → oviposition → larval establishment is biological, not a mathematical demonstration of why one mechanism must dominate. Predators may include Diptera and Lepidoptera and guild/species composition may vary across patches. Measure guild identity independently where feasible; never equate unverified egg scars or damage with a particular insect taxon.

The 2016 long-tube/trait correlations are already published; do not claim this design newly discovered pollinator–enemy conflict.

## Prospective water intervention and randomization

**Prerequisite:** source-linked, *same-population, same-season* `PEDICULARIS_WATER_B0_METHOD_FEASIBILITY_RECEIPT_V1` with `B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL`, checked by exact file SHA256. B0 requires validated nonperforating dry and refilled wet methods, no unintended effects on floral exsertion, physical pollinator access, or mechanical damage. The proposed pilot does **not** make the water defence effect causal by itself; method fidelity must be checked again in the new patch ecology.

The B0 *method* pilot can have its own `context_id` and `protocol_version`, different from the definitive B1 treatment-effect trial, provided its source-verified population and season are the same. Freeze the **expected B0 method context ID and version separately** and verify them against the content-hashed B0 receipt; never relabel a B0 method pilot as the same causal experiment as B1. The pilot's documented water method must also remain feasible in both sparse and dense patches; validated methods in one habitat do not automatically transfer to another.

The B1 experiment randomizes **one confirmed water compartment per plant** *within each density patch* into the three arms:
- `INTACT_WET`: unmanipulated natural wet control;
- `INTACT_DRY`: verified nonperforating removal, maintaining dry state;
- `INTACT_REFILLED_WET`: identical water removal/handling followed by refill, maintained wet.

The primary causal treatment is **refilled wet vs dry**, which shares the manipulation history. Unmanipulated wet vs refilled wet is a handling-equivalence **test with a preregistered tolerance**, not a nuisance difference to ignore because p>0.05.

Measure patch flowering density (plants/m²) and patch size **before water assignment and before reproductive outcomes**. The source 2013 categories (<2 sparse and >5 dense) can justify *candidate* strata, but B1 numerical boundaries, the minimum patches per stratum and independent plants/arm/patch **must be justified and prospectively frozen**. Densities inside the gap are HOLD in the binary confirmatory allocation, rather than silently dropped post hoc. The density measurement, rainfall/microclimate, altitude, calendar dates, baseline floral geometry and pre-treatment predator guild presence should be retained for interpretation.

**Additional non-obvious allocation trap:** if every sparse patch is at one field site and every dense patch is at another, a density-by-water comparison is confounded with site-level climate, predator community and observation history. The design gate therefore demands a predeclared minimum number of **sites with both sparse and dense patch strata** as well as **at least two independent patches per stratum**. Plant counts cannot repair having only one independent patch, even if each patch has hundreds of flowers.

The three-arm-within-patch requirement also restricts the ecological target: some naturally sparse patches contain only one or two plants and **cannot** support a three-arm randomized comparison. The required target is therefore *sufficiently large sparse patches*, predeclared before outcomes. Do not generalize any estimated treatment effect to singleton patches. If field survey shows such patches are unavailable, this specific design must HOLD and be redesigned with enough independently randomized matched patches; do not invent within-patch treatment cells by imputing unobserved potential outcomes.

Within a patch, treatment arms must have overlapping randomization blocks: a wet-only subplot and dry-only subplot would be a confounded treatment comparison. In the first design every randomized plant has one water-compartment unit; several flowers in the same whorl cannot be independently assigned. Repeat flowers/time within plant are subsamples; patch replication, not flower count, supports population-density effect heterogeneity.

### Core estimands (frozen before biological outcome analysis)

Let `Y_ip(w)` be **the count of undamaged viable mature seeds per prospectively designated focal flower** on plant i in patch p if assigned water state w. Assign the focal flower and missing/censoring rules before knowing seed outcomes. A lost flower does not automatically equal zero; distinguish a verified zero viable seed result from unknown outcome/failed sampling.

Within patch p, the intention-to-treat contrast is

`tau_p = mean(Y | REFILLED_WET, p) - mean(Y | DRY, p)`.

For an ordered registered sparse/dense design, the *heterogeneity contrast* is

`theta = mean_patch(tau_p | SPARSE) - mean_patch(tau_p | DENSE)`.

Predeclare patch-level weighting; equal weights across independently sampled patches are the design default, not pooling flowers across patches. Report individual patch effects and uncertainty as well as the group contrast. **Even if the within-patch water assignments are randomized, patch density is observational:** theta is **causal water-treatment effect modification conditional on observed patch context**, not the causal effect of changing density or a universal adaptation gradient.

Continuous log-density and patch-size sensitivity may be defined before outcomes, with overlapping density support. Do not rechoose density boundaries after seeing a positive interaction. Do not condition the *primary* water ITT on post-treatment predator visits, oviposition, fruit set or seed counts (potential mediators/colliders).

### Discriminating the mechanism

Collect separate, time-aligned observations:
1. **Approach** — identifiable predator visits/oviposition approaches per registered plant-hour (video effort in the denominator; zero must mean watched-and-none, not missing video).
2. **Oviposition** — verified deposition attempt/egg count and target position; separate absence from unreadable observations.
3. **Establishment** — larval survival/damage conditional on reliably verified deposition, with separate rearing/dissection where possible.
4. **Mutualist channel** — bumblebee visits, pollen receipt and handling/flower-geometry checks to rule out major off-target perturbation.
5. **Reproductive output** — primary undamaged viable mature seed count and loss reason per preassigned focal flower.

Conditioning on observed approach is **post-treatment selection** if water changes approaches; `eggs / observed approaches` is a mechanistic description, not automatically a causal direct effect. To identify a physical waterline barrier independent of adult encounter context, an **independent standardized encounter experiment** (or independently justified selective approach intervention) is needed, without making water/oviposition manipulation alter the measured geometry. No such predator-access experiment is claimed as already feasible.

### Statistical guardrails

- **Primary:** patch-level ITT contrasts with plant as the water assignment unit; replicate patches in sparse and dense contexts, preserving site/season strata.
- **Uncertainty:** patch-level resampling or hierarchical model that does not treat several plants sharing one patch as independent density contexts; small patch counts cannot license a precise theta.
- **No fixed sample size:** field n needs independent B0 method feasibility, patch availability and prospectively specified minimum relevant water fitness effects, then cluster-aware power for the *heterogeneity* contrast, not merely a water main effect.
- **No counterfactual architecture claim:** natural water/dry/refill states all retain the same cupulate-bract/corolla architecture; this is a context-sensitive **functional-state benefit**, not a directly measured developmental architecture cost K, recoverable conflict R or structural-BALANCE occupancy.
- **Same-context caveat:** do not combine published 2013 patch-density contrasts and 2015 treatment means from unrelated populations/years as if they were one matched randomized experiment.

## Executable prospective allocation checks

- `balance_domain/pedicularis_density_water_allocation.py`: zero-outcome, same-context checker for actual B0 receipt, density stratification, independent patch replication, 3 arms inside *every* patch, common within-patch randomization blocks, plant/whorl identity, patch density/size consistency and complete source support.
- `data/PEDICULARIS_DENSITY_WATER_ALLOCATION_TEMPLATE_V1.csv`: exact-header pre-outcome assignment and patch measurements, no egg/pollen/fitness variables.
- `data/PEDICULARIS_DENSITY_WATER_ALLOCATION_PROTOCOL_TEMPLATE_V1.json`: all numerical cutoffs, sample requirements and site/season identifiers `REQUIRED_BEFORE_USE`.
- `scripts/audit_pedicularis_density_water_allocation.py`: exact source CSV/JSON/B0 method SHA256-bound and no-overwrite report with `DENSITY_WATER_ALLOCATION_HOLD` or `DENSITY_STRATIFIED_WATER_ALLOCATION_SUPPORTED_NOT_EFFECT`.
- `tests/test_pedicularis_density_water_allocation.py`: synthetic method/allocation witnesses only.

CLI (after a real matching B0 pilot and prospective frozen design):

```bash
python scripts/audit_pedicularis_density_water_allocation.py \
  --allocation /path/to/actual-plant-patch-assignments.csv \
  --protocol /path/to/frozen-protocol.json \
  --b0-method-receipt /path/to/verified-B0-method-receipt.json \
  --out /path/to/density-water-design-audit.json
```

**CURRENT EMPIRICAL RESULT: none.** There is no real joint density × validated water × predator behaviour × seed dataset in this repository. Positive design status is not confirmation of water fitness benefit, effect modification, causal density, or BALANCE architecture value.

## Sources

- Xia J, Sun S-G, Liu G-H (2013) *Biology Letters*. DOI https://doi.org/10.1098/rsbl.2013.0387
- Sun S-G & Huang S-Q (2015) *AoB PLANTS*. DOI https://doi.org/10.1093/aobpla/plv019
- Sun S-G, Armbruster WS & Huang S-Q (2016) *Annals of Botany*. DOI https://doi.org/10.1093/aob/mcw097
- `docs/PEDICULARIS_WATER_PERFORATION_IDENTIFICATION_AUDIT_V1.md`
- `docs/PEDICULARIS_PARTIAL_MODULARITY_EXPOSURE_GEOMETRY_V1.md`

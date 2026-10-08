# Pedicularis: partially modular bract defence and residual geometric coupling

Status: PROSPECTIVE MEASUREMENT / NO NEW FIELD DATA / NO ECOLOGICAL EFFECT  
Owners: BALANCE functional-state measurement support only; SCH identifies conflict, SLK owns structural architecture-value and transport, BITA asks which mechanism selective manipulations identify.

## Why this is a better question than another selection-gradient sign

Sun & Huang (2015), *AoB PLANTS* DOI 10.1093/aobpla/plv019, experimentally drained *P. rex* bracts (by physical puncture) and observed more seed predation, with no detectable pollinator/nectar-robber visitation difference. The experiment changes water and bract integrity simultaneously and **does not** isolate a water-only causal effect. Sun et al. (2016), *Annals of Botany*, DOI 10.1093/aob/mcw097, found that floral exsertion was associated with both pollinator-related pollen receipt and seed-predation risk across populations. These observations are **already published**, not newly discovered by this repository.

The 2016 exsertion variable is a **morphological composite**, not a direct measurement of tissue accessible to a predator:

```
relative_exsertion = (flower_length - bract_height) / flower_length
```

Two anatomically distinct organs (corolla and cupulate bract) contribute to this ratio. The waterline is a further independently varying **state** of the existing bract structure. The original exsertion ratio alone cannot reconstruct exposure of a particular oviposition target to water, because one must also know where that target lies and the contemporaneous water height.

This is a simple measurement-identifiability statement, **not a novel mathematical theorem**. The testable ecological hypothesis is whether the extra measured axis predicts specific predator behaviours or improves held-out prediction beyond published exsertion and floral size under verified water manipulation.

## Existing source data cannot substitute for the new exposure axis

The 2016 field study reported six floral and six vegetative traits, including flower length and cupulate-bract height. Its Supplementary Appendix S1 contains population trait means and standard errors. The study quantified pollen receipt and seed components, but the described morphology protocol does not supply matched **water-surface elevations and directly verified oviposition-site elevations at a known time**. Furthermore, trait/seed outcomes were linked at the same plant level in seven populations; labels were lost for five other seed-predation populations, so those populations contributed to between-population summaries rather than plant-level trait–fitness mediation. These are important limits to retrospective causal reconstruction (Sun, Armbruster & Huang 2016, DOI 10.1093/aob/mcw097, Methods/Appendix S1).

Therefore, this protocol does **not** compute a previously unpublished "waterline barrier effect" from the existing 2016 summary coefficients. The new site-to-waterline axis and independent replicated manipulation must actually be measured.

## Two separately measured coordinates

Use a *common instrument-calibrated vertical datum*, not a mixture of along-corolla lengths and projected elevations:

1. `E_length = (flower_length_mm-bract_height_mm)/flower_length_mm`. This matches the published **length-based** exsertion convention.
2. `C_site = oviposition_site_elevation_mm-water_surface_elevation_mm`. This is the directly measured **vertical clearance of an independently verified oviposition site**.
3. `C_pollinator = flower_tip_elevation_mm-bract_rim_elevation_mm`. This is direct **vertical flower-tip clearance** above the rim (not necessarily equivalent to mechanical pollinator accessibility).

These are distinct quantities. The plant's bract rim, water surface and flower can be tilted or morphologically curved. Do **not** infer `water_surface_elevation_mm` by subtracting cup depth from corolla length or use `E_length` as a proxy for `C_site`. Direct measurement/reconstruction must share a reference datum, calibrated camera/calliper position and declared error bounds.

For an individual site elevation `s` and water elevation `w`, `s-w=0` is a **geometric boundary**, not a biological threshold proven to prevent oviposition. With maximum elevation uncertainty ±u at each endpoint, clearances within ±2u must remain `WATERLINE_BOUNDARY_UNRESOLVED`. Even confidently submerged tissue is **not** assumed protected until predator behaviour is measured.

## Falsifiable ecological alternatives

| Registered alternative | Adult approach rate | Egg deposition / observed insertion at fixed approach effort | Larval establishment given verified egg deposition |
|---|---|---|---|
| H_access: exposed-tissue barrier | No required difference | May increase sharply as `C_site` crosses 0, conditional on taxon and real reachable target | No required difference |
| H_cue: water-dependent orientation | Changes with water/cues even at otherwise matched geometry where feasible | Changes may track altered approach, rather than contact with target tissue | No required difference |
| H_post: post-oviposition protection | No required difference | No required difference | Establishment/damage changes after deposition |
| H_mixed | More than one pathway changes | More than one pathway changes | Potential interaction |

Do not infer any of these mechanisms solely from `C_site` or a model fit to final seed counts. Attempted entry, verified deposition and larval establishment are separate observation protocols; failures to identify eggs/larvae must not be replaced by assumed zeros. Predator guild identity (Diptera vs Lepidoptera) must be recorded when independently justified, not inferred from one generic egg-count coefficient.

**Key within-context prediction:** require directly measured water-surface movement **and** unchanged flower length, bract size/rim, flower-tip elevation and verified target-site elevation within a separately frozen morphology-drift tolerance. A clearance shift caused solely by flower growth or displacement is **not** a waterline manipulation and cannot qualify as a waterline contrast. When *the same flower* retains essentially unchanged `E_length` but water level shifts enough to change `C_site`, a physical-barrier hypothesis predicts a corresponding shift in deposition success *under comparable predator encounter and oviposition opportunity*. If no shift occurs despite validated access variation and adequate power, the simplistic clearance barrier is challenged. Repeated observations of the same flower do not constitute independent randomized plants.

An adult cue hypothesis is not excluded by a positive clearance effect unless cues are independently controlled; a regression coefficient is not an allocated causal pathway.

## Design-support modes and their different nulls

**Important limitation of the first software version:** the `n_contrasting_whorls` PASS criterion is deliberately a **same-flower repeated-geometry** contrast. It asks whether a flower's waterline changed substantially while its morphology stayed stable. That can be observed during nonexperimental rainfall variation or deliberate within-flower water adjustment, but **does not** establish a causal effect: flower age, weather and predator availability change with time.

A stable randomized B0 **between-plant** treatment design may maintain constant wet/dry states through the entire observation period. Such an experiment could be perfectly implemented yet have **zero within-flower waterline contrasts**. Its `EXPOSURE_GEOMETRY_SUPPORT_HOLD` therefore must not be interpreted as a B0 method failure or as absence of cross-arm water exposure; B0 has its separate arm/state qualification contract. A future between-arm predictor-outcome analysis needs plant-level randomization/block IDs and overlap of the morphology predictor across independently assigned arms, rather than manufacturing same-flower water variation.

The `assigned_water_arm` field is retained as provenance/consistency metadata only; version 1 computes **no** between-arm fitness, behavioural effect or causal interpretation. No status in this geometry route overrides the B0 pilot receipt.

## Unit of analysis and genuine identification

- One bract/whorl forms a shared water compartment: all flowers occupying it have the **same water state** at a time point and are not independent water-treatment replicates.
- One plant is the conservative first-stage treatment randomization unit (B0). A later hierarchical design can include repeated whorls/flowers but must declare dependence and hydrological spillover.
- `flower_id × observation_time_id` indexes repeated geometry measurements; unique plants/whorls, **not** repeated timepoints/flowers, define replication for water-treatment effects.
- Geometry-only audits are deliberately performed blind to egg counts, pollen loads and seeds, and cannot estimate a treatment effect.
- Method-qualified B0 water-versus-handling arms remain prerequisite for causal interpretation; `B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL` itself is not a biological effect.
- Observational rainfall-induced water fluctuations are useful for design support, but time of day, flower age and predator activity confound naive before/after interpretation.

## New exact-schema measurement route

```text
data/PEDICULARIS_EXPOSURE_GEOMETRY_FIELD_TEMPLATE_V1.csv
data/PEDICULARIS_EXPOSURE_GEOMETRY_PROTOCOL_TEMPLATE_V1.json
balance_domain/pedicularis_exposure_geometry.py
scripts/audit_pedicularis_exposure_geometry.py
tests/test_pedicularis_exposure_geometry.py
```

Every numeric field threshold in the template is `REQUIRED_BEFORE_USE`, and all observed positions must be collected with calibrated *shared* elevation datum. A source SHA256-bound JSON receipt audits calibration, direct verification of the target tissue, treatment-arm consistency, shared-whorl waterline agreement, and **whether enough independent plants have same-exsertion/different-clearance contrasts**. It does not fit or inspect biological outcomes. A geometrical `PASS` never identifies a predator mechanism.

Prospective design thresholds should be justified by instrument measurement error, expected field manipulation range and minimally useful waterline separation; never tune them after seeing attack rates. Exact data/protocol source hashes are recorded by the CLI.

## Implication for the BALANCE programme

*Pedicularis* **already has two distinct organs**: a corolla mediating pollinator presentation and a water-bearing bract potentially protecting floral reproductive tissue. Its conflict therefore exemplifies **residual functional coupling despite existing anatomical modules**. That is potentially interesting but is *not equivalent* to the absence of structural division of labour.

The B0/below-waterline programme can test how a partly modular morphology fails to remove a spatially shared vulnerability; it cannot directly compare an undifferentiated ancestor to a novel differentiated architecture. For a true **structural-architecture BALANCE** receipt, separately define a feasible same-context structural alternative, its development/maintenance costs, the shared comparator and independently optimized fitness on a common scale, in addition to a positive SCH conflict receipt. Water refill/drainage or a hole in the bract are **functional-state interventions**, never surrogate costs `K` or historical transitions.

## Existing evidence and status
- Sun & Huang 2015 DOI: https://doi.org/10.1093/aobpla/plv019
- Geographic conflict study 2016 DOI: https://doi.org/10.1093/aob/mcw097
- B0 source-method protocol: `docs/PEDICULARIS_WATER_PERFORATION_IDENTIFICATION_AUDIT_V1.md`
- STATUS: **testable geometry hypothesis and input/QA software only; no field geometry or oviposition observations and no statistical test**.

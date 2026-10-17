# Dalechampia: identify bract-to-seed carbon source without conflating labelled fruit gas

**Status: prospective isotope-compartment methodology and executable source-discrimination SCREEN. There are zero real Dalechampia isotope observations, tracer-calibration records, maturity-fitness measurements or net structural BALANCE worldline receipts in this project.**

## The next nontrivial biological question

A pollinator-attracting *Dalechampia scandens* bract closes and turns green after fertilization. It is photosynthetically active at this late stage, but does any of the *bract-fixed carbon* actually reach the seeds? The original Pélabon et al. 2015 (DOI https://doi.org/10.1111/1365-2435.12427) hand-pollinated study measured early seed masses under whole-blossom foil and bract removal, not under a selectively isolated bract photosynthetic perturbation. Its separately assayed green bracts showed increased net photosynthetic potential, not the carbon-to-seed path.

A seed enriched in 13C after nearby enriched CO2 exposure can arise from at least three pathways:

- **desired**: bract photosynthesis and subsequent plant internal carbon transport to the seed;
- **confounder**: leaked enriched headspace gas photosynthesized directly by enclosing fruit or other tissues, then reaching the seed;
- **confounder**: ambient labelled gas leaking to nearby photosynthetic organs/other plants, followed by re-fixation and translocation.

A positive seed atom-% excess by itself therefore cannot distinguish the organ of assimilation. A static labelled chamber without non-target exposure controls does not solve this.

### Original methods and why leakage matters

Selective leaf-labelling cuvettes have been used in carbon transport work (e.g., [Kölling et al., Plant Methods 2013](https://doi.org/10.1186/1746-4811-9-45)), where a deliberately induced cuvette leak produces measurable background uptake in previously untargeted tissue. These are methodological precedents, **not evidence that a localized chamber is already feasible on closed Dalechampia bracts**. A strawberry source-leaf tracer study also illustrates the importance of keeping a distinct source tissue isolated while detecting later fruit sink enrichment ([Miyazaki et al., 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6338039/)). Carbon label atom fraction changes as newly assimilated labelled molecules are diluted with preexisting carbon ([13CO2 pulse-chase pathways review](https://pmc.ncbi.nlm.nih.gov/articles/PMC5041120/)). These sources do not supply any Dalechampia-specific leakage tolerance or expected seed isotope response.

## Independent randomized blocks: the central design correction

**Use separate maternal plants for every isotope-source arm.** In contrast to the Stage-0 optical manipulation (where two blossoms on one mother can be *measured* without applying a carbon tracer), isotope-labeled photoassimilates can move through a maternal plant to other blossoms. An unlabelled control flower sharing that maternal vascular system may already contain carbon from the treated labelled flower.

Therefore an isotope-assay randomization block has **three distinct maternal plants**, each with one registered blossom:

| Arm | Label delivery | Necessary question |
| --- | --- | --- |
| SHAM_UNLABELLED | Same chamber, handling and atmosphere but no enriched CO2 | What isotope background does an unlabeled seed/bract have at the same developmental stage? |
| BRACT_13CO2_PULSE | A bract-local enriched source chamber; simultaneously monitor fruit and ambient gas | Is bract tissue actually labelled, and are seeds labelled above background without excessive off-target exposure? |
| FRUIT_LEAK_MIMIC | No bract source pulse; expose the fruit compartment to a **controlled, at-least-worst-case** version of measured fruit headspace leak exposure | Could direct fruit uptake of the leaked gas explain the seed signal? |

Randomize *whole independent maternal plants*, in stage- and greenhouse-context-matched blocks; do not silently treat seeds from an individual plant as independent randomized blocks. One sampled developing-seed tissue preparation per treated maternal plant is the screen's unit. Additional biological replication and longitudinal destructive timepoints require a later versioned, properly powered analytical plan. Stage-matched, pretreatment plant backgrounds are measured; they are not inferred from a universal 1.1% natural abundance constant.

**External requirements not verified by the code:** a true dated pre-outcome randomization, chamber gas-tightness and calibration, comparable light/temperature/CO2 across treatments, isolation of nearby plants from airborne tracer, tissue sample independence and lack of cross-plant tracer spillover. A hash of a data file is a reproducibility fingerprint, not proof of the timestamp of its preregistration or the quality of a physical calibration.

## What the executable source screen actually calculates

For each source block and tissue define apparent atom percent excess (APE) as

\[
\mathrm{APE}_{tissue,arm} = ^{13}C\text{ atom-%}_{\mathrm{post}}
- ^{13}C\text{ atom-%}_{\mathrm{pretreatment\ matched\ baseline}}.
\]

The source-screen requires all of the following, under **external, pre-outcome** instrument thresholds:

1. Source bract gas exposure and labelled **bract tissue APE** exceed the sham plus a prespecified positive assay detection floor (including analytical SD).
2. The measured *fruit* enriched-gas exposure time integral in the bract-pulse arm is small relative to that within the source chamber.
3. The **FRUIT_LEAK_MIMIC** fruit headspace enriched-gas exposure is positive and at least a prospectively specified multiple of the actually monitored leak exposure in the bract-pulse arm; mock bract headspace gas cannot itself receive the source label.
4. The bract-pulse seed APE exceeds both **unlabelled sham** and **fruit-leak mimic** seed APE by a positive threshold **and** a calibrated multiple of combined analytical uncertainty.
5. All plants within the randomized block are stage- and chase-time-matched, microclimate-matched, damage-free, closure-intact and instrument/laboratory QC-passing, with no flagged ambient chamber contamination.
6. Every pre-registered block supplies three **different maternal plants**, no two arms from the same plant, and at least the declared minimum independently randomized blocks are available. No failed blocks may be dropped after viewing seed isotope outcomes.

The screen uses gas exposure **atom-percent excess × time** as an *exposure proxy*, not a flux of labelled carbon entering fruit. Even if the fruit leak mimic has a larger exposure integral, monotonic or quantitatively comparable fruit CO2 assimilation is **not proven by those integrals**. This is a decisive limitation: an assay SCREEN PASS is not a finished carbon-transfer causal inference.

The screen compares each contrast against a pre-frozen positive threshold and **analytical** measurement uncertainty. It does **not** compute biological confidence intervals from the independent plants, isotope mixing fractions, tracer mass-balance, carbon contribution to seeds or any treatment effect on mature seed viability. A subsequent source-isotope inference must estimate biological variation across blocks and demonstrate uptake-comparability and gas exposure calibration independently.

### Why no "carbon percentage supplied by bracts" number is estimated

A seed atom-% excess is a tracer **concentration**, not a mass of carbon imported from a specific organ. Deriving source carbon contributions would require the amount of 13C assimilated in bract tissue, source enrichment over time, carbon pool masses in seed/fruit, chase loss/dilution, respiration and a validated multi-source mixing model. Neither an isotope atom ratio nor headspace gas exposure AUC identifies those quantities automatically.

## Fail-closed implementation

- balance_domain/dalechampia_tracer_source.py validates strict three-arm, three-independent-mother blocks, unambiguous assay fields, calibrated source/mimic gas exposure, seed/bract pretreatment references, analytical SD, physical stage controls and gross ambient contamination.
- data/DALECHAMPIA_BRACT_13C_CALIBRATION_TEMPLATE_V1.json is **intentionally NOT_FROZEN** with invalid threshold placeholders; it cannot produce a spurious positive. Users must obtain actual chamber and isotope-laboratory calibration and externally freeze it before processing future measurements.
- data/DALECHAMPIA_BRACT_13C_MEASUREMENTS_TEMPLATE_V1.csv contains one row per independent randomized plant and no seed fitness outcomes.
- scripts/evaluate_dalechampia_bract_13c_source.py produces source-JSON and isotope-CSV SHA256 hashes, never overwrites a previous receipt and returns either SOURCE_ATTRIBUTION_HOLD or COMPARTMENT_SOURCE_SIGNATURE_SCREEN_PASSED_NOT_CAUSAL_FITNESS.
- tests/test_dalechampia_tracer_source.py contains synthetic **false-positive controls**: same-plant sham, target seed enrichment explained by leak mimic, excessive direct fruit leakage, mock also labeling the bract, uncalibrated instrument variation, postlabel stage mismatch, closed bract injury, unstable chamber atmosphere, incomplete blocks and biological outcome contamination. These are artificial tests, **not real isotope results**.

Only with a prospectively frozen real calibration and measured valid assay:
    python scripts/evaluate_dalechampia_bract_13c_source.py --calibration calibrated_pre_outcome_contract.json --isotope-measurements stage_matched_tracer_measurements.csv --out new_source_screen_receipt.json

The published original 2015 dataset contains no such 13CO2 tracer observations, and the executable screen has **not** been run on any real new plant measurements. A positive screening signal would at best justify independent source attribution and isotope recovery validation, not the immediate publication claim that carbon source or organ retention is settled.

## Hierarchy of publishable scientific hypotheses

**C1: localized carbon transport.** Bract-fixed carbon reaches developing seeds, above any signal explainable by directly exposed fruit gas and ambient leak. To establish it, validate true source gas isolation and use a blocked population-level isotope/mass-balance analysis, not just the per-block software SCREEN.

**C2: fitness advantage of temporal reuse.** Independently validated *bract-local photosynthesis inhibition*, with unchanged fruit light/CO2, bract integrity and microclimate, causes a reduction in mature viable seeds (and where appropriate germination). This is a separate randomized outcome study; finding transported carbon is not enough.

**C3: structural BALANCE.** Distinct net integrated and differentiated floral architectures are accessible in the same biological context, with independently identified conflict L, common net fitness and joint uncertainty. Neither C1 nor C2 establishes C3.

**The immediate scientific bottleneck is physical source isolation**, not a new algebraic identity or an additional retrospective reanalysis of 2015 seed AIC. Verify the optical treatment feasibility and independent carbon source tracer contamination before investing in a large reproductive trial.

This programme continues the [Stage-0 optical gate](DALECHAMPIA_BRACT_CARBON_ISOLATION_FIELD_PROGRAMME_V1.md) and is tracked by [issue 239](https://github.com/zuizui0223/balance/issues/239). Existing natural phenotypic study cohorts are not recounted as independent replicates.

# Same species, different conflict: a source-defined plant review contrast

**STATUS:** source-screened original-review coverage, NOT independent dual-coder adjudication, evolutionary transition inference, natural prevalence, or direct structural BALANCE worldline identification.

## Ecological question

**Is functional conflict a fixed property of the flower/species, or does it depend on which two functions, organs and ecological conditions are measured?**

The existing BALANCE programme has two independent, explicitly defined flower-literature screening frames:
- U1: [Haas & Lortie 2020, PeerJ](https://doi.org/10.7717/peerj.9049), 47 plant taxa in a broad review of *herbivory effects mediated by pollination*. Frozen source-screen rows U1_001–U1_047;
- U2: sexual interference review frame, [Barrett 2002](https://doi.org/10.1038/sj.hdy.6800020), 22 species/dependency groups in male/female reproductive interference, with independently source-resolved original-screen rows U2_001–U2_022.

The datasets were **not sampled from the same species universe**. U1 explores damage, herbivore/pollinator interactions and plant reproductive consequences; U2 purposely explores male-female conflict mechanisms. Directly comparing 0/47 to 8/22 as a general risk ratio, conducting an inter-review Fisher test, or interpreting the fractions as flowering-plant prevalence would be invalid.

## New cross-frame result from the original source-screen ledgers

| Frozen source-screen property | U1 damage–pollination review | U2 male–female interference review |
|---|---:|---:|
| Reviewed species/taxon records | 47 | 22 |
| Positive shared-coordinate conflict under the relevant source study | 0 | 8 |
| No demonstrated direct conflict | 46 | 14 |
| Aligned, no measured conflict | 1 | 0 |
| Independently double-adjudicated? | **No** | **No** |

Records across frames = 69; only **67 distinct recorded dependency groups**, because exactly two species occur in both review screens. These dependency groups are **not** interchangeable independent phylogenetic replications.

### The two within-species cross-frame comparisons

**Mimulus aurantiacus** (currently also treated taxonomically in the monkeyflower complex):
- U1 species record U1_031: floral damage in the registered source did **not** reproduce the observed visit-frequency association as a causal effect; no shared herbivore–pollinator preferred-state tradeoff was identified. Original experiment: [Tsuji et al. 2016, AoB PLANTS](https://doi.org/10.1093/aobpla/plw036).
- U2 species record U2_006: closing the touch-sensitive stigma relieves female-organ physical interference with male pollen export; the experiment demonstrated a functional benefit of stigma closure for the male function rather than a large reduction in within-flower selfing. Original experiment: [Fetscher 2001, Proceedings B](https://doi.org/10.1098/rspb.2000.1395). U2 architecture: **SPATIAL_SEPARATION**, with no source-licensed evidence of structural duplication.
- These are **different studies** of different functional pairs and morphological traits in different contexts, not the same flower switching from no conflict to conflict over time.

**Ipomopsis aggregata**:
- U1 U1_025: herbivory/compensation is linked to reproductive ecology but does **not** identify two opposing optima on one herbivore–pollinator plant trait axis in its source design.
- U2 U2_021: self-pollen versus compatible outcross reproductive function is a **positive interference conflict** under the source screen; experiments find reduced outcross fertility/seed set after mixed self and cross pollen (see [Waser & Price 1991, American Journal of Botany](https://doi.org/10.1002/j.1537-2197.1991.tb14511.x)). Its U2 architecture is classified as **SHARED_INTEGRATED**; a causal differentiated alternative is not demonstrated in that cited study.
- Thus neither a label of “conflicted species” nor “conflict-free species” is justified without naming the functional pair and tested coordinate.

**Inference supported:** evidence for functional conflict depends on which function pair, plant trait and source experiment were observed. Both same-species mismatches survive review-record deduplication because they are *genuinely different biological questions*. A U1 value of **NO_DEMONSTRATED_CONFLICT is NOT a proof that the conflict is absent**.

### Conditional architecture in the U2 direct-conflict subset

Among the eight source-screened U2 conflict-positive species:

| Observed reproductive organization | Species records |
| --- | ---: |
| **SHARED_INTEGRATED** | **4** |
| **NONSTRUCTURAL_SEPARATION** (temporal / spatial / both) | **3** |
| **POLYMORPHIC_OR_MOSAIC** / mixed | **1** |
| **STRUCTURAL_MODULE_DIVISION** | **0** |

Four studies thus register experimentally established functional interference while the characterized architecture remains shared; another three display **temporal/spatial resolution without a separately differentiated structural module**. This is a biologically important illustration of the distinction between **conflict**, **functional relief** and **structural duplication/division**. Yet the positive subset is intentionally mechanism-selected and *SCREENED*, not a confirmatory sample of all flowering plants or a historical evolutionary transition test.

The inverse proxy mistake is visible in U2 as well: **9 of the 14 NO_DEMONSTRATED_CONFLICT records have conspicuous polymorphic/mosaic architectures** (e.g. stigma-height morphs, heterostyly/enantiostyly); their original cited designs did not demonstrate the registered sexual-interference mechanism. Complex reproductive morphology therefore cannot be treated as proof that measurable antagonistic selection occurred.

## What the result contributes to BALANCE

The original strict BALANCE hypothesis distinguishes:
1. independently identified **positive conflict on a defined shared coordinate** (SCH);
2. observed **functional use/routing/structural mode**, a distinct descriptive variable;
3. **same-context net architectural fitness** of a viable differentiated alternative compared with a shared one (strict BALANCE).

The source-screen result robustly warns against replacing any of these by a species-level binary “conflict present” or by a morphological proxy. It supplies an ecological observation about the **scale of functional-conflict specificity**, not a numerical Phi/K/xi/dB parameter or a direct structural BALANCE certificate.

No original U1/U2 rows were changed, no new independent biological cluster was added, and the cross-frame cases are not counted as four independent species.

## Prospectively testable next biological experiment

**Question:** *In Mimulus aurantiacus, does floral damage modify the independently demonstrated male–female mechanical interference, and are those effects separable from visitation?*

The cross-review studies cannot answer it because the U1 and U2 experiments were not coordinated. One plausible prospectively randomized **same-population, same-season** factorial trial would manipulate:
- standardized flower petal damage versus sham;
- transient closure-capable stigma versus independently controlled, physically held-open/closure-perturbed stigma, with adequate handling controls.

On the same randomized flowers/recipient arrays, measure pollen export (male fitness component), deposition, visitation and mature viable seed success (female component) with the maternal plant and flower ID retained. Design the factorial interaction test **before** looking at outcomes and include a sham distinguishing stigma manipulation damage from closure function. The sign of the damage × stigma interaction is **unknown**; neither prior null florivory visitation nor positive stigma-interference studies fix it.

This is a test of **external antagonist context × internal sexual interference** in one species. Even a strong interaction does not by itself identify a more profitable structural alternative or BALANCE occupancy.

## Reproducibility and limits

Code: balance_domain/plant_cross_frame_conflict.py, scripts/audit_plant_cross_frame_conflict.py, tests/test_plant_cross_frame_conflict.py.

The readout uses the **complete** source-screen universe, not only the two interesting species: U1 first 20 + 27 production screens and U2 conflict 22 + corresponding architecture 22. It requires an exact primary-source dependency join, explicitly permits only the documented Todd (1882) Cassia/Chamaecrista naming annotation, checks architecture-state frequencies and never promotes U2 SCREENED rows to ADJUDICATED status. A script-generated receipt includes SHA256 of each original file, with no additional source data inferred.

Run source readout:

    python scripts/audit_plant_cross_frame_conflict.py --out /path/to/new_review_cross_frame_receipt.json

**Important:** this is a new source-level ecological synthesis **within two original published review universes**, not a fresh independently collected outcome-blind cross-flora database or universal meta-analysis. To estimate how often these patterns occur, the next step remains a genuinely prospective, outcome-blind function-pair sampling frame and independent double-coding of the original screens.

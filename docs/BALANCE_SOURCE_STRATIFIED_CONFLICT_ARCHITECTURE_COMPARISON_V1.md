# Real source-stratified conflict–architecture comparison V1

**Source data:** tracked primary-source screening ledgers, not newly collected organisms, new experiments, a random species frame, a V4 confirmatory model, or a meta-analysis. Date: 2026-10-19.

## Main scientific question

Do the data support the causal claim that functional conflicts generated *new structural modules*, or are there independently observable counterexamples in which verified conflict remains shared and morphology is complex without demonstrated conflict?

The current sources support the second, narrower observation. They do **not** establish either a universal conflict-to-module effect or a historic evolutionary transition.

## Sources and independence

1. **U2 Barrett sexual-interference review:** [22 source-screened species](../data/BALANCE_PLANT_U2_SCREENING_V1.csv). One species/dependency group per row; source-selected for male–female interference topics. `NO_DEMONSTRATED_CONFLICT` means **no direct evidence from the registered experiment**, not an ecological zero.
2. **PLANT_PILOT_V1:** [29 source-screened species/context rows](../data/BALANCE_PLANT_MACRO_PILOT_V1.csv), **28 dependency groups**. Includes intentionally selected functional-conflict and morphology examples; *Dalechampia scandens* contributes two contexts. Some source groups are multispecies exemplars (e.g. Senna), not new species-level independent replications. It is not exchangeable with U2.
3. **U3 heteranthery matched controls:** source-adjudicated four pairs, reported here as a separate existing result ([U3 matched readout](BALANCE_PLANT_U3_MATCHED_EXTRACTION_DIAGNOSTIC_V6.md)); *not* imported into the two-source computation.

The [script](../scripts/audit_source_stratified_trait_architecture.py) independently reads the exact **U2 and PILOT source records** and produces separate frame counts and SHA256 hashes. It explicitly forbids pooling the two selected frames or opening the independent U2/U6 confirmatory architecture outcomes.

## Result A: Direct functional conflict is common with retained shared architecture

U2 conflict-positive review-source subset **8/22 source rows**. Of the eight source-positive systems:

| Observed architecture | Number |
| --- | ---: |
| Shared, integrated | **4** |
| Temporal and/or spatial separation, not structural module division | **3** |
| Morphological polymorphism/mosaic | **1** |
| Independently confirmed structural-module division | **0** |

The structural-status field for these eight is **seven `false`, one `unresolved`, zero `true`**: "0 confirmed" is **not** "structural modules experimentally disproved in all eight." The source reviews are rich in male–female interference and therefore cannot establish population prevalence.

Leaving the one unknown structural status unconstrained gives a **record-level logical interval of 0–1 structurally divided candidates among these eight source-positive U2 rows**. This is not a population interval, confidence interval, or evidence of a missed causal origin.

## Result B: Architecture complexity does not identify the opposing-demand cause

In the remaining **14 U2 records labelled `NO_DEMONSTRATED_CONFLICT`**:

| Architecture | Number |
| --- | ---: |
| Polymorphic/mosaic | **9** |
| Temporal or spatial separation | **2** |
| Architecture unresolved | **3** |

This is a strong **evidence-identification counterexample** to using complex floral morphology as a proxy for a source-demonstrated measured trade-off. It is **not** evidence that those eleven morphologically complex systems lack any conflict in nature.

Compare the source-screen identification rates only as descriptions of this selected literature universe: U2 has four shared architectures among the eight positives but zero coded shared among the 14 non-demonstrated (three of which have unresolved architecture). This inverse-looking pattern cannot be interpreted as a protective effect of shared architecture; study selection, source measurement, differing function pairs, and missingness are plausible generators.

## Result C: Function-pair classes concentrate architecture states inside the selected plant pilot

Among **16 conflict-positive PILOT source rows**:

| Registered conflict family | Positive source rows | Confirmed structural division | Other positive architecture |
| --- | ---: | ---: | --- |
| Pollinator–antagonist | **7** | **0** | 7 shared |
| Pollen reward–gamete transfer | **3** | **3** | 0 |
| Sexual interference | **5** | **1** | 4 nonstructural/mosaic |
| Pollinator–prey | **1** | **0** | 1 spatial separation |
| **Total (selected PILOT rows only)** | **16** | **4** | **12** |

Across all sixteen positive PILOT rows, structural-status receipts are **four `true`, ten `false`, two `unresolved`**. The source-record logical interval is therefore **4–6 of 16**, not a forced point prevalence estimate. In this selected PILOT, all seven positive pollinator–antagonist rows have explicitly nonstructural states, while all three pollen reward–gamete rows have source-coded structural division; the contrast persists under the missing-status envelope but remains inseparable from the way studies entered the pilot.

These apparent **7/7 versus 3/3 contrasts are *not* an unbiased comparison**. The Pollen reward–gamete studies were identified partly because division-of-labour morphologies were of interest, while pollinator–antagonist cases intentionally sampled integrated floral traits. Morphology and source ascertainment are inseparable. The correct biological interpretation is a **candidate function-pair-specific architectural pattern**, not a fitted evolutionary law, odds ratio or population-level difference.

In particular, an unqualified "4 of 16 positives are structural" discards the ecological function pair and renders the ratio non-generalizable. The exact sample cases can inform **prospective, outcome-blind sampling** only.

## Result D: Species-name joins can construct false architecture transitions

Exact `dependency_group` joins between the two independent frames yield **three** overlaps:

| Exact shared group | U2 primary source | PILOT primary source | Why a species-level label would mislead |
| --- | --- | --- | --- |
| *Polemonium viscosum* | Galen et al. 1989: **POSITIVE**, temporal + spatial pollen/stigma separation | Galen & Cuba 2001: **POSITIVE**, integrated corolla under bee attraction versus ant predation | Two **different function pairs and tissue coordinates**; not a transition within a common evolutionary axis |
| *Narcissus assoanus* | Baker et al. 2000: **NO_DEMONSTRATED_CONFLICT**, polymorphism | Cesaro et al. 2004: **POSITIVE**, polymorphism | Different experiments and conflict-identification sensitivity; **not** evidence that a species acquired conflict between 2000 and 2004 |
| *Ipomopsis aggregata* | Waser & Price 1991: **POSITIVE**, shared sexual-interference coordinate | Irwin 2006: **UNRESOLVED**, integrated pollinator–robber coordinate | Different target function pair, with a source-side unresolved status |

A *fourth tempting match* is `Solanum_rostratum_historical` (Todd 1882) versus `Solanum_rostratum` (modern pollen functional-division source). This is intentionally a **held cross-source identity** rather than an automatic name replacement. The initial GloBI pilot already encountered a serious `Solanum rostratum` authorship/homonym conflict, so no history of trait differentiation is inferred from bare names.

Source: [functional-pair multiplex](BALANCE_PLANT_CONFLICT_MULTIPLEX_ECOLOGY_V1.md), [GloBI taxon audit](BALANCE_GLOBI_PUBLIC_INTERACTION_OPPORTUNITY_PILOT_V1.md).

## Result E: Heteranthery has independent matched counterexamples (prior U3 readout)

U3's four PASS-adjudicated heterantherous matched cases were **all conflict-positive**, while **three of four** nonheterantherous matched controls were also conflict-positive and one was unresolved. Conflict presence is therefore **not a deterministic predictor** of heteranthery: the raw matched contrast is bounded **[0, 0.25]**. Routing differs among the positive nonheterantherous controls (*Solanum lycocarpum* among flowers vs *Senna spectabilis* within a flower). These are existing U3 findings, **not newly generated by the U2/PILOT audit**; they do not identify historical origins or a finite binary regression coefficient.

## Updated core predictions; evidence needed next

1. **Shared conflict can persist** — already directly observed as a source-screen pattern; to attribute persistence to high architecture costs, measure feasible structural alternatives and their fitness **on the same scale and ecological context**.
2. **A function pair may constrain *where* biological functions are separated** — candidate U2/PILOT/U3 heterogeneity now documented. Prospectively code anatomical module substrate and timing **without opening observed architecture**. Independently validate positive and negative same-coordinate conflict, then fit an appropriately stratified model.
3. **Conflict causes a new structure to originate** — **not recovered**. Requires historical state ordering, independently replicated transitions or appropriate phylogenetic controls, heritable developmentally feasible paths, direct conflict-dependent net benefit, and explicit comparison with exaptation, ecological filtering and drift.

Under the current [V4 frozen contract](BALANCE_PLANT_CONFIRMATORY_MODEL_FREEZE_V4.md), U2 and U6 architecture coding is still independently adjudication-dependent; these existing U2/PILOT source screens are not added to V4 as independent outcomes. [V4 common-support limits](BALANCE_PLANT_V4_GENERALITY_REACHABILITY_V1.md) remain unchanged.

## Reproduction

```bash
python scripts/audit_source_stratified_trait_architecture.py
pytest -q tests/test_plant_architecture_source_patterns.py
```

The script reads the two versioned CSV source datasets, outputs source-specific hashes and counts, and holds all source status gates. `--out /path/to/new/receipt.json` writes a **new** JSON file only and fails rather than overwrite an existing result. No original datasets, V4 frozen design artifacts or journal manuscripts are modified.

### Claim freeze

**Observed now:** positive functional-conflict sources coexist with shared and nonstructural architectures; structurally complex flowers can lack source-confirmed conflict; the apparent architecture pattern varies by tested function pair and source-selection frame; species-name joining can be ecologically invalid.

**Not observed now:** direct matched structural `W_D^* - W_S^*`, independent architecture-maintenance cost `K`, historical conflict-driven origin of a new module, representative macroevolutionary frequency, or a causal cross-frame architecture coefficient.

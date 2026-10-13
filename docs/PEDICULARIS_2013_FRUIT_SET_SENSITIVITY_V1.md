# Pedicularis rex 2013: exact-source pooled fruit-set ANCOVA sensitivity

**Status: VERIFIED PUBLIC XLSX; FULL-MODEL INTERACTION DISCREPANCY UNRESOLVED; EXPLORATORY ROBUSTNESS ONLY.**

## Question and provenance

Xia, Sun & Liu (2013) Table 1 reports a year-by-density interaction F=0.355 for fruit set, with plant size as a covariate. The original-public-data reproduction fitted year, density, year-by-density and recorded flowers as assumed plant size on 74 fruit/spike observations. It recreated the year, density and size F values at printed precision, but its interaction F=0.080051129.

This post-publication exercise checks whether the small interaction statistic changes when excluding **source-defined denominator-incompatible rows** and in leave-one-spike-out fits. This is not a recreation of original SPSS syntax and is not a preregistered ecological test.

The original published Dryad XLSX is exactly **89,597 bytes**, SHA256 **d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380**; source data DOI 10.5061/dryad.6cv06, version 11193. Every calculation rechecks the exact XLSX source digest, sheet schema, source group support, and frozen source row identities. The archived ZIP wrapper may change bytewise due to repackaging, so its SHA256 is recorded, not assumed stable.

## Observed reproducibility and sensitivity results

| Source-supported sensitivity | Biological rows | Residual df | Density F | Year × density F | 2005 dense minus sparse | 2011 dense minus sparse |
|---|---:|---:|---:|---:|---:|---:|
| Full original fruit sheet | 74 | 69 | 2.945008 | **0.080051** | +5.096609 pp | +7.099334 pp |
| Exclude 4 fruit-set-denominator-incompatible rows | 70 | 65 | 1.559390 | **0.093043** | +3.301488 pp | +5.424453 pp |
| Exclude all 20 nested-denominator-incompatible rows | 54 | 49 | 1.069577 | **0.264726** | +1.963444 pp | +5.910846 pp |

The original printed interaction F is **0.355**; the mismatch remains. Exclusions change the sample size and degrees of freedom and thus **cannot themselves be described as reproducing the paper's fit**. These same-denominator incompatibilities may arise from different observation cohorts or counting definitions and are not proven errors; especially the 20-row restriction is not a neutral missingness correction.

In the full model, the row-level interaction partial eta-squared is **0.001159**. The factor-coding invariance check returned interaction F **0.0800511293741157** with effect coding and **0.0800511293741490** with dummy coding. The response fraction-versus-percentage unit change gave **0.0800511293741154**. Thus these algebraically equivalent choices cannot produce the printed 0.355.

The 74 leave-one-spike-out interaction F values range from **0.0000042309 to 0.4272107113**, median **0.0854772352**. Excel source rows **5, 2, 16, 14, 37** cause the five largest absolute changes when each is omitted. Individual records move the low F statistic, but there is no support for deleting them from the primary model or alleging an original omission.

## Ecological interpretation and strict ceiling

The adjusted density contrasts represent conditional changes in **percentage points of fruit set at the same recorded flower count**, not fitness of independently replicated patches. In 2005 there was only one sparse and one dense patch; 2011 sampled five sparse and six dense patches. The public workbook has no original patch or plant crosswalk. Year also changes location, so the large row-level year F is not a pure time effect. No valid patch-clustered p-values or causal density interventions are identified.

The finding is **computational sensitivity**, not a newly discovered density-dependent biological interaction or demonstration of selection. It neither confirms nor refutes the original ecological Allee interpretation at the proper sampling scale, and does not establish any BALANCE architecture-value difference or water-bract defence mechanism.

What remains necessary: original SPSS commands/output and plant-size definition; independent measured fruit-production counts for the separate fruit-predation ANCOVA; real flower-to-plant-to-patch record linkages. These are preserved in Issue #224.

## Reproduction

The case subsets and prior F receipt are frozen before this source-sensitivity run. Source manifests:
- data/PEDICULARIS_2013_FRUIT_INTEGER_DENOMINATOR_FREEZE_V1.json
- data/PEDICULARIS_2013_FRUIT_SET_ANCOVA_AUDIT_V1.json
- data/PEDICULARIS_2013_FRUIT_SET_SENSITIVITY_V1.json

The source-retrieval and numerical workflow is .github/workflows/pedicularis-2013-fruit-set-sensitivity.yml. The fixed-source audit lives in scripts/audit_pedicularis_2013_ancova_sensitivity.py; independent linear algebra verification in scripts/verify_pedicularis_2013_ancova_sensitivity_numpy.py. A successful workflow means the intended source arithmetic executed, not that the ecological interpretation passed a causal test.

Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC3971674/ ; https://doi.org/10.5061/dryad.6cv06

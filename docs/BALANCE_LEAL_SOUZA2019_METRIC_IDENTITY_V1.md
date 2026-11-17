# Original Souza 2019 primary paper: why Leal 2025 sample 178 is *scent*, not *nectar*

**2026-11-17 / primary-publication JATS + two source-locked meta-analysis archives.**
This identifies a particular original-study-to-meta endpoint and taxonomic discrepancy. It does **not** create an independent biological experiment, recalculate the Leal multivariate phylogenetic model, or establish an evolved BALANCE differentiation benefit.

## Three independently verified public source witnesses

1. Primary paper Souza et al. (2019), *PLOS ONE*, [DOI 10.1371/journal.pone.0225252](https://doi.org/10.1371/journal.pone.0225252), "I've been robbed! – Can changes in floral traits discourage bee pollination?", actual plant species ***Jacaranda caroba***. Source Table 2 [direct table DOI](https://doi.org/10.1371/journal.pone.0225252.t002). Original article [PMC6872153 full-text JATS XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6872153/fullTextXML) SHA256 `73faada0de428ccb4f83420d4e545e77e8cf9768c89f1480d60158aff28e7c55`, source-audited via independent [GitHub Actions run 44088154588](https://github.com/zuizui0223/balance/actions/runs/44088154588).
2. Leal et al. (2025), *Ecology* [10.1002/ecy.70036](https://doi.org/10.1002/ecy.70036), author [original Zenodo record](https://doi.org/10.5281/zenodo.14773082) ZIP SHA256 `3f6e9b5b55ad8090f41f62faeb2f306c6700a9beb274ac6467106ebab9573c2d`. Original nested CSV (267 effects) SHA256 `4ecd656251f778189d8c13f3608ba99f4de942656fecfe6f2edc8d2509a3d2cb`.
3. Zhong et al. (2025), *Plant Diversity* [10.1016/j.pld.2024.12.004](https://doi.org/10.1016/j.pld.2024.12.004), [original Figshare share](https://figshare.com/s/99df84fe5c473dc85d85). Original 776-effect XLSX SHA256 `6554409f22b09156ee1c2a35ee2547eb5ae28c4a25934b9c639d8a19ea7fe9b4`.

## What the original primary Table 2 actually measures

| PLOS original 2019 Table 2 | Intact control WITH nectar | Artificially slit/damaged flower WITH nectar |
|---|---:|---:|
| Mean total floral scent emitted (ng/h) | **29.90** | **58.24** |
| SD (ng/h) | **22.48** | **11.39** |
| Number of sampled flowers | **2** | **3** |

**Neither group is a flower with nectar removed.** The comparison is **corolla slit/damage vs intact**, using the source's total volatile-organic-compound emission, NOT nectar volume. The original study *also* studied nectar in a distinct experiment and reported nectar as the median 0.9 μL robbed and 4.6 μL non-visited. Those actual nectar medians are **not** the 29.90/58.24 scent means. Do not substitute medians as group means.

Leal's source row **sample 178**, labeled *Jacaranda rugosa* and metric **nectar**, contains the 2019 **J. caroba scent** numbers in misleading group columns: archived larcenist mean 29.90 (actually intact control), archived control mean 58.24 (actually artificially damaged), while SD columns 11.39 / 22.48 are assigned in the **opposite** (original damaged / original control) order.

The archived effect value `yi = +0.666713923` **equals** the correct *scent damaged/intact* mean ratio `ln(58.24/29.90)`, and its archived variance `vi = 0.295380506` agrees with the published *scent* standard deviations:

`vi = (11.39/58.24)^2/3 + (22.48/29.90)^2/2 = 0.29538050594`.

Thus the earlier opposite-sign `yi` and swapped-`SD` anomaly for sample 178 is not simply a mysterious numerical sign error: **the published effect points in the direction of the original artificial-damage scent comparison**, while the archived treatment means/SD and endpoint/taxon labels do not faithfully identify it. This does NOT validate scent as a nectar effect; original 2019 scent experiment was small and not a measured pollinator/seed fitness effect.

## Distinguish two 2019/2007 studies and two different endpoints in Zhong

The independently published Zhong original workbook contains:
- **effect ID 508**, ref 136, ***Jacaranda caroba***, title exactly Souza et al. (2019) primary paper, endpoint **nectar volume** (lnRR −1.30427). Thus the *same primary 2019 paper* contains an actual nectar result *separate* from Leal's scent source number.
- **effect ID 510**, ref 42, ***Jacaranda rugosa***, title **Milet-Pinheiro et al. 2007/2009** "Pollination in Jacaranda rugosa..." — **a different primary source**, not the Souza 2019 paper.

The last cross-meta overlap report had 45 provisional surname–year–plant candidates plus two primary-DOI-recovered taxon cases (Fumero and Gélvez) = at least 47 candidate paper×species links. Correcting the primary identity of Souza 2019 adds **one further candidate** (≥48). These are **candidate primary publications**; they are *not* 48 DOI/contrast-verified effect pairs or independent ecosystem experiments.

## Sensitivity: REMOVE the one misclassified scent record (do not alter the original archive)

Leal's original `Robbers × nectar` label contains **39 effect records / 23 primary study IDs**; removing **sample 178** reduces it to **38 records / 22 source studies**:

| Descriptive group metric (source `yi`) | Archive as labeled | With sample 178 excluded |
|---|---:|---:|
| Unweighted mean log response ratio | −0.68951182 | −0.72520197 |
| Inverse published-vi weighted mean lnRR | −0.17987794 | −0.18028854 |
| First average effect within each original study, then equal-study average | −0.57665879 | −0.63317573 |

These three are **descriptive sensitivity diagnostics only**. They do NOT reproduce Leal's `metafor::rma.mv` random study/plant/taxon plus phylogenetic covariance model; do not report them as refitted point estimates, confidence intervals, p-values or a correction to the published meta results. Source 178 has very low precision and its contribution to the inverse-variance mean is small. Original data must remain unchanged pending journal/author reconciliation.

## Why this is ecologically material for BALANCE

The 2019 original study measured **three distinct mechanisms**: actual nectar removal (resource loss), visual/corolla slits and VOC scent (information/cues), and pollinator visitation/pollen receipt. It reported a substantial nectar resource deficit but no statistically detectable visitor avoidance under its artificial factorial comparison. Conflating VOC emission with nectar volume destroys the separation that a *resource vs signal vs service* macro analysis needs.

This also warns against over-interpreting nominal `robber/thief` classes without operational slit/open-entrance behavior, and against connecting two different Jacaranda species/primary studies through an incorrectly assigned plant taxon.

No direct `L/R/K/Φ/W_D^*−W_S^*` or shared-vs-differentiated architectural cost/fitness has been identified here. No V4, U6 (21 sources, 42 A/B coders), or SLK evidence is opened or modified.

## Reproduce from official original inputs

```bash
BALANCE_LEAL_ORIGINAL_ZIP=/path/to/Leal_original.zip \
BALANCE_ZHONG_ORIGINAL_XLSX=/path/to/Zhong_original.xlsx \
BALANCE_SOUZA2019_JATS=/path/to/PMC6872153_fullTextXML.xml \
  python -m pytest -q tests/test_leal_souza2019_original_scent.py

python scripts/audit_leal_souza2019_original_scent.py \
  --leal-zip /path/to/Leal_original.zip \
  --zhong-xlsx /path/to/Zhong_original.xlsx \
  --source-jats /path/to/PMC6872153_fullTextXML.xml \
  --out /tmp/2019_souza_source_classification.json
```

The source-gated GitHub Actions workflow `.github/workflows/leal-souza-primary-2019-source.yml` **re-downloads and source-hash-verifies all three public originals** and runs eight tests plus numerical readout generation. Audit conclusions are source/provenance, not an independent ecology effect claim.

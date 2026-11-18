# Source-scoped robber behavior versus pollen deposition: *Pitcairnia angustifolia* (2007)

**2026-11-18, source-transcribed exploratory receipt.** Original source: Fumero-Cabán & Meléndez-Ackerman (2007), *American Journal of Botany* 94:419–424, [DOI 10.3732/ajb.94.3.419](https://doi.org/10.3732/ajb.94.3.419), [open publisher full text](https://bsapubs.onlinelibrary.wiley.com/doi/10.3732/ajb.94.3.419). This manually transcribes published 2002 visitor totals, behavioral roles, and approximate per-visit pollen-deposition contrasts from the original full text. **No original individual visit/stigma records, publisher artifact SHA256 or independently downloaded source byte-validation**: do not call this source-authenticated raw-data replay. Provenance anchors are the original article's Methods (visitation, pollen loads) and Results (visitor frequencies, efficiency, effectiveness).

## Data and distinct units

The original investigators observed 60 plants across six patches for 90 hours in 2002. They counted 1,146 **flower visits**, not independent experimental plants. Pollination efficiency was determined from **20 virgin-flower stigmas per visitor taxon, plus 20 unvisited controls**. The paper's effectiveness index combines *within-patch* plant-normalized visitation and per-visit stigma pollen load; the published total visit counts cannot simply be multiplied by approximate pollen efficiency ratios to reproduce its patch-level index. The published comparison is not compatible with a viable-seed fitness meta-effect.

| Visitor | Behavioral route | Original recorded visits | Single-visit stigma-pollen finding |
|---|---|---:|---|
| *Anthracothorax viridis* | Legitimate nectar visitor | 111 | Reference highest load |
| *Apis mellifera* | Legitimate pollen collector | 338 | About one-third of *A. viridis* load |
| *Coereba flaveola* | **Primary nectar robber** | **664** | **Some pollen deposited**; ~6.7% of *A. viridis* per-visit load |
| *Chlorostilbon maugaeus* | Secondary nectar robber | 33 | Load **not detectably different from unvisited controls** |

Behavioral nectar robbers account for **697/1146 = 60.82% of observed visits**. Primary robber *C. flaveola* alone accounts for **664/1146 = 57.94%**. The original authors report a similar **patch-level stigma-pollen effectiveness index** for *A. viridis*, *A. mellifera*, and *C. flaveola* despite large per-visit differences. That was already a published result in 2007, **not a new discovery of this audit**. A measured positive pollen-load contrast does **not** mean every one of 664 visits pollinated, that pollen came from another plant, or that seeds were fertilized. The authors discuss mechanically displaced/self pollen as a possibility; no outcross paternity or final viable seed counts for the four visitors were measured.

## Source-level interpretation and the 2013 Fumero case

This is a **witness of nonexclusive behavioral and functional labels**: `primary_robber` and `stigma_pollen_deposition_detected` can both be true; a secondary robber's assay can instead be control-like. Therefore GloBI or meta-archive labels such as `nectar robber`, `bird`, and `visitation` must not be automatically recoded as pollination quality or reproductive fitness. Separate fields are necessary for (i) direct entry/nectar extraction behavior, (ii) pollen placement, (iii) effective pollen transfer, (iv) fruit maturation, and (v) viable seed outcome.

The same authors' 2013 *P. angustifolia* paper ([DOI 10.1111/j.1442-1984.2012.00388.x](https://doi.org/10.1111/j.1442-1984.2012.00388.x)) is the Fumero source behind unresolved Leal 2025 rows 79/81/83/84. The 2007 article **does not recover those 2013 treatment-specific source means or the direction of archived sample 79**. Same plant species and research programme are **not independent species-level replication**; nor does this 2007 source-adjudication imply any publication error in the 2025 meta-analysis.

## Macro design use, and stop rule

This source-only case yields a *measurement-ontology and false-negative-classification witness*, not an estimate of how often nectar robbers provide service among plant species. It was selected for a reason and is **not part of the outcome-independent denominator** required by `balance` issue #245. A prospective, species-first sample must retain `NO_DATA`, `TESTED_NULL`, `POLLEN_DETECTED` (not necessarily outcross), and measured seed success separately, and evaluate missingness by study and sampling effort. For BALANCE itself, no `L`, `K`, `Phi`, optimized shared/differentiated architecture, or functional conflict is directly identified.

Read-only command: `python scripts/audit_pitcairnia_2007_role_duality.py` (prints JSON); run `pytest -q tests/test_pitcairnia_2007_role_duality.py`. The tiny CSV contains original-published quantitative facts only; the tests verify internal transcription and claim guardrails, **not independent raw source verification**. The 21 U6 admissions, 42 blind architectural coding slots, V4 fit, original Leal/Zhong meta data, and SLK flagship are unchanged.

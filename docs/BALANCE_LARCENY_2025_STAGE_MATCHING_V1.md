# BALANCE: global floral-larceny evidence-stage pairability audit (2026-11-17)

**One reanalysis of the existing Zhong et al. 2025 meta-analysis, not 153 new studies or a novel causal result.** The scientific question is whether the published cross-outcome contrasts can be evaluated *within original studies* rather than as comparisons across non-exchangeable subsets.

## Provenance and existing research

- Zhong et al. (2025), *Plant Diversity*, doi:[10.1016/j.pld.2024.12.004](https://doi.org/10.1016/j.pld.2024.12.004). This paper already reports average negative larceny responses for nectar traits, legitimate visitation, pollen deposition, and fruit set, but weak or neutral overall average responses in seed fitness measures.
- Publisher's data-availability statement links to [Figshare original shared dataset and code](https://figshare.com/s/99df84fe5c473dc85d85). Its hosted item is [10.6084/m9.figshare.27129204](https://doi.org/10.6084/m9.figshare.27129204) (CC BY 4.0; unpublished-to-search private-share URL). File id `50193012`, downloaded official original ZIP SHA256 `84d310948e1da97c091ca27e9dcc45521cf72512ba14e30d3cd269d46e5b274c`, 1,572,161 bytes. The original workbook `Dataset for floral larceny effect size calculation.xlsx` has SHA256 `6554409f22b09156ee1c2a35ee2547eb5ae28c4a25934b9c639d8a19ea7fe9b4`.
- The original workbook contains **776 positive-variance effect-size rows** from **153 distinct publication IDs** and **120 species**; all `yi` and `vi` are numeric and `vi>0`. It contains 170 unique `(publication ref-ID, species)` groups, with 30 source columns including response-stage labels and ecological moderators. The authors' original R code uses nested publication/effect random effects and plant phylogenetic covariance. We do **not** replace or claim to have reproduced their complete multivariate meta-analysis.

## Coverage of co-reported stages within the same paper and species

These counts are **upper bounds on usable matched contrasts**, not fully matched experimental observations. Same paper+species is a necessary condition, not sufficient for same experimental exposure, site, measured flower, or covariance.

| Endpoint overlap required | Publication×species groups | Distinct publications |
|---|---:|---:|
| Nectar volume + visitation rate + pollen deposition + fruit set + seed set | **2** | **2** |
| Visitation rate + pollen deposition + fruit set + seed set | 4 | 4 |
| Pollen deposition + fruit set + seed set | 8 | 8 |
| Visitation rate + fruit set + seed set | 10 | 10 |
| Pollen deposition + fruit set | 13 | 13 |
| Fruit set + seed set | **37** | **36** |

The five-stage paper-species candidates are original reference IDs **29 *Corydalis caseana*** and **101 *Gentiana straminea***. Neither is yet verified as a joint longitudinal flower-level panel. Their original data must be traced before any mediated path calculation or stage-to-stage fitness interpretation.

## What survives a stricter *candidate* screen?

Among the 37 fruit+seed paper-species groups, 35 have a shared `experiment_level` (individual-flower or whole-plant). Requiring **exactly one fruit-set effect and one seed-set effect per paper/species**, and agreement in all archived contextual moderator fields (`country`, location, climate, plant traits, larcenist, pollinator, experimental level, etc.), leaves **17 unique one-to-one candidates from 16 publications**.

For the 17, the exploratory arithmetic difference `yi_seed − yi_fruit` has:

- **8 positive**, **9 negative**, zero exact ties;
- descriptive mean **−0.0364** and median **−0.0118** on the published log-response-ratio scale.

**This is not an effect size to meta-analyze**. Even these 17 source-eligible pairs do **not** carry a unique experimental contrast identifier, shared assignment record, fruit-to-seed sample linkage, known sampling covariance, or harmonized seed-set denominator. Different response categories can use different measured units and conditional samples. Neither a sign-count nor a naïve paired p-value would identify stage-wise biological attenuation. The near-zero median does not establish effect equivalence or no mechanisms.

## Scientific gap and proposed test

The existing meta-analysis has already answered whether *different endpoint categories* have different average associations with floral larceny. What is still untested is whether, **within the same experimental contrast and floral cohort**, costs to legitimate visitation or pollen delivery are transmitted or absorbed during fruit initiation and seed maturation, and whether this transfer depends on `pollen_limitation`, `self_compatible`, explicit flower damage, or legitimate pollinator guild.

For a confirmatory future analysis, first rebuild original-study **contrast keys** (same source, site, year, treatment and control definition, plant cohort, temporal unit, source sampling variance) independently of outcomes, then retain only pairs with verified common experimental exposure. Prespecify response-denominator differences (e.g. seeds *per fruit* conditional on survival versus seeds *per flower*), and use a multivariate covariance model only when within-study covariance is available or a defensible bounded sensitivity analysis is stated. A group with missing experimental link becomes **UNRESOLVED**, never negative or zero.

A different stage of inference would test an intervention or matched mediation path from effective visitors to deposition to mature seed output with independent plot-level replication. Existing S1/S2 *Alpinia* values do not meet that standard because exposure and site identity are confounded, as audited separately in PR #266. Most importantly, none of these source-matching analyses identifies the net optimized fitness difference of viable shared versus separated floral architectures (`W_D*−W_S*`) or BALANCE strict `L`, `K` and `Phi` occupancy.

## Strict source-audit reproduction

Run the original source workflow to download the publisher-linked ZIP, verify SHA256, extract the unchanged XLSX and rerun:

```bash
python -m pytest -q tests/test_larceny_meta_stage_pairability.py
python scripts/audit_larceny_meta_stage_pairability.py \
    --source '/path/to/Dataset for floral larceny effect size calculation.xlsx' \
    --out /tmp/BALANCE_LARCENY_2025_STAGE_READINESS_V1.json
```

The source, endpoint denominator, study IDs, 2/4/8/10/13/37 coverage, 17 unique candidate rows, and inference ceilings are regression-tested. No BALANCE U6 frozen 21-taxon roster, 42 independent architecture code slots, V4 outcome, original theory document, or flagship SLK manuscript is modified.
# Campanula 2018: grouped geographic transport and fixed single-visit quality index

**Status:** exploratory post-publication sensitivity analysis of **one plant species**. Sources: Koski et al. (2018), *Proceedings B* [10.1098/rspb.2018.0635](https://doi.org/10.1098/rspb.2018.0635), and original public data [10.5061/dryad.5nj81nf](https://doi.org/10.5061/dryad.5nj81nf), independently archived [here](https://zenodo.org/records/4969330). Not an independent biological replication, a new ecological experiment, a plant-wide prevalence estimate, a structural architecture fitness comparison or a V4 confirmatory result.

## Question and source-gated unit of analysis

Can the **observed visitor mix** help predict pollen limitation beyond total visit frequency when nearby populations are held out? Is a fixed index formed by multiplying visits by observed single-visit seed production sufficient to capture the same association?

The original pollen-limitation/visitation table contributes **23 population-level rows in 14 US states**, and the same workbook supplies **118 single-visit seed outcomes**. The independent biological species count remains **one**. The original workbook SHA256 is `b81b77248b75330049e1ddd8ae026db127f838e979620a0415a5addb9a7e8f27` (published MD5 `2d26307743e8a22384781854b8f2f33b`). The unchanged population extract has SHA256 `b66ec8c1471ddfe08bcfca990cb907eadcf0898f7bef45f9fdc28257a4135cde`. The separately exported **line-ending-normalized** single-visit sheet has SHA256 `4660d1d49a0d0bb4ad9e3ecc14048bbc40138fe3e5f88ab76c7c966484501cf8` (original CSV extraction before CRLF normalisation: `dc1eefb132507ce268e260cf961447dcc1ec67ea2cf6ba97d1415c01087568bb`). The latter is a faithful copy of one sheet from the **same 2018 workbook**, not another independent study. Both source checks fail closed.

The dependent variable is **sqrt of archived population PL**. The archived PL index is neither a count of seeds nor a separately fitted selective coefficient. Original PL zero values remain the two present in the archive; no third negative/censored value is invented.

## Four models, same 23 held-out populations

- `total`: `sqrt(PL) ~ log(total visits + 0.1)`.
- `total_plus_composition`: `sqrt(PL) ~ log(total + 0.1) + Megachile share + small-bee share`; the missing bumblebee fraction is the reference. These are **substitution contrasts**, not additive increases in small-bee abundance at fixed other group visits.
- `three_group_rates`: `sqrt(PL) ~ log(bumblebee rate + 0.1) + log(Megachile rate + 0.1) + log(small-bee rate + 0.1)`. This reproduces the source-like flexible visitation model, not a parsimonious quality-only model.
- `single_visit_seedset_weighted`: `sqrt(PL) ~ log(Q + 0.1)`, where `Q = sum_g visits_g * (mean single-visit seeds_g / mean single-visit seeds_bumblebee)`. This is **one fixed scalar predictor** with observed group weights; no outcome-fitted species-specific quality weights are permitted.

The single-visit records contain B **31** flowers (raw mean **11.5161** seeds), M **54** (**7.2407**) and H **33** (**3.0303**). Their measurement supports are severely unbalanced: B has 26/31 from site FV, M has 42/54 from site K, H has 32/33 from site K. Therefore **group mean seed counts confound visitor type and assay site**. The quality-only index is an *exploratory, weak mechanistic proxy*, not an experimentally isolated intrinsic efficiency correction. Linear additive quality weights also omit pollen-transfer saturation, competition for limited pollen, and male/female flower-phase visitation bias documented in the original study.

## Refit held-out comparison, equal population weighting

All holdout predictions refit coefficients from training observations only. Every original population is predicted exactly once under each scheme; summary RMSE and MAE weight each population equally, **not each fold or state equally**. Rank-deficient designs fail rather than silently dropping groups. Geographic holdouts do not create new independent biological studies.

| Holdout strategy | Folds | Min training n | Total only RMSE | Total + mix RMSE | Three group rates RMSE | Quality-only RMSE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| One population at a time | 23 | 22 | 0.213405 | 0.183088 | 0.155599 | 0.221673 |
| All populations of one state at a time | 14 | 19 | 0.213140 | 0.180307 | 0.150510 | 0.225373 |
| Four rank-based latitude blocks | 4 | 17 | 0.215062 | 0.162889 | 0.135539 | 0.230185 |
| Four rank-based longitude blocks | 4 | 17 | 0.211386 | 0.177992 | 0.141999 | 0.221114 |
| Hold out one population and exclude all training sites ≤250 km away | 23 | 18 | 0.216886 | 0.183841 | 0.150824 | 0.226073 |

Relative total-versus-composition pooled holdout RMSE reduction: **15.40%** for state blocks, **15.24%** with a 250-km spatial exclusion buffer. Among **14** state-specific holdout groups, composition improves within-state mean squared error in **9**, worsens in **5**. This is not a universal improvement across every state. This buffer radius and the rank partitions were explored **after** the previous ordinary LOO result, so they are not an independently prespecified validation study. The source has only 23 populations and spatially overlapping training folds.

The single-visit seed-quality scalar does **not** outperform total visitation under the tested transformations and holdout geometries. This does **not** show that pollinator efficiency is ecologically irrelevant: it shows that a simple raw-mean-weighted scalar, with substantial site confounding and no timing/competition adjustment, is inadequate here. Visitor composition and separate group rates are predictive in this selected data set, but population observational models do not identify the cause.

## Scientific interpretation and non-inference

The incremental result is a **within-taxon association** that persists in the declared grouped/spatial holdouts. It strengthens the ecological motivation for keeping **functional composition** separate from **total interaction intensity**. It does not demonstrate that small bees are inherently harmful in all contexts, that active same-trait directional conflict `L` is measured from the visitation table, that an architectural alternative is genetically accessible, or that a structural shared-versus-differentiated fitness difference `W_D* - W_S*` has been observed.

Two generalization obstacles remain: independently collected plant species with comparable flower-stage interaction measurements, and independent source-blinded assessment of the proposed division of floral functions. In future systems, directly measure flower-phase-specific pollen removal and deposition, subsequent paternity and mature seed success, floral module architecture, and the extra fitness cost of a viable alternative structure. Do not pool source-anther theft, stigma-side post-deposition stripping, and shed wind-pollen predator diets as identical causal events. The 21-case U6 roster, all 42 independent coder worksheets, V4 outcome freeze, manuscripts, SLK architecture-value parameters and original workbook remain untouched.

## Execute and audit

```bash
python -m pytest -q tests/test_campanula_2018_visitation.py tests/test_campanula_2018_spatial_quality.py
python scripts/audit_campanula_2018_spatial_quality.py --out-dir /tmp/new-spatial-quality-readout
```

The result directory contains `SPATIAL_QUALITY_RESULTS.json` (per-population held-out predictions, group counts, no-causal-claim boundary) and `CV_COMPARISON.csv`. The command refuses to overwrite an existing output directory. Original workbook recovery and numerical replay are pinned in `.github/workflows/campanula-2018-source-recovery.yml`.

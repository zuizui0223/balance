# Independent Wisconsin apple orchard source and condition-sensitive model comparison

**2026-11-15; exploratory, original MD5-verified observations only.** Dataset: Mallinger & Gratton, [Dryad 10.5061/dryad.t75c4](https://doi.org/10.5061/dryad.t75c4), originally published in *Journal of Applied Ecology* [10.1111/1365-2664.12377](https://doi.org/10.1111/1365-2664.12377). Their article had already documented the relationship between native wild bee richness and apple fruit set. This is a new strictly constrained *out-of-orchard predictive diagnosis*, not a new study or a causal identification claim.

The independent publication contains **47 orchard-year rows, 21 different orchards**, and **11 bee-abundance / richness NA rows in 2011**. Do not reinterpret those missing counts as no bees. There are **36 complete orchard-year records**: 17 (2012) and 19 (2013), from 21 orchard identities, some repeatedly studied. Official 2015 mirrored XLSX was re-downloaded from [Zenodo 4943340](https://zenodo.org/records/4943340) and checked against source MD5 \`5445fb585421e6d9b1f5b5869342bbb4\` (fruit set) and \`f5a99ce414f7294841ba11d46d80b805\` (bee sampling). Source original archive is retained as a GitHub Actions artifact, not silently replaced with synthetic rows.

**Outcome:** \`asin(sqrt(proportion fruit set on open branches))\`. **Primary baseline:** context (year indicator and measured frost damage when applicable) plus log1p(wild bee abundance **per 1 week** + honey bee abundance). Models add wild-bee proportion, log1p(observed native bee richness), or both. The two abundance columns may not be perfectly exchangeable between years; a raw-wild-abundance alternate readout is retained. All assessments leave out **entire orchards** (all years in that orchard) and score RMSE with equal orchard weighting, not 36 independent orchards.

| Model context | Orchard-year N | Total-only RMSE | Total + wild share + richness RMSE | % change (positive is improvement) |
| --- | ---: | ---: | ---: | ---: |
| 2012+2013, year+frost | 36 | 0.12175 | 0.11351 | **+6.76** |
| 2012+2013, year+frost+management | 36 | 0.12524 | 0.11683 | +6.71 |
| 2012+2013, year only (no frost) | 36 | 0.15212 | 0.13829 | +9.09 |
| 2012 only, frost adjusted | 17 | 0.16158 | 0.13057 | **+19.19** |
| 2012 only, no frost adjustment | 17 | 0.20406 | 0.19795 | +2.99 |
| 2013 only | 19 | 0.05595 | 0.06005 | **−7.34** |

The share-only increment is **+0.62%** in pooled year+frost, **+8.77%** in 2012 with frost adjustment, **−11.68%** in 2012 without frost adjustment, and **−1.64%** in 2013. Combined share+richness models must not be labelled biological synergy: correlated measurements, suppression, season/frost confounding and limited N remain plausible. In 2013 the intercept-only model outperforms the total/composition competitors. The published study had already addressed frost impacts; this analysis does not establish frost **causes** pollinator functional reallocation. Outcomes and visitor metrics differ from *Campanula* pollen limitation and Zurich phytometer seed/fruit data: **do not pool percent RMSE gains or estimate a single ecological selection coefficient**.

The current cross-programme census is three separate original research programmes (*Campanula americana*, four Zurich taxa in one garden experiment, and *Malus domestica*), **six focal plant taxa total**. The first inferentially distinct hypothesis worth prospectively testing is **environment-conditional utility of interaction-guild composition**, not universal superiority of more predictor categories. This study does not measure the cost of architectural differentiation, historical organ evolution or a matched shared-versus-differentiated fitness worldline. All original U6 independent architecture coder sheets remain unopened; BALANCE stays a dormant technical certification module supporting SLK.

Reproduce with exact original workbook:

\`\`\`bash
python -m pip install numpy
python scripts/audit_wisconsin_apple_independent.py --source /path/to/fruitsetbees.xlsx --out /tmp/wisconsin.json
BALANCE_WISCONSIN_APPLE_ORIGINAL=/path/to/fruitsetbees.xlsx python -m pytest tests/test_wisconsin_apple_independent.py
\`\`\`

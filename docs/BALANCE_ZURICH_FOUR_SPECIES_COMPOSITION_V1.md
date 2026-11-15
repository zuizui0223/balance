# 2025 Zurich four-phytometer composition benchmark — source-audited exploratory receipt

**Status: POST-PUBLICATION EXPLORATORY, one existing 24-garden research programme. Never a new experiment, cross-study meta-analysis, causal source-loss test, four independent research programmes or BALANCE S/D fitness worldline.**

## Original source and already-published analysis

- Independent raw-data acquisition, EnviDat dataset DOI [10.16904/envidat.676](https://doi.org/10.16904/envidat.676). Source archive SHA256 `b1ea0dc54d0c6e33bfacb44d7285377ec3e113807cc945fc2dfbfcc3e534bcc9` (4,995,435 bytes).
- [GitHub source-check workflow run #43672888698](https://github.com/zuizui0223/balance/actions/runs/43672888698) succeeded and contains the original ZIP plus source provenance and per-file checksums.
- Reji Chacko et al., 2025, *Data in Brief*: [10.1016/j.dib.2025.112013](https://doi.org/10.1016/j.dib.2025.112013).
- Reji Chacko et al., 2026, *Journal of Applied Ecology*: [10.1111/1365-2664.70384](https://doi.org/10.1111/1365-2664.70384). **This paper already analyzes the same biological experiment**. We test a narrower out-of-garden predictive comparison that must not be passed off as an entirely new biological discovery.
- All source data were collected in 2016. Twenty-four gardens were used for all four species, so the four species are correlated species-level responses within one biological programme.

## Source matrix audit — critical exposure denominator

The supplied time-grid CSV contains 21,120 nominal rows (24 gardens × 4 plants × 22 days × 10 time cells). Only **670 real sampling windows** appear in the separate sampling ledger, corresponding to **2,680 garden × plant exposure cells**. The original individual-visitor table has 5,794 captures, of which **5,767 match a sampling window**. The other **27 visits in 6 plant-time rows** are retained as a flagged unmatched-source item and included only in an explicit alternate sensitivity. The nominal zero rows are **not automatically true zero-visitor field observations**. The raw collector flags identify **256 nectar robbers** (222 on Symphytum; 34 on Onobrychis). Do not interpret any of these counts as a measured loss of gamete export or pollen limitation.

The visitor exposure is counts per **recorded observer-hour**, not counts per flower or independently measured effective pollen deposition.

## Descriptive models and denominator

Garden holdout unit (24 independent holdouts **per species**): each garden is predicted from models fitted to the other 23. Independent seed/flower-level replicates are aggregated at **plant** and **garden** levels and are **not** counted as independent exposure clusters. Garden-specific response is log1p(mean seeds per umbel) for Daucus, and arcsin(sqrt(mean plant fruit/seed set fraction)) for Raphanus/Onobrychis/Symphytum. These outcomes have different scales and cannot be pooled numerically across taxa.

Compare M0 = intercept + log1p(total visitor-capture rate) with M1 = M0 + active visitor-group **shares** (omit dominant group to avoid collinearity). Defined groups: honeybee / other bee / nonbee / source-flagged nectar robber. These groups are operational labels, not independently measured pollination efficiencies. No model tunes taxonomy from reproductive outcomes.

| Species | M0 LOO RMSE | M1 LOO RMSE | Relative RMSE reduction | M1 garden-specific prediction better in |
|---|---:|---:|---:|---:|
| *Daucus carota* | 0.2525405 | 0.2035595 | **19.40%** | 11/24 gardens |
| *Raphanus sativus* | 0.0574445 | 0.0575034 | **−0.10%** | 12/24 |
| *Onobrychis viciifolia* | 0.1403447 | 0.1474651 | **−5.07%** | 10/24 |
| *Symphytum officinale* | 0.1759804 | 0.1646906 | **6.42%** | 11/24 |

**The positive statement is contingent:** only Daucus retains a substantial gain under changing the flower-exposure denominator. In Symphytum the only composition contrast in M1 is nectar robbers versus other bees, not a comparison among independent legitimate pollinator guilds. Its initial +6.42% becomes +0.23% under flowering-only observation windows.

## All prespecified-in-reanalysis and post-open stress cases

| Species | Original | Pool garden fraction instead of equal per-plant fraction | Exposure where focal flowers observed | Add 27 unmatched captures, no extra observer hours |
|---|---:|---:|---:|---:|
| Daucus | +19.40% | +23.08% | +18.07% | +19.47% |
| Raphanus | −0.10% | −1.09% | −0.77% | −0.04% |
| Onobrychis | −5.07% | −10.58% | +1.24% | −6.35% |
| Symphytum | +6.42% | +10.92% | +0.23% | +5.60% |

Leave each garden out of the **entire dataset** then redo holdout training/validation: Daucus maintains positive aggregate reduction in 24/24 (minimum +4.08%, maximum +24.49%). Onobrychis remains negative in 24/24. This does not show that all independent garden predictions improve (only 11/24 do for Daucus) and is not another biological experiment or a p-value. The flower-presence filter changes the time-at-risk estimand and is disclosed for all four species, not selected by result.

## Interpretation and limitations

These exploratory real-source calculations reject the simplistic inference **“visitor composition universally outperforms aggregate visitation.”** Some contexts can show additional predictive information, but crop-/species-specific phenology, flower availability, habitat, urbanization, different true pollinator identities and observer effort are confounded. No pollen thief causation, donor/recipient stage-conflict `L`, a heritable structure, a net partitioning benefit `R-K`, a viable structural alternative `W_D^*`, or a measured BALANCE domain is identified.

**Do not pool** these different response-scale RMSEs with the 2018 Campanula americana *pollen-limitation* RMSE or represent these four garden-responses as four independent studies. The garden (not seed, date, hour or focal plant) is the out-of-garden prediction unit.

## Code and promotion rule

The extracted original-source receipt and the complete local code/tests/results are preserved with the exploratory research packet. A source-based readout may be cited, but **do not promote to preregistered U2/U6 V4 architecture outcomes or independent A/B coder assessments**. A proper confirmatory next step uses an independent programme and actual matched reproductive consequences of visitor functional groups, followed separately by experimentally available shared/differentiated structural fitness comparisons.

Current repository branch is a stacked draft above PR #259, which is above #258 and #257. All pre-frozen U6 21-taxon denominator, 42 independent human coder rows and publication-status gates remain untouched.

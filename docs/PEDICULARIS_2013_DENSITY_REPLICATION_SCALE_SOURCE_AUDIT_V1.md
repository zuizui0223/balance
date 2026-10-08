# Xia et al. (2013) Pedicularis density archive: replication-scale audit

Status: SOURCE PAPER AUDITED / ARCHIVE METADATA PENDING / RAW DATA NOT INSPECTED  
Source paper: Xia J, Sun S-G & Liu G-H (2013), *Biology Letters* 9:20130387, DOI [10.1098/rsbl.2013.0387](https://doi.org/10.1098/rsbl.2013.0387)  
Source archive declared by authors: Dryad DOI [10.5061/dryad.6cv06](https://doi.org/10.5061/dryad.6cv06)

## Non-obvious replication-scale risk, grounded in the published methods

The ecological exposure under study is **plant density measured at the patch level**. The source paper reports the following design:

| Year | Independently sampled sparse patches | Independently sampled dense patches | Independently harvested spikes | Scale of density exposure |
| --- | ---: | ---: | ---: | --- |
| 2005 | 1 | 1 | 16 (6 sparse, 10 dense) | patch |
| 2011 | 5 | 6 | 58 (26 sparse, 32 dense) | patch |

The source also reports 60 and 175 sampled wilted flowers for pollination assessment in 2005 and 2011; these **are not** additional independent density patches. In 2011 patch sizes ranged from 1 to 500 flowering plants, with sparse <2 and dense >5 flowering plants m⁻². The source's two-year ANOVA table reports residual df **2,926 for final seed set and seed predation**, whereas fruit-set and fruit-predation comparisons report df **69**. The 2011 patch size × density table reports seed predation residual df **2,345**.

**Scientific risk:** standard errors from thousands of flowers/seeds/capsules do not necessarily represent the uncertainty about density contrasts supported by only 2 patches in 2005 and 11 patches in 2011. It is unclear from the printed ANOVA table alone exactly how the original analysis accounted for plant/patch clustering. This is an **audit target, not proof of a methodological error**. Flower-level statistical significance cannot by itself establish a population-level component Allee effect that is robust across independently sampled patches.

2005's one sparse and one dense patch provide no independent within-stratum patch variance; effects are confounded with the two specific patch environments. A 2005 density-by-year result cannot be promoted as **two independent replicated density manipulations** without considering this support structure.

This is not a claim that the documented 2013 pattern is false, and it is not a new water-defence treatment comparison. Published differences in final seed set and predation remain evidence of association in the observed samples.

## Archive evidence hierarchy

1. **DOI citation**: verified in the published paper. This alone does not establish that the archive still resolves.
2. **Dryad dataset metadata**: verify DOI, exact title/creators and version identity. No raw data possession yet.
3. **Dryad file manifest**: verify file names, sizes, digests and accessible URLs. No ecological variable provenance yet.
4. **Downloaded file bytes**: record exact SHA256 and separately verify original-vs-transformed contents.
5. **Actual data semantic audit**: identify rows representing years, patches, plants, spikes/flowers, and seed units; validate absent/duplicate identifiers, whether patch membership is available and outcome scale.
6. **Independent hierarchical replication**: only then compute density-vs-predation associations with honest patch-level uncertainty and holdout/sensitivity to high-leverage patches.

Never claim #4–#6 from a successful #2 or #3. A historical Dryad DOI or web search snippet is not a raw file.

## Prespecified audit questions if archive bytes become available

- Are **patch IDs** present and stable across seeds/flowers/plants, or only density labels? A data file with no patch identity **cannot** identify cluster-robust patch-level uncertainty, even if it has several thousand rows.
- In the 2011 observations, do patch sizes overlap across density strata and across site/spatial blocks, or are density, size and patch landscape context nearly nonidentifiable?
- Reproduce original reported per-patch and per-density rates and published final-seed/fruit-predation definitions **before** fitting any new model; source seeds with zero or missing damaged intact counts must not be silently imputed.
- Primary observational estimand: association between patch density category and mean patch-level final viable seed set (separately predation/initial seed set), with **2011 independent patches** as replication. The 2005 one-vs-one result is a descriptive historical check; any pooled model must retain year/site and not pretend 2005 has within-density replication.
- Sensitivities: leave-one-patch-out; patch-size stratification; time/year context; count/zero semantics; compare plant-/flower-level fit with cluster-aware patch-level confidence intervals. No statistical correction alone turns observed density into a randomized intervention.
- If patch identifiers are absent, publish a **PATCH_LEVEL_INFERENCE_NOT_IDENTIFIABLE_FROM_ARCHIVE** receipt rather than treating flowers as independent density replicates.

## Relationship to PR #220

The 2015 water-drainage experiment *deliberately sampled dense patches* (Sun & Huang 2015, DOI 10.1093/aobpla/plv019). Thus even perfect replication of the 2013 observed density association cannot provide the missing *water manipulated in sparse patches* data. PR #220 correctly treats a future water-by-density interaction as an unmeasured experiment and requires independently replicated patches and arm overlap.

The current source-probe is a metadata-only gateway; it does **not** re-estimate 2013 Allee effects, causal density responses, predator redistribution, structural architecture, or BALANCE occupancy.

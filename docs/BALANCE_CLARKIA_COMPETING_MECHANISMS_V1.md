# Clarkia as a necessary causal-alternative test for heteranthery and structural evolution

Date: 2026-10-20. Status: **original 2020 primary publication located and independent, source-retrieval pipeline built; original raw-data effect sizes must be rechecked before promotion.** The study was found through an outcome-known published result, NOT through an outcome-blind angiosperm taxon frame.

## Contrasting causal hypotheses in the same visually differentiated architecture

**Original source:** Kay, K. M., Jogesh, T., Tataru, D. & Akiba, S. 2020, "Darwin's vexing contrivance: a new hypothesis for why some flowers have two kinds of anther", *Proceedings of the Royal Society B* 287:20202593, DOI [10.1098/rspb.2020.2593](https://doi.org/10.1098/rspb.2020.2593); full open article [PMC7779490](https://pmc.ncbi.nlm.nih.gov/articles/PMC7779490/). Original Dryad source DOI [10.5061/dryad.8cz8w9gmp](https://doi.org/10.5061/dryad.8cz8w9gmp).

The same visible two-whorl anther heteranthery can arise alongside different mechanisms:

| Registered biological explanation | Prediction for the two anther whorls | Required primary evidence |
| --- | --- | --- |
| Pollen **reward vs gamete export division of labour** | One anther type is disproportionately carried into bee pollen provisions/scopae; the other disproportionately exports pollen onto conspecific stigmas during access to a flower | Distinct quantitative pollen fates, joint conditioning on amount produced; preferential role loading under controlled bee access |
| **Gradual pollen dosing / temporal presentation** | Both whorls are collected **and** exported, but different exposure/dehiscence times improve total pollen export across visits | Different timing/availability; scopa/stigma pollen from both whorls; experimental same-flower pollen export under altered dosing |
| Apparent floral dimorphism only | No unique functional route shown | Source-verified morph + missing experimental function allocation; **do not code as zero conflict or zero evolutionary selection** |

This is not a claim that these mechanisms are mutually exclusive in every taxon. Their discriminating outcomes and required measurements differ.

## Published original-paper evidence (not newly computed in this audit)

The authors explicitly reported **no support for the classic simultaneous pollen reward/export division-of-labour explanation in Clarkia**, but evidence for delayed dehiscence/gradual pollen presentation. They reported:
- heteranthery in Clarkia to have probably arisen once with two later losses under their source phylogenetic reconstruction, not a validated independent repeated origin count;
- the across-species heteranthery–bee-pollination correlated-evolution test was marginal (`p=0.055` in the source), while its correlation with anther movement was stronger (`p=0.004`);
- source-tested pollen from **both** inner and outer anthers of *C. cylindrica* appears on bee scopae and floral stigmas, with an observed scopa-versus-stigma difference test `p=0.17` (this is **not** equivalence evidence);
- manipulative and observational tests of outer anther cryptic positioning, delayed presentation and export in *C. unguiculata* favor the authors' temporal dosing explanation.

Those reported values are cited only as **published-source claims** and remain separate from any future raw-data reanalysis. They must not be counted as independent replication of BALANCE's already sampled *Solanum* / *Senna* case-control studies.

## Why this is important for SCH–BALANCE–SLK/PAYOFF–BITA

The core structure-causation argument **fails** if visible heteranthery is automatically mapped to a new differentiated pollen-reward and pollen-export module. *Clarkia* is an original-data example where the two whorls are morphologically differentiated but do **not** support distinct pollen reward vs gamete-transfer roles as assigned under the old standard interpretation.

The same apparent morphology can therefore encode:
- **simultaneous** allocation across types, as experimentally demonstrated in *Solanum rostratum*, or
- **staggered exposure** of pollen from both types, as experimentally favored in *Clarkia*.

The route matters. For SCH, an external reward/transfer pollen-use conflict is still biologically relevant but an experimentally isolated two-optima scalar trait must be identified before estimating `L`. For BALANCE, the relevant comparison is not "heteranthery present or absent" but **within-flower division vs temporal dosing vs feasible shared/predictive plastic states**. For SLK/PAYOFF, a temporally differentiated pollen reservoir is not a second independent simultaneously coexpressed optimum and cannot automatically be assigned the idealized `K<C` module benefit. For BITA, pollinator handling vs delayed access must be distinguished by selectively measured pathway evidence, not morphology.

**Crucial historical limit:** the study's lineage reconstruction supports a history of heteranthery's visible features, not the historical causal direction from an experimentally measured fitness conflict to the origination of independently functional stamen modules. Evolutionary routes such as selection for pollen persistence/male competition, preexisting developmental anisotropy, phylogenetic sorting and demographic change remain different alternatives.

## Published numeric results: a positive alternative mechanism, with important null-test limits

The [article-text source receipt](../data/CLARKIA_KAY2020_PUBLISHED_STATISTIC_RECEIPTS_V1.json) and its [reproducible arithmetic audit](../balance_domain/clarkia_published_receipts.py) preserve quantities that the **2020 paper itself** reports. These were **not estimated from newly accessible Dryad row-level data**.

| Mechanism prediction | Original source observation/statistic | Admissible conclusion |
| --- | --- | --- |
| Delay between anther whorls | Greenhouse timing of **6 heterantherous versus 5 nonheterantherous species**, phylogenetic ANOVA `F=75.71, p=.002` | Source-reported lower dehiscence-time overlap in heterantherous Clarkia supports **temporal staging** |
| Exclusive pollen reward/export roles | Both whorls supply pollen to bee scopae and stigmas; scopa–stigma proportion test `t=-1.401, p=.17` | **No detected** destination specialization, **not** a test proving equivalence |
| Pollen amount potentially available | Fully dehisced/no-dosing treatment **4.6 mm** exposed pollen versus gradual/dosing **1.9 mm**, `F=483.17, p<.001`; ratio **2.421** | Manipulated/flower-age-related difference in **pollen exposure**, not proof of more pollen exported |
| Pollen arriving on receptive stigmas | Original negative-binomial model reports no-dose log effect `-0.3507, p=.27`; exponentiated coefficient **~0.704**; **13** dosing and **15** no-dosing flower arrays | Point direction is compatible with no-dose receiving less, but **no significant improvement in stigma deposition by dosing** is identified. Link-dependent coefficient is not raw pollen-count ratio |
| Pollen groomed/provisioned by bees | Corbicular pollen **6.7 mg** dosing versus **6.5 mg** no dosing; `p=.923` | No detected difference, **not evidence of equivalence** |
| Evolutionary correlation | Heteranthery–bee pollination `p=.055`; heteranthery–anther movement `p=.004` in published phylogenetic comparisons | Distinct source associations, **not the historical causal origin of new functional modules** |

**Important experimental limitation:** In the source greenhouse trial, fully dehisced/no-dosing flowers were **one day older** than dosing flowers; the experiment does not exclusively manipulate pollen availability while holding every aspect of flower age constant. The test uses one bumblebee per array; the **array**, not individual pollen grains or stigmas alone, defines the treatment unit. The authors' interpretation favors gradual pollen presentation on the *joint evidence*, not on a statistically significant 30% stigma-delivery increase.

The source paper describes one likely ancestral gain and two losses of Clarkia heteranthery, *not* multiple independent new origins. These historical branches do not establish that pollen consumption versus transport conflict historically caused the new morphology.

## Public Dryad data-access result: metadata PASS, raw experiment HOLD

[Read-only Dryad source audit](../balance_domain/clarkia_kay2020_source.py) was actually executed against the 2020 archive. The public metadata identify **dataset version 97733 with 29 deposited files**. Seven original targeted filenames and their **author-declared SHA256 and file sizes** can be checked against the live metadata, including:
`Clarkia_Phenotype_Heteranthery.csv`, `ClarkiaITS.nex`, `time_lapse_data.csv`, `pollen_data.csv`, `pollen_available.csv`, `CungSeeds.csv`, `CungManipulative.csv`.

However, Dryad's REST `datasets/.../download` returned **401**, and its human-facing `downloads/file_stream/...` returned **403** from the unauthenticated GitHub runner. The Dryad API documentation confirms raw file/archive downloads can require OAuth credentials. Accordingly, **no raw table rows, raw hashes verified against actual bytes, row-level confidence intervals, or re-estimated ecological effects are claimed**. The metadata-only JSON is a **source-admission HOLD**, not a negative biological result. A locally supplied authorized copy can later be independently SHA256-verified without changing the original inference contract.

There is an additional **source completeness** caveat: the deposited file inventory lists `BombusTrials2018.R`, and the source's usage notes refer to `BombusTrials2018.csv`, but the CSV is **absent from the published 29-file version**. Thus the particular pollen-dosing trial cannot currently be reconstructed from its registered experimental rows through this source lane. Do not invent its missing inputs.

## Publication and biological causal ceiling

The cross-system, two-original-study observation is defensible:
- ***Solanum rostratum*:** source experiments support functional specialization between feeding and pollinating anthers;
- ***Clarkia*:** source experiments support timing/gradual pollen dosing, with no **detected** whorl specialization in the studied species.

These two data programmes invalidate a deterministic equation of **heteranthery morphology = functional division of pollen roles**. They do **not** yield a representative probability of a mechanism, a comparable common-fitness `R-K`, or an independent estimate of conflict-caused morphological origin.

For PAYOFF/SLK, **programmed irreversible developmental staggering** is distinct both from reversible cue-memory plasticity and from independently coexpressed structural function separation. A biological three-option model **SHARED / PLASTIC / FIXED MODULE** must not relabel temporal dosing as memory-based plasticity. For the full empirical ecology, time-partitioned developmental pollen release is a **fourth feasible strategy class** whose time-resolved costs and gamete exports would need independent measurement.

Reproduction commands:

```bash
python -m pytest -q tests/test_clarkia_kay2020_source.py tests/test_clarkia_published_receipts.py
python scripts/audit_clarkia_kay2020_dryad.py --out /tmp/clarkia_metadata_only.json
python scripts/audit_clarkia_published_receipts.py --out /tmp/clarkia_published_receipts.json
```

No original data, BALANCE V4 confirmatory source outcomes, active SLK journal manuscript or BITA Letter has been edited. *Clarkia* was discovered from a published outcome-driven study; the independent future macro denominator still requires outcome-blind taxon/family selection.

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

## First executable public-source gate

[Source acquisition code](../balance_domain/clarkia_kay2020_source.py) uses the published dataset's exact Dryad DOI, downloads the public source archive, and requires seven predetermined files from the original experiment and phylogeny:
`Clarkia_Phenotype_Heteranthery.csv`, `ClarkiaITS.nex`, `time_lapse_data.csv`, `pollen_data.csv`, `pollen_available.csv`, `CungSeeds.csv`, `CungManipulative.csv`.

It records archive and input-file hashes, exact original column names, row counts, preview source fields and low-cardinality categories. The script does **not** reinterpret raw data, calculate a significance test or substitute an unknown value for negative evidence yet. A source mismatch or missing file **fails closed**; no third-party full dataset is committed. After obtaining real source schema and provenance, a separate locked analysis can test timing, pollen-fate channel and export manipulation. Predeclared interpretation:
- source `p>=0.05` **not equal** proof of no functional specialization;
- anther whorl/cue positions **not equal** biological functions until pollen fates are experimentally determined;
- source phylogeny **not equal** historical causality;
- a selected Clarkia genus **not equal** a representative global macro frame.

## Execution

```bash
python -m pytest -q tests/test_clarkia_kay2020_source.py
python scripts/audit_clarkia_kay2020_dryad.py --out /tmp/clarkia_source_schema.json
```

GitHub Actions for this separate source lane runs the original-data admission and creates a bounded auditable schema-only JSON. The journal-facing SLK and BITA manuscripts and BALANCE V4 confirmatory data stay unchanged.

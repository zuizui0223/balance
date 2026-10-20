# Wurmbea: original-voucher plastid source replay and inheritance-sensitive ecological fitness gate

**Date:** 2026-10-19. **Status:** real-data acquisition and pre-specified failure/claim ceilings. The existence of published accession IDs is independently verified in the [original open author PDF](https://barrett.eeb.utoronto.ca/publications/files/2020/06/Case_et_al_IJPS169_141-156.pdf), *Case et al.* (2008), DOI [10.1086/523368](https://doi.org/10.1086/523368), Table A1.

## One biological question

Is there an empirical bridge from **environment-dependent sexual fitness advantage** to **observed population-level ancestral/derived architectures**, or do genetic inheritance and poor historical identification prevent attributing the origin of separate sex organs to a functional trade-off?

This audit is NOT a reconstruction of the origin of sexual separation. It asks whether the relevant original population vouchers remain publicly accessible and whether the strongest published fitness intervention gives a universally valid architecture advantage (it does not).

## A. Original Case (2008) marker and population study

The full original source used **four chloroplast regions** (`ndhF`, `atpB-rbcL`, `trnLF`, `psbBTNH`, about 5.3 kb of aligned sites). The paper's own ancestral-state analysis found **a minimum of five changes in sexual-system state on the considered gene-tree**, but failed to resolve their direction or position with confidence; *W. dioica* and *W. biglandulosa* population samples could violate species monophyly. This is a ***published source analysis***, not a calculation made by this audit.

Table A1 provides voucher-specific M (gender-monomorphic) and D (gender-dimorphic) states alongside publicly deposited GenBank accessions. Unlike a genus-level name match, these preserve the same biological terminal that was photographed, sequenced and coded by the original experimenters.

The [frozen exact 22-row Australian voucher ledger](../data/WURMBEA_CASE_2008_TABLE_A1_NDHF_VOUCHERS.csv) retains **12 M and 10 D** states with every ndhF accession. In particular:

- *W. biglandulosa* subsp. *biglandulosa*: `MR1/MR2` (M) and `MR3/MR4` (D). All four vouchers have separate ndhF accessions (EU044643–EU044646).
- *W. dioica* subsp. *alba*: `AC53` (M, EU044633) and `AC38` (D, EU044634).
- *W. dioica* subsp. *dioica*: `AC13` (D, EU044647), a different subspecies/environmental source context; never pool this automatically with `W. dioica alba` as a matched experimental replicate.
- Taxon `W. citrina` in this manifest has a source-name warning because the PDF table prints `W. citrine`; the accession is unaltered, the botanical string is not silently considered an accepted taxonomic decision.

This study-design boundary is critical: *different sex-system states do occur in source-confirmed populations of one nominated taxon*. That fact is not a derived ecological stimulus or proof of multiple independent historical origins.

### Actual sequence retrieval contract

```bash
python -m pip install 'biopython>=1.84,<2' pytest
python -m pytest -q tests/test_wurmbea_case2008_genbank.py
python scripts/audit_wurmbea_case2008.py --outdir /tmp/wurmbea-source-audit
```

- Each exact accession is retrieved live from [ENA/INSDC](https://www.ebi.ac.uk/ena/browser/home), not a generic online taxon search.
- A valid response must be one FASTA sequence whose header contains the accession and Wurmbea, at least 300 bases long, with a valid IUPAC DNA alphabet; failures appear as `HOLD_INCOMPLETE_SEQUENCE_RECOVERY`, never as absence of a genetic pattern.
- Sequence SHA256, length, exact voucher and accession are retained; raw nucleotide bytes are NOT redistributed in GitHub artifacts. A gap-aware global Biopython pairwise alignment calculates p-distance among the **4 population-specific subsp. biglandulosa** and **2 subsp. alba** records, subject to a 300 comparable A/C/G/T site minimum.
- Neither 22 accessions nor 7 focal within-subspecies pairwise comparisons are biologically independent lineage-origin replicates. No confidence intervals, naïve pairwise permutation or four-locus original-paper replay is performed.

## B. Real intervention ratio versus the unobserved architecture payoff

Published [Ramsey, Vaughton & Peakall (2006)](https://doi.org/10.1111/j.1420-9101.2006.01129.x) recorded the relative **female seed-fitness advantage** as **3.7** under open pollination of females versus fruiting males; after increasing male outcrossing, this advantage was **1.4**. Source: [PubMed PMID 16910980](https://pubmed.ncbi.nlm.nih.gov/16910980/). Inbreeding depression of fruiting males' selfed offspring was >0.85.

This implies an **observed 3.7/1.4 ≈ 2.64-fold difference in the reported relative seed-fitness advantage** across source treatments. It does **not** identify the sum of male + female lifetime contributions or the construction/maintenance cost `K` of structural sexual separation.

Let `T` be the **unknown, conditional threshold** of seed-fitness advantage needed for a particular heritable female genotype to spread or persist, with male pollen transmission, selfing, seed quality and inherited sex determination all fixed by a specific model. Then:

```text
if T <= 1.4         both observed ratios are on/above threshold
if 1.4 < T < 3.7   ecological treatment moves the relative ratio across threshold
if T >= 3.7         both observed ratios are on/below threshold
```

Exactly at boundaries outcomes are neutral, not `above` or `below`; an appropriate genetic invasion model is needed to interpret equality.

**Counterfactual illustration 1:** an idealized **twofold** maternal-fitness advantage requirement for a biparentally inherited male-sterility locus under simple random-mating assumptions gives margins `3.7-2=+1.7` and `1.4-2=-0.6`, so treatment crosses the hypothetical threshold.

**Counterfactual illustration 2:** an idealized **onefold** requirement for a strictly maternally transmitted sterility determinant with no restorers/cytoplasmic costs gives both ratios `>1`, so treatment does **not** cross that threshold. Real nuclear-cytoplasmic systems have restorers and other costs, so this illustration is not a general CMS inference.

**IMPORTANT:** Wurmbea sex inheritance was not established by these ratios, and the high inbreeding depression changes generic nuclear maintenance criteria. Therefore **the observed treatment cannot be promoted to an actual heritable rare-invasion sign flip or full architecture-value crossing**. A twofold benchmark is a transparent test of sensitivity, not an identified Wurmbea genetic law. Literature context: [Varga (2021), female seed quality meta-analysis, DOI 10.1111/plb.13295](https://doi.org/10.1111/plb.13295); [Dufay & Billard (2012), female advantage review](https://pmc.ncbi.nlm.nih.gov/articles/PMC3278283/).

The runnable [threshold module](../balance_domain/wurmbea_fitness_threshold.py) preserves these conditions as explicit output and tests. It never labels the result `Phi`, `I_D`, `R`, `K`, an evolutionary rate or an observed ancestral state.

## C. Remaining irreducible gates

| Gate | Current evidence | Actual next independent requirement |
| --- | --- | --- |
| Source-matched population M/D | Table A1 voucher states and the published gene-tree | Verify ENA accession bytes and independent source metadata; distinguish population-level from species names |
| Structural trait origin | Source-reported minimum five gene-tree changes **without direction or confidence** | All four locus partitions, alternative topology/branch-length ensembles, nuclear markers, population-resolved taxonomic boundaries and ancestor-state uncertainty |
| Ecological female advantage | 3.7 vs 1.4 seed-fitness ratios under intervention | Female/male siring and viable offspring on the same lifetime scale, genotype-level inheritance and environmental effect interactions |
| SCH functional conflict | Selfing/inbreeding and resource-related sexual fitness effects observed in distinct experiments | Same manipulated phenotypic coordinate and simultaneous opposing male/female selection gradients |
| SLK/PAYOFF new structural advantage | Illustrative threshold sign may depend on inheritance | Viable shared/differentiated genotype architecture comparator, independent K, actual heritability and invasion trajectory |
| BITA mechanism allocation | Some mating/inbreeding and resource-mediated pathways measured | Selective mechanism contrasts under the same common-fitness surface |

**Scientific claim ceiling:** observed mating ecology can change reported relative female seed-fitness advantage, and published Wurmbea plastid vouchers support population-level sexual-state variation. Whether that caused the *historical evolutionary origin* of a new sex architecture remains unidentified. If this source genetic audit succeeds, it is a **necessary evidence-link and data-access validation**, not an evolutionary transition result.

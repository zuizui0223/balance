# Wurmbea 2008: actual ENA/GenBank source-voucher audit and bounded sex-state genetic contrasts

**Acquired and verified on 2026-10-19. Evidence status: `SOURCE_TABLE_ARCHIVE_DISCORDANCE_HELD` for focal multilocus data.** This is a real publicly deposited *plastid source audit*, NOT new sampling, a source-verified four-locus inferred phylogeny, or a test of the historical cause of sexual architecture evolution.

## Exact original sources and independent playback

- Case et al. (2008), *International Journal of Plant Sciences* 169:141–156, DOI [10.1086/523368](https://doi.org/10.1086/523368), [original author PDF](https://barrett.eeb.utoronto.ca/publications/files/2020/06/Case_et_al_IJPS169_141-156.pdf), Table A1.
- All **22 source-specified Australasian chloroplast ndhF accessions** successfully recovered from [ENA/INSDC](https://www.ebi.ac.uk/ena/browser/home) (12 original **M** gender-monomorphic, 10 **D** gender-dimorphic vouchers). FASTA header **accession identity** verified in 22/22, but original source-versus-archive **voucher number** independently verified in **21/22**. Legacy `AF547012` (*W. pygmaea*) lacks a source voucher string in its ENA header, and is therefore explicitly `ARCHIVE_VOUCHER_UNSPECIFIED`, not a voucher-identity positive.
- For the **six pre-registered focal vouchers** (MR1–MR4; AC53/AC38), Table A1 contains **23 expected accession–locus records** among `ndhF`, `atpB-rbcL`, `trnLF`, and `psbBTNH`; MR4 `trnLF` is missing **in the paper itself** and was not imputed.
- **23/23 ENA FASTA accessions downloaded**; **21/23 source-printed vs archive-voucher identities match**; two fail because of a reproducible two-record swap described below. The genotype comparison treats them as a **source metadata HOLD**.
- Latest complete [GitHub Actions original-source run 39272123560](https://github.com/zuizui0223/balance/actions/runs/39272123560): provenance regression tests, source recovery, source HOLD contract and complementary conditional fitness calculations **passed**. Aggregated-only artifact `12194339573`, digest `sha256:b78b66c6d0846c66db41e74438366c1fbd2ddf7d21939e702c025ee63761e244`. Original sequences were **not redistributed**.

## Critical primary-source provenance discrepancy

For `psbBTNH`, **Table A1 and ENA disagree**:

| Exact accession | Original paper's voucher | Deposited ENA header's voucher | Current disposition |
| --- | --- | --- | --- |
| [EU044681](https://www.ebi.ac.uk/ena/browser/view/EU044681) | MR2 (M, `M. Ramsey 2`) | MR3 (D, `M. Ramsey 3`) | **HOLD**, exclude strict voucher comparison |
| [EU044680](https://www.ebi.ac.uk/ena/browser/view/EU044680) | MR3 (D, `M. Ramsey 3`) | MR2 (M, `M. Ramsey 2`) | **HOLD**, exclude strict voucher comparison |

The code **does not silently 'repair'** a published biological sample to match a deposited string, or treat archive-record identity as evidence that either source is correct. Both interpretations are carried as separately labeled `ORIGINAL_TABLE_STRICT` (only independently concordant loci) versus **post-open `GENBANK_VOUCHER_ASSIGNMENT_SENSITIVITY`** (explicit 2-record swapped assignment), not pooled as biological replications.

## Strict source-voucher genetic comparisons

Site counts below are **aligned pairs with unambiguous A/C/G/T at both terminals** under the specified global pairwise gap-aware algorithm. The sites differ by pair and locus. They are not complete whole plastid genomes, genome-wide genotype identity, an original authors' tree or independently evolving loci.

| Same nominated taxon, M vs D source populations | Valid source-aligned loci | Exact A/C/G/T differences | Permitted inference |
| --- | --- | --- | --- |
| *W. biglandulosa* subsp. *biglandulosa*: **MR2 (M) vs MR4 (D)** | `ndhF` 1,107 and `atpB-rbcL` 521, **1,628 total** | **0/1,628** | Opposing sex states co-occur on plastid regions with identical aligned A/C/G/T in these TWO loci |
| *W. dioica* subsp. *alba*: **AC53 (M) vs AC38 (D)** | `ndhF`, `atpB-rbcL`, `trnLF`, `psbBTNH`, **5,004 total** | **16/5,004** | Different populations/sexual systems show small but nonzero sampled plastid differences |

**MR2/MR4**: the original paper does not provide MR4 `trnLF`; MR2's paper-assigned `psbBTNH` accession contradicts the ENA source voucher. Therefore a previous initial output of **0/3,709 sites across three loci** (which followed paper-only assignments) has been **superseded**, not retained as a primary source-verified genetic result.

### Post-open alternative, not source adjudication

If, solely as a sensitivity, `EU044680` is assigned to **MR2** and `EU044681` to **MR3** according to the **ENA** voucher labels, then the otherwise fixed MR2 (M) – MR4 (D) comparison covers three observed loci totaling **3,709** aligned A/C/G/T site pairs with **1 mismatch** (the `psbBTNH` component); `trnLF` remains missing.

The two feasible source readings give **0/1,628 strict sites**, versus **1/3,709 under the archive-voucher-only reallocation**. These have **different denominators**; subtracting them is not a biological effect estimate, nor can either establish identity of complete chloroplast haplotypes. The appropriate result is a *low-divergence, voucher-metadata-conditioned population comparison*, not a validated population transition or new-module origin.

## Original historical interpretation and limits

The published Case et al. study reports a minimum of **five sexual-system changes** under its plastid-based reconstruction, but roots, directions and some topology/ancestral assignments were not securely resolved; sex-state polymorphism of source-named species and possible non-monophyly remain central caveats.

The current source analysis is **pairwise, not a fully re-estimated original four-locus gene tree**. Repeated pairwise contrasts over shared voucher terminals are not independent evolutionary changes, and a plastid genealogy does not identify the nuclear sex-determining architecture. Multiple sex states near the same plastid genotype are compatible with repeated or recent change, ancestral polymorphism, introgression, sex phenotype plasticity and sampling; this audit cannot choose among these alternatives.

## Strong biological alternative: sex expression can switch within a marked living plant

An independent original longitudinal *W. dioica* study by **Barrett, Case & Peters (1999)**, [*Journal of Ecology*, DOI 10.1046/j.1365-2745.1999.00336.x](https://doi.org/10.1046/j.1365-2745.1999.00336.x), followed sex expression in the same population over two flowering seasons (1981 and 1983) and also observed **marked individuals**. The female population fraction stayed approximately stable (**48.6% of 211 in 1981; 48.9% of 230 in 1983**), while phenotypic males declined from **43.1% to 29.6%** and plants with hermaphroditic flowers increased from **8.3% to 21.5%**. The study reports that **approximately half of marked plants expressed as male in 1981 and also flowering in 1983 developed hermaphroditic flowers**, whereas females that flowered in both years retained their sex phenotype. These original-study changes are *within the lifetime of marked individuals* and therefore **cannot represent new genetic architecture origins between species or independent macroevolutionary transitions**.

This source supplies an important ecological alternative to a naive interpretation of plastid sex-state association: a population or individual can change its *observed phenotypic sexual expression* under ecology/size/resource-mediated plasticity **without a new mutation or transition in nuclear sex-determination machinery**. The observed source data do **not**, by themselves, establish the immediate physiological causal trigger of each 1981→1983 state change or explain a difference among the distinct Case (2008) voucher populations. They do, however, invalidate assuming a morphological "M" or "D" observation is a permanently canalized heritable architecture state.

A separate original high/low resource manipulation in *Wurmbea* by Vaughton & Ramsey (2011), [DOI 10.1093/aob/mcr163](https://doi.org/10.1093/aob/mcr163), further reports that **66%** of phenotypic males in sub-dioecious *W. dioica* expressed perfect flowers under high resources versus **42%** under low resources; dioecious-population phenotypic males did not show the same gender plasticity. This is a genotype/environment conditional *phenotypic allocation* result, not direct evidence of new structural modules.

**Causal consequence:** test whether the ecological regime changes the distribution of **reversibly expressed sexual states** before interpreting population structure or cpDNA variants as fixed evolutionary states. The next experimental design must separate `sex_expression_within_individual`, `inherited_nuclear_sex_architecture`, and `phylogenetic_origin` as three different response variables. The original 1999 and 2011 studies are **two source programmes**, not 2008 cpDNA source experimental replications.

### Source-level context: plasticity costs differ across sex systems

The independently organized [original *Wurmbea* sex allocation source comparison](BALANCE_WURMBEA_FUNCTIONAL_COST_HETEROGENEITY_V1.md) records the **same study's** three sexual-system populations with both males and hermaphrodites. Phenotypic males made ~2x as much pollen per flower as hermaphrodites in subdioecious *W. dioica* but ~40% less in two *W. biglandulosa* populations. Negative partial associations of female perfect-flower expression with male pollen/flower size were confined to the subdioecious population. This is a **source-supported heterogeneity of male-component payoff proxies**, not independent multiple-source confirmation of a genetic cost of plasticity, a matched lifetime-fitness balance, or evidence of sexual-system origins.

## Ecological payoff gate remains separate

The **source-published** maternal seed-fitness advantage of females relative to fruiting males in *W. dioica* was **3.7 versus 1.4** after manipulated male outcrossing. [Ramsey et al. 2006](https://doi.org/10.1111/j.1420-9101.2006.01129.x). That is a `2.64`-fold relative ratio change, not a general fecundity or population invasion measurement.

An **assumed** simple nuclear inheritance threshold `T=2` lies between 1.4 and 3.7, whereas an idealized maternal `T=1` lies below both. The observed eco-treatment crosses **only thresholds strictly between 1.4 and 3.7**. The actual *Wurmbea* fitness/inheritance threshold and `L, R, K, Phi, eta` are **not empirically identified** by these published seed ratios.

## Next tests and claim ceiling

- **Real primary-source correspondence achieved:** original voucher/source sex M/D, deposited exact plastid accessions and controlled post-open swaps, including 21/23 focal proven table-voucher matches.
- **New real empirical pattern:** distinct sex-system states in sampled *Wurmbea* populations need not be distinguished by the two strictly paired plastid loci; another sex-polymorphic subspecies exhibits differences across four aligned plastid loci.
- **Irreducible empirical missing pieces:** adjudication of the two exact ENA/paper voucher conflicts; population nuclear haplotypes and sex-determination heritability; an independently rooted/time-resolved species tree; aligned pollen-siring and offspring contributions for each sex/genotype; direct comparison of *shared versus differentiated* structural costs and viability under manipulated mating ecology.
- **Prohibited:** claiming an experimentally demonstrated trade-off caused the historic origin of sex-separated architecture, claiming 22 source accessions equal 22 independent origins, or calling a hypothetical threshold crossing an observed genotype invasion.

Canonical scope: SCH identifies causal opposing gradients on a shared axis; BALANCE identifies persistent compromise and matched alternative structural worldlines when available; SLK/PAYOFF require architecture value/accessibility; BITA identifies ecological interaction mechanisms without mistaking a statistical trait interaction for the originating mechanism.

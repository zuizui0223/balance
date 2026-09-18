# BALANCE plant U1 source-resolution audit v4

## Current state

The U1 outcome-blind entry surface now has a complete primary-source resolution for the **provisional first 20 network-visible taxon labels**.

```text
full review-reported plant taxa        47
Figure 4 network-visible taxon labels  44
supplement-only taxa still to recover   3

provisional first-20 source-ready       20 / 20
taxon-grain conflicts                    0
formal double-code sample frozen?       NO
```

The sample is not frozen because the three review taxa omitted from Figure 4 can alter the lexicographic first-20 dependency-group sample once the complete 47-taxon universe is reconstructed.

## Figure 4 correction

The first manual Figure 4 extraction contained one concrete error:

```text
incorrect extra label: Alstroemeria ligtu
missing label:         Tristerix aphyllus
```

The corrected network-visible universe contains one label:

```text
Alstroemeria ligtu var. Simsii
```

and includes `Tristerix aphyllus`.

The corrected lexicographic first-20 network-visible labels are U1_001 through U1_020 and end with `Cynanchum diemii`.

This removed the apparent *Alstroemeria* taxon-grain conflict; it was an extraction duplication, not a biological ambiguity.

## Final three first-20 source resolutions

### Brassica napus

Kirk, Ali & Breadmore (1995), *Journal of Apicultural Research* 34:15–22.

DOI:

```text
10.1080/00218839.1995.11100881
```

The primary field study directly tests how pollen beetles (*Meligethes aeneus*) in oilseed rape flowers affect honey-bee landing and foraging behaviour, including larval effects on nectar.

### Clarkia xantiana ssp. xantiana

Benning & Moeller (2019), *Evolution* 73:2044–2059.

DOI:

```text
10.1111/evo.13836
```

The reciprocal-transplant experiment manipulates biotic context across a range gradient. Protection from herbivory together with pollen supplementation produced large lifetime-fitness gains outside the range margin.

### Cucumis melo

Strauss & Murch (2004), *Ecological Entomology* 29:234–239.

DOI:

```text
10.1111/j.0307-6946.2004.00587.x
```

The cantaloupe experiment independently manipulates plant damage and pollination. Supplemental pollination restored fruit production in damaged plants, directly linking herbivore damage, pollination and reproduction.

## Interpretation of 44 versus 47

Haas & Lortie (2020) report 47 plant taxa across the full 59-study review.

Figure 4 is not a complete plant list. Its caption explicitly excludes plant species from studies in which no actual herbivore or pollinator taxon was used, for example simulated herbivory combined with hand-pollination measurements.

Therefore:

```text
44 network-visible labels
!=
47 full-review taxa
```

is not evidence of a remaining Figure 4 extraction error.

The remaining task is to recover the three additional plant taxa from the supplementary study/species tables.

## Freeze rule

The current 20 rows remain:

```text
SOURCE_READY_SAMPLE_NOT_FROZEN
```

Formal independent double coding begins only after:

1. all 47 full-review taxa are reconstructed;
2. duplicate/taxonomic grain is reconciled across the 47;
3. the first 20 dependency groups are recomputed from that complete universe;
4. every resulting sampled group has a resolved primary source.

This avoids replacing difficult records and preserves the outcome-blind sampling rule.

## Current scientific significance

U1 is now an actual denominator-building workflow rather than a collection of known positive examples:

```text
systematic-review membership
-> full taxon reconstruction
-> deterministic sample selection
-> primary-source resolution
-> independent coding
-> adjudication
-> analysis eligibility
```

No U1 species has been promoted to BALANCE-positive or to the confirmatory model merely because its primary paper was found.

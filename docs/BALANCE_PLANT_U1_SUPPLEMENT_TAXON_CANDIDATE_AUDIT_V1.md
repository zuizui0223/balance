# BALANCE plant U1 supplement-only taxon candidate audit v1

## Purpose

Prevent the unresolved difference between the 47 plant taxa reported by Haas & Lortie (2020) and the 44 Figure-4 network-visible plant labels from being closed by guesswork.

The candidate registry is:

```text
data/BALANCE_PLANT_U1_SUPPLEMENT_TAXON_CANDIDATES_V1.csv
```

None of its rows are part of the canonical U1 universe.

## Why Figure 4 is incomplete by design

Haas & Lortie report 47 plant taxa across 59 included studies. Their Figure 4 omits plant species from studies in which no actual herbivore or pollinator taxon was used, including artificial-herbivory / hand-pollination designs. Therefore three full-review taxa can be absent from the 44 network-visible labels without any extraction error.

## Current candidates

### High-confidence candidate — Cucurbita pepo ssp. texana

Avila-Sakar et al. (2003) is explicitly cited by the review when discussing vegetative herbivory and pollen production. The plant is absent from the corrected Figure 4 label set, and the experiment used imposed leaf damage.

This is consistent with a supplement-only taxon, but consistency is not Table-S1 membership proof.

### High-confidence candidate — Nemophila menziesii

McCall (2010) is explicitly cited in the review discussion of floral damage and pollination-related consequences. The species is absent from Figure 4 and the experimental design is compatible with the class omitted from the network.

Again, exact Table-S1/Table-S2 linkage remains required.

### Medium candidate — Mimulus luteus

Pohl et al. (2006) is a classic artificial floral-damage / hummingbird-pollination experiment and is cited repeatedly in later florivory syntheses that cite Haas & Lortie.

However, the currently accessible Haas & Lortie article surface has not yielded a direct Pohl-to-review mapping. It therefore remains a weaker candidate and cannot be used to complete the 47 taxa.

### Low candidate — Mimulus guttatus

Retained only as a discovery alternative because later meta-analyses contain Mimulus systems. No direct U1 study linkage has been recovered.

## Promotion rule

A candidate becomes `CONFIRMED_SUPPLEMENT_TAXON` only with one of:

1. direct Haas & Lortie Supplemental Information 1 taxon listing;
2. Supplemental Information 2 study-species mapping;
3. Figshare dataset mapping demonstrably equivalent to those supplemental tables.

Article-body citation alone is insufficient.

## Freeze rule

U1 cannot set

```text
double_code_sample_frozen = true
```

from this candidate registry.

The complete full-review universe must contain exactly 47 reconciled plant dependency groups, including exactly three source-confirmed supplement-only taxa, before the first-20 sample is recomputed.

This explicitly separates:

```text
biologically plausible candidate
!=
review-universe membership
```

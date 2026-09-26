# BALANCE U3 prospective routing expansion queue v6

## Queue reopened by provenance repair

The original four-family prospective expansion reached evidence ceilings without dropping any family. A later provenance repair replaced the post-review Scrophulariaceae representative with the pre-2010 independent representative `Diascia anastrepta`.

Because the frozen selection rule is:

```text
ALL_INDEPENDENT_SPECIES_REPRESENTATIVES_OUTSIDE_EXISTING_MATCHED_FAMILIES
SORT_FAMILY_LEXICOGRAPHIC
```

Scrophulariaceae now becomes an eligible fifth dependence block. It cannot be omitted merely because the previous four-row queue had been called exhausted.

Current queue:

```text
1  Bixaceae          Amoreuxia wrightii    EVIDENCE_CEILING_BLOCKED
2  Brassicaceae      Brassica rapa          EVIDENCE_CEILING_BLOCKED
3  Lythraceae        Lagerstroemia indica   EVIDENCE_CEILING_BLOCKED
4  Malvaceae         Mollia lepidota        EVIDENCE_CEILING_BLOCKED
5  Scrophulariaceae  Diascia anastrepta     IN_PROGRESS
```

## Why Diascia is a high-information next case

Manning & Brothers (1986) directly document marked heteranthery in `D. anastrepta`. The same field study also documents effective `Rediviva politissima` pollination and pollen placement in three congeneric species with different stamen configurations:

- `D. cordata`
- `D. barberae`
- `D. integerrima`

That makes the new block unusually useful for a blinded matched-control search: candidate ecology is already source-rich before any BALANCE routing outcome is extracted.

The source also notes that the four Diascia species occupy different morphological groups within section Racemosae, so no candidate is promoted by convenience. Heteranthery absence and relative phylogenetic proximity still require explicit adjudication.

## Frozen progression

The previous four evidence-ceiling rows remain retained as missing dependence blocks. The fifth row is the only active search. No earlier row is reopened or replaced by an easier case.

```text
prospective_queue_exhausted = false
new dependence blocks        = 5
blocked prior blocks          = 4
active case                   = Diascia anastrepta
```

## Claim ceiling

This queue update follows a pre-existing selection rule after a provenance improvement. It is not a control selection, conflict result, routing result, prevalence estimate, or historical transition inference.

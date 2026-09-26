# BALANCE plant U1 supplement-taxon candidate audit v2

## Purpose

Update the unresolved 47-versus-44 reconciliation without pretending that article-level triangulation is equivalent to the unavailable Supplemental Information 1/2 mapping.

Canonical candidate registry:

```text
data/BALANCE_PLANT_U1_SUPPLEMENT_TAXON_CANDIDATES_V1.csv
```

None of these candidates is added to the canonical U1 universe in this version.

## What is now strongly constrained

Haas & Lortie (2020) report 47 plant taxa across the 59-study review, whereas Figure 4 exposes 44 plant labels. The Figure 4 caption explicitly excludes plant species from studies where no actual herbivore or pollinator taxon was used, including artificial herbivory and hand-pollination designs.

Three article-linked empirical systems fit this omission logic unusually well and are absent from the corrected 44-label network.

### Cucurbita pepo ssp. texana

Avila-Sakar et al. (2003) is explicitly used by the review synthesis when discussing vegetative herbivory effects on pollen production.

The experiment imposes simulated leaf damage and measures male reproductive traits. The taxon is absent from Figure 4.

Status:

```text
VERY_HIGH
ARTICLE_TRIANGULATED_NOT_SUPPLEMENT_CONFIRMED
```

### Nemophila menziesii

McCall (2010) is explicitly cited in the review discussion of dose-dependent floral damage and pollen limitation.

The primary experiment crosses six levels of artificial petal damage with pollen addition. The taxon is absent from Figure 4.

Status:

```text
VERY_HIGH
ARTICLE_TRIANGULATED_NOT_SUPPLEMENT_CONFIRMED
```

### Eichhornia crassipes

This is the strongest article-body inclusion signal.

The Haas & Lortie Results explicitly name Buchanan (2015) among the included studies when describing publications that compared multiple vegetative herbivory types.

Buchanan (2015) uses manual leaf/apical/axillary damage and a hand-pollination treatment in *Eichhornia crassipes*. The species is absent from Figure 4.

Status:

```text
VERY_HIGH
ARTICLE_TRIANGULATED_NOT_SUPPLEMENT_CONFIRMED
```

## Why this still does not close the universe

The equality

```text
44 network-visible labels
+ 3 strongly triangulated candidates
= 47 reported taxa
```

is compelling but remains an inference.

The existing freeze contract requires one of:

1. direct Supplemental Information 1 plant-taxon listing;
2. Supplemental Information 2 study-species mapping;
3. Figshare data demonstrably equivalent to those tables.

Until one of those surfaces is recovered:

```text
double_code_sample_frozen = false
```

remains correct.

## Candidates downgraded relative to v1

*Mimulus luteus* remains biologically compatible with the omitted-study class, but the accessible Haas & Lortie article does not directly cite Pohl et al. (2006). It is therefore a low-confidence discovery alternative rather than one of the three article-triangulated leading candidates.

*Mimulus guttatus* remains discovery-only.

## Programme consequence

U1 no longer blocks useful scientific work.

Its formal reliability sample remains unfrozen, but the source-ready provisional first 20 can continue to serve as a codebook-specificity audit. The first screen already shows that broad herbivory-pollination literature has low yield for the stricter shared-reproductive-coordinate estimand.

The confirmatory plant programme should therefore continue building independent, mechanism-targeted universes (such as U2 sexual interference) while U1 supplement recovery remains open.

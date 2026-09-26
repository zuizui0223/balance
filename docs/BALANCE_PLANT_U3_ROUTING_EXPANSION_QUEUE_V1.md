# BALANCE U3 prospective routing expansion queue v1

## Purpose

Freeze the order of new U3 case families **before** prospective control conflict or routing outcomes are examined.

The current public-evidence ceilings for `Senna covesii`, `Osbeckia chinensis`, and the two Monochoria pollination gates are already frozen. Additional routing information must therefore come from new direct evidence or new prospectively matched dependence blocks.

## Eligibility rule

Starting from the 16-family U3 review universe:

1. exclude families already represented in the current matched lane;
2. require a species-level representative already coded `SOURCE_RESOLVED_INDEPENDENTLY`;
3. require a frozen source basis for that representative;
4. sort the eligible families lexicographically;
5. freeze the order before any prospective control's conflict or routing architecture is extracted.

This yields:

```text
1  Bixaceae        Amoreuxia wrightii
2  Brassicaceae    Brassica rapa
3  Lythraceae      Lagerstroemia indica
4  Malvaceae       Mollia lepidota
```

`Scrophulariaceae` is not in this queue because its current representative is explicitly post-review. Body-text genus-only representatives are not promoted to species cases merely to enlarge the sample.

## Anti-selection rule

A difficult or failed control search is informative. The queue may not skip a case because a later family supplies a more convenient routing category.

For each queued case, the existing matched-control hierarchy still applies:

```text
C1  nearest nonheterantherous congener
C2  nearest same tribe/subfamily relative
C3  same-family widening with explicit receipt
```

Allowed matching information remains limited to taxonomy/phylogeny, heteranthery absence, source availability, and minimal animal-pollination eligibility.

Conflict strength, module substrate, timing/spatial geometry, and routing architecture remain hidden until the control identity is frozen.

## First active case

The active prospective expansion case is:

```text
Amoreuxia wrightii
Bixaceae
new dependence block: U3_DEP_BIXACEAE_01
```

No control is yet promoted by this queue.

## Executable surfaces

```text
data/BALANCE_PLANT_U3_ROUTING_EXPANSION_QUEUE_V1.csv
balance_domain/plant_u3_routing_expansion.py
tests/test_plant_u3_routing_expansion.py
```

## Claim ceiling

This queue freezes acquisition order and protects predictor blindness. It does not establish control eligibility, conflict presence, routing architecture, effect size, or prevalence.

# BALANCE plant U1 reference-level reconstruction audit v1

## Purpose

The U1 full-review universe reports 47 plant taxa, while Figure 4 exposes 44 network-visible plant labels.

The current programme does **not** close the remaining three taxa by arithmetic alone.

Instead, evidence for non-network taxa is classified at reference level and promotion is fail-closed.

## Current leading non-network candidates

### Eichhornia crassipes — strongest article-body signal

Buchanan (2015) is explicitly named in the Haas & Lortie Results among the reviewed herbivory studies.

The primary experiment crosses manual leaf/apical/axillary damage with hand-pollination treatments in *Eichhornia crassipes*.

Because the design has no named natural herbivore or pollinator taxon for the relevant treatments, absence from Figure 4 is expected.

Status:

```text
ARTICLE_BODY_INCLUDED_NONNETWORK
SUPPLEMENT_CONFIRMATION_REQUIRED
```

### Nemophila menziesii — strong mechanistic-citation candidate

McCall (2010) crosses artificial floral damage with pollen addition and measures pollen limitation/female fitness.

The review cites the study in its florivory/pollen-limitation synthesis.

Status:

```text
ARTICLE_TRIANGULATED_NONNETWORK
SUPPLEMENT_CONFIRMATION_REQUIRED
```

### Alstroemeria exerens — strong mechanistic-citation candidate

Suárez et al. (2009) links foliar damage to floral attractiveness and pollinator visitation.

The review uses the study in its mechanistic synthesis. Because damage is not assigned to a named herbivore taxon, Figure 4 omission is compatible with the network construction rule.

DOI:

```text
10.1007/s10682-008-9254-4
```

Status:

```text
ARTICLE_TRIANGULATED_NONNETWORK
SUPPLEMENT_CONFIRMATION_REQUIRED
```

## Downgraded candidate: Cucurbita pepo ssp. texana

Avila-Sakar et al. (2003) is relevant to herbivory effects on male reproductive function, but the primary experiment measures simulated leaf damage, anther development and pollen production rather than pollinator visitation, pollen receipt or a direct pollination treatment.

The study may still occur in the review source set, but article-level evidence is insufficient to identify it as one of the three non-network taxa.

Therefore its previous `VERY_HIGH` classification was too strong.

## Freeze contract

A taxon absent from Figure 4 can enter the canonical 47-taxon U1 universe only when:

```text
coverage_status = SUPPLEMENT_CONFIRMED_NONNETWORK
and
full47_promotion_status = CANONICAL_SUPPLEMENT_ONLY
```

Article-body inclusion or mechanistic citation alone is not sufficient.

Current state:

```text
canonical supplement-only taxa = 0 / 3
leading candidates             = 3
formal full-47 closure         = OPEN
```

This prevents an attractive 44 + 3 numerical match from being mistaken for direct source reconstruction.

## Scientific consequence

U1 can continue serving as a specificity universe even while full-47 reconstruction remains open.

The provisional first-20 screen already shows:

```text
herbivory x pollination interaction
!=
shared-reproductive-coordinate functional conflict
```

because most source-ready U1 systems fail the shared-coordinate S0 gate.

The missing-three reconstruction therefore affects the formal reliability-sample freeze, not the validity of that provisional specificity observation.

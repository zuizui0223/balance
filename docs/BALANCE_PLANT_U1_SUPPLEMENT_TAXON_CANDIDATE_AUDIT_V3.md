# BALANCE plant U1 supplement-taxon candidate audit v3

## Status

This version supersedes v2 for the 47-versus-44 reconciliation status.

The key change is that the missing source surfaces are no longer treated as unidentified. The PeerJ/PMC article exposes the registered supplementary-object identifiers, and the article also identifies the associated Figshare dataset.

The source surfaces are now frozen as:

```text
Supplemental Information 1
DOI: 10.7717/peerj.9049/supp-1
content: list of all pollinator, herbivore and plant species in the review
format: DOCX
status: LOCATED_NOT_INGESTED

Supplemental Information 2
DOI: 10.7717/peerj.9049/supp-2
content: analysis type, species and outcome for each relevant analysis in each included study
format: CSV
status: LOCATED_NOT_INGESTED

Figshare dataset
DOI: 10.6084/m9.figshare.12397772.v1
status: LOCATED_NOT_INGESTED
```

Canonical machine-readable receipt:

```text
data/BALANCE_PLANT_U1_SUPPLEMENT_SOURCE_RECOVERY_V1.json
```

## What has not changed

The canonical universe still contains 44 Figure-4 network-visible plant labels while Haas & Lortie report 47 plant taxa.

Therefore:

```text
reported taxa              = 47
network-visible taxa       = 44
reconciliation gap         = 3
canonical U1 universe      = OPEN
double-code frame frozen   = false
```

Locating the supplementary surfaces is not equivalent to parsing them. No candidate is promoted from article-level triangulation alone.

## Corrected candidate ranking

v2 contained a prose inconsistency: the CSV registry had already downgraded *Cucurbita pepo* ssp. *texana* to MEDIUM confidence, while the narrative still displayed it as VERY_HIGH.

The canonical registry is authoritative.

Current article-level candidate state is:

```text
VERY_HIGH
- Nemophila menziesii
- Eichhornia crassipes
- Alstroemeria exerens

MEDIUM
- Cucurbita pepo ssp. texana

LOW
- Mimulus luteus
- Mimulus guttatus
```

The three VERY_HIGH candidates are attractive because their study designs fit the Figure-4 omission rule and the review article links them to the synthesis. But the numerical coincidence of three high-confidence candidates and a three-taxon reconciliation gap is not used as evidence of identity.

## Freeze rule

Promotion requires direct supplement-equivalent membership evidence.

At least one of the following must be ingested and reconciled reproducibly:

1. Supplemental Information 1 plant-taxon listing;
2. Supplemental Information 2 study-species mapping;
3. raw Figshare data demonstrably equivalent to those tables.

Only after the direct source surface reproduces all 47 plant taxa may the missing three taxa be written into the canonical U1 universe and the deterministic first-20 dependency-group double-code frame be recomputed.

## Why this is progress

The blocker has changed from:

```text
unknown / inaccessible supplementary mapping
```

to:

```text
identified source objects, bytes not yet ingested
```

That removes ambiguity about what evidence is needed next and prevents article-level candidate inference from silently becoming confirmatory membership.

## Claim ceiling

This audit supports only source-surface recovery and candidate-priority bookkeeping.

It does not confirm any candidate as one of the three missing review taxa, does not alter the canonical 44-row universe, and does not freeze the U1 confirmatory or reliability sample.

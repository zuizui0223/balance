# BALANCE plant U3 heteranthery review universe audit v2

## Purpose

U3 is anchored to Vallejo-Marín et al. (2010), *Trait correlates and functional significance of heteranthery in flowering plants* (New Phytologist 188:418–425; DOI `10.1111/j.1469-8137.2010.03430.x`).

The review intentionally identifies heteranthery-positive families. U3 is therefore an outcome-selected structural-positive discovery surface, not a prevalence denominator.

## Review-defined universe

Figure 2 fixes exactly:

```text
16 heteranthery-positive families
12 orders
```

All 16 family representatives now have a source-resolved representative at an explicit provenance level:

```text
BODY_TEXT_NAMED                         11
SOURCE_RESOLVED_INDEPENDENTLY            4
SOURCE_RESOLVED_INDEPENDENTLY_POST_REVIEW 1
TABLE_S1_REPRESENTATIVE_PENDING          0
TOTAL                                   16
```

The inaccessible Wiley Supporting Table S1 itself has **not** been recovered. Direct automated recovery attempts are preserved separately and returned HTTP 403. Nothing below is represented as a Table-S1 transcription.

## Independently resolved representatives

### Pre-2010 independent evidence

```text
Lythraceae      Lagerstroemia indica
Brassicaceae    Brassica rapa
Malvaceae       Mollia lepidota
Bixaceae        Amoreuxia wrightii
```

These are registered as `SOURCE_RESOLVED_INDEPENDENTLY`.

For Malvaceae, the evidence chain is independent of the inaccessible supplement: Darwin/Spruce-era observations plus the 1978 *Mollia* treatment resolve differentiated stamen cohorts in `Mollia lepidota`. The repository does not claim this proves that the 2010 Table S1 printed that exact species.

For Bixaceae, `Amoreuxia wrightii` is independently source-resolved with two dimorphic fertile-stamen sets. The APG-family mapping is consistent with the 2010 review's treatment of Bixaceae.

### Post-review independent evidence

```text
Scrophulariaceae  Verbascum phoeniceum
```

This row is deliberately coded `SOURCE_RESOLVED_INDEPENDENTLY_POST_REVIEW`.

The species is an independently documented Scrophulariaceae heteranthery representative, but it is **not** asserted to be the exact representative species printed in the inaccessible 2010 Table S1.

## What is closed and what remains archival

Closed for the current BALANCE programme:

```text
Figure-2 family membership                    16 / 16
representative-family coverage                16 / 16
representative provenance explicit            16 / 16
Table-S1 representative pending                0 / 16
```

Still archival/open:

```text
exact recovery of NPH_3430_sm_TableS1.doc
exact verification of the species names printed there
for Malvaceae, Bixaceae and Scrophulariaceae
```

That archival question does not block the current matched-control or routing programme, because those analyses use separately source-resolved species cases and frozen control-selection receipts.

## Anti-bias rule

Every U3 family remains:

```text
analysis_role = POSITIVE_ARCHITECTURE_DISCOVERY_ONLY
```

Representative resolution does not convert the 16-family review into an outcome-blind denominator.

## Current empirical role

The matched species lane now asks a different question from the 2010 family-level correlate analysis:

> conditional on independently demonstrated pollen-reward versus gamete-transfer conflict, where is that conflict routed, and is morphological heteranthery required for that routing state?

This avoids repackaging the published associations with poricidal anthers, nectary state or enantiostyly as BALANCE novelty.

## Claim ceiling

U3 has complete representative-family coverage for programme bookkeeping and prospective matching.

It does not estimate heteranthery prevalence, does not claim Table S1 was inspected, and does not identify the historical cause of any heteranthery transition.

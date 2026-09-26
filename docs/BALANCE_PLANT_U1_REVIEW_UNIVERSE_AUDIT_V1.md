# BALANCE plant U1 review universe audit v1

## Purpose

Register an outcome-blind plant screening entry surface independently of the pre-existing BALANCE-positive literature ledgers.

## Source universe

U1 is anchored to:

- Haas SM & Lortie CJ (2020), *PeerJ* 8:e9049;
- DOI: 10.7717/peerj.9049;
- systematic search: 4,304 unique records -> 117 full texts -> 59 included studies;
- the review reports **47 plant taxa** across the included studies.

The review's Figure 4 network exposes plant names without conditioning on BALANCE conflict or architecture outcome.

## Current machine-readable extraction

The accessible Figure 4 text yielded **44 named plant taxon labels** that were registered in:

```text
data/BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv
```

No conflict state, architecture mode or predictor value is coded in this universe file.

Every row begins as:

```text
screening_status      = UNSCREENED
primary_source_status = SOURCE_RESOLUTION_PENDING
```

Existing BALANCE overlap is recorded only as a provenance flag and does not change inclusion.

## Reconciliation gap

The source review reports 47 plant taxa, whereas the current accessible network extraction contains 44 taxon labels.

Therefore:

```text
U1_SOURCE_REVIEW_REPORTED_TAXA = 47
U1_CURRENT_EXTRACTED_TAXA      = 44
U1_RECONCILIATION_GAP          = 3
```

The U1 frame is **not frozen for confirmatory analysis** until the three missing source taxa are recovered from the review supplementary files or otherwise reconciled.

Do not silently replace the missing taxa with easier or more familiar BALANCE systems.

## Independent double-coding sample

The first coder-agreement sample is fixed mechanically as the first 20 dependency groups after lexicographic taxon ordering.

Registered file:

```text
data/BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv
```

The sample is not outcome-selected.

A sampled group remains in place even if source resolution is difficult. Its double-coding state remains blocked until the primary study or studies linked by the systematic review are resolved.

## Why this improves the programme

The earlier 29-record plant pilot deliberately stress-tested all architecture categories and is therefore not a valid confirmatory denominator.

U1 reverses that logic:

```text
systematic-review membership
-> source resolution
-> multifunctionality/conflict screen
-> architecture coding
```

rather than:

```text
interesting architecture
-> search for a supporting paper
```

This is the first actual outcome-blind denominator surface in the BALANCE macro programme.

## Claim ceiling

U1 membership means only that the taxon occurred in a systematic review of herbivory effects on animal-mediated pollination.

It does not mean that:

- the same floral coordinate experiences opposing pollinator and herbivore selection;
- BALANCE conflict is present;
- a particular architecture is a conflict-resolution adaptation;
- the taxon is primary-model eligible.

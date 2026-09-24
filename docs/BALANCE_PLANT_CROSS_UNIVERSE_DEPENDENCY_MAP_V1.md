# BALANCE plant cross-universe dependency map v1

## Purpose

U1 (Haas & Lortie 2020) and U2 (Barrett 2002) are independently constructed, outcome-blind review universes. Review membership is bibliographic provenance, not biological replication.

The union is therefore frozen at the **dependency-group** level before any combined analysis.

## Frozen source-closed union

Direct U1 Figshare reconciliation closed U1 at 47 plant taxa. U2 is source-closed at 22 dependency groups.

```text
U1 full-review groups          47
U2 source-closed groups        22
raw review memberships         69
cross-universe overlaps         2
unique biological groups       67
```

The two exact cross-review overlaps remain:

```text
Ipomopsis_aggregata
Mimulus_aurantiacus
```

Each retains both review record IDs but contributes one biological dependency group.

The three newly recovered U1 supplement-only taxa enter once each:

```text
Eichhornia_crassipes
Nemophila_menziesii
Ruellia_nudiflora
```

## Canonical contract

```text
data/BALANCE_PLANT_CROSS_UNIVERSE_DEPENDENCY_MAP_V1.csv
balance_domain/plant_universe_union.py
```

Every row now carries:

```text
FROZEN_SOURCE_CLOSED_U1_FULL47_PLUS_SOURCE_CLOSED_U2
```

This prevents a later analysis from silently falling back to the obsolete 44-label U1 surface.

## Screening state versus denominator state

The denominator is source-closed, but source screening is intentionally asymmetric:

- U1 has a frozen, source-ready first-20 reliability frame; later U1 taxa remain unscreened;
- U2 has conservative source screening for all 22 groups.

Therefore source closure does not imply that every one of the 67 groups is conflict-adjudicated.

## Claim ceiling

The frozen union supports unique biological group counts, cross-review overlap accounting, and prevention of bibliographic pseudoreplication.

It does not support natural prevalence, conflict prevalence across flowering plants, or a confirmatory macro coefficient before independent coding and remaining mechanism gates close.

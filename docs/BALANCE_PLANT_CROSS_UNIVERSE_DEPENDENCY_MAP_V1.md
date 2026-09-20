# BALANCE plant cross-universe dependency map v1

## Purpose

The plant macro programme now has two independently constructed discovery universes:

- U1: Haas & Lortie (2020) herbivory-pollination universe;
- U2: Barrett (2002) sexual-interference universe.

Review membership is bibliographic provenance, not biological replication.

The union must therefore be formed at the **dependency-group** level before any combined analysis.

## Current union

Current registered surfaces:

```text
U1 network-visible groups    44
U2 source-closed groups      22
raw review memberships       66
cross-universe overlaps       2
unique biological groups     64
```

The two exact overlaps are:

```text
Ipomopsis_aggregata
Mimulus_aurantiacus
```

They retain both review memberships and both source record IDs, but each occupies one biological dependency-group row.

## Canonical file

```text
data/BALANCE_PLANT_CROSS_UNIVERSE_DEPENDENCY_MAP_V1.csv
```

Validator:

```text
balance_domain/plant_universe_union.py
```

## Why this matters

Without this layer, a species cited by both a broad herbivory-pollination review and a sexual-interference review could be counted twice merely because it entered through two literature routes.

The macro unit is biological:

```text
review memberships
-> dependency group
-> one biological contribution
```

not:

```text
review memberships
-> independent replication
```

## Current frame ceiling

The union is still provisional because U1 currently contains the 44 Figure-4 network-visible labels rather than the reconstructed full 47-taxon review universe.

Therefore the current 64-group union is a bookkeeping surface, not a frozen confirmatory denominator.

When the three U1 supplement-only taxa are recovered:

1. append/reconcile them in U1;
2. rerun dependency-group matching;
3. recompute cross-universe overlaps;
4. version the union;
5. only then freeze the combined denominator.

## Screening status

U2 has completed conservative source screening for all 22 groups.

U1 has completed conservative screening only for its provisional source-ready first 20.

The union map preserves these different states rather than pretending both review universes are equally complete.

## Claim ceiling

The map can support statements about:

- unique dependency-group counts inside the registered discovery surfaces;
- overlap between literature universes;
- screening progress without bibliographic pseudoreplication.

It cannot support:

- natural prevalence;
- conflict prevalence across flowering plants;
- independent replication counts from review membership;
- confirmatory macro coefficients.

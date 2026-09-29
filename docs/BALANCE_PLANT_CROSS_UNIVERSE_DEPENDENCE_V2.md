# BALANCE plant cross-universe exact-species dependence skeleton v2

## Purpose

Freeze exact-species reuse across U1, U2 and the registered U3 matched lane
**before** U1/U2 independent coding determines final model membership.

Universe-specific rows are preserved, but the same biological species may not
silently become independent replication merely because it entered through a
different review or matched programme.

## Current source-closed union

```text
U1 review taxa                         47
U2 review dependency groups            22
U3 registered case occurrences          6
U3 registered control occurrences       6
raw occurrence rows                    81

unique exact-species taxon units       77
repeated exact-taxon groups              4
cross-universe same-species groups       3
```

The four repeated groups are:

```text
Ipomopsis aggregata
  U1_025
  U2_015

Mimulus aurantiacus
  U1_031
  U2_006

Solanum rostratum
  U2_021
  U3_CASE_001
  U3 dependence block: U3_DEP_SOLANUM_01

Monochoria australasica
  control reused in U3_PAIR_MONKO_001 and U3_PAIR_MONVA_001
  U3 dependence block: U3_DEP_MONOCHORIA_01
```

## Frozen rule

```text
CLUSTER_SAME_TAXON_DO_NOT_COUNT_AS_INDEPENDENT
```

A species may retain multiple universe-specific observations because the
literature families ask different biological questions. Those observations
must nevertheless share an exact-species dependence unit in any combined
uncertainty calculation.

The U3 pair/block dependence rules remain additional constraints; this skeleton
does not replace them.

## Why this matters

The previous U1-U2 dependency map correctly caught `Ipomopsis aggregata` and
`Mimulus aurantiacus`, but did not include U3. That omission would allow
`Solanum rostratum` to appear once as a Barrett-review historical record and
again as a modern U3 heteranthery case without an explicit shared-species
dependence receipt.

V2 closes that gap prospectively.

## What remains

This freezes exact-species reuse, not the full final covariance model.

After independent U1/U2 coding determines the surviving confirmatory rows, the
analysis must still freeze/construct the appropriate phylogenetic or higher
taxonomic covariance for distinct species. Exact-species clustering cannot be
replaced by treating all 77 taxa as independent.

## Canonical surfaces

```text
balance_domain/plant_cross_universe_dependence.py
data/BALANCE_PLANT_CROSS_UNIVERSE_OVERLAP_V2.csv
tests/test_plant_cross_universe_dependence.py
```

## Claim ceiling

This is an outcome-blind dependence skeleton. It is not final model membership,
a phylogenetic covariance matrix, a prevalence estimate, or an effect estimate.

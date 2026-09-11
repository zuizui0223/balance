# BALANCE Gymnadenia Q1B extraction blocker v1

## Current gate

Q1B diffuse-factorial effect-size-ready positive clusters:

```text
Fragaria vesca       READY
Impatiens capensis   READY
Gymnadenia conopsea  POSITIVE BIOLOGICAL CANDIDATE, NUMERIC RECEIPT NOT YET CLOSED
pooling gate         2 / 3
```

Pooling remains prohibited.

## What was attempted

A CI extractor queried the public Caruso et al. 2019 Dryad dataset (`10.5061/dryad.2v8c5g0`) to recover the exact Sletvold, Moritz & Agren 2015 records for DOI `10.1890/14-0119.1`.

Dataset/version metadata and file manifests are anonymously readable. The current Dryad API, however, returns HTTP 401 for file bytes without authenticated download credentials. The failed run therefore reflects a retrieval boundary, not absence of the source records and not a negative scientific result.

## Scientific status of Gymnadenia

The primary source remains a strong positive biological Q1B candidate:

- 2 x 2 pollination x herbivory factorial field experiment;
- one common female-fitness analysis;
- same flowering-phenology coordinate;
- pollinators select later flowering;
- herbivores select earlier flowering;
- approximately additive effects;
- Appendix A2 is documented as reporting treatment-group linear selection gradients +/- SE for all four treatment groups.

The source is not promoted to effect-size-ready until exact numerical sufficient statistics and valid joint uncertainty are recovered.

## Recovery routes, in order

1. Recover Ecological Archives `E096-022-A1` / source supplement directly and extract Table A2 exactly.
2. Use an authenticated Dryad download only if credentials are already available in an approved environment; credentials are never committed to the repository.
3. If neither route is available, retain Gymnadenia as a positive pattern candidate and seek another independent public full-factorial positive study.

No figure digitization, visual approximation, covariance-zero convenience assumption, or post-hoc weakening of the Q1B contract is allowed to open pooling.

## Claim ceiling

This blocker is provenance/audit information only. It does not change the scientific numerator. Q1B remains 2/3 effect-size-ready positives until a third independent receipt is actually closed.

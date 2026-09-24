# BALANCE plant U3 matched-control audit v5

## Status

The Monochoria control problem is now split into a closed candidate-ranking component and an open pollination-eligibility component.

The six PRIMARY U3 pairs remain four ADJUDICATED controls plus two SCREENED Monochoria controls. Both Monochoria pairs remain OPEN overall and are not promoted to ADJUDICATED.

## High-resolution Monochoria proximity result

The earlier ndhF+rbcL surface was non-identifying because M. australasica and M. cyanea were identical on the candidate-comparable sites used by that audit.

The registered higher-resolution audit uses 68 shared single-copy plastome protein-coding genes from complete plastomes:

- Pontederia australasica: NC_063307.1
- Pontederia cyanea: PQ010091.1
- Pontederia korsakowii: PQ010093.1
- Pontederia vaginalis: PQ010094.1

Each gene is aligned separately with MAFFT and concatenated. Candidate ranking uses one joint A/C/G/T site mask across the case plus both candidate controls.

For P. korsakowii, P. australasica differs at 460 of 51,357 jointly comparable sites (p = 0.0089569) and P. cyanea at 475 (p = 0.0092490). Gene-wise support is 24 versus 14, with 30 ties.

For P. vaginalis, P. australasica differs at 484 of 51,357 sites (p = 0.0094242) and P. cyanea at 501 (p = 0.0097552). Gene-wise support is 24 versus 15, with 29 ties.

The candidate plastomes differ at 158 sites on the shared-CDS surface, so the previous exact tie is no longer present.

## Adjudication consequence

Under the frozen U3 tie-break order, this surface closes the candidate-ranking comparison:

- M. australasica: closest-eligible-search gate = PASS;
- M. cyanea: closest-eligible-search gate = FAIL and candidate status = REJECTED;
- tie-break used = PHYLOGENETIC_DISTANCE.

This is a plastid proximity diagnostic only. It does not establish a nuclear species tree, historical sister relationship, or causal transition.

## Remaining blocker

The only remaining matched-control gate for both Monochoria pairs is:

```
DIRECT_SPECIES_LEVEL_EFFECTIVE_ANIMAL_POLLINATION_OPEN
```

The existing Amegilla record concerns territorial behaviour above water and is not treated as a flower-visitation or effective-pollination event. General statements about animal pollination of enantiostylous taxa also remain below the registered species-level evidence gate.

## Frozen receipt

The workflow result is persisted in:

```
data/BALANCE_PLANT_U3_MONOCHORIA_PLASTOME_RESULT_V1.json
```

The dedicated Monochoria workflow regenerates the plastome audit and fails closed if the registered accessions, shared-gene count, candidate distances, winners, gene-wise support, or claim ceiling drift.

## Separate U3 blockers

Closing this candidate ranking does not close the matched conflict estimand. Control-side pollen-fate conflict remains unresolved for Osbeckia chinensis, and the Senna matched pairs still require their registered pollen-fate extraction before a full matched conflict analysis is licensed.

## Claim ceiling

U3 can state that the registered plastome proximity diagnostic resolves the M. australasica versus M. cyanea candidate-ranking tie in favor of M. australasica for both focal Monochoria cases.

It cannot state that M. australasica is the nuclear-genomic sister of either case, that direct effective animal pollination has been demonstrated by this receipt, that either Monochoria pair is fully adjudicated, or that a historical transition was caused by the inferred architecture.

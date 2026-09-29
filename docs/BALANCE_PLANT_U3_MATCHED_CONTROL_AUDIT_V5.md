# BALANCE plant U3 matched-control audit v5

## Status

The Monochoria control problem is now separated into two ordered components:

1. phylogenetic ranking of the two registered nonheterantherous congeners;
2. ecological eligibility and final closest-eligible-control adjudication.

The first component is resolved on the registered plastome proximity surface. The second remains OPEN.

The six PRIMARY U3 pairs therefore remain four ADJUDICATED controls plus two SCREENED Monochoria controls. Both Monochoria pairs remain OPEN overall.

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

The candidate plastomes differ at 158 sites on the shared-CDS surface, so the previous exact molecular tie is no longer present.

## What this closes

The high-resolution surface supports one narrow statement:

```
conditional_phylogenetic_ranking:
    M. australasica before M. cyanea
```

for both focal cases.

This is sufficient to record the frozen PHYLOGENETIC_DISTANCE tie-break ordering if the candidates are otherwise ecologically eligible.

It is not sufficient to mark `closest_eligible_search_status = PASS`.

## Why closest-eligible remains OPEN

Ecological eligibility is a separate gate. Direct species-level effective-pollination evidence remains unresolved for both registered Monochoria candidates.

Therefore M. cyanea cannot yet be permanently rejected merely because it is farther on the plastome surface. If M. australasica ultimately fails the ecological eligibility criterion and M. cyanea passes, M. cyanea can still become the closest eligible control.

The candidate registry consequently keeps both Monochoria candidates OPEN, while recording the plastome ranking in their receipts.

The adjudication blocker remains:

```
DIRECT_ANIMAL_POLLINATION_AND_ELIGIBILITY_CONDITIONAL_CLOSEST_CONTROL_OPEN
```

## Pollination search ceiling

The strongest currently recovered evidence for M. australasica is still indirect for the registered gate:

- comparative enantiostyly literature links these floral systems to pollen-collecting bees;
- Monochoria is discussed as a pollen-reward / buzz-pollination lineage;
- an Amegilla source documents male territorial behaviour above water containing M. australasica.

None of these is a species-level flower-visitation or effective-pollination receipt for M. australasica under the current contract.

## Frozen receipt

The high-resolution molecular result is persisted in:

```
data/BALANCE_PLANT_U3_MONOCHORIA_PLASTOME_RESULT_V1.json
```

The dedicated Monochoria workflow regenerates the plastome audit and fails closed if the registered accessions, shared-gene count, candidate distances, winners, gene-wise support, or claim ceiling drift.

## Separate U3 blockers

The matched conflict estimand also remains open independently of Monochoria matching. Osbeckia chinensis and the two Senna pairs have extracted records but still lack the registered direct matched pollen-fate evidence needed to resolve their conflict contrasts.

## Claim ceiling

U3 can state that the registered plastome proximity diagnostic ranks M. australasica ahead of M. cyanea for both focal Monochoria cases.

U3 cannot yet state that:

- M. australasica is the nuclear-genomic sister of either case;
- either Monochoria candidate has passed the direct species-level effective-pollination gate;
- the closest eligible control has been fully adjudicated;
- M. cyanea is permanently excluded;
- either Monochoria pair is fully adjudicated;
- the matched conflict effect is estimable;
- a historical transition was caused by the inferred architecture.

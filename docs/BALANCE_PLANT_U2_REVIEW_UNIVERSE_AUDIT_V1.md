# BALANCE plant U2 sexual-interference review universe v1

## Purpose

U2 is the first **source-closed outcome-independent sexual-interference discovery universe** in the plant macro programme.

It is anchored to Barrett (2002), *Sexual interference of the floral kind* (Heredity 88:154–159; DOI 10.1038/sj.hdy.6800020).

The review defines sexual interference broadly as conflicts between maternal and paternal function that can waste gametes or mating opportunities and explicitly discusses positive, negative and ambiguous experimental evidence.

## Current closure state

Current registry: 22 biological dependency groups; 37 Barrett-2002 references classified; all taxon-empirical references mapped; zero pending reference classifications; zero unresolved primary-source groups.

Every U2 biological group remains `screening_status = UNSCREENED`. Source closure therefore does **not** mean conflict-positive or analysis-eligible.

## Construction

The 22 groups are the biological units recoverable from taxon-specific empirical studies cited by Barrett (2002), with repeated studies on one species merged before analysis.

The registry deliberately retains different inferential outcomes, including a null physical-interference test in *Pontederia cordata*; prior/self-pollen interference cases; movement herkogamy in *Mimulus aurantiacus*; display and sexual-segregation experiments in *Eichhornia paniculata*; stylar-polymorphism studies in *Narcissus*; historical heteranthery observations; and self-sterility/incompatibility cases that may fail the strict BALANCE conflict gate.

U2 membership is review-citation membership, not a list of successful conflict-resolution architectures.

## Source grain

Multiple studies on one species are one dependency group. For example, Kohn & Barrett 1992, Harder & Barrett 1995, and Harder, Barrett & Cole 2000 all map to one `Eichhornia_paniculata` group.

The former genus-level flexistyly record has been resolved to *Alpinia kwangsiensis* with the review-cited primary programme attached.

The comparative *Wachendorfia* paper is represented by separate species rows because the primary source resolves species-level states, while shared-source provenance is retained.

## Full review-reference audit

`data/BALANCE_PLANT_U2_REFERENCE_COVERAGE_V1.csv` classifies all 37 references in Barrett (2002) as taxon-specific empirical evidence, synthesis/review, theory/general, historical synthesis, or broad comparative dataset.

Every taxon-specific empirical reference is mapped to one or more registered U2 dependency groups. Non-taxon references are not silently converted into biological replication.

The canonical validator fails closed if one of the 37 references disappears, a taxon-empirical citation becomes unmapped, a registered dependency group lacks taxon-specific reference support, or a primary source returns to unresolved status.

## Independent double-coding sample

Because the source universe is closed, U2 now has a deterministic first-20 sample in `data/BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv` using `FIRST_20_DEPENDENCY_GROUPS_LEXICOGRAPHIC_FROM_SOURCE_CLOSED_U2`.

All 20 sampled groups are source-resolved and marked `READY_FOR_INDEPENDENT_DOUBLE_CODING`.

The blinded source packet is `data/BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv`. Coders are instructed to use the primary source only and not the review-side `evidence_family` or interpretive notes.

## Why U2 is useful

U1 primarily addresses herbivore–pollinator interactions. U2 supplies an independently constructed literature family in which competing functions are male and female reproductive roles.

It directly probes whether architecture can be classified along shared simultaneous function, temporal separation, spatial separation, and inflorescence/module-level sexual segregation without selecting the first 20 rows by observed architecture.

## Claim ceiling

Even with source closure, U2 does not establish that sexual interference is present in every cited species, that dichogamy/herkogamy evolved because of interference, that anti-selfing and sexual-interference mechanisms are distinguishable from citation membership, or that any U2 row belongs in the confirmatory primary model.

Those claims require the independent source-level coding and adjudication stage.

## Current next gate

U2 literature discovery is no longer the bottleneck. The next operation is 20 source-resolved groups -> independent coder A/B classifications -> raw agreement + Cohen kappa + Gwet AC1 -> disagreement adjudication -> versioned codebook repair if required.

No synthetic second coder will be generated. Until an independent second coding pass exists, U2 remains source-ready but not reliability-closed.

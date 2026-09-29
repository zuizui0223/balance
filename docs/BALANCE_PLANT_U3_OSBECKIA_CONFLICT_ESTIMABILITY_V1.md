# BALANCE U3 Osbeckia chinensis conflict estimability contract v1

## Purpose

`Osbeckia chinensis` is the sole unresolved control-side binary conflict
measurement in the current four PASS matched pairs.

Repeated public-source retrieval has reached a frozen ceiling. The historical
source shows bee pollen extraction and stigma contact, but not source-resolved
competition between reward/grooming loss and conspecific pollen transfer.

This contract turns that gap into a minimal decisive empirical assay.

## Primary measurement

Track pollen originating from one focal `O. chinensis` donor flower through a
single registered visitor sequence.

Every recovered focal pollen grain is assigned at a standardized scoring time
to one of three classes:

```text
REWARD / GROOMING FATE
  pollen in preregistered groomed or collected compartments

TRANSFER FATE
  pollen on a conspecific recipient stigma or in a preregistered
  transfer-associated visitor-body sector

UNRESOLVED / LOST
  all grains not source-securely assignable to either fate
```

Reward and transfer fates must be mutually exclusive at the scoring time.
Unresolved grains are never redistributed to make the partition cleaner.

## Positive conflict rule

Before focal fate proportions are inspected, freeze independent floors:

- minimum biologically/assay-relevant reward-fate probability;
- minimum biologically/assay-relevant transfer-fate probability;
- maximum acceptable source-misclassification rate.

A final `POSITIVE` call requires simultaneous lower confidence bounds for both
fate probabilities to exceed their frozen floors while source error remains
below its ceiling.

Failure to satisfy that rule remains:

```text
UNRESOLVED
```

not `NO_DEMONSTRATED_CONFLICT`.

This prevents low precision from being converted into a biological negative.

## Stage-0 role

Stage-0 may estimate only nuisance quantities:

- plant-level clustering;
- visitor-class heterogeneity;
- source-label recovery;
- background contamination;
- source misclassification;
- unresolved/lost-fate fraction;
- recipient-stigma recovery;
- attrition;
- focal pollen-pool variation before outcome unblinding.

It may not use observed reward or transfer fate proportions to choose convenient
classification floors.

## Why this is more informative than another visitation record

The existing evidence already shows that bees remove pollen and contact the
stigma. Another descriptive visit would not close the registered gate.

The missing observation is the **fate of focal pollen**: how much enters the
pollinator's reward/grooming pathway versus the conspecific transfer pathway.

That is the direct ecological conflict object.

## Canonical surfaces

```text
balance_domain/plant_u3_osbeckia_estimability.py
data/BALANCE_PLANT_U3_OSBECKIA_CONFLICT_POWER_TARGETS_TEMPLATE_V1.json
data/BALANCE_PLANT_U3_OSBECKIA_STAGE0_NUISANCE_TEMPLATE_V1.json
tests/test_plant_u3_osbeckia_estimability.py
```

## Claim ceiling

This contract defines an estimable path to a positive control-side
pollen-fate-conflict receipt. It is not a conflict result, a sample-size result,
a routing classification, a population effect, or historical causal evidence.

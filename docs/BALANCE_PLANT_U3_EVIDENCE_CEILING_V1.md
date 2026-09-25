# BALANCE plant U3 evidence ceiling v1

## Purpose

The remaining U3 empirical blockers are no longer recorded as generic "search more" tasks.

This receipt freezes the strongest public evidence recovered so far, the exact evidence still missing, and the reason each gate remains OPEN. An OPEN evidence ceiling means **insufficient evidence was recovered**, not that the biological process is absent.

Canonical surfaces:

```text
data/BALANCE_PLANT_U3_EVIDENCE_CEILING_V1.csv
balance_domain/plant_u3_evidence_ceiling.py
tests/test_plant_u3_evidence_ceiling.py
```

## Monochoria australasica

Strongest recovered evidence:

- species-level floral morphology is source-secure;
- comparative literature places the system in the enantiostyly / buzz-pollination context;
- the Amegilla source records male territorial behaviour over water vegetated with `M. australasica`.

What is **not** recovered:

```text
species-level flower visit
+
pollen transfer / stigma deposition / reproductive effectiveness
```

Territorial behaviour above the plant is not promoted to a flower visit.

Decision:

```text
DIRECT_SPECIES_LEVEL_EFFECTIVE_ANIMAL_POLLINATION = OPEN
```

## Monochoria cyanea

Species morphology and phylogenetic placement are recoverable, but no source-secure species-level effective-pollination study was recovered.

General family/genus statements about buzz pollination do not satisfy the frozen matched-control eligibility gate.

Decision:

```text
DIRECT_SPECIES_LEVEL_EFFECTIVE_ANIMAL_POLLINATION = OPEN
```

The frozen 68-shared-CDS plastome ranking remains conditional: if both candidates pass ecological eligibility, `M. australasica` ranks before `M. cyanea`.

## Osbeckia chinensis

The historical observation is real and useful:

- Hymenoptera handle the stamen bundle;
- pollen is extracted from poricidal anthers;
- visitor body position can contact the stigma.

But the registered matched conflict estimand needs a stronger pollen-fate receipt.

Still missing:

```text
reward removal / grooming
versus
export or stigma deposition
or
reproductive consequence of altered pollen removal
```

Decision:

```text
CONTROL_POLLEN_FATE_CONFLICT = OPEN
```

This is deliberately stricter than merely showing that bees take pollen while touching the stigma.

## Consequence

The current U3 programme has:

```text
family representatives source-resolved     16 / 16
heteranthery case-side conflict positive     4 / 4
matched controls adjudicated PASS            4 / 6
matched pairs conflict-resolved both sides   3 / 4 PASS pairs
U3 dependence structure                      FROZEN
```

The two genuine empirical ceilings are now:

1. Monochoria control ecological eligibility;
2. Osbeckia control pollen-fate measurement.

Repeated retrieval should resume only when a new source surface, citation trail, dataset, or targeted field measurement can supply the missing registered evidence.

## Claim ceiling

This receipt documents search ceilings and missing measurements. It does not convert failure to recover a study into evidence that pollination or pollen-fate conflict is absent.

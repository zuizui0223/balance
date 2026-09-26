# BALANCE U3 morphology–routing proxy non-identifiability v1

## Result

The current matched U3 lane rejects a one-to-one mapping between visible
heteranthery morphology and ecological pollen-fate routing in **both
directions**.

This is a logical identification result from source-resolved counterexamples,
not a frequency or transition estimate.

## Same morphology, different routing

Among nonheterantherous controls with directly positive pollen-reward versus
gamete-transfer conflict, two source-resolved controls occupy different frozen
dependence blocks and different routing states:

```text
Solanum lycocarpum
  heteranthery: ABSENT
  conflict:     POSITIVE
  routing:      AMONG_FLOWER_MODULE_DIVISION
  block:        U3_DEP_SOLANUM_01

Senna spectabilis
  heteranthery: ABSENT
  conflict:     POSITIVE
  routing:      WITHIN_FLOWER_DIVISION_OF_LABOUR
  block:        U3_DEP_SENNA_01
```

Therefore:

```text
nonheteranthery morphology
does not uniquely identify
routing architecture
```

This lower bound survives every completion of the unresolved controls: later
measurements can add or repeat routing states, but cannot erase these two
already observed states.

## Same routing, different morphology

The matched Senna pair supplies the reverse counterexample:

```text
Senna alata
  heteranthery: PRESENT
  conflict:     POSITIVE
  routing:      WITHIN_FLOWER_DIVISION_OF_LABOUR

Senna spectabilis
  heteranthery: ABSENT
  conflict:     POSITIVE
  routing:      WITHIN_FLOWER_DIVISION_OF_LABOUR
```

Thus:

```text
WITHIN_FLOWER_DIVISION_OF_LABOUR
does not uniquely identify
heteranthery morphology
```

## Biological interpretation

The useful ecological object is not “heteranthery” alone.

The current evidence separates three layers:

1. **functional conflict** — pollen is both pollinator reward and male gamete;
2. **routing architecture** — where the competing pollen fates are separated;
3. **visible implementation** — whether fertile stamens are morphologically
   differentiated.

Those layers can decouple.

A nonheterantherous flower can route the conflict within one flower through
position/petal geometry, or at a larger organizational level among flowers.
Conversely, the same within-flower routing category can occur with or without
morphological heteranthery.

That makes visible stamen morphology a poor deterministic proxy for the
ecological process that BALANCE is trying to explain.

## Consequence for comparative analysis

Do not code:

```text
heteranthery = routing
```

or:

```text
nonheteranthery = shared integration
```

as data transformations.

Conflict presence/strength, routing architecture and morphology must remain
separate variables. This also explains why the next useful measurements are
the unresolved routing state of `Senna covesii` and quantitative conflict/routing
in `Osbeckia chinensis`, rather than simply accumulating more morphology
records.

## Executable surface

```text
balance_domain/plant_u3_morphology_routing_nonidentifiability.py
tests/test_plant_u3_morphology_routing_nonidentifiability.py
```

## Claim ceiling

This certificate establishes bidirectional proxy non-identifiability on the
registered matched evidence surface. It does not estimate how frequent either
mapping is, evolutionary transition rates, a morphology effect, or historical
causation.

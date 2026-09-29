# BALANCE U3 morphology-routing decoupling identification certificate v1

## Question

Is morphological heteranthery itself equivalent to the functional routing state
that separates pollen reward from gamete transfer?

The current matched lane already supplies a direct counterexample.

## Matched counterexample

```text
Senna alata
  heteranthery morphology: PRESENT
  pollen-fate conflict:    POSITIVE
  routing:                 WITHIN_FLOWER_DIVISION_OF_LABOUR

Senna spectabilis
  heteranthery morphology: ABSENT under the frozen control definition
  pollen-fate conflict:    POSITIVE
  routing:                 WITHIN_FLOWER_DIVISION_OF_LABOUR
```

The pair differs in the registered heteranthery morphology state but shares the
same source-resolved functional routing category.

For `S. spectabilis`, equal fertile-stamen morphology does not imply global
integration: direct ricochet experiments show positional pollen routing within
the flower.

## Identification result

The existence of this matched control is sufficient for the narrow logical
statement:

```text
heteranthery is not necessary
for within-flower functional division of labour
```

and therefore:

```text
heteranthery morphology
!=
functional routing state
```

This is not based on cross-family prevalence. It is a counterexample inside a
frozen matched pair with positive pollen-fate conflict on both sides.

## A second matched pattern

The other fully route-resolved positive pair behaves differently:

```text
Solanum rostratum     WITHIN_FLOWER_DIVISION_OF_LABOUR
Solanum lycocarpum    AMONG_FLOWER_MODULE_DIVISION
```

Thus among the two currently evaluable positive-conflict matched pairs, one
morphology contrast preserves routing state and one changes routing level.

The useful biological question is no longer simply "does heteranthery resolve
the conflict?" It is:

> which developmental and floral mechanisms implement a routing solution once
> the pollen-reward versus gamete-transfer conflict exists?

## Consequence for BALANCE

The empirical programme should keep three variables separate:

1. presence/strength of the functional conflict;
2. visible stamen morphology;
3. organizational level of routing.

Collapsing any two would erase the observed `S. spectabilis` counterexample.

## Executable surface

```text
balance_domain/plant_u3_morphology_routing_identification.py
tests/test_plant_u3_morphology_routing_identification.py
```

## Claim ceiling

This certificate establishes a matched counterexample to morphology-routing
equivalence. It does not estimate how often the decoupling occurs, a transition
probability, or a causal effect of heteranthery on routing.

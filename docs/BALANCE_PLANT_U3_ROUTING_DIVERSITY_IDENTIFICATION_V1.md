# BALANCE U3 minimum routing-diversity identification certificate v1

## Question

Once pollen-reward versus gamete-transfer conflict is present, does that binary
conflict determine one architectural routing solution in nonheterantherous
controls?

The answer is already **no**, independent of how the remaining unresolved
controls are eventually classified.

## Source-resolved positive controls

Three current nonheterantherous controls have positive binary pollen-fate
conflict.

Two already have source-resolved routing:

```text
Solanum lycocarpum
  dependence block: U3_DEP_SOLANUM_01
  route: AMONG_FLOWER_MODULE_DIVISION

Senna spectabilis
  dependence block: U3_DEP_SENNA_01
  route: WITHIN_FLOWER_DIVISION_OF_LABOUR
```

`Senna covesii` is positive for conflict but routing-unresolved.

## Identification result

The observed lower bound is therefore:

```text
distinct routing states among positive nonheterantherous controls >= 2
independent frozen dependence blocks carrying those states          >= 2
```

No completion of `S. covesii` or the conflict-unresolved
`Osbeckia chinensis` can reduce that lower bound. Future resolutions may add
states or repeat an existing one; they cannot erase the two source-resolved
routes already observed.

Thus:

```text
binary conflict present
!=
unique routing architecture
```

and, in the current matched lane:

```text
absence of heteranthery
!=
shared/global integration
```

## Biological interpretation

The same underlying pollen-use conflict can be routed at different
organizational levels.

In `S. lycocarpum`, functional partitioning is routed among flower modules.
In `S. spectabilis`, it is routed within the flower despite equal
fertile-stamen morphology under the frozen heteranthery definition.

This makes the empirically interesting question conditional:

> given that conflict exists, what determines the level and geometry at which
> the lineage routes it?

That question is distinct from asking whether conflict is present.

## Executable surface

```text
balance_domain/plant_u3_routing_diversity.py
tests/test_plant_u3_routing_diversity.py
```

## Claim ceiling

This certificate establishes a minimum observed routing diversity in the
registered matched lane. It does not estimate the population frequency of
routing states, transition probabilities, conflict strength or a causal routing
effect.

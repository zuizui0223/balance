# BALANCE plant U3 matched extraction diagnostic v3

## Status

The four PASS-adjudicated pairs remain the extraction set, but one major functional evidence gap is now closed.

```text
pairs                                        4
case conflict POSITIVE                      3 / 4
case conflict UNRESOLVED                    1 / 4
control conflict POSITIVE                   2 / 4
control conflict UNRESOLVED                 2 / 4
pairs with both conflict states resolved    2 / 4
```

The two fully resolved conflict pairs are:

- `Solanum rostratum -> Solanum lycocarpum`
- `Senna alata -> Senna spectabilis`

## Senna alata -> Senna spectabilis

Amorim et al. (2017; DOI `10.1111/plb.12607`) directly studied both focal species using floral-organ measurements, artificial sonication, field bee interactions, division-of-labour experiments and petal-removal experiments.

The source resolves pollen routing rather than merely naming stamen classes. Pollen associated with reward collection is routed to bee regions accessible for grooming/collection, while the pollination route uses floral position and, in `S. spectabilis`, deflector-petal ricochet to deliver pollen toward transfer-favoring body regions.

Therefore both sides are now coded `pollen_fate_conflict_status = POSITIVE`.

### Why the control remains valid

`S. spectabilis` remains nonheterantherous under the frozen U3 morphology gate: independent morphology sources record seven fertile stamens equal in size and shape plus three sterile staminodes.

The functional experiment nevertheless shows within-flower division of labour.

This separates two variables that had been easy to conflate:

```text
heteranthery morphology
!=
within-flower functional division of labour
```

A lineage can lack discrete fertile-stamen morphs and still route pollen reward and gamete transfer through position, petals and pollen trajectory.

That result strengthens the BALANCE architecture programme: the relevant response is not simply whether specialised anther morphs exist, but **where the system routes the conflict**.

## Remaining conflict-measurement blockers

### Melastoma malabathricum -> Osbeckia chinensis

Case conflict is positive; control conflict remains unresolved. The historical source establishes bee handling and stigma contact but not the registered quantitative reward-versus-transfer comparison.

### Senna bicapsularis -> Senna covesii

Both conflict states remain unresolved under the current strict direct-functional criterion.

`S. bicapsularis` has strong supporting evidence for functional differentiation: stamen-specific pollen viability and later lipidomic/proteomic differences, with bees selectively foraging among stamen types. Those data make the reward-routing hypothesis stronger, but they are not silently promoted to the same evidence class as a direct pollen-fate routing experiment.

`S. covesii` still lacks a matched direct functional pollen-fate experiment.

## Readout bug fixed

The previous `matched_conflict_estimand_ready` implementation inspected only control rows. That could have returned true if all controls were resolved while a case remained unresolved.

The readout now requires every case **and** every control row to be non-`UNRESOLVED`.

Current state remains:

```text
matched_conflict_estimand_ready = false
```

## Architecture state of controls

```text
Solanum lycocarpum   AMONG_FLOWER_MODULE_DIVISION
Senna spectabilis   WITHIN_FLOWER_DIVISION_OF_LABOUR
Osbeckia chinensis  UNRESOLVED
Senna covesii       UNRESOLVED
```

No control is currently `SHARED_INTEGRATED`. A nonheterantherous control is therefore never automatically interpreted as a globally integrated or low-conflict system.

## Claim ceiling

U3 now has two matched pairs with direct conflict evidence on both sides and demonstrates that heteranthery absence can coexist with within-flower functional division.

It still does not provide a complete four-pair conflict-effect estimate, a shared-integrated control contrast, heteranthery prevalence, or historical causal transition probabilities.

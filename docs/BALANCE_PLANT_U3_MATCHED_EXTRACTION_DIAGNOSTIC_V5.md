# BALANCE plant U3 matched extraction diagnostic v5

## Status

The matched conflict lane is now resolved for **three of four** PASS pairs.

```text
case conflict POSITIVE                      4 / 4
control conflict POSITIVE                   3 / 4
control conflict UNRESOLVED                 1 / 4
pairs with both conflict states resolved    3 / 4
matched_conflict_estimand_ready             false
```

The sole remaining conflict-measurement blocker is now:

```text
Osbeckia chinensis
```

## Senna bicapsularis -> Senna covesii

The case-side route was already direct: `S. bicapsularis` bees buzz the short feeding stamens, pollen from long stamens reaches the dorsal bee surface, and the stigma contacts that same region.

The control side is now also positive for **binary conflict presence**.

### Senna covesii evidence

Marazzi's species-level field account records small bees visiting `S. covesii`; each visit is audibly buzz-pollinated. The same source explains the Senna floral route: flowers are nectarless, pollen is the reward, sonication ejects pollen onto bees, and pollen grains that escape grooming are carried to stigmas of conspecific flowers.

Felger & Rutman independently describe seven fertile stamens with terminal pores and explicitly state that `S. covesii` is buzz-pollinated by bees.

Russell, Buchmann & Papaj (2017; DOI `10.1093/beheco/arx058`) independently document `S. covesii` as a poricidal pollen-concealing flower.

Together these receipts establish the two competing fates of the same pollen resource:

```text
bee collection / grooming -> reward fate
escape from grooming + stigma transfer -> gamete fate
```

The control is therefore `pollen_fate_conflict_status = POSITIVE`.

This is deliberately a **presence** call, not a quantitative conflict-strength estimate. No broader architecture is inferred, so `architecture_mode = UNRESOLVED` remains unchanged.

## Current fully resolved conflict pairs

- `Solanum rostratum -> Solanum lycocarpum`
- `Senna alata -> Senna spectabilis`
- `Senna bicapsularis -> Senna covesii`

The only case/control pair still missing one side is:

- `Melastoma malabathricum -> Osbeckia chinensis`

## Biological consequence

The matched lane now makes a stronger point than a simple heteranthery contrast.

All three resolved nonheterantherous controls retain pollen-reward / gamete-transfer conflict, but route it differently or remain structurally unresolved:

- `S. lycocarpum`: among-flower module division;
- `S. spectabilis`: within-flower functional division despite equal fertile-stamen morphology;
- `S. covesii`: conflict positive, broader routing architecture not yet source-resolved.

Thus absence of heteranthery is not evidence that the underlying pollen-fate conflict disappeared.

## Remaining gate

`matched_conflict_estimand_ready` remains false because `Osbeckia chinensis` is still `UNRESOLVED` under the registered evidence criterion.

No control is currently `SHARED_INTEGRATED`, so a clean structural-division-versus-global-integration contrast is also still unavailable.

## Claim ceiling

U3 now supports four positive case-side conflict receipts and three fully resolved matched conflict pairs. It does not yet support the complete four-pair conflict effect, quantitative conflict-strength comparisons for every control, a shared-integrated control contrast, heteranthery prevalence, or historical causation.

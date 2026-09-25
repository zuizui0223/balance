# BALANCE plant U3 matched extraction diagnostic v4

## Status

All four heteranthery **case** taxa in the current PASS matched lane now have positive pollen-fate conflict evidence.

```text
case conflict POSITIVE                      4 / 4
control conflict POSITIVE                   2 / 4
control conflict UNRESOLVED                 2 / 4
pairs with both conflict states resolved    2 / 4
matched_conflict_estimand_ready             false
```

The remaining conflict-measurement gaps are now entirely on the control side:

- `Osbeckia chinensis`
- `Senna covesii`

## Senna bicapsularis case closure

Luo, Gu & Zhang (2009; DOI `10.1111/j.1759-6831.2009.00002.x`) provide direct natural observations of pollen routing.

Female `Xylocopa` bees preferentially buzzed the short feeding stamens. The transmitted vibration caused pollen from the long pollinating stamens to form a cloud over the bee's dorsal abdomen, while the stigma contacted that same pollen-bearing dorsal region.

This is direct evidence of different pollen fates:

```text
short stamens -> bee-accessible pollen collection / reward
long stamens  -> dorsal deposition aligned with stigma contact / transfer
```

The case is therefore upgraded from `UNRESOLVED` to `POSITIVE`.

Huang & Gong (2022; DOI `10.1111/plb.13457`) independently strengthen the reward side: short-stamen pollen differs in lipid/protein composition and is enriched in fatty-acid profiles plausibly associated with selective bee foraging.

The 2022 chemistry does not create the positive call by itself; the direct 2009 bee-behaviour and pollen-routing observation does.

## Current matched pairs

### Fully resolved on both conflict sides

- `Solanum rostratum -> Solanum lycocarpum`
- `Senna alata -> Senna spectabilis`

### Case resolved, control unresolved

- `Melastoma malabathricum -> Osbeckia chinensis`
- `Senna bicapsularis -> Senna covesii`

Thus the next search target is no longer "Senna" generically. It is specifically `S. covesii` control-side pollen fate, plus `O. chinensis`.

## Architecture lesson

The extraction now contains two especially informative nonheterantherous controls:

- `S. lycocarpum`: conflict positive, routed among flower modules;
- `S. spectabilis`: conflict positive, routed within the flower despite equal fertile-stamen morphology.

So the empirical programme now separates at least three objects:

```text
presence of pollen-reward / gamete-transfer conflict
morphological heteranthery
level at which functional routing occurs
```

They are not interchangeable.

## Readiness

`matched_conflict_estimand_ready` correctly requires every case and control conflict state to be resolved. All cases now pass that measurement gate, but two controls do not.

No control is currently `SHARED_INTEGRATED`, so a structural-division-versus-global-integration contrast also remains unavailable.

## Claim ceiling

U3 supports four case-side positive conflict receipts and two fully resolved matched conflict pairs. It does not yet support the complete four-pair conflict effect, a shared-integrated control contrast, heteranthery prevalence, or historical causation.

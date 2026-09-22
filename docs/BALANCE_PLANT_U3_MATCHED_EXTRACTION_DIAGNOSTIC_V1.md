# BALANCE plant U3 matched extraction diagnostic v1

## Purpose

Test whether the first source-adjudicated heteranthery case-control pairs are already capable of estimating the BALANCE matched conflict architecture question.

Canonical extraction:

```text
data/BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv
balance_domain/plant_u3_matched_extraction.py
```

## Current closed pairs

Two PRIMARY pairs have passed matched-control adjudication:

1. `Solanum rostratum` -> `Solanum lycocarpum`
2. `Melastoma malabathricum` -> `Osbeckia chinensis`

For both pairs:

- the case has within-flower structural division of labour;
- the control is source-secure as nonheterantherous;
- animal-pollination eligibility is source-secure.

However, nonheteranthery does **not** imply globally integrated reproductive architecture, and module substrate was deliberately not used as a matching variable.

Current control extraction:

```text
Solanum lycocarpum:
  architecture_mode = AMONG_FLOWER_MODULE_DIVISION
  module_substrate  = REPEATED_FLOWERS
  conflict_status   = POSITIVE

Osbeckia chinensis:
  architecture_mode = UNRESOLVED
  module_substrate  = SERIAL_WITHIN_FLOWER
  conflict_status   = UNRESOLVED
```

Thus only one of the two current pairs shares the same `SERIAL_WITHIN_FLOWER` substrate, and neither control is presently coded `SHARED_INTEGRATED`.

This is not a matching failure. The U3 protocol freezes controls before BALANCE predictor extraction; forcing `module_substrate` to match after seeing the case would condition on a primary predictor and create design leakage.

## New control-side conflict resolution: Solanum lycocarpum

The `S. lycocarpum` control no longer remains conflict-unresolved.

Two source-resolved results jointly establish the relevant pollen-reward versus gamete-transfer conflict:

```text
Tavares et al. 2018, Entomological News
DOI 10.3157/021.127.0410
  - pollen is the only floral reward;
  - anther presence strongly increases visitation;
  - pollen availability declines rapidly under bee visitation;
  - much of the pollen is groomed from the bee body into pollen-carrying structures.

Tavares et al. 2017, Interciencia 42:375-379
  - visitor body size and behavior determine stigma contact;
  - single visits by the strongest pollinators produce high fruit-set success;
  - visitor species therefore differ in how much removed pollen contributes to gamete transfer.
```

The control is therefore coded:

```text
pollen_fate_conflict_status = POSITIVE
conflict_evidence_class =
  DIRECT_POLLEN_REWARD_REMOVAL_AND_VISITOR_EFFECTIVENESS
```

This update does not infer conflict from andromonoecy or from the absence of heteranthery. It uses independent pollen-removal and pollination-effectiveness evidence.

## Critical result

The heteranthery contrast is source-secure, but the full matched conflict estimand remains open.

### Conflict contrast

```text
CASE conflict:
  POSITIVE 2 / 2

CONTROL conflict:
  POSITIVE    1 / 2
  UNRESOLVED  1 / 2
```

Therefore:

```text
matched_conflict_estimand_ready = false
```

The sole remaining control-side conflict blocker among adjudicated pairs is `Osbeckia chinensis`.

### Integrated-architecture contrast

```text
CONTROL architecture:
  AMONG_FLOWER_MODULE_DIVISION  1 / 2
  UNRESOLVED                    1 / 2
  SHARED_INTEGRATED             0 / 2
```

Therefore:

```text
matched_integrated_control_contrast_ready = false
```

The current U3 lane is a matched **heteranthery-present versus heteranthery-absent** comparison. It is not yet a clean comparison of structural division versus globally retained integration.

## Why this matters

A nonheterantherous flower is not automatically a low-conflict or integrated system.

The absence of feeding-versus-pollinating anther differentiation can coexist with at least four possibilities:

1. pollen-reward/gamete conflict is genuinely weak;
2. conflict is strong but retained within a shared architecture;
3. conflict is routed into another architecture, such as among-flower division;
4. the relevant conflict or broader architecture has not been measured.

`Solanum lycocarpum` now demonstrates a particularly informative combination in the current extraction:

```text
heteranthery absent
conflict positive
broader architecture = among-flower module division
```

That is stronger than treating the control merely as "not heterantherous." It shows that one lineage can retain the pollen-reward/gamete conflict while routing functional differentiation to a different architectural level.

Treating all nonheterantherous controls as both "low conflict" and "integrated" would therefore create the desired association by coding rule.

## Consequence for U3

U3 now has three separate closure problems.

### Matching closure

```text
6 registered PRIMARY controls
2 adjudicated
4 open
```

### Conflict-measurement closure

Among the two adjudicated pairs:

```text
case-side direct conflict evidence       2 / 2
control-side conflict resolved           1 / 2
control-side conflict unresolved         1 / 2
```

### General-architecture closure

Among the two adjudicated controls:

```text
shared-integrated controls               0 / 2
alternative resolved architecture        1 / 2
broader architecture unresolved          1 / 2
```

The U3 matched conflict effect is not estimable until conflict evidence is recovered for `O. chinensis` or a different estimand is prospectively frozen. A structural-division-versus-integration effect is also not licensed by the current controls.

## Legitimate near-term uses

The current U3 data can support:

- source and architecture audits;
- a matched heteranthery-present versus heteranthery-absent design;
- testing whether control selection can be done without predictor leakage;
- documenting whether module substrate matches or differs after blinded matching;
- identifying alternative conflict-routing architectures;
- showing that positive pollen-fate conflict can persist without heteranthery in `S. lycocarpum`;
- identifying exactly which control experiments are still missing.

It cannot yet support a complete matched estimate of:

```text
heteranthery ~ conflict strength
```

or a matched estimate that interprets control architecture as evidence of weak conflict or global integration.

## Next empirical search target

The immediate control-side search target is now `Osbeckia chinensis`.

Search specifically for experiments or quantitative observations on:

```text
pollen removal by visitors
pollen deposited on stigmas / exported between flowers
visitor manipulation of stamens
pollen allocation or viability among equivalent stamens
pollen limitation / reward removal
```

For broader architecture, also recover source-secure evidence on sex-function partitioning among flowers or modules before assigning `SHARED_INTEGRATED`.

The target is not merely another floral-description paper.

The target is evidence capable of adjudicating whether this nonheterantherous system experiences measurable pollen-reward versus gamete-function conflict and where that conflict is routed.

## Claim ceiling

This diagnostic identifies missing matched measurement and protects predictor-blind matching.

It does not imply that conflict is absent in `Osbeckia chinensis`, and it does not equate nonheteranthery with globally integrated architecture.

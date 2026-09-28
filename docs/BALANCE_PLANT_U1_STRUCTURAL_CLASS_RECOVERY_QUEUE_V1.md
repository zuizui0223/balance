# BALANCE U1 structural-class recovery queue v1

## Status

Targeted full-text adjudication queue only.

This queue was opened because the frozen U1 first-20 screen contributes no conflict-positive
rows and the current U2 conflict-positive surface has no
`STRUCTURAL_MODULE_DIVISION` primary-response cases.

The queue does **not** repair that empty class by assumption. Every candidate remains:

```text
current_conflict_state = UNADJUDICATED
current_architecture_state = UNADJUDICATED
primary-model promotion = forbidden
```

until the registered source gates are passed.

Canonical data surface:

`data/BALANCE_PLANT_U1_STRUCTURAL_CLASS_RECOVERY_QUEUE_V1.csv`.

## Selection principle

Candidates come only from the frozen, outcome-blind U1 review universe. They are prioritized
because the primary sources expose distinct reproductive routes or modules that could make a
routing test possible.

A visible alternative reproductive route is not itself evidence of BALANCE conflict
resolution.

## Queue

### U1SR_001 — Ruellia nudiflora — HIGH

Primary source:
Munguía-Rosas et al., *Effects of herbivores and pollinators on fruit yield and survival
in a cleistogamous herb*, Plant Ecology (2015).

Why targeted:

- one plant produces chasmogamous (CH) and cleistogamous (CL) reproductive routes;
- the experiment manipulates defoliation and pollination environment factorially;
- defoliation has route-dependent effects on CH versus CL fruit production.

Promotion question:

> Do the CH/CL response differences establish opposing functional demands on a registered
> reproductive decision, with route-specific fitness measured strongly enough to call
> architecture routing?

Failure mode:

If the result is only differential damage/resource sensitivity without an independently
identified shared conflict, retain it as a mixed-mating response study and do not call
structural routing.

### U1SR_002 — Impatiens capensis — HIGH

Primary source:
Soper Gorden & Adler 2016, Ecosphere 7:e01326, DOI 10.1002/ecs2.1326.

Why targeted:

- the species has obligately selfing CL and open-pollinated CH flowers;
- the primary study experimentally manipulates florivory;
- moderate florivory shifts proportional reproduction away from CH toward selfed
  reproduction.

Promotion question:

> Is the shift between CH and CL routes a measured response to a genuine pollination-
> antagonist conflict, or simply a general damage/tolerance response?

Failure mode:

Mixed mating plus an herbivory-induced mating-system shift is insufficient unless the
registered conflict and route-specific fitness bridge are independently established.

### U1SR_003 — Isomeris arborea — MEDIUM_HIGH

Primary sources:
Krupnick & Weis 1999, Ecology 80:135-149; Krupnick, Weis & Campbell 1999,
Ecology 80:125-134.

Why targeted:

- the species is andromonoecious, providing male and hermaphroditic flower modules;
- floral herbivory and pollinator service are manipulated/measured;
- male pollen export and female reproductive success are both quantified.

Promotion question:

> Is the male-versus-hermaphroditic module system part of the demonstrated functional
> conflict/routing surface, or merely background sexual architecture?

Failure mode:

If herbivore damage independently lowers reproductive performance without an opposing
shared-coordinate demand that is routed between flower types, do not promote.

### U1SR_004 — Eichhornia crassipes — SPECIFICITY

Primary source:
Buchanan 2015, *Effects of damage and pollination on sexual and asexual reproduction in a
flowering clonal plant*, Plant Ecology.

Why retained:

The species offers sexual and clonal reproductive routes and is therefore a useful stress
test against overcalling any alternative route as conflict resolution.

Promotion question:

> Is there a direct opposing-demand receipt linking damage/pollination to allocation among
> reproductive routes?

Default interpretation:

Keep as a specificity/negative-control candidate unless that stronger receipt is recovered.

## Adjudication order

```text
1. Ruellia nudiflora
2. Impatiens capensis
3. Isomeris arborea
4. Eichhornia crassipes
```

The order is frozen by information yield, not by desired outcome.

## Required receipts before any promotion

A candidate must separately establish:

1. **conflict** — opposing functional demands, not just a negative interaction;
2. **shared decision/coordinate** — a common allocation, trait, or reproductive decision on
   which the demands bear;
3. **routing architecture** — the distinct route/module is source-resolved;
4. **route-specific fitness** — the comparison is on a biologically commensurate outcome;
5. **predictor independence** — module/timing/spatial predictors are not reverse-coded from
   the focal architecture outcome;
6. **dependence identity** — the candidate remains tied to its frozen U1 dependency group.

Failure at any gate leaves the row in the recovery queue or closes it as a specificity
case. It does not justify changing the frozen four-class primary response.

## Current implication

The missing structural primary class is now attached to a bounded retrieval problem rather
than an invitation to outcome-targeted case harvesting.

If none of these U1 candidates passes the full gate, the correct result remains:

```text
STRUCTURAL_MODULE_DIVISION absent from the outcome-blind confirmatory surface
-> primary four-class multinomial not estimable as frozen
```

U3 structural cases remain available for their separately registered matched/case-control
analyses, not for denominator repair.


## Source-screen outcome

The frozen four-candidate queue has now been screened against the current primary-source
surface.

```text
candidates screened       4 / 4
promoted                   0 / 4
independently adjudicated  0 / 4
```

Source-screen decisions:

- **Ruellia nudiflora** — route-specific CH/CL sensitivity is real, but the current source
  shows buffering/context dependence rather than a direct opposing-demand receipt on one
  CH↔CL allocation axis.
- **Impatiens capensis** — florivory shifts relative CH/selfed reproduction, but the source
  does not provide the matched opposing pollination-demand receipt needed to identify
  BALANCE conflict.
- **Isomeris arborea** — andromonoecious modules and male/female fitness effects are
  source-resolved, but the studies do not identify male-versus-hermaphroditic allocation as
  the routing mechanism of a shared conflict.
- **Eichhornia crassipes** — sexual/asexual routes are present, but pollination does not
  affect the reported growth/clone/flower outputs; this remains a specificity case.

These are source-screen ceilings, not independent coder/adjudicator decisions.

Canonical screen:
`data/BALANCE_PLANT_U1_STRUCTURAL_CLASS_RECOVERY_SCREEN_V1.csv`.

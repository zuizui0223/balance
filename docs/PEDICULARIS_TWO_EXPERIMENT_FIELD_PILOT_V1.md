# Pedicularis rex — two-experiment field pilot protocol v1

## Purpose

Collect the minimum **method / variance information** needed to power the same-context SCH → BALANCE → BITA causal chain without using the pilot as a biological significance test.

The pilot is not Chapter-1/2/3 evidence. Its outputs are planning receipts only.

## Freeze before touching biological outcomes

Register one focal context:

```text
context_id
system = Pedicularis rex
population_id
season_id
fitness_scale_id = UNDAMAGED_MATURE_SEEDS_PER_FOCAL_FLOWER
```

Also freeze method-quality thresholds before the pilot is inspected:

```text
maximum acceptable mechanical-damage rate
maximum G-exclusion leakage / early-attack rate
maximum water-depth variation allowed while y is held fixed in Experiment A
minimum water-depth separation required between y0 and y1 in Experiment B
minimum acceptable realized spacing of adjacent x/z manipulation levels
rules for excluding flowers lost before outcome measurement
```

Do not choose minimum biological release, conflict or fitness-gap thresholds from pilot significance tests.

---

## Prerequisite — independent seed-predator G method

Experiment A does not start until the SCH predator-method lane qualifies an exclusion / exposure manipulation that preserves pollinator access.

Required logic:

```text
G0 = seed predator independently excluded
G1 = seed predator exposed
water-y = held fixed
pollinator access = preserved
```

A generic bag that changes pollination and antagonist access simultaneously is not acceptable.

---

# Experiment A pilot — SCH shared-coordinate surface

## Design skeleton

```text
>=5 assigned exsertion z levels
× P0/P1
× G0/G1
```

where:

```text
P0 = supplemented/open-pollination dependence neutralized
P1 = natural/open-pollination dependence active
G0 = independent seed-predator exclusion
G1 = exposed
```

Water defence remains fixed across all cells.

The production design has >=20 treatment cells. The pilot does **not** need to establish biological significance; it must establish that these cells can be implemented and measured without unacceptable cross-effects.

## Experimental unit / clustering

`plant_id` is the biological bootstrap cluster.

Each focal flower retains a unique `flower_id`. Multiple flowers on one plant are never treated as independent plants.

A balanced complete-block design is preferred when a plant has enough comparable flowers, because the current power simulator assumes one focal flower from each plant in each cell. If this is not feasible, record the actual incomplete-block allocation and extend the simulator before accepting its n recommendation.

Do not force a 20-flower-per-plant design merely to match the current simulator.

## Randomization

Within each plant/block where feasible:

1. identify comparable unopened / newly opened focal flowers;
2. assign z levels before outcome information is available;
3. randomize P and G states within the available flower set;
4. retain treatment-assignment records even for failed flowers;
5. separate Experiment-A and Experiment-B flower identities if both occur on one plant.

## Timing

- measure pre-manipulation flower / bract geometry;
- impose assigned z manipulation;
- record realized exsertion after manipulation;
- apply the P treatment during the relevant pollination window;
- apply the qualified G treatment according to the registered timing/barrier method;
- verify water-y remains fixed through the focal antagonist window;
- score early predator attack and mechanical damage before final maturation;
- collect mature capsules for seed outcomes.

## Required raw fields

Use the SCH production schema already registered for the Pedicularis V2 full surface. At minimum it contains:

```text
population_id
season_id
plant_id
flower_id
assigned_z_level
realized_exsertion
pollination_treatment
predator_treatment
exclusion_method
water_depth
ovule_count
undamaged_seed_count
damaged_seed_count
pollen_grains
early_predator_attack_present
mechanical_damage
```

## Pilot-only readout

Run:

```text
scripts/extract_pedicularis_experiment_a_pilot_parameters.py
```

from SCH PR #22.

The receipt supplies planning moments such as:

```text
pooled within-cell fitness variance
residualized plant-cluster variance / ICC when estimable
realized z spread by assigned level
water-depth variation
mechanical-damage rate
G0/G1 early-attack rates
pollen-count variance
```

It intentionally does not call the SCH mechanism positive or negative.

---

# Experiment B pilot — shared BALANCE + BITA x-by-water surface

## Design skeleton

Use the same exsertion coordinate and, where biologically feasible, the same assigned x-level grid as Experiment A:

```text
>=5 x levels
× y0/y1
```

where:

```text
y0 = water defence disabled / bract drained
y1 = water defence active / protected
```

The production design has >=10 cells.

## Same-context requirement

Experiment B must use the same registered population, season and mature-intact-seed fitness scale as Experiment A if a direct three-world bridge is claimed.

A different population/season can be analysed, but it receives a different `context_id` and cannot be silently combined with Experiment A.

## Manipulation checks

The pilot must quantify, without biological promotion:

```text
realized x spacing and manipulation error
water-depth separation between y0 and y1
mechanical-damage rate
damaged-seed distributions under both y states
pollen-response variance
matched y effect on pollen as a cross-effect diagnostic
```

The y manipulation should alter the water-defence state without materially changing realized x or damaging the flower.

## Required raw fields

Use the existing BITA Pedicularis dimensional-release raw schema:

```text
population_id
season_id
plant_id
flower_id
assigned_x_level
realized_exsertion
water_treatment
ovule_count
undamaged_seed_count
damaged_seed_count
pollen_grains
pollinator_visits
water_depth
mechanical_damage
```

## Pilot-only readout

Run:

```text
scripts/extract_pedicularis_experiment_b_pilot_parameters.py
```

from BITA PR #182.

It returns planning moments for:

```text
within-cell fitness variance
residualized plant-cluster variance / ICC
realized x distributions
water-state separation
damaged-seed mean / variation
pollen cross-effect diagnostic
mechanical-damage rate
```

It does not test R_state, BALANCE occupancy or BITA differentiation.

---

# From pilot to final sample size

After both pilot receipts exist:

1. freeze meaningful biological thresholds independently of pilot p-values;
2. construct optimistic / central / conservative generating scenarios;
3. replace variance/manipulation parameters with pilot estimates or declared sensitivity bounds;
4. choose candidate independent plant-cluster counts;
5. run the production-pipeline power simulators:

```text
SCH
scripts/simulate_pedicularis_experiment_a_power.py

BITA / shared Experiment B
scripts/simulate_pedicularis_experiment_b_power.py
```

6. choose the smallest design meeting the prospectively frozen joint-power rule in all primary gates;
7. add a separately declared field-loss inflation factor.

The simulation wrappers are planning tools and must not be tuned until a convenient n appears.

---

# Pilot inclusion rule

Preferred design: keep method/power pilot flowers outside the confirmatory biological dataset.

If logistical constraints require an internal pilot to contribute to the final dataset, predeclare before pilot inspection:

- which nuisance parameters may be updated;
- that treatment-effect thresholds and directional hypotheses cannot be changed;
- whether sample-size re-estimation is blinded to biological treatment effects;
- how type-I error / inferential validity is protected.

Absent such a rule, do not pool pilot outcomes into the confirmatory causal test.

---

# Current status

```text
three-world context/scale interface       MAIN + GREEN
Experiment-A causal analyzer              MAIN
Experiment-A shared bundle                PR #21 GREEN, NOT MERGED
Experiment-A pilot/power wrapper           PR #22 GREEN, NOT MERGED
Experiment-B causal release analyzer       MAIN
Experiment-B shared x-y handoff            PR #181 GREEN, NOT MERGED
Experiment-B BALANCE consumer              PR #10 GREEN, NOT MERGED
Experiment-B pilot/power wrapper           PR #182 GREEN, NOT MERGED
real Pedicularis Experiment A              NOT YET EXECUTED
real Pedicularis Experiment B              NOT YET EXECUTED
```

No biological claim is promoted by this protocol.

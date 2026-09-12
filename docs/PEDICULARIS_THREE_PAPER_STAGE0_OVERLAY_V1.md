# Pedicularis three-paper Stage-0 qualification overlay v1

## Purpose

This is the **pre-execution qualification layer** for the registered final SCH/BALANCE/BITA identification programme.

It does not replace the detailed SCH manipulation/intervention protocols or the BITA identification design. It adds the cross-paper gates required before the integrated 40-cell ecological super-factorial can be powered or launched.

Primary design manifest:

```text
data/PEDICULARIS_FINAL_IDENTIFICATION_PROGRAM_V1.json
```

Three-world inference contract:

```text
docs/PEDICULARIS_THREE_WORLD_CHAIN_V1.md
```

## Stage-0 principle

Do not power or execute the 40-cell experiment until the biological interventions themselves have passed qualification.

The pilot asks whether the proposed factors mean what the three papers require them to mean.

```text
z manipulation valid?
P selective?
G selective?
D selective enough for BITA?
D-world legitimate enough for BALANCE?
fitness outcome measurable with usable variance?
```

A failed gate routes only the affected inference away from Pedicularis. It does not retroactively weaken the literature synthesis.

---

## Q0 — population-season qualification

Freeze a candidate:

```text
population_id
season_id
observation_window
phenology_stage
seed_predator_presence
pollinator_presence
```

Required pass condition for SCH inheritance:

```text
conflict-active context is biologically plausible
+ both functional agents occur at usable frequency
+ the registered reproductive endpoint can mature within the observation window.
```

If the antagonist is effectively absent, retain the site as a low-pressure/context control if useful, but do not launch the full causal-compromise surface there.

---

## Q1 — z manipulation qualification

Target:

```text
z = realized corolla exsertion above the cupulate bract.
```

Validate at least five reproducible levels spanning an informative range.

For every candidate level record:

```text
target_z
realized_z
flower geometry
visible / UV appearance where relevant
reward / nectar state
mechanical damage
post-manipulation persistence
```

Pass requires:

- monotone separation of realized z levels;
- acceptable overlap only inside a prospectively frozen tolerance;
- no material alteration of water-defence state D;
- no uncontrolled reward manipulation that would turn z into a compound treatment;
- no severe tissue damage that dominates fitness.

The five levels are frozen from manipulation validity, not from reproductive outcomes.

---

## Q2 — antagonist intervention G qualification

`G` must be independent of the water-defence trait `D`.

Candidate intervention examples may include selective predator exposure/exclusion or controlled exposure windows, but the exact method is system-specific.

Measure at minimum:

```text
seed_predator_attack_or_entry
predation_damage
pollinator visitation / contact
realized z
water-defence D state
```

Pass requires:

```text
large registered change in antagonist exposure/damage
+ no material change in pollinator channel beyond equivalence margin
+ no material movement of z or D.
```

Do **not** use water retained/drained as `G`.

---

## Q3 — pollinator intervention P qualification

The P intervention must alter pollinator-mediated reproductive input without silently toggling seed-predator exposure or the focal traits.

Measure at minimum:

```text
legitimate visitation / stigma contact / pollen receipt
seed-predator access or attack
realized z
water-defence D state
```

Pass requires:

```text
registered change in pollinator-mediated input
+ antagonist exposure retained within the declared equivalence margin
+ no material movement of z or D.
```

If physical bagging changes both P and G, it fails the selective-intervention gate even if all factorial cells are numerically available.

---

## Q4 — water-defence manipulation D qualification

The D manipulation has two distinct requirements.

### BITA requirement

D must act as a biologically defensible flower-specific antagonist-reducing defence contrast.

Measure:

```text
water volume / retention state
seed-predator attack
legitimate pollinator visitation / contact
nectar or reward state
realized z
flower geometry
```

Pass for BITA requires:

```text
antagonist pathway changes in the intended direction
+ A/z contrast remains interpretable
+ direct pollinator effect is absent, small, or explicitly carried as part of the identified system rather than ignored.
```

A detected D -> pollination effect does not automatically kill BITA; it changes the mechanism allocation problem and must be retained.

### BALANCE requirement

The same D contrast must additionally support a prospectively registered **accessible architecture-world interpretation** rather than merely being an arbitrary treatment with a fitness effect.

Before seeing the target worldline result, write down:

```text
what S means biologically
what D-world access means biologically
which states are reachable
which states are excluded and why
what cost / constraint is represented by enabling the additional axis
why the comparison is an architecture contrast rather than a generic environment contrast.
```

If this interpretation cannot be defended independently of the fitness result:

```text
BALANCE_PEDICULARIS_ARCHITECTURE_GATE = FAIL
```

and BALANCE must route to another system/design. SCH and BITA may continue if their own gates pass.

---

## Q5 — pollinator-independent baseline qualification

BITA requires explicit handling of reproduction when pollinators are absent.

Pilot the registered A × D contrasts under the candidate P=0 condition and determine whether:

```text
m0_delta = Delta_AD M0
```

is plausibly negligible under a prospectively frozen equivalence margin or must be estimated in the main analysis.

Do not infer `m0_delta = 0` from a nonsignificant test alone.

---

## Q6 — common fitness-scale feasibility

Primary endpoint:

```text
undamaged mature viable seeds per focal flower.
```

Stage-0 must recover enough repeated observations to estimate, without claiming the final biological effect:

```text
mean / variance by provisional treatment family
zero inflation or count dispersion
plant-level ICC / block variance
flower loss / missingness
maturation success
measurement error
```

These are power-design inputs, not evidence for SCH/BALANCE/BITA claims.

The pilot must be analysed response-blind with respect to the final directional hypotheses where possible; do not select A/D/z levels because they maximize the target outcome.

---

## Q7 — operational retention and dependence

Record:

```text
plant_id
flower_id
block / patch / date
all assigned factor states
realized manipulation values
all predeclared manipulation checks
fate / loss reason
```

If multiple flowers per plant enter the experiment, plant-level dependence must be preserved in power simulation and final uncertainty estimation.

A blossom is not automatically an independent biological replicate because it occupies a different factorial cell.

---

## Power handoff

Only after Q0–Q7 pass do we freeze:

```text
n_plants
flowers_per_plant
n_per_cell_or_allocation_ratio
blocking scheme
minimum detectable SCH optimum separation
minimum detectable BALANCE Delta_W
minimum detectable BITA A0/A1/Delta_AD W
four-way equivalence margin
attrition allowance
```

Until then:

```text
SAMPLE_SIZE = NOT FROZEN
```

The integrated design is powered for its hardest registered decision, not by choosing a convenient n per cell.

---

## Fail-closed routing table

```text
Q0 conflict context fails
  -> do not execute SCH compromise surface there;
     route to another population/season.

Q1 z manipulation fails
  -> stop SCH and any BITA A contrast based on z;
     redesign manipulation or system.

Q2 G selectivity fails
  -> no SCH causal channel receipt and no BITA antagonist allocation;
     redesign G.

Q3 P selectivity fails
  -> no SCH causal channel receipt and no BITA pollinator allocation;
     redesign P.

Q4 BITA D qualification fails
  -> BITA routes to another D manipulation/system.

Q4 BALANCE architecture qualification fails
  -> BALANCE routes independently;
     SCH/BITA may continue.

Q5 baseline cannot be treated as zero
  -> estimate m0_delta explicitly; not a programme failure.

Q6/Q7 variance or retention infeasible
  -> redesign allocation, endpoint, or field scale before main execution.
```

## Deliverable from Stage-0

The only admissible Stage-0 output is a qualification/power receipt:

```text
context qualified / not qualified
z valid levels
G selectivity status
P selectivity status
D BITA status
D BALANCE architecture status
m0 handling decision
variance / ICC / attrition estimates
recommended power simulation inputs
```

Stage-0 is **not** used to claim positive SCH conflict, BALANCE occupancy, or BITA mechanism allocation.

# Pedicularis final-programme power calibration contract v1

## Purpose

Determine the field scale for the registered final identification programme **after** Stage-0, without using pilot treatment effects to choose a convenient detectable effect.

The power workflow has two independent inputs:

```text
Stage-0 pilot
  -> nuisance parameters only

biological/theoretical decision contract
  -> minimum meaningful effects and equivalence margins
```

They are joined only after both are frozen.

## Input A — Stage-0 nuisance receipt

Build with:

```bash
python scripts/build_pedicularis_stage0_nuisance_receipt.py \
  data/PEDICULARIS_STAGE0_PILOT_TEMPLATE_V1.csv \
  --output data/PEDICULARIS_STAGE0_NUISANCE_RECEIPT_V1.json
```

The builder extracts only design nuisance quantities:

```text
seed-count mean
seed-count variance
variance/mean ratio
zero fraction
flower maturation / retention fraction
missingness / loss reasons
plant-level dependence (one-way ICC where estimable)
provisional factor-cell occupancy
```

These quantities may be used to choose a count/overdispersion model, plant-level clustering structure, attrition inflation, and feasible allocation.

They must **not** be used to define the minimum biological effect that the final programme is supposed to detect.

## Input B — prospectively frozen targets

Template:

```text
data/PEDICULARIS_POWER_TARGETS_TEMPLATE_V1.json
```

Before any final power simulation, replace every `REQUIRED_BEFORE_USE` field with a prospectively justified value.

Target values may come from:

- a biologically meaningful change on the registered scale;
- theoretical decision boundaries;
- independent published estimates not selected because they match the pilot outcome;
- a conservative range declared before reading the focal pilot treatment contrast.

They may not be chosen by inspecting which Stage-0 effect happens to look largest or significant.

## Paper-specific targets

### SCH

Power must cover the hardest registered causal-compromise decision, not merely a generic treatment main effect.

Required targets include:

```text
minimum z_P* vs z_G* separation
minimum directional optimum shift after removing each functional demand
minimum absolute component gradient near z_C*
minimum curvature needed to locate an interior optimum
minimum distance of z_C* from the tested boundary
```

A sample size that detects a P or G main effect but cannot resolve optimum geometry is not an SCH-powered design.

### BALANCE

Power target:

```text
Delta_W = W_D* - W_S*
```

on the common registered seed-fitness scale.

The BALANCE Pedicularis architecture-qualification gate must pass before this power calculation is allowed. If the D-world is not a defensible accessible architecture, no amount of sample size rescues the estimand.

### BITA

Power must address the outcome ladder and identification checks:

```text
Delta_AD W
A1 > 0 when the release claim is targeted
A0 boundary around 0
four-way A x D x G x P equivalence / non-separability decision
m0_delta equivalence if a zero pollinator-independent baseline is claimed
```

A design powered only for `Delta_AD W > 0` is not automatically powered for Level-2 functional release or the separability gate.

## Allocation principle

The integrated 40-cell ecological design is not necessarily balanced at the flower level.

Candidate allocations may differ because:

- SCH requires five z levels within one D baseline;
- BITA uses two frozen z levels but all D/G/P combinations;
- BALANCE needs adequate information over both z and D under the full ecological state;
- plant-level clustering and flower availability can make strict equal-cell allocation inefficient.

Any unequal allocation must be chosen by a frozen design criterion before final outcome analysis.

## Plant-level dependence

Repeated flowers from one plant are not independent replicates.

Power simulation and final uncertainty must preserve at least:

```text
plant_id random/block dependence
flowers per plant
cell assignment within plant
block / patch / date if used in randomization
```

The Stage-0 one-way ICC is a nuisance estimate, not a biological result. If ICC is unstable, run sensitivity power calculations over a registered plausible interval rather than setting it to zero.

## Count distribution

The primary fitness endpoint is a seed count. Stage-0 determines whether a simple Poisson approximation is untenable through:

```text
variance / mean ratio
zero fraction
plant heterogeneity
```

The final simulator should use a negative-binomial or other preregistered count model when overdispersion is material. Zero inflation should be added only if it reflects a defensible data-generating process rather than used as a generic fit improvement.

## Fail-closed status

Power is not ready when any of the following holds:

```text
Stage-0 nuisance receipt incomplete
minimum meaningful targets not frozen
BALANCE architecture gate unresolved for BALANCE power
A/D/z levels selected from the target pilot outcome
plant dependence not represented
attrition rule not frozen
```

Until all applicable gates pass:

```text
FINAL_SAMPLE_SIZE = NOT FROZEN
```

## Required power report

The first admissible final power report must show, for each candidate design:

```text
n plants
flowers per plant / expected total flowers
allocation across 40 ecological cells
expected retained flowers after attrition
nuisance parameter source and sensitivity range
SCH decision power
BALANCE decision power if architecture-qualified
BITA Level-1 / Level-2 / separability decision power
which registered decision is limiting
```

Choose the field scale against the hardest required decision or explicitly declare that one paper is being routed to a separate experiment.

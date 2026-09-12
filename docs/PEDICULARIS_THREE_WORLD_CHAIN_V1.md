# Pedicularis rex three-world validation chain v2

## Purpose

`Pedicularis rex` is the preferred shared biological platform for asking whether SCH, BALANCE, and BITA describe adjacent identification problems in one system.

The programme shares logistics, context, trait manipulations, and a primary reproductive outcome where defensible. It does **not** treat one statistical result as proof of all three papers.

The chain is ordered to avoid circularity:

```text
SCH     identify shared-coordinate conflict / compromise geometry
BALANCE compare matched shared and accessible alternative worldlines
BITA    identify the ecological mechanism of a focal trait interaction
```

Architecture-value transport (`R`, `K`, `s`, `Phi`) belongs to SLK and is not reassigned to BITA.

## Frozen cross-paper identifiers

Before execution, freeze:

```text
context_id      = population x season x protocol version
fitness_scale_id = undamaged mature viable seeds per focal flower
z_trait_id      = realized corolla exsertion above the cupulate bract
defence_trait_id = registered water-bract defence manipulation
```

If a paper uses a different outcome or context, it receives a different identifier and cannot be algebraically combined without an explicit bridge.

---

## Paper 1 / SCH — shared-coordinate conflict world

### Target

Identify whether one shared coordinate is causally pulled by opposing functional demands and, if supported, recover state-specific compromise geometry.

Registered shared coordinate:

```text
z = realized corolla exsertion above the cupulate bract.
```

SCH manipulates:

```text
z = >=5 validated exsertion levels
P = selective pollination-state intervention
G = independently qualified seed-predator exposure intervention
```

The water-defence axis intended for the later BALANCE/BITA blocks is held fixed during the SCH receipt.

Primary common fitness scale:

```text
undamaged mature viable seeds per focal flower.
```

The full surface is:

```text
W00(z), W10(z), W01(z), W11(z).
```

Required SCH receipt:

```text
z_P* = state-specific pollinator-context reproductive optimum
z_G* = state-specific antagonist-context reproductive optimum
z_C* = combined-state reproductive optimum
optimum-shift contrasts
opposing functional-component gradients
joint uncertainty / bootstrap receipt
```

Positive causal-compromise support requires:

```text
z_P* != z_G*
+ supported interior z_C*
+ removing G shifts toward z_P*
+ removing P shifts toward z_G*
+ opposed functional-component gradients near z_C*.
```

These are state-specific reproductive optima, not automatically pure-function optima. A stricter pure-function label requires the separate SCH context-stability promotion gate.

The independent predator intervention is essential. Water retained/drained must not be reused as SCH antagonist `G` when water defence is the later focal defence axis.

---

## Paper 2 / BALANCE — matched architecture worldlines

### Target

Test whether conflict can remain active while the optimized shared architecture still beats a registered accessible alternative on the same fitness scale and in the same context.

The SCH receipt supplies independent evidence that conflict is active. BALANCE then compares two explicitly registered worlds.

### Shared world S

```text
S = the preregistered one-axis exsertion architecture
    with water defence fixed at the baseline state used for the SCH receipt.
```

Optimize over the valid exsertion range:

```text
W_S* = max_z W_S(z).
```

### Accessible alternative world D

```text
D = the registered exsertion x water-defence architecture surface,
    evaluated in the same context_id and fitness_scale_id.
```

The alternative must be specified prospectively. It is not chosen after observing which treatment gives the largest fitness.

Optimize over its registered accessible states:

```text
W_D* = max_(z,y) W_D(z,y).
```

Primary direct estimand:

```text
Delta_W = W_D* - W_S*.
```

Direct BALANCE support requires:

```text
active conflict from the independent SCH receipt
and
Delta_W < 0
```

with joint uncertainty for the optimized worldline difference.

This is the minimum direct BALANCE receipt. It does **not** require estimates of `s`, `K`, `Phi`, `xi`, `d_B`, or a historical differentiation process.

### Optional environmental crossing

If predator pressure, water context, or another prospectively registered environment is traversed, estimate:

```text
Delta_W(e)
e_c such that Delta_W(e_c) = 0
```

with uncertainty. This tests the architecture boundary directly. Hysteresis requires a genuine forward/reverse protocol and is not inferred from a static cross-section.

---

## Paper 3 / BITA — mechanism allocation for the focal trait interaction

### Target

Given two biologically validated trait contrasts, determine what ecological mechanism generates their reproductive interaction.

BITA does **not** re-estimate the architecture-value chain. Its focal warning is:

```text
trait interaction != ecological mechanism.
```

### Frozen focal contrasts

Use prospectively frozen, biologically valid contrasts:

```text
A = low / high attraction-facing exsertion contrast
D = low / high water-bract defence contrast
```

The A and D levels must be frozen before inspecting the BITA outcome interaction. They may be informed by manipulation validity and the SCH/BALANCE experimental range, but not chosen post hoc to maximize `Delta_AD W`.

### Primary four-cell trait estimands

Under the full ecological state:

```text
A0 = W10 - W00
A1 = W11 - W01
Delta_AD W = A1 - A0.
```

This distinguishes:

```text
Level 1  positive interaction relief:      Delta_AD W > 0
Level 2  functional constraint release:    A0 <= 0 < A1
Level 3  strict reversal:                   A0 < 0 < A1.
```

None of these alone identifies mechanism.

### Crossed consumer-allocation experiment

Cross:

```text
A x D x E_G x E_P
```

where:

```text
E_G = selective seed-predator excluded / present
E_P = selective pollinator excluded / present
```

giving 16 cells.

The design is admissible only if the consumer interventions preserve the registered A and D contrasts and are selective enough for causal channel interpretation.

Estimate antagonist relief at both pollinator states and pollinator-dependent increments at both antagonist states. The `A x D x E_G x E_P` four-way interaction is the internal separability diagnostic; it is not a nuisance term.

### Pollinator-independent baseline

Pollinator exclusion does not automatically imply zero reproduction. Estimate or independently justify the `A x D` interaction in the pollinator-absent baseline (`m0_delta`) before promoting the pollinator contrast to total pollinator interference.

### Remaining channel

After the total interaction and identifiable consumer channels are estimated, retain the unallocated remainder as:

```text
U_delta
```

rather than labelling it a cost by subtraction.

Run an independent `A x D` assay under conditions that suppress or standardize the focal consumer channels. For example, a consumer-standardized hand-pollination / predator-exclusion assay may test a direct physiological or allocation channel if the manipulation itself remains valid. A biological `kappa` label is allowed only if that independent assay supports it on an appropriate scale.

### BITA positive receipt

The strongest BITA receipt therefore contains:

```text
focal A x D total interaction
+ uncertainty for A0, A1 and Delta_AD W
+ selective antagonist allocation face
+ selective pollinator allocation face
+ pollinator-independent baseline handling
+ four-way separability result
+ independent assay of any remaining joint channel before biological labelling.
```

---

## SLK handoff — optional architecture-value transport

If the programme later wants to estimate or test:

```text
R
K
s
Phi = R - K   (or the registered SLK equivalent)
accessibility
invasion
fixation
occupancy
```

those quantities are handled in SLK using valid upstream receipts from SCH/BALANCE and any independently identified cost information. They are not BITA outputs by default.

---

## Reuse rules across the three papers

The same raw plants or experimental infrastructure may support more than one paper only when the estimands remain prospectively distinct.

Allowed reuse:

```text
same context_id
same fitness_scale_id
shared manipulation-validation data
shared environmental covariates
shared randomization blocks when declared
```

Not allowed:

```text
using the same contrast as both independent prerequisite and outcome proof
choosing BITA A/D levels after seeing the target interaction
using water defence as both SCH antagonist intervention and BITA defence trait
calling a BALANCE worldline difference an identified BITA mechanism
calling a BITA residual an SLK/BALANCE architecture cost without an independent assay
```

## Minimal programme sequence

```text
0. qualify one population-season and manipulation validity
1. SCH: >=5 z levels x P x G -> causal compromise receipt
2. BALANCE: matched S vs registered z x y accessible world -> Delta_W receipt
3. BITA: frozen A x D x E_G x E_P -> mechanism-allocation receipt
4. optional SLK transport using only justified upstream quantities
```

## Stop rules

- If SCH does not recover conflict, do not force BALANCE or BITA to inherit a conflict premise.
- If the BALANCE alternative is not a prospectively registered accessible architecture, do not report `W_D* - W_S*` as a direct architecture comparison.
- If BITA consumer interventions are nonselective or the four-way separability diagnostic fails, retain partial identification rather than forcing channel allocation.
- If an independent remaining-channel assay does not match the residual, report the mismatch as evidence of omitted channels or intervention leakage.

## Current status

The literature-first synthesis phases for SCH, BALANCE, and BITA are complete on their current main branches. This chain therefore represents the **final direct-identification layer**, not the empirical starting point of any of the three papers.

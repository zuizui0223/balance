# BALANCE — persistence inside the compromise domain

`balance` is the middle-world theory between [`sch`](https://github.com/zuizui0223/sch) conflict identification and [`slk`](https://github.com/zuizui0223/slk) architecture value/evolutionary transport. [`bita`](https://github.com/zuizui0223/bita) is an orthogonal mechanism-identification layer rather than the owner of the architecture-value boundary.

## Programme structure

```text
SCH
shared trait coordinate
-> is there a real functional conflict, and what is its load L?

BALANCE
conflict is real, but differentiation still does not pay
-> how broad, deep, resilient, connected, and persistent is this compromise domain?

SLK
architecture value and evolutionary transport
-> Phi = R-K -> accessibility -> invasion -> fixation -> occupancy

BITA (orthogonal)
trait interaction -> identified set -> mechanism allocation
```

The value hierarchy is therefore

```text
SCH -> BALANCE -> SLK
conflict -> persistent compromise -> architecture value and realization
```

while BITA asks a different question: what ecological mechanism is identified by a measured trait interaction?

## BALANCE as a middle world

SCH and SLK supply the two theoretical boundaries.

```text
SCH-facing certificate
L > 0
= a real shared-axis conflict exists

SLK-facing architecture-value certificate
Phi = R-K > 0
= recoverable benefit exceeds extra architecture cost
```

BALANCE is their sandwiched intersection:

```text
L > 0
and
Phi < 0.
```

Under the registered quadratic bridge only,

```text
R = sL,  s in [0,1],
Phi = sL-K.
```

`R=sL` is not a universal identity for arbitrary landscapes.

On a common fitness scale define

```text
rho = K-R
xi  = L / (L+rho)
d_B = min(L,rho).
```

Inside BALANCE, `0 < xi < 1`. `xi -> 0` approaches the SCH-facing no-conflict boundary, `xi -> 1` approaches the SLK-facing architecture-value boundary, and `d_B` measures two-sided depth inside the middle world.

See `docs/MIDDLE_WORLD_DEFINITION.md`, `docs/THEORY_OWNERSHIP_CLOSURE_V1.md`, and `balance_domain/world.py`.

## Direct empirical two-worldline route

BALANCE does **not** require the decomposed `R,K` representation before it can be tested.

If the two worldlines can be optimized on one matched reproductive-fitness scale, define

```text
W_S*(e) = optimized shared-coordinate fitness
W_D*(e) = optimized differentiated-accessible fitness
Delta_W(e) = W_D*(e)-W_S*(e).
```

Then a direct middle-world receipt is

```text
L(e) > 0
and
Delta_W(e) < 0.
```

This makes BALANCE logically independent: SCH supplies evidence that the shared world is genuinely conflicted, BALANCE compares the optimized worldlines, and SLK supplies the architecture-value decomposition

```text
Delta_W = Phi = R-K
```

when the direct and decomposed descriptions share a valid bridge. Under the registered quadratic bridge this becomes

```text
Delta_W = sL-K.
```

BITA does not own this decomposition. BITA separately asks what a measured `A x D` interaction identifies about ecological channel allocation. A bridge residual is retained as a diagnostic mismatch rather than automatically assigned to a BITA mechanism or an SLK cost.

See `docs/TWO_WORLDLINE_CONCORDANCE.md`, `balance_domain/worldlines.py`, and `balance_domain/worldline_path.py`.

## Static domain

Let

```text
L(e) = shared-coordinate conflict / compromise load
R(e) = recoverable conflict loss for the registered differentiated architecture
K(e) = added architecture cost
Phi(e) = R(e)-K(e)
```

Then

```text
L = 0              no identified shared-axis conflict
L > 0, Phi < 0     BALANCE domain
Phi = 0            architecture-value critical surface
Phi > 0            positive global architecture margin
```

For the registered quadratic bridge `R=sL`,

```text
0 < L < K/s
```

is the BALANCE-only region when `s>0`.

## BALANCE estimands

This repository studies properties of the *interior* of that region rather than either boundary alone:

```text
xi                        position between SCH- and SLK-facing boundaries
d_B                       two-sided depth inside BALANCE
q = R/K                   dimensionless proximity to the architecture crossing
rho = K-R                 critical reserve
W_e                       environmental width of BALANCE occupancy
A_rho                     integrated reserve across environment
N_B                       number of connected BALANCE intervals
N_0                       number of Phi=0 crossings
```

## Current theoretical results

1. **Two-sided world certificate.** BALANCE is exactly the intersection `L>0` and `Phi<0`; `xi` and `d_B` locate a context inside that sandwiched region on a common fitness scale.

2. **Direct worldline route.** `L>0` and `W_D*-W_S*<0` identify the middle world without requiring a prior `R,K` decomposition.

3. **Deepest BALANCE point under the quadratic bridge.** For fixed `s>0` and `K>0`, the BALANCE interval is `0<L<K/s`, and maximum two-sided depth occurs at

```text
L_deep = K/(1+s)
rho_deep = K/(1+s)
xi_deep = 1/2.
```

Relative to the full conflict-load width, the deepest point lies at `s/(1+s)`.

4. **Positive affine-scale invariance.** Applying the same positive affine transformation to the common fitness scale leaves the BALANCE state, `xi`, and `q` unchanged. Dimensional quantities such as `rho` and `d_B` rescale.

5. **No-reentry sufficient condition under the quadratic bridge.** If along an ordered environment `L` and `s` are nondecreasing and `K` is nonincreasing, then `Phi=sL-K` is nondecreasing. BALANCE can therefore form at most one connected interval before the positive-margin domain under those sufficient assumptions.

6. **Switching-cost persistence.** If shared→differentiated switching costs `C_SD`, differentiated→shared costs `C_DS`, and a context persists for horizon `T`, then history dependence occurs for

```text
-C_DS/T <= Phi <= C_SD/T
```

with hysteresis-band width

```text
Delta_Phi_hyst = (C_SD + C_DS)/T.
```

This persistence halo is distinct from the static BALANCE core and does not by itself identify accessibility, invasion, fixation, or occupancy.

See `theory/MIDDLE_WORLD_RESULTS_V1.md`.

## Empirical claim levels

BALANCE separates two empirical levels.

```text
FUNCTIONAL_STATE_MIDDLE_WORLD
second functional state/axis is experimentally enabled or disabled
but the structural architecture itself is not removed or costed

STRUCTURAL_ARCHITECTURE_MIDDLE_WORLD
repeatable structural/performance difference is established
and matched architecture/maintenance cost is on the same fitness scale
```

For `Pedicularis rex`, the current water retained/drained intervention belongs first to the **functional-state** level. It does not by itself establish a structural-architecture middle world because the cupulate bract architecture is still present.

The empirical gate is tracked in issue #3 and `empirical/BALANCE_EXECUTION_RECOVERY_LEDGER_V1.csv`.

## Current observational anchor: Peucedanum

Published `Peucedanum multivittatum` results provide an external critical-region anchor. Three operational definitions—final fruit-set selection gradient, selection differential, and female-gain shape—each cross their threshold between the same ordered contexts `HL` and `HC`.

Registered result:

```text
SAME_COARSE_CRITICAL_BRACKET = HL--HC.
```

This does **not** establish `L`, `W_S*`, `W_D*`, or the common architecture boundary. It shows only that multiple definitions independently locate one observational transition region.

See `docs/PEUCEDANUM_CRITICAL_REGION_ANCHOR_V1.md` and `empirical/peucedanum/PEUCEDANUM_CRITICAL_DEFINITIONS_V1.json`.

## Separation from sister repositories

- **SCH owns** conflict identification and, when admissible, export of a fitness-scale conflict load `L`.
- **BALANCE owns** direct ordering of shared and differentiated-accessible worldlines and the geometry, depth, reserve, topology, and persistence of the region `L>0, Phi<0`.
- **SLK owns** the architecture-value object `Phi=R-K`, the quadratic bridge `R=sL`, and the subsequent accessibility → invasion → fixation → occupancy hierarchy.
- **BITA owns** `trait interaction != ecological mechanism`, identified sets, partial identification, selective interventions, separability diagnostics, and mechanism allocation.

The programme therefore says:

```text
SCH:      conflict exists.
BALANCE:  the shared world still outranks the differentiated-accessible world.
SLK:      when Phi crosses zero, global value changes; realization still has further gates.
BITA:     a trait interaction does not identify its ecological mechanism without extra information.
```

Do not claim historical trait splitting from this repository without independent historical evidence.

## Current status

Implemented with regression guards:

- static BALANCE path analysis,
- critical reserve and topology,
- switching-cost hysteresis,
- middle-world certificate,
- middle-world position `xi`,
- two-sided depth `d_B`,
- deepest-point geometry,
- direct shared-vs-differentiated worldline comparison,
- direct empirical worldline-path mapping,
- direct-versus-decomposed bridge concordance checks,
- same-critical-point versus parallel-critical-points classification,
- bounded cross-repository receipts that preserve uncertainty,
- Peucedanum multi-definition critical-region fixture,
- explicit functional-state versus structural-architecture claim ceiling.

Legacy code identifiers containing `bita_*` are retained temporarily for backward compatibility only; they no longer define scientific ownership of the `Phi=0` boundary.

## Literature-synthesis milestone

The manuscript programme places literature-pattern recovery before final direct validation. The source-adjudicated pattern ledger contains 17 independent biological clusters, including 9 middle-regime signatures. A strict Q1B quantitative layer has three independent effect-size-ready positive-admitted systems (`Fragaria vesca`, `Impatiens capensis`, and `Gymnadenia conopsea` 2015), alongside two design-matched negative controls and explicit estimand/attribution boundaries.

Because positive Q1B admission requires the preregistered same-coordinate conflict pattern, the three-cluster random-effects result is interpreted as a **conditional positive-case summary of magnitude and heterogeneity**. It is not an unbiased design-wide meta-analytic mean and its sign is not an independent test of recurrence. Recurrence is supported by recovery of the registered pattern in three independent biological systems; the matched negative controls show that comparable factorial designs do not inevitably produce the pattern.

The literature synthesis still has zero matched direct shared-versus-differentiated worldline receipts. Therefore the remaining empirical task is the same-context, common-fitness-scale comparison of `W_S*` and `W_D*` with joint uncertainty. That empirical gap does not prevent the theoretical ownership structure from being closed.

# BALANCE — Chapter 2: persistence inside the compromise domain

`balance` is the middle chapter between [`sch`](https://github.com/zuizui0223/sch) and [`bita`](https://github.com/zuizui0223/bita).

## Three-chapter programme

```text
Chapter 1 / SCH
shared trait coordinate
-> where does compromise settle?

Chapter 2 / BALANCE
conflict is real, but differentiation still does not pay
-> how broad, deep, resilient, connected, and persistent is the compromise domain?

Chapter 3 / BITA
additional trait dimensions become worthwhile
-> when does differentiation win, and through which mechanism?
```

The chapter ordering is therefore:

```text
SCH -> BALANCE -> BITA
where to compromise -> why compromise persists -> when/how to differentiate
```

## BALANCE as a middle world

SCH and BITA supply complementary boundary definitions.

```text
SCH-facing certificate
L > 0
= a real shared-axis conflict exists

BITA-facing certificate
Phi = sL-K > 0
= recovered conflict loss exceeds extra architecture cost
```

BALANCE is their sandwiched intersection:

```text
L > 0
and
Phi < 0.
```

It is therefore not a third unrelated fitness model or a third architecture. It is the world in which the SCH conflict is already real while the BITA architecture switch is still not worth paying for.

On a common fitness scale define

```text
rho = K-sL
xi  = L / (L+rho)
d_B = min(L,rho).
```

Inside BALANCE, `0 < xi < 1`. `xi -> 0` approaches the SCH-facing no-conflict boundary, `xi -> 1` approaches the BITA-facing differentiation boundary, and `d_B` measures two-sided depth inside the middle world.

See `docs/MIDDLE_WORLD_DEFINITION.md` and `balance_domain/world.py`.

## Direct empirical two-worldline route

Chapter 2 does **not** require the full Chapter-3 decomposition before it can be tested.

If the two worldlines can be optimized on one matched reproductive fitness scale, define

```text
W_S*(e) = optimized shared-coordinate fitness
W_D*(e) = optimized differentiated-accessible fitness
Delta_W(e) = W_D*(e)-W_S*(e).
```

Then a direct middle-world receipt can be obtained from

```text
L(e) > 0
and
Delta_W(e) < 0.
```

This makes the chapter logically independent: SCH supplies evidence that the shared world is genuinely conflicted, BALANCE compares the optimized worldlines, and BITA may later decompose the observed gap into

```text
Delta_W = sL-K
```

and identify its mechanism.

When both the direct and decomposed routes are available, they must agree on the registered common fitness scale. A mismatch is exposed as a bridge residual rather than averaged away.

See `docs/TWO_WORLDLINE_CONCORDANCE.md`, `balance_domain/worldlines.py`, and `balance_domain/worldline_path.py`.

## Static domain

Let

```text
L(e) = one-axis conflict / compromise load
s(e) = fraction of that load recoverable by extra dimensionality
K(e) = added architecture cost
R(e) = s(e)L(e)
Phi(e) = R(e)-K(e)
```

Then

```text
L = 0              no shared-axis conflict
L > 0, Phi < 0     BALANCE domain
Phi = 0            architecture critical surface
Phi > 0            DIFFERENTIATION domain
```

For the quadratic bridge used by SCH and BITA,

```text
0 < L_S* < K/s
```

is the BALANCE-only region.

## Chapter-2 estimands

This repository studies properties of the *interior* of that region rather than either boundary alone:

```text
xi                        position between SCH- and BITA-facing boundaries
d_B                       two-sided depth inside BALANCE
q = R/K                   dimensionless proximity to differentiation
rho = K-R                 critical reserve
W_e                       environmental width of BALANCE occupancy
A_rho                     integrated reserve across environment
N_B                       number of connected BALANCE intervals
N_0                       number of Phi=0 crossings
```

## Current theoretical results

1. **Two-sided world certificate.** BALANCE is exactly the intersection `L>0` and `Phi<0`; `xi` and `d_B` locate a context inside that sandwiched region on a common fitness scale.

2. **Direct worldline route.** `L>0` and `W_D*-W_S*<0` identify the middle world without requiring a prior `s,K` decomposition. This removes circular dependence on Chapter 3.

3. **Deepest BALANCE point.** For fixed `s>0` and `K>0`, the BALANCE interval is `0<L<K/s`, but its deepest point in the two-margin fitness geometry is not generally halfway along that interval. It occurs at

```text
L_deep = K/(1+s)
rho_deep = K/(1+s)
xi_deep = 1/2.
```

Relative to the full conflict-load width, the deepest point lies at `s/(1+s)`. Weak decoupling therefore displaces the most robust BALANCE state toward the SCH-facing side.

4. **Positive affine-scale invariance.** Applying the same positive affine transformation to the common fitness scale leaves the BALANCE state, `xi`, and `q` unchanged. Dimensional quantities such as `rho` and `d_B` rescale.

5. **No-reentry sufficient condition.** If along an ordered environment `L` and `s` are nondecreasing and `K` is nonincreasing, then `Phi=sL-K` is nondecreasing. BALANCE can therefore form at most one connected interval before differentiation; a BALANCE→DIFFERENTIATION→BALANCE sequence requires at least one monotonicity condition or the common-world mapping to fail.

6. **Switching-cost persistence.** If moving shared→differentiated costs `C_SD`, moving differentiated→shared costs `C_DS`, and a context persists for horizon `T`, then history dependence occurs for

```text
-C_DS/T <= Phi <= C_SD/T
```

with hysteresis-band width

```text
Delta_Phi_hyst = (C_SD + C_DS)/T.
```

Thus shared and differentiated states can both persist around the static crossing depending on history.

See `theory/MIDDLE_WORLD_RESULTS_V1.md`.

## Empirical claim levels

Chapter 2 separates two empirical levels.

```text
FUNCTIONAL_STATE_MIDDLE_WORLD
second functional state/axis is experimentally enabled or disabled
but the structural architecture itself is not removed or costed

STRUCTURAL_ARCHITECTURE_MIDDLE_WORLD
repeatable structural/performance y is established
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

## Separation from the sister chapters

- **SCH supplies** the shared-coordinate compromise geometry and, when identified, a fitness-scale conflict budget `L`.
- **BALANCE studies** the direct ordering of the shared and differentiated-accessible worldlines and the geometry, two-sided depth, reserve, topology, and persistence of the region where conflict exists but the shared world still wins.
- **BITA supplies** the mechanistic decomposition into recoverability `s`, architecture cost `K`, dimensional release, and ecological mechanism identification once differentiated axes become relevant.

The definitions intentionally complement one another:

```text
SCH says:      conflict exists.
BALANCE says:  the shared world still outranks the differentiated-accessible world despite that conflict.
BITA says:     the differentiated world has crossed above it, and asks why.
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

The main empirical target is now a matched same-context chain in `Pedicularis rex`: positive SCH conflict receipt → direct functional-state BALANCE worldline comparison → BITA dimensional-release/mechanism analysis → optional structural-architecture promotion. `Peucedanum` remains an observational critical-region anchor rather than a direct BALANCE worldline receipt.

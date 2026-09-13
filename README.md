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
3. **Deepest BALANCE point under the quadratic bridge.** For fixed `s>0` and `K>0`, maximum two-sided depth occurs at `L_deep=K/(1+s)`, `rho_deep=K/(1+s)`, `xi_deep=1/2`.
4. **Positive affine-scale invariance.** Common positive affine transformations preserve BALANCE state and dimensionless coordinates.
5. **No-reentry sufficient condition under the quadratic bridge.** Nondecreasing `L,s` with nonincreasing `K` makes `Phi=sL-K` nondecreasing.
6. **Switching-cost persistence.** Switching costs create a history-dependent halo around the static crossing; this does not identify accessibility, invasion, fixation, or occupancy.

See `theory/MIDDLE_WORLD_RESULTS_V1.md`.

## Separation from sister repositories

- **SCH owns** conflict identification and, when admissible, export of a fitness-scale conflict load `L`.
- **BALANCE owns** direct ordering of shared and differentiated-accessible worldlines and the geometry, depth, reserve, topology, and persistence of the region `L>0, Phi<0`.
- **SLK owns** the architecture-value object `Phi=R-K`, the quadratic bridge `R=sL`, and the subsequent accessibility → invasion → fixation → occupancy hierarchy.
- **BITA owns** `trait interaction != ecological mechanism`, identified sets, partial identification, selective interventions, separability diagnostics, and mechanism allocation.

Legacy code identifiers containing `bita_*` are retained temporarily for backward compatibility only; they no longer define scientific ownership of the `Phi=0` boundary.

The literature synthesis still has zero matched direct shared-versus-differentiated worldline receipts. That empirical gap does not prevent the theoretical ownership structure from being closed.

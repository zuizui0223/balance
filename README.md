# BALANCE — Chapter 2: persistence inside the compromise domain

`balance` is the middle chapter between [`sch`](https://github.com/zuizui0223/sch) and [`bita`](https://github.com/zuizui0223/bita).

## Three-chapter programme

```text
Chapter 1 / SCH
shared trait coordinate
-> where does compromise settle?

Chapter 2 / BALANCE
conflict is real, but differentiation still does not pay
-> how broad, resilient, connected, and persistent is the compromise domain?

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

It is therefore not a third unrelated fitness model. It is the world in which the SCH conflict is already real while the BITA architecture switch is still not worth paying for.

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

If the two architectures can be optimized on one matched reproductive fitness scale, define

```text
W_S*(e) = optimized shared-coordinate fitness
W_D*(e) = optimized differentiated-coordinate fitness
Delta_W(e) = W_D*(e)-W_S*(e).
```

Then an empirical BALANCE receipt can be obtained directly from

```text
L(e) > 0
and
Delta_W(e) < 0.
```

This makes the chapter logically independent: SCH supplies evidence that the shared world is genuinely conflicted, BALANCE compares the two optimized worldlines, and BITA may later decompose the observed gap into

```text
Delta_W = sL-K
```

and identify its mechanism.

When both the direct and decomposed routes are available, they must agree on the registered common fitness scale. A mismatch is exposed as a bridge failure rather than averaged away.

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

## First results

1. **Two-sided world certificate.** BALANCE is exactly the intersection `L>0` and `Phi<0`; the new `xi` and `d_B` estimands locate a context inside that sandwiched region on a common fitness scale.

2. **Direct worldline route.** `L>0` and `W_D*-W_S*<0` identify the middle world without requiring a prior `s,K` decomposition. This removes circular dependence on Chapter 3.

3. **No-reentry sufficient condition.** If along an ordered environment `L` and `s` are nondecreasing and `K` is nonincreasing, then `Phi=sL-K` is nondecreasing. BALANCE can therefore form at most one connected interval before differentiation; a BALANCE→DIFFERENTIATION→BALANCE sequence requires at least one monotonicity condition or the common-world mapping to fail.

4. **Switching-cost persistence.** If moving shared→differentiated costs `C_SD`, moving differentiated→shared costs `C_DS`, and a context persists for horizon `T`, then history dependence occurs for

```text
-C_DS/T <= Phi <= C_SD/T
```

with hysteresis-band width

```text
Delta_Phi_hyst = (C_SD + C_DS)/T.
```

Thus BALANCE can be a persistent state even after the instantaneous fitness ordering has become weakly favourable to differentiation.

## Separation from the sister chapters

- **SCH supplies** the shared-coordinate compromise geometry and, when identified, a fitness-scale conflict budget `L`.
- **BALANCE studies** the direct ordering of the shared and differentiated worldlines and the geometry, two-sided depth, reserve, topology, and persistence of the region where conflict exists but shared architecture still wins.
- **BITA supplies** the mechanistic decomposition into recoverability `s`, architecture cost `K`, dimensional release, and ecological mechanism identification once differentiated axes become relevant.

The definitions intentionally complement one another:

```text
SCH says:   conflict exists.
BALANCE says: the shared world still outranks the differentiated world despite that conflict.
BITA says:  the differentiated world has crossed above it, and asks why.
```

Do not claim historical trait splitting from this repository without independent historical evidence.

## Current status

Implemented and regression-tested:

- static BALANCE path analysis,
- critical reserve and topology,
- switching-cost hysteresis,
- middle-world certificate,
- middle-world position `xi`,
- two-sided depth `d_B`,
- direct shared-vs-differentiated worldline comparison,
- direct empirical worldline-path mapping,
- direct-versus-decomposed bridge concordance checks.

Immediate empirical validation targets are paired SCH/BALANCE/BITA receipts from systems such as *Pedicularis rex* and observational critical brackets such as *Peucedanum multivittatum*. The main empirical question is whether natural systems occupy a measurable interior BALANCE world, merely sit close to one boundary, or show history-dependent overlap of the shared and differentiated worldlines.

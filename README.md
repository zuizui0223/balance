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
q = R/K                   dimensionless proximity to differentiation
rho = K-R                 critical reserve
W_e                       environmental width of BALANCE occupancy
A_rho                     integrated reserve across environment
N_B                       number of connected BALANCE intervals
N_0                       number of Phi=0 crossings
```

## First results

1. **No-reentry sufficient condition.** If along an ordered environment `L` and `s` are nondecreasing and `K` is nonincreasing, then `Phi=sL-K` is nondecreasing. BALANCE can therefore form at most one connected interval before differentiation; a BALANCE→DIFFERENTIATION→BALANCE sequence requires at least one monotonicity condition or the common-world mapping to fail.

2. **Switching-cost persistence.** If moving shared→differentiated costs `C_SD`, moving differentiated→shared costs `C_DS`, and a context persists for horizon `T`, then history dependence occurs for

```text
-C_DS/T <= Phi <= C_SD/T
```

with hysteresis-band width

```text
Delta_Phi_hyst = (C_SD + C_DS)/T.
```

Thus BALANCE can be a persistent state even after the instantaneous fitness ordering has become weakly favourable to differentiation.

## Separation from the sister chapters

- **SCH supplies** the shared-coordinate compromise geometry and, when identified, a fitness-scale conflict budget.
- **BALANCE studies** the geometry, reserve, topology, and persistence inside the region where shared architecture still wins.
- **BITA supplies** dimensional release, architecture cost, and mechanism identification once differentiated axes become relevant.

Do not claim historical trait splitting from this repository without independent historical evidence.

## Current status

The repository is initialized as a theory/analysis Chapter-2 programme. The immediate validation target is to implement the static path analyser and switching-cost dynamics with regression tests, then apply them first to synthetic paths and later to paired SCH/BITA receipts from systems such as *Pedicularis rex* and observational critical brackets such as *Peucedanum multivittatum*.

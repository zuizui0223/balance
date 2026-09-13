# BALANCE manuscript Theory text v1

## A sandwiched persistence domain

We consider a biological coordinate that contributes to multiple functions and is therefore subject to a shared-coordinate conflict load `L >= 0`. Let `R >= 0` denote recoverable conflict loss available to a registered differentiated architecture, and let `K >= 0` denote its additional architecture cost on the same fitness scale. Define

```text
Phi = R-K
rho = K-R = -Phi.
```

The static BALANCE core is exactly

```text
B = {L>0} ∩ {Phi<0}.
```

Thus conflict must already be present, but the registered differentiated architecture must still have lower optimized net fitness. The regime is sandwiched between a no-conflict boundary at `L=0` and an architecture-value boundary at `Phi=0`.

For the registered quadratic bridge only, let `s in [0,1]` denote the recoverable fraction of the shared-coordinate conflict load, so that

```text
R = sL
Phi = sL-K.
```

For `s>0`, BALANCE becomes `0<L<K/s`. The relation `R=sL` is therefore a model-specific bridge/corollary, not the general definition of recoverable benefit.

## Direct worldline identification

The decomposed variables `R` and `K`, and `s` when the quadratic bridge is invoked, are not required to define BALANCE empirically. Suppose the shared and differentiated-accessible alternatives can be optimized in matched contexts on one common fitness scale. Let

```text
W_S* = optimized shared-architecture fitness
W_D* = optimized differentiated-accessible fitness
Delta_W = W_D* - W_S*.
```

A direct BALANCE receipt is

```text
L > 0
and
Delta_W < 0.
```

The architecture boundary is `Delta_W=0`, and the positive architecture-margin side is `Delta_W>0`. Under a valid bridge,

```text
Delta_W = Phi = R-K,
```

and only under the registered quadratic bridge,

```text
Delta_W = sL-K.
```

This separates the programme layers. SCH establishes whether conflict is active (`L>0`); BALANCE identifies whether the shared worldline still outranks an accessible differentiated alternative; SLK owns the architecture-value object `Phi=R-K` and the subsequent distinction between global value, accessibility, invasion, fixation, and occupancy. BITA is orthogonal: it asks what a measured cross-trait interaction identifies about ecological channel allocation. BITA mechanism terms are not identical to `R`, `K`, or `Phi` unless an additional biological bridge is justified.

## Position and depth inside the middle world

Inside BALANCE, define

```text
rho = K-R > 0
xi = L/(L+rho)
d_B = min(L,rho).
```

As `L->0+`, `xi->0`; as `rho->0+`, `xi->1`. The two-sided depth `d_B` gives the smaller of the distances to the SCH-facing and SLK-facing architecture-value margins. When direct worldlines are observed,

```text
rho_direct = W_S* - W_D*
xi_direct = L/(L+rho_direct)
d_B,direct = min(L,rho_direct).
```

Under bridge concordance the direct and decomposed coordinates must agree. Neither `xi` nor `d_B` is evolutionary time.

Under the quadratic bridge with fixed `s>0` and `K>0`, `d_B(L)=min[L,K-sL]`, and maximum depth occurs at

```text
L_deep = K/(1+s)
rho_deep = K/(1+s)
xi_deep = 1/2
d_B,max = K/(1+s).
```

Relative to the full conflict-load width `K/s`, the deepest point occurs at `s/(1+s)`.

## Scale and shape of the persistence region

Under the same quadratic bridge, the SCH-boundary-limited width is

```text
W_S = K/(1+s)
```

and the SLK-boundary-limited width is

```text
W_A = K/[s(1+s)],
```

so `W_A/W_S=1/s`. Increasing `K` stretches both sides proportionally, while changing `s` changes normalized skew.

The state classification is invariant to a common positive affine transformation of the fitness scale. If `W'=aW+b` with `a>0` applied identically to linked SCH, BALANCE, and SLK architecture comparisons, all fitness differences scale by `a` and the additive constant cancels. BALANCE occupancy and dimensionless coordinates are unchanged, whereas dimensional quantities such as `rho` and `d_B` rescale.

## Environmental paths and topology

Under the quadratic bridge, if along an ordered context `L(e)` and `s(e)` are nondecreasing while `K(e)` is nonincreasing, then

```text
Phi(e)=s(e)L(e)-K(e)
```

is nondecreasing. Under these sufficient conditions BALANCE can occupy at most one connected interval before the positive architecture-margin domain. Re-entry therefore requires at least one monotonicity condition, or the common-world mapping, to fail. This is a bridge-conditional result rather than a general identity for arbitrary landscapes.

## Direct–decomposed concordance

When the direct optimized-worldline comparison and decomposed architecture-value route describe the same contexts, reproductive-fitness outcome, architecture-cost definition, and modeled channels, they must satisfy

```text
Delta_W = R-K.
```

Under the quadratic bridge this becomes `Delta_W=sL-K`. Define

```text
delta_parallel = Delta_W-(R-K).
```

Under a valid common-world mapping `delta_parallel=0`. A non-zero residual is informative only after excluding scale mismatch, context mismatch, inconsistent cost definitions, and omitted channels. It is not automatically a BITA mechanism term, an SLK architecture cost, or a named biological process.

## Switching costs and history dependence

Let `C_SD` be the cost of switching from shared to differentiated, `C_DS` the reverse switching cost, and `T>0` the persistence horizon. Starting shared, switching pays only when `Phi>C_SD/T`; starting differentiated, switching back pays only when `Phi<-C_DS/T`. Hence the history-dependent band is

```text
-C_DS/T <= Phi <= C_SD/T
```

with width `(C_SD+C_DS)/T`. This persistence halo is distinct from the static BALANCE core and does not identify the SLK accessibility, invasion, fixation, or occupancy stages without their own process assumptions.

## Empirical consequences and falsifiers

Opposing selection can establish active conflict without showing that the shared architecture currently outranks an alternative. Persistence of an integrated state can provide a middle-regime signature without identifying the worldline difference. A differentiated outcome can locate the positive architecture-margin side without showing where the crossing occurred. Strict BALANCE occupancy requires linked evidence on conflict and relative optimized worldlines.

Direct and decomposed worldline estimates should agree after bridge audits; direct and decomposed `xi` and `d_B` should coincide under the same mapping; re-entry under the quadratic monotonicity assumptions would reject those sufficient conditions; forward and reverse architecture thresholds can test the switching-cost extension; and quadratic deep-BALANCE geometry can test the registered `L_deep=K/(1+s)` prediction. These predictions do not alter the ownership split: SCH identifies conflict, BALANCE owns the persistent middle world, SLK owns architecture value and evolutionary transport, and BITA owns ecological mechanism identification for trait interactions.

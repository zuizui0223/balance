# BALANCE manuscript Theory text v1

## A sandwiched persistence domain

We consider a biological coordinate that contributes to multiple functions and is therefore subject to a shared-coordinate conflict load `L >= 0`. Additional dimensionality can recover only part of that loss. Let `s in [0,1]` denote the recoverable fraction, `R=sL` the corresponding benefit of differentiation, and `K>=0` the added architecture cost. Define the differentiated-minus-shared architecture margin

```text
Phi = R-K = sL-K,
```

and the BALANCE reserve

```text
rho = K-R = -Phi.
```

The static BALANCE core is exactly

```text
B = {L>0} ∩ {Phi<0}.
```

Thus conflict must already be present, but differentiation must still reduce net fitness. For `s>0`, the same condition is

```text
0 < L < K/s.
```

The regime is therefore sandwiched between a no-conflict boundary at `L=0` and a differentiation boundary at `Phi=0`. It is not a third architecture state. It is the region in which the shared architecture persists despite active conflict because the recoverable benefit of additional dimensionality is still smaller than its cost.

## Direct worldline identification

The decomposed variables `s` and `K` are useful for mechanism, but they are not required to define BALANCE empirically. Suppose the shared and differentiated-accessible alternatives can be optimized in matched contexts on one common fitness scale. Let

```text
W_S* = optimized shared-architecture fitness
W_D* = optimized differentiated-accessible fitness
Delta_W = W_D* - W_S*.
```

A direct BALANCE receipt is then

```text
L > 0
and
Delta_W < 0.
```

The architecture boundary is `Delta_W=0`, and the differentiated side is `Delta_W>0`. Under a valid bridge between the direct and decomposed descriptions,

```text
Delta_W = Phi = sL-K.
```

This relation separates the three chapters conceptually. SCH can establish that conflict is active (`L>0`); BALANCE can identify whether the shared worldline still outranks an accessible differentiated alternative; BITA can subsequently decompose the observed worldline difference into recoverability and architecture cost. BITA decomposition is therefore a reconciliation and mechanism test rather than a prerequisite for defining the BALANCE state.

## Position and depth inside the middle world

Inside BALANCE, define

```text
rho = K-sL > 0
xi = L/(L+rho)
d_B = min(L,rho).
```

The coordinate `xi` locates a context between the two theoretical boundaries. As `L -> 0+`, `xi -> 0`; as `rho -> 0+`, `xi -> 1`. The two-sided depth `d_B` gives the smaller of the distances to the SCH-facing and BITA-facing margins. When direct worldlines are observed, the equivalent quantities are obtained from

```text
rho_direct = W_S* - W_D*
xi_direct = L/(L+rho_direct)
d_B,direct = min(L,rho_direct).
```

Under bridge concordance the direct and decomposed coordinates must agree. Neither `xi` nor `d_B` is an evolutionary time variable: both describe location in a contemporaneous fitness geometry.

For fixed `s>0` and `K>0`, the BALANCE interval is `0<L<K/s`, but the point of maximum two-sided depth is generally not the midpoint of that interval. Because

```text
d_B(L)=min[L,K-sL],
```

the maximum occurs where the two margins are equal:

```text
L_deep = K/(1+s)
rho_deep = K/(1+s)
xi_deep = 1/2
d_B,max = K/(1+s).
```

Relative to the full conflict-load width `K/s`, the deepest point occurs at `s/(1+s)`. Weak decoupling therefore pushes the most robust middle-world context toward the low-conflict side, whereas complete recoverability (`s=1`) places it halfway along the conflict-load interval.

## Scale and shape of the persistence region

The baseline geometry separates the scale of the BALANCE region from its normalized shape. Splitting the interval at its deepest ridge gives a SCH-boundary-limited width

```text
W_S = K/(1+s)
```

and a BITA-boundary-limited width

```text
W_B = K/[s(1+s)].
```

Therefore

```text
W_B/W_S = 1/s.
```

Increasing architecture cost `K` stretches both sides proportionally, while changing recoverability `s` changes the normalized skew of the persistence domain. In the dimensionless phase plane `c=L/K` and `q=sL/K`, BALANCE is `c>0` and `q<1`, its architecture boundary is `c=1/s`, and the deepest ridge is `c=1/(1+s)`.

The state classification is invariant to a common positive affine transformation of the fitness scale. If `W'=aW+b` with `a>0` applied identically to the linked SCH, BALANCE, and BITA comparisons, all fitness differences scale by `a` and the additive constant cancels. BALANCE occupancy, `xi`, and `q` are unchanged, whereas dimensional quantities such as `rho` and `d_B` rescale. This invariance does not permit comparison of biologically different fitness outcomes merely because the resulting coordinates are dimensionless.

## Environmental paths and topology

Let the theoretical quantities vary along an ordered environmental or functional context `e`. If

```text
L(e) is nondecreasing,
s(e) is nondecreasing,
K(e) is nonincreasing,
```

then

```text
Phi(e)=s(e)L(e)-K(e)
```

is nondecreasing. Under these sufficient conditions, BALANCE can occupy at most one connected interval before the system enters the differentiation domain. A sequence

```text
BALANCE -> DIFFERENTIATION -> BALANCE
```

therefore requires at least one monotonicity condition, or the assumed common-world mapping, to fail. Re-entry is not forbidden in general; rather, it diagnoses non-monotone conflict, recoverability, cost, or architecture mapping.

This environmental formulation motivates empirical quantities such as the width and connectedness of BALANCE occupancy, the number and location of critical crossings, and integrated reserve across a context path. It also distinguishes a static snapshot from a transition mosaic: observations of shared, intermediate, and differentiated states across ordered contexts can be compatible with the predicted topology even when no study directly measures both optimized worldlines.

## Direct–decomposed concordance

When the direct optimized-worldline comparison and the decomposed `sL-K` route describe the same contexts, the same reproductive-fitness outcome, the same architecture-cost definition, and the same modeled ecological channels, they must satisfy

```text
Delta_W = sL-K.
```

We define the bridge residual

```text
delta_parallel = Delta_W-(sL-K).
```

Under a valid common-world mapping, `delta_parallel=0`. A non-zero residual is informative only after excluding scale mismatch, context mismatch, inconsistent cost definitions, and omitted channels. The same concordance requirement applies to direct and decomposed estimates of `rho`, `xi`, and `d_B`. This creates an empirical falsification route rather than allowing the two descriptions to be averaged when they disagree.

## Switching costs and history dependence

Static worldline crossing need not imply instantaneous architecture switching. Let `C_SD` be the cost of switching from shared to differentiated, `C_DS` the reverse switching cost, and `T>0` the persistence horizon of the current context. Starting from the shared state, differentiation pays only when

```text
Phi > C_SD/T.
```

Starting from the differentiated state, switching back pays only when

```text
Phi < -C_DS/T.
```

The resulting history-dependent band is

```text
-C_DS/T <= Phi <= C_SD/T,
```

with width

```text
(C_SD+C_DS)/T.
```

Thus both architecture states can persist around the static crossing depending on history. This hysteresis band is a dynamic extension surrounding the static BALANCE boundary; it is not itself identical to the static BALANCE core.

## Empirical consequences and falsifiers

The theory separates empirical observations that are often conflated. Opposing selection can establish active conflict without showing that the shared architecture is currently favoured over an alternative. Persistence of an integrated state can supply a middle-regime signature without identifying the worldline difference. A differentiated outcome can locate the BITA-facing side without showing where the crossing occurred. Strict BALANCE occupancy requires the linked conditions on conflict and relative optimized worldlines.

The theory is falsifiable at several levels. Direct and decomposed worldline estimates should agree after bridge audits; direct and decomposed `xi` and `d_B` should coincide under the same mapping; observed re-entry under apparently monotone `L`, `s`, and `K` would reject the sufficient no-reentry conditions; forward and reverse architecture thresholds can test the switching-cost extension; and the position of deep-BALANCE contexts should move with recoverability in the direction predicted by `L_deep=K/(1+s)`. These predictions motivate the final direct-validation experiments, but they do not need to be measured before testing whether the prerequisite and persistence signatures recur across existing biological systems.

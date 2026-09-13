# Middle-world results — BALANCE

## Definitions

Let

```text
L >= 0       shared-coordinate conflict load
R >= 0       recoverable conflict loss for a registered differentiated architecture
K >= 0       additional architecture cost on the same fitness scale
Phi = R-K    differentiated-minus-shared architecture margin
rho = K-R    BALANCE reserve
```

When both optimized worldlines are directly observed on one common fitness scale,

```text
Delta_W = W_D* - W_S*.
```

Under a valid direct/decomposed bridge,

```text
Delta_W = Phi = R-K.
```

For the registered quadratic bridge only,

```text
R = sL,  s in [0,1],
Delta_W = Phi = sL-K.
```

`R=sL` is a model-specific bridge/corollary rather than the general definition of recoverable benefit.

---

## Proposition 1 — sandwich equivalence

The static BALANCE core is exactly

```text
B = {L > 0} intersection {Phi < 0}.
```

Under the quadratic bridge, if `s>0`, this is equivalent to

```text
0 < L < K/s.
```

**Interpretation.** The SCH-facing statement "conflict exists" is true, while the SLK-facing architecture-value statement "differentiation has positive global value" is false. BALANCE is therefore a two-sided ecological regime, not a third unrelated architecture.

---

## Proposition 2 — direct worldline identification and localization

If `L`, `W_S*`, and `W_D*` are measured in matched contexts on one common fitness scale, then BALANCE can be identified without a prior `R,K` decomposition:

```text
L > 0
and
Delta_W < 0.
```

The architecture interface is `Delta_W=0` and the positive architecture-value side is `Delta_W>0`.

Inside a directly identified BALANCE context define

```text
rho_direct = W_S* - W_D* = -Delta_W
xi_direct  = L/(L+rho_direct)
d_B,direct = min(L,rho_direct).
```

Thus BALANCE can estimate **occupancy** and **position/depth inside the middle world** before the decomposed architecture-value bridge is estimated.

**Consequence.** BALANCE is empirically testable and internally measurable without circular dependence on SLK decomposition or BITA mechanism identification.

---

## Proposition 3 — decomposed middle-world position and direct equivalence

Under the registered architecture-value decomposition, inside BALANCE let

```text
rho = K-R > 0
xi = L/(L+rho)
d_B = min(L,rho).
```

Then

```text
0 < xi < 1.
```

Moreover,

```text
L -> 0+       implies xi -> 0
rho -> 0+     implies xi -> 1.
```

If the direct and decomposed worldline descriptions are consistent,

```text
rho_direct = rho
xi_direct  = xi
d_B,direct = d_B.
```

Thus the SLK architecture-value decomposition provides an independent reconciliation test of BALANCE coordinates rather than a prerequisite for defining them. BITA remains orthogonal and does not own this decomposition.

`xi` is not evolutionary time and `d_B` is not a historical transition cost.

---

## Proposition 4 — the deepest point is decoupling-dependent under the quadratic bridge

Fix `s>0` and `K>0` under `R=sL`. The BALANCE interval in conflict-load coordinates is

```text
0 < L < K/s.
```

The two-sided depth is

```text
d_B(L) = min[L, K-sL].
```

It rises with `L` while the SCH-facing margin is limiting, then falls when the SLK-facing architecture reserve becomes limiting. The maximum occurs where

```text
L = K-sL,
```

so

```text
L_deep = K/(1+s)
rho_deep = K/(1+s)
xi_deep = 1/2
d_B,max = K/(1+s).
```

Relative to the full conflict-load width `K/s`,

```text
L_deep / (K/s) = s/(1+s).
```

Thus the deepest BALANCE point is generally **not** halfway along the conflict-load interval. When decoupling is weak (`s` small), the widest safety margin is displaced toward the SCH-facing side; when `s=1`, it lies at half the conflict-load threshold.

For `s=0`, no finite SLK-facing architecture-value boundary exists in this bridge and there is no unique finite middle point of this kind.

---

## Proposition 5 — architecture cost sets scale, decoupling sets normalized shape under the quadratic bridge

For fixed `s>0` and `K>0`, split the conflict-load interval at the deepest ridge. The SCH-boundary-limited width is

```text
W_S = K/(1+s),
```

whereas the architecture-boundary-limited width is

```text
W_A = K/[s(1+s)].
```

Therefore

```text
W_A/W_S = 1/s.
```

Increasing `K` stretches both subregions proportionally but leaves this ratio unchanged. Changing `s` changes the normalized skew of the middle world.

Equivalently, in the dimensionless phase plane

```text
c = L/K
q = sL/K = sc,
```

BALANCE is `c>0` and `q<1`, the architecture boundary is `c=1/s`, and the deepest ridge is

```text
c_deep = 1/(1+s).
```

---

## Proposition 6 — positive affine-scale invariance

Suppose the common reproductive-fitness scale is transformed by

```text
W' = aW + b
```

with `a>0` applied identically to the linked SCH, BALANCE and SLK architecture comparisons.

All fitness **differences** are multiplied by `a`, while the additive constant cancels. Hence

```text
L'       = aL
R'       = aR
K'       = aK
rho'     = a rho
Phi'     = a Phi
Delta_W' = a Delta_W.
```

Therefore:

```text
BALANCE state is unchanged
xi' = xi
q' = q    (when q is defined under the quadratic bridge)
```

while dimensional quantities such as `rho` and `d_B` scale by `a`.

**Consequence.** Dimensionless coordinates are comparable only when the same biological outcome and orientation are used.

---

## Proposition 7 — direct/decomposed concordance

If the direct optimized worldline comparison and the decomposed architecture-value bridge describe the same contexts, same reproductive fitness scale, same architecture cost definition, and same modeled channels, then

```text
Delta_W = R-K.
```

Define

```text
delta_parallel = Delta_W-(R-K).
```

Under those assumptions `delta_parallel=0`.

Under the quadratic bridge this is equivalently

```text
delta_parallel = Delta_W-(sL-K).
```

A non-zero value is a **bridge residual**. It can motivate a parallel-world hypothesis only after scale mismatch, context mismatch, cost mismatch, and omitted ecological channels have been excluded. It is not automatically a BITA mechanism term, an SLK architecture cost, or a named biological process.

The same logic applies to direct and decomposed `rho`, `xi`, and `d_B`.

---

## Proposition 8 — no-reentry sufficient condition under the quadratic bridge

Along an ordered environment `e`, if

```text
L(e) nondecreasing
s(e) nondecreasing
K(e) nonincreasing,
```

then

```text
Phi(e)=s(e)L(e)-K(e)
```

is nondecreasing.

Therefore BALANCE can occupy at most one connected interval before the positive architecture-margin domain. A sequence

```text
BALANCE -> DIFFERENTIATION -> BALANCE
```

requires at least one registered monotonicity condition, or the common-world mapping itself, to fail.

---

## Proposition 9 — switching-cost hysteresis

Let switching shared->differentiated cost `C_SD`, differentiated->shared cost `C_DS`, and context persistence horizon `T>0`.

Starting shared, differentiation is worth switching to only when

```text
Phi > C_SD/T.
```

Starting differentiated, switching back is worth it only when

```text
Phi < -C_DS/T.
```

Hence the history-dependent band is

```text
-C_DS/T <= Phi <= C_SD/T
```

with width

```text
(C_SD+C_DS)/T.
```

**Interpretation.** Around the static architecture crossing, both worldlines can be dynamically persistent depending on history. This persistence halo is distinct from the static BALANCE core and does not itself identify accessibility, invasion, fixation, or occupancy.

---

## Empirical falsifiers

The BALANCE theory becomes especially informative if data recover any of the following:

1. direct `Delta_W` and decomposed `R-K` disagree after bridge audits;
2. under the quadratic bridge, direct `Delta_W` and `sL-K` disagree after bridge audits;
3. direct and decomposed `xi` or `d_B` disagree after bridge audits;
4. natural re-entry occurs despite apparently monotone `L`, `s`, and `K` under the registered bridge;
5. forward and reverse architecture thresholds differ and scale with context duration as predicted;
6. systems with comparable conflict load `L` occupy very different direct `xi` or `d_B`, showing that conflict magnitude alone does not determine architecture state;
7. empirical deep-BALANCE contexts do not shift with estimated decoupling in the direction predicted by `L_deep=K/(1+s)` when the quadratic bridge applies;
8. normalized BALANCE-domain skew fails to track `1/s` after the declared scale/model assumptions are met.

These are BALANCE-specific questions. SCH owns conflict identification; SLK owns architecture value and evolutionary transport; BITA owns ecological mechanism identification for trait interactions.

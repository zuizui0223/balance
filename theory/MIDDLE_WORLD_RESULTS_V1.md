# Middle-world results — Chapter 2 BALANCE

## Definitions

Let

```text
L >= 0       shared-coordinate conflict load
s in [0,1]   recoverable fraction under additional dimensionality
R = sL       recoverable conflict loss
K >= 0       additional architecture cost
Phi = R-K    differentiated-minus-shared architecture margin
rho = K-R    BALANCE reserve
```

When both optimized worldlines are directly observed on one common fitness scale,

```text
Delta_W = W_D* - W_S*.
```

Under the registered bridge decomposition,

```text
Delta_W = Phi = sL-K.
```

---

## Proposition 1 — sandwich equivalence

The static BALANCE core is exactly

```text
B = {L > 0} intersection {Phi < 0}.
```

If `s>0`, this is equivalent to

```text
0 < L < K/s.
```

**Interpretation.** The SCH-facing statement "conflict exists" is true, while the BITA-facing statement "differentiation pays" is false. BALANCE is therefore a two-sided ecological regime, not a third unrelated architecture.

---

## Proposition 2 — direct worldline identification and localization

If `L`, `W_S*`, and `W_D*` are measured in matched contexts on one common fitness scale, then BALANCE can be identified without a prior `s,K` decomposition:

```text
L > 0
and
Delta_W < 0.
```

The architecture interface is `Delta_W=0` and the BITA side is `Delta_W>0`.

Inside a directly identified BALANCE context define

```text
rho_direct = W_S* - W_D* = -Delta_W
xi_direct  = L/(L+rho_direct)
d_B,direct = min(L,rho_direct).
```

Thus Chapter 2 can estimate both **occupancy** and **position/depth inside the middle world** before Chapter 3 estimates `s` or `K`.

**Consequence.** Chapter 2 is empirically testable and internally measurable before Chapter 3 mechanism decomposition, removing a circular chapter-order dependency.

---

## Proposition 3 — decomposed middle-world position and direct equivalence

Under the registered decomposition, inside BALANCE let

```text
rho = K-sL > 0
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

Thus BITA decomposition becomes an independent reconciliation test of Chapter-2 coordinates rather than a prerequisite for defining them.

`xi` is not evolutionary time and `d_B` is not a historical transition cost.

---

## Proposition 4 — the deepest point is decoupling-dependent

Fix `s>0` and `K>0`. The BALANCE interval in conflict-load coordinates is

```text
0 < L < K/s.
```

The two-sided depth is

```text
d_B(L) = min[L, K-sL].
```

It rises with `L` while the SCH-facing margin is limiting, then falls when the BITA-facing reserve becomes limiting. The maximum occurs where the two margins are equal:

```text
L = K-sL
```

so

```text
L_deep = K/(1+s)
rho_deep = K/(1+s)
xi_deep = 1/2
d_B,max = K/(1+s).
```

Relative to the full conflict-load width `K/s`, the deepest point lies at

```text
L_deep / (K/s) = s/(1+s).
```

Thus the deepest BALANCE point is generally **not** halfway along the conflict-load interval. When decoupling is weak (`s` small), the widest safety margin is displaced toward the SCH-facing side; when `s=1`, it lies at half the conflict-load threshold.

For `s=0`, no finite BITA-facing boundary exists and there is no unique finite middle point of this kind.

**Consequence.** The geometry of the BALANCE interior contains information about decoupling even before the differentiated state becomes favoured.

---

## Proposition 5 — architecture cost sets scale, decoupling sets normalized shape

For fixed `s>0` and `K>0`, split the conflict-load interval at the deepest ridge. The SCH-boundary-limited width is

```text
W_S = K/(1+s),
```

whereas the BITA-boundary-limited width is

```text
W_B = K/[s(1+s)].
```

Therefore

```text
W_B/W_S = 1/s.
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

**Consequence.** Chapter 2 separates a domain **scale parameter** (`K`) from a domain **shape parameter** (`s`) in this baseline geometry.

---

## Proposition 6 — positive affine-scale invariance

Suppose the common reproductive-fitness scale is transformed by

```text
W' = aW + b
```

with `a>0` applied identically to the SCH, BALANCE and BITA comparisons.

All fitness **differences** are multiplied by `a`, while the additive constant cancels. Hence

```text
L'   = aL
rho' = a rho
Phi' = a Phi
Delta_W' = a Delta_W.
```

Therefore:

```text
BALANCE state is unchanged
xi' = xi
q' = q
```

while dimensional quantities such as `rho` and `d_B` scale by `a`.

**Consequence.** `xi` and `q` are natural dimensionless comparative coordinates once the same biological outcome and orientation are used. This does not license comparison across different outcome definitions merely because the ratios are dimensionless.

---

## Proposition 7 — direct/decomposed concordance

If the direct optimized worldline comparison and the decomposed bridge describe the same contexts, same reproductive fitness scale, same architecture cost definition, and same modeled channels, then

```text
Delta_W = sL-K.
```

Define

```text
delta_parallel = Delta_W-(sL-K).
```

Under those assumptions `delta_parallel=0`.

A non-zero value is therefore a **bridge residual**. It can motivate a parallel-world hypothesis only after scale mismatch, context mismatch, cost mismatch, and omitted ecological channels have been excluded.

The same logic applies to the inferred middle-world coordinates: under bridge consistency, direct and decomposed `rho`, `xi`, and `d_B` must agree.

---

## Proposition 8 — no-reentry sufficient condition

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

Therefore BALANCE can occupy at most one connected interval before differentiation. A sequence

```text
BALANCE -> DIFFERENTIATION -> BALANCE
```

requires at least one registered monotonicity condition, or the common-world mapping itself, to fail.

---

## Proposition 9 — switching-cost hysteresis

Let switching shared->differentiated cost `C_SD`, differentiated->shared cost `C_DS`, and let the context persist for horizon `T>0`.

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

**Interpretation.** Around the static architecture crossing, both worldlines can be dynamically persistent depending on history. This persistence halo is distinct from the static BALANCE core.

---

## Empirical falsifiers

The Chapter-2 theory becomes especially informative if data recover any of the following:

1. direct `Delta_W` and decomposed `sL-K` disagree after bridge audits;
2. direct and decomposed `xi` or `d_B` disagree after bridge audits;
3. natural re-entry occurs despite apparently monotone `L`, `s`, and `K`;
4. forward and reverse architecture thresholds differ and scale with context duration as predicted;
5. systems with comparable conflict load `L` occupy very different direct `xi` or `d_B`, showing that conflict magnitude alone does not determine architecture state;
6. systems thought to share one architecture critical point instead show reproducibly separated direct and decomposed environmental crossings;
7. empirical deep-BALANCE contexts do not shift with estimated decoupling in the direction predicted by `L_deep=K/(1+s)`;
8. normalized BALANCE-domain skew fails to track `1/s` after the declared scale/model assumptions are met.

These are BALANCE-specific questions rather than restatements of the SCH optimum or BITA mechanism problems.

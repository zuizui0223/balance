# Middle-world results — Chapter 2 BALANCE

## Definitions

Let

```text
L >= 0       shared-coordinate conflict load
R >= 0       recoverable conflict loss for a registered differentiated architecture
K >= 0       additional architecture cost
Phi = R-K    differentiated-minus-shared architecture margin
rho = K-R    BALANCE reserve
```

When both optimized worldlines are directly observed on one common fitness scale,

```text
Delta_W = W_D* - W_S*.
```

Under a valid common-world bridge,

```text
Delta_W = Phi = R-K.
```

Under the registered quadratic bridge only,

```text
R = sL,  s in [0,1],
Delta_W = Phi = sL-K.
```

`R=sL` is a model-specific bridge/corollary rather than a universal definition of recoverable benefit.

---

## Proposition 1 — sandwich equivalence

The static BALANCE core is exactly

```text
B = {L > 0} intersection {Phi < 0}.
```

Under the registered quadratic bridge, if `s>0`, this is equivalent to

```text
0 < L < K/s.
```

**Interpretation.** The SCH-facing statement "conflict exists" is true, while the SLK-facing architecture-value statement "the differentiated architecture has higher optimized value" is false. BALANCE is therefore a two-sided ecological regime, not a third unrelated architecture.

---

## Proposition 2 — direct worldline identification and localization

If `L`, `W_S*`, and `W_D*` are measured in matched contexts on one common fitness scale, then BALANCE can be identified without a prior `R,K` decomposition:

```text
L > 0
and
Delta_W < 0.
```

The architecture interface is `Delta_W=0`; the positive architecture-margin side is `Delta_W>0`.

Inside a directly identified BALANCE context define

```text
rho_direct = W_S* - W_D* = -Delta_W
xi_direct  = L/(L+rho_direct)
d_B,direct = min(L,rho_direct).
```

Thus BALANCE can estimate occupancy and position/depth inside the middle world before any mechanism allocation is attempted.

---

## Proposition 3 — decomposed middle-world position and direct equivalence

Under a valid architecture-value decomposition, inside BALANCE let

```text
rho = K-R > 0
xi = L/(L+rho)
d_B = min(L,rho).
```

Then `0<xi<1`, with `L->0+` implying `xi->0` and `rho->0+` implying `xi->1`.

If the direct and decomposed worldline descriptions are consistent,

```text
rho_direct = rho
xi_direct  = xi
d_B,direct = d_B.
```

The decomposed SLK-facing architecture-value representation is therefore an independent reconciliation test of BALANCE coordinates rather than a prerequisite for defining them. `xi` is not evolutionary time and `d_B` is not a historical transition cost.

---

## Proposition 4 — the deepest point under the quadratic bridge

Under the registered quadratic bridge with fixed `s>0` and `K>0`, the BALANCE interval is

```text
0 < L < K/s.
```

The two-sided depth is

```text
d_B(L) = min[L, K-sL].
```

It rises with `L` while the SCH-facing margin is limiting and falls when the SLK-facing architecture reserve becomes limiting. The maximum occurs where the two margins are equal:

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

Relative to the full conflict-load width `K/s`, the deepest point lies at `s/(1+s)`. For `s=0`, no finite architecture-value boundary exists in this bridge and there is no unique finite middle point of this kind.

---

## Proposition 5 — architecture cost sets scale, recoverability sets normalized shape

Under the same quadratic bridge, split the conflict-load interval at the deepest ridge. The SCH-boundary-limited width is

```text
W_S = K/(1+s),
```

whereas the SLK-boundary-limited width is

```text
W_A = K/[s(1+s)].
```

Therefore

```text
W_A/W_S = 1/s.
```

Increasing `K` stretches both subregions proportionally, while changing `s` changes normalized skew. In the dimensionless phase plane `c=L/K` and `q=sL/K`, BALANCE is `c>0` and `q<1`, the architecture boundary is `c=1/s`, and the deepest ridge is `c=1/(1+s)`.

---

## Proposition 6 — positive affine-scale invariance

Suppose the common reproductive-fitness scale is transformed by

```text
W' = aW + b
```

with `a>0` applied identically to the linked SCH, BALANCE and SLK architecture comparisons. All fitness differences are multiplied by `a` and the additive constant cancels. Hence

```text
L'       = aL
rho'     = a rho
Phi'     = a Phi
Delta_W' = a Delta_W.
```

BALANCE state is unchanged, `xi'=xi`, and dimensionless architecture ratios are unchanged, while dimensional quantities such as `rho` and `d_B` scale by `a`. This does not license comparison across different biological outcome definitions.

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

Under those assumptions `delta_parallel=0`. Under the registered quadratic bridge this reduces to `Delta_W=sL-K` and `delta_parallel=Delta_W-(sL-K)`.

A non-zero value is a **bridge residual**. It is not automatically a BITA mechanism term, an SLK architecture cost, or a named biological channel. Scale mismatch, context mismatch, cost mismatch, and omitted channels must first be audited. Under bridge consistency, direct and decomposed `rho`, `xi`, and `d_B` must agree.

---

## Proposition 8 — no-reentry sufficient condition under the quadratic bridge

Along an ordered environment `e`, under the registered quadratic bridge, if

```text
L(e) nondecreasing
s(e) nondecreasing
K(e) nonincreasing,
```

then

```text
Phi(e)=s(e)L(e)-K(e)
```

is nondecreasing. Therefore BALANCE can occupy at most one connected interval before the positive architecture-margin domain. A sequence

```text
BALANCE -> POSITIVE_ARCHITECTURE_MARGIN -> BALANCE
```

requires at least one registered monotonicity condition, or the common-world mapping itself, to fail.

---

## Proposition 9 — switching-cost hysteresis

Let switching shared->differentiated cost `C_SD`, differentiated->shared cost `C_DS`, and let the context persist for horizon `T>0`.

Starting shared, switching is worth it only when

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

with width `(C_SD+C_DS)/T`.

**Interpretation.** Around the static architecture crossing, both worldlines can be dynamically persistent depending on history. This persistence halo is distinct from the static BALANCE core and does not by itself identify accessibility, invasion, fixation, or occupancy.

---

## Empirical falsifiers

The BALANCE theory becomes especially informative if data recover any of the following:

1. direct `Delta_W` and decomposed `R-K` disagree after bridge audits;
2. direct and decomposed `xi` or `d_B` disagree after bridge audits;
3. under the quadratic bridge, natural re-entry occurs despite apparently monotone `L`, `s`, and `K`;
4. forward and reverse architecture thresholds differ and scale with context duration as predicted;
5. systems with comparable conflict load `L` occupy very different direct `xi` or `d_B`;
6. systems thought to share one architecture critical point instead show reproducibly separated direct and decomposed environmental crossings;
7. under the quadratic bridge, empirical deep-BALANCE contexts do not shift with estimated recoverability in the direction predicted by `L_deep=K/(1+s)`;
8. under the quadratic bridge, normalized BALANCE-domain skew fails to track `1/s` after the declared assumptions are met.

These are BALANCE-specific questions. They neither restate the SCH conflict problem nor identify BITA ecological mechanisms, and they do not collapse the SLK value-to-realization hierarchy.

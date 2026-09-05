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

When both optimized architectures are directly observed on one common fitness scale,

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

## Proposition 2 — direct worldline identification

If `L`, `W_S*`, and `W_D*` are measured in matched contexts on one common fitness scale, then BALANCE can be identified without a prior `s,K` decomposition:

```text
L > 0
and
Delta_W < 0.
```

The architecture interface is `Delta_W=0` and the BITA side is `Delta_W>0`.

**Consequence.** Chapter 2 is empirically testable before Chapter 3 mechanism decomposition, removing a circular chapter-order dependency.

---

## Proposition 3 — middle-world position and depth

Inside BALANCE let

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

Thus `xi` is an orientation from the SCH-facing boundary toward the BITA-facing boundary, while `d_B` measures the minimum one-margin perturbation needed to reach either boundary on the common fitness scale.

`xi` is not evolutionary time and `d_B` is not a historical transition cost.

---

## Proposition 4 — direct/decomposed concordance

If the direct optimized architecture comparison and the decomposed bridge describe the same contexts, same reproductive fitness scale, same architecture cost definition, and same modeled channels, then

```text
Delta_W = sL-K.
```

Define

```text
delta_parallel = Delta_W-(sL-K).
```

Under those assumptions `delta_parallel=0`.

A non-zero value is therefore a **bridge residual**. It can motivate a parallel-world hypothesis only after scale mismatch, context mismatch, cost mismatch, and omitted ecological channels have been excluded.

---

## Proposition 5 — no-reentry sufficient condition

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

## Proposition 6 — switching-cost hysteresis

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
2. natural re-entry occurs despite apparently monotone `L`, `s`, and `K`;
3. forward and reverse architecture thresholds differ and scale with context duration as predicted;
4. systems with comparable conflict load `L` occupy very different `xi` or `d_B`, showing that conflict magnitude alone does not determine architecture state.

These are BALANCE-specific questions rather than restatements of the SCH optimum or BITA mechanism problems.

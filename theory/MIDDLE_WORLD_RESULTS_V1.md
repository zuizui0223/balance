# Middle-world coordinates and testable restrictions — BALANCE

## Purpose

BALANCE uses a two-margin coordinate system to describe persistent compromise. This file
separates three things that must not be conflated:

1. **definitions**;
2. **algebraic consequences of those definitions or of a registered bridge**;
3. **empirical restrictions that can fail when confronted with data**.

Items in sections A and B are useful coordinate identities, but they are not presented as
novel theorems merely because they can be written in closed form.

---

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

`R=sL` is model-specific. It is not the general definition of recoverable benefit.

---

## A. Coordinate identities

### A1 — static sandwich

The BALANCE core is defined by

```text
L > 0
Phi < 0.
```

Under `R=sL`, if `s>0`, this is algebraically equivalent to

```text
0 < L < K/s.
```

This interval is a coordinate consequence of two inequalities. It is not treated as a
standalone discovery.

### A2 — direct worldline coordinate

Matched direct worldlines identify the same descriptive state without prior `R,K`
decomposition:

```text
L > 0
Delta_W < 0.
```

Inside that state define

```text
rho_direct = W_S* - W_D* = -Delta_W
xi_direct  = L/(L+rho_direct)
d_B,direct = min(L,rho_direct).
```

These quantities localize an observed context between the SCH-facing conflict boundary
and the SLK-facing architecture-value boundary.

### A3 — decomposed coordinate

When the decomposition is available,

```text
rho = K-R
xi  = L/(L+rho)
d_B = min(L,rho).
```

Inside BALANCE, `0<xi<1`. Under a valid direct/decomposed bridge,

```text
rho_direct = rho
xi_direct  = xi
d_B,direct = d_B.
```

`xi` is not evolutionary time, and `d_B` is not a historical transition cost.

---

## B. Algebraic consequences of the quadratic bridge

The following statements are useful for calibration and visualization but remain algebraic
consequences of `R=sL`.

### B1 — equal-margin point

For fixed `s>0` and `K>0`,

```text
d_B(L) = min[L, K-sL].
```

The two margins are equal at

```text
L_equal   = K/(1+s)
rho_equal = K/(1+s)
xi_equal  = 1/2.
```

Relative to the full conflict-load interval `K/s`,

```text
L_equal/(K/s) = s/(1+s).
```

This is a property of the chosen two-margin depth coordinate, not an independent biological
prediction.

### B2 — normalized width decomposition

Splitting the conflict-load interval at the equal-margin point gives

```text
W_S = K/(1+s)
W_A = K/[s(1+s)]
W_A/W_S = 1/s.
```

Again, this follows directly from the bridge and coordinate definition.

### B3 — positive affine-scale invariance

Under a common transformation `W'=aW+b` with `a>0`,

```text
L'       = aL
R'       = aR
K'       = aK
rho'     = a rho
Phi'     = a Phi
Delta_W' = a Delta_W.
```

State, `xi`, and dimensionless ratios are unchanged; dimensional margins rescale.

---

## C. Empirically testable restrictions and diagnostics

These claims require additional measured structure beyond the coordinate identities.

### C1 — direct/decomposed bridge concordance

If direct and decomposed descriptions refer to the same context, outcome scale, architecture
definition, and modeled channels, then

```text
Delta_W = R-K.
```

Define

```text
delta_parallel = Delta_W-(R-K).
```

Under the quadratic bridge,

```text
delta_parallel = Delta_W-(sL-K).
```

A persistent non-zero residual after scale, context, cost, and omitted-channel audits is a
failure of the registered bridge. It is not automatically a named mechanism.

### C2 — no-reentry under registered monotonicity

Along an ordered environment `e`, if

```text
L(e) nondecreasing
s(e) nondecreasing
K(e) nonincreasing,
```

then `Phi(e)=s(e)L(e)-K(e)` is nondecreasing. Therefore the static architecture-value
crossing cannot show genuine

```text
BALANCE -> ARCHITECTURE_FAVOURED -> BALANCE
```

re-entry while all registered assumptions hold.

Observed re-entry is informative because it falsifies at least one assumption or the common
worldline mapping; the monotonicity proof itself is elementary.

### C3 — switching-cost duration restriction

With shared-to-differentiated switching cost `C_SD`, reverse cost `C_DS`, and context
persistence horizon `T>0`,

```text
-C_DS/T <= Phi <= C_SD/T
```

is the history-dependent band, with width

```text
(C_SD+C_DS)/T.
```

The empirical content is the predicted dependence on transition costs and duration, not the
algebraic rearrangement.

### C4 — repeated-context geometry

When worldlines are prospectively restricted to affine or otherwise registered shape
classes, BALANCE obtains additional falsifiable signatures: connected reserve sets,
bounded threat switching, endpoint certificates, and held-out interior checks. See
`docs/THEORY_TO_CAUSAL_PREDICTIONS_V2.md`.

---

## D. Comparative predictions are outside the algebra

The macro programme asks a question the two inequalities cannot answer:

> Among systems with independently established functional conflict, what predicts persistence
> of a shared architecture versus temporal, spatial, signal, or structural separation?

Primary candidate predictors are coded independently of the architecture outcome. Current
plant-first variables include pre-existing module substrate and the timing/space geometry
of competing demands. Broad latent constructs such as "alternative accessibility" are not
admitted merely because a differentiated outcome exists.

No value of `L`, `rho`, `xi`, or `d_B` alone determines these comparative outcomes by
definition.

---

## Empirical falsifiers / model-audit triggers

Priority falsifiers are:

1. direct `Delta_W` and decomposed `R-K` disagree after bridge audits;
2. a registered monotone path shows robust architecture-value re-entry;
3. forward/reverse thresholds do not show the registered duration dependence under the
   switching-cost model;
4. held-out contexts reject a prospectively registered affine/convex worldline restriction;
5. comparative architecture outcomes remain unexplained by the prospectively coded
   structural/temporal/spatial predictors, or reverse direction relative to the registered
   hypotheses.

Equal-margin location and `1/s` width skew are retained as calibration checks of the
quadratic coordinate system, not headline novelty claims.

SCH owns conflict identification. SLK owns architecture value and evolutionary transport.
BITA owns mechanism identification for trait interactions. BALANCE owns the measurement and
empirical study of persistent compromise between the SCH- and SLK-facing boundaries.

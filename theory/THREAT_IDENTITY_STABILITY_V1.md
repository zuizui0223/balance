# BALANCE threat-identity stability theorem v1

## Purpose

Quantify how stable the identity of the **best accessible alternative architecture** is to environmental perturbation.

BALANCE state can remain unchanged while the alternative attaining the upper competing worldline changes. The present theorem separates:

- robustness of the **state** (`shared still beats every alternative`), from
- robustness of the **active threat identity** (`which alternative is closest to beating shared`).

## Setup

At environmental context `e_0`, let registered alternative optimized fitnesses be

\[
W_{D_j}^*(e),\qquad j=1,\ldots,m.
\]

Assume a unique active threat `j*` at `e_0`:

\[
W_{D_{j^*}}^*(e_0)>
W_{D_k}^*(e_0)
\qquad\forall k\ne j^*.
\]

Define pairwise threat gaps

\[
\gamma_k
=
W_{D_{j^*}}^*(e_0)-W_{D_k}^*(e_0)
>0.
\]

Let environmental perturbations be measured by a registered norm `||.||_Q`.

## Theorem 1 — Lipschitz threat-stability radius

Suppose every pairwise fitness difference

\[
d_k(e)=W_{D_{j^*}}^*(e)-W_{D_k}^*(e)
\]

is Lipschitz on the declared neighborhood with constant `L_k`:

\[
|d_k(e)-d_k(e_0)|
\le
L_k\|e-e_0\|_Q.
\]

Then the active threat remains `j*` for every perturbation satisfying

\[
\boxed{
\|e-e_0\|_Q
<
r_{\rm threat}
}
\]

where

\[
\boxed{
r_{\rm threat}
=
\min_{k\ne j^*}
\frac{\gamma_k}{L_k}.}
\]

Proof: for every competitor `k`,

\[
d_k(e)
\ge
\gamma_k-L_k\|e-e_0\|_Q>0.
\]

Therefore no alternative can overtake `j*` inside that ball.

## Corollary 1a — conservative bound from individual worldline Lipschitz constants

If only individual constants are available,

\[
|W_{D_j}^*(e)-W_{D_j}^*(e_0)|
\le
M_j\|e-e_0\|_Q,
\]

then

\[
L_k\le M_{j^*}+M_k
\]

and a conservative radius is

\[
\boxed{
\widetilde r_{\rm threat}
=
\min_{k\ne j^*}
\frac{\gamma_k}{M_{j^*}+M_k}.}
\]

## Theorem 2 — exact affine metric distance to a threat switch

Suppose alternative worldlines are affine in environment:

\[
W_{D_j}^*(e)=a_j^\top e+b_j,
\]

and environmental distance is induced by positive-definite metric matrix `Q`:

\[
\|\Delta e\|_Q
=\sqrt{\Delta e^\top Q\Delta e}.
\]

The tie surface between `j*` and `k` is

\[
(a_{j^*}-a_k)^\top e+(b_{j^*}-b_k)=0.
\]

Its exact metric distance from `e_0` is

\[
\boxed{
r_{j^*k,Q}
=
\frac{\gamma_k}
{\sqrt{(a_{j^*}-a_k)^\top Q^{-1}(a_{j^*}-a_k)}}.}
\]

Therefore the exact nearest affine threat-switch distance is

\[
\boxed{
r_{\rm threat,Q}
=
\min_{k\ne j^*}r_{j^*k,Q}.}
\]

The shortest perturbation toward the switch with competitor `k` is proportional to

\[
-Q^{-1}(a_{j^*}-a_k).
\]

## Definition — threat fragility index

Let

\[
d_{B,Q}(e_0)
\]

be the registered metric distance from the current BALANCE context to the nearest **state exit** (`L=0` or any architecture reserve `rho_j=0`).

Define

\[
\boxed{
\Psi_T
=
\frac{r_{\rm threat,Q}}
{d_{B,Q}}
}
\]

when both quantities are finite and positive.

Interpretation:

- `Psi_T < 1`: some alternative-identity switch is metrically closer than any BALANCE-state exit;
- `Psi_T > 1`: the current threat identity is locally more robust than the BALANCE state itself;
- `Psi_T = 1`: a threat switch and a state boundary are equally close in the registered metric.

This is a local geometric comparison, not evolutionary time.

## Theorem 3 — threat switch does not imply state switch

At a tie where

\[
W_{D_i}^*=W_{D_j}^*,
\]

if both are still below shared fitness,

\[
W_{D_i}^*=W_{D_j}^*<W_S^*,
\]

then

\[
\rho_A>0
\]

and BALANCE persists through the threat-identity switch.

Therefore an envelope kink is evidence that the **nearest competitor changed**, not that the shared architecture ceased to win.

## Empirical consequence

A repeated-context BALANCE design can report two distinct robustness quantities:

```text
state robustness          d_B,Q
active-threat robustness  r_threat,Q
```

A small `r_threat,Q` warns that mechanism interpretation based on one alternative architecture is fragile even if the BALANCE state call itself is robust.

This suggests a prospective sampling rule: place additional environmental observations near the nearest predicted threat-tie surface when the goal is to identify which differentiated architecture constrains the middle world.

## Claim ceiling

The Lipschitz result requires valid local continuity bounds. The affine formula is exact only under the registered affine worldline model and metric. A newly discovered alternative outside the accessibility registry can invalidate the identity calculation. Threat identity concerns static optimized worldlines; PAYOFF invasion, frequency dependence and coexistence remain separate.

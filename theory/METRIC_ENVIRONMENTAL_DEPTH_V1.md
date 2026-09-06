# BALANCE metric-corrected environmental depth theorem v1

## Purpose

Make environmental robustness independent of arbitrary measurement units and allow unequal ecological costs for changing different environmental coordinates.

The existing local environmental depth uses a gradient magnitude. A Euclidean gradient is only meaningful after a coordinate metric has been declared. Temperature in degrees, precipitation in millimetres and predator density in counts cannot be compared by raw numerical distance without such a metric.

## Setup

Let the environmental coordinate be

\[
e\in\mathbb R^d
\]

and let one positive BALANCE margin be

\[
f(e)>0,
\]

with local gradient

\[
g=\nabla f(e).
\]

The relevant boundary is `f=0`.

Let environmental perturbation cost be measured by a positive-definite quadratic metric

\[
\|\delta e\|_Q^2
=
\delta e^\top Q\,\delta e,
\qquad Q\succ0.
\]

The local linearized boundary constraint is

\[
f+g^\top\delta e=0.
\]

## Theorem 1 — metric-corrected shortest distance to a boundary

Minimizing the perturbation cost subject to the linearized boundary constraint gives

\[
\boxed{
\delta e^*
=
-\frac{f\,Q^{-1}g}{g^\top Q^{-1}g}
}
\]

and

\[
\boxed{
d_Q(f)
=
\frac{f}{\sqrt{g^\top Q^{-1}g}}.
}
\]

Thus the environmental distance is the fitness margin divided by the gradient magnitude measured in the **dual metric** `Q^{-1}`.

For `Q=I`, this reduces to the previously registered Euclidean formula

\[
d_E=f/\|\nabla f\|_2.
\]

## Theorem 2 — BALANCE metric depth

Inside BALANCE there are two positive margins:

\[
L(e)>0,
\qquad
\rho(e)=W_S^*(e)-W_D^*(e)>0.
\]

Define

\[
d_{S,Q}
=
\frac{L}{\sqrt{\nabla L^\top Q^{-1}\nabla L}},
\]

\[
d_{D,Q}
=
\frac{\rho}{\sqrt{\nabla\rho^\top Q^{-1}\nabla\rho}}.
\]

Then the local metric-corrected environmental robustness of the middle world is

\[
\boxed{
d_{B,Q}=\min(d_{S,Q},d_{D,Q}).}
\]

The corresponding shortest exit perturbation is the optimizer for whichever boundary gives the smaller distance.

## Theorem 3 — coordinate-change invariance

Let environmental coordinates be reparameterized linearly by

\[
y=Ae,
\]

with invertible `A`. The perturbation metric and gradient transform as

\[
Q_y=A^{-\top}Q_eA^{-1},
\qquad
\nabla_y f=A^{-\top}\nabla_e f.
\]

Then

\[
\nabla_y f^\top Q_y^{-1}\nabla_y f
=
\nabla_e f^\top Q_e^{-1}\nabla_e f,
\]

so

\[
\boxed{d_{Q_y}(f)=d_{Q_e}(f).}
\]

Therefore changing environmental units or applying an invertible linear rescaling does not change the declared environmental depth when the metric is transformed consistently.

## Corollary — standardized independent coordinates

If environmental dimensions are assigned independent perturbation scales `s_i>0`, choose

\[
Q=\operatorname{diag}(1/s_i^2).
\]

Then

\[
Q^{-1}=\operatorname{diag}(s_i^2)
\]

and

\[
\boxed{
d_Q(f)=
\frac{f}
{\sqrt{\sum_i s_i^2(\partial_i f)^2}}.
}
\]

This is equivalent to measuring environmental perturbations in standardized units `delta e_i / s_i`.

## Biological interpretation

The theorem distinguishes three objects that should not be conflated:

1. **fitness depth** — `min(L,rho)` in reproductive-fitness units;
2. **raw coordinate distance** — dependent on chosen environmental units;
3. **metric environmental depth** — the minimum declared ecological perturbation required to reach either boundary.

A BALANCE state can be deep in fitness units but environmentally fragile if its margins change steeply along a low-cost environmental direction.

Conversely, modest fitness margins can be environmentally robust if all directions capable of eroding them are costly or weakly coupled to the margins.

## Empirical consequence

Cross-system comparison of BALANCE environmental robustness should register a metric before calculating depth. Possible choices include:

- standardized physical units fixed prospectively;
- covariance-scaled environmental perturbations;
- experimentally calibrated intervention costs;
- a mechanistic distance metric supplied by the biological system.

The metric must not be chosen after observing which system looks most robust.

## Claim ceiling

This is a local linear-boundary theorem. Curved boundaries require geodesic or nonlinear optimization for large perturbations. A chosen metric encodes biological assumptions about perturbation cost; the theorem makes those assumptions explicit but does not identify the correct metric from data automatically. PAYOFF frequency dependence is not involved.

# BALANCE strong-concave margin chord theorem v1

## Purpose

Strengthen the concave-domain convexity result from a sign certificate into a quantitative interior-depth prediction. If BALANCE status margins have known lower/upper curvature along an environmental chord, endpoint measurements bound how far the interior margins must bulge above the straight endpoint interpolation.

## Setup

Let `f(e)` denote any BALANCE status margin: the SCH-facing conflict margin `L(e)` or an architecture reserve `rho_j(e)`. Choose endpoints `e_0,e_1` in a convex environmental domain and define

\[
e_t=(1-t)e_0+t e_1,
\qquad v=e_1-e_0.
\]

Let

\[
g(t)=f(e_t).
\]

Assume along the segment

\[
\alpha Q\preceq-\nabla^2f(e_t)\preceq\beta Q,
\qquad 0\le\alpha\le\beta,
\]

for a preregistered positive-semidefinite environmental metric/curvature reference `Q`.

Then

\[
\alpha v^TQv
\le-g''(t)\le
\beta v^TQv.
\]

## Theorem 1 — quantitative concavity bulge

Define the endpoint chord

\[
\ell_f(t)=(1-t)f(e_0)+t f(e_1)
\]

and interior bulge

\[
J_f(t)=f(e_t)-\ell_f(t).
\]

Then

\[
\boxed{
\frac{\alpha}{2}t(1-t)v^TQv
\le J_f(t)\le
\frac{\beta}{2}t(1-t)v^TQv.
}
\]

At the midpoint,

\[
\boxed{
\frac{\alpha}{8}v^TQv
\le
f\!\left(\frac{e_0+e_1}{2}\right)
-\frac{f(e_0)+f(e_1)}{2}
\le
\frac{\beta}{8}v^TQv.
}
\]

Thus strong concavity predicts not merely that the interior stays above zero, but how much additional reserve should appear above endpoint interpolation.

## Corollary 1a — strict interior BALANCE buffer

If both endpoint margins are positive, then

\[
f(e_t)
\ge
(1-t)f(e_0)+tf(e_1)
+\frac{\alpha}{2}t(1-t)v^TQv.
\]

When `alpha>0`, the interior has a guaranteed extra buffer above the simple Jensen chord.

If the same lower curvature constant applies to every registered architecture reserve, the best-alternative reserve `rho_A=min_j rho_j` inherits that strong-concavity lower bound because adding the common quadratic term preserves pointwise-minimum concavity.

## Corollary 1b — whole-domain direct-depth floor along a chord

Let the status margins be `f_k in {L,rho_1,...,rho_m}` with lower curvature constants `alpha_k`. At any interior `t`, a conservative direct fitness-depth floor is

\[
\boxed{
 d_F(e_t)
\ge
\min_k\left[(1-t)f_k(e_0)+tf_k(e_1)
+\frac{\alpha_k}{2}t(1-t)v^TQv\right].
}
\]

This is stronger than the endpoint-only floor when any registered `alpha_k` is positive.

## Theorem 2 — three-context curvature audit

Given endpoints and one held-out interior context, define

\[
\widehat J_f(t)
=\widehat f(e_t)-[(1-t)\widehat f(e_0)+t\widehat f(e_1)].
\]

The registered curvature interval requires

\[
\frac{\alpha}{2}t(1-t)v^TQv
\le\widehat J_f(t)\le
\frac{\beta}{2}t(1-t)v^TQv
\]

after uncertainty propagation.

A negative bulge rejects concavity. A bulge below the lower bound rejects the claimed strong-concavity floor. A bulge above the upper bound rejects the smoothness/upper-curvature ceiling.

## Empirical consequence

Repeated same-context worldline experiments can place two environmental endpoints plus a midpoint or other interior context. This supports a prospective three-level geometry test before fitting a flexible response surface.

The design is especially useful when the goal is to claim continuous-domain BALANCE persistence: the interior point is not merely another sample but a direct curvature audit of the interpolation theorem.

## Claim ceiling

The theorem requires the curvature bounds to hold on the full environmental segment and the same accessibility scope, fitness scale and optimized worldline definitions at all points. Environmental history/frequency dependence or changing feasible architecture sets invalidate the static chord certificate. PAYOFF remains separate.

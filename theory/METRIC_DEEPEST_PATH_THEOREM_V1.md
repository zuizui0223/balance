# BALANCE metric-deepest path theorem v1

## Purpose

Distinguish the **fitness-deepest** BALANCE state from the **environmentally deepest** BALANCE state after a biologically declared perturbation metric has been imposed.

The previous metric-depth theorem gives the local shortest perturbation from one context to either boundary. Here we characterize the unique center along an ordered environmental path when the two metric distances vary monotonically in opposite directions.

## Setup

Let `t` index a connected path through a BALANCE domain. At each context define the metric-corrected local distances to the SCH-facing and BITA-facing boundaries:

\[
d_S(t)
=
\frac{L(t)}{\sqrt{\nabla L(t)^\top Q^{-1}\nabla L(t)}},
\]

\[
d_D(t)
=
\frac{\rho(t)}{\sqrt{\nabla\rho(t)^\top Q^{-1}\nabla\rho(t)}}.
\]

Define the metric environmental depth

\[
d_Q(t)=\min\{d_S(t),d_D(t)\}
\]

and normalized metric coordinate

\[
\xi_Q(t)=\frac{d_S(t)}{d_S(t)+d_D(t)}.
\]

Assume on the path:

1. `d_S(t)` is continuous and strictly increasing;
2. `d_D(t)` is continuous and strictly decreasing;
3. they straddle one another between the path endpoints.

## Theorem 1 — unique metric center

There is a unique context `t_Q` such that

\[
\boxed{d_S(t_Q)=d_D(t_Q).}
\]

Before `t_Q`, the nearest boundary is the SCH-facing boundary and `d_Q=d_S`, which increases. After `t_Q`, the nearest boundary is the BITA-facing boundary and `d_Q=d_D`, which decreases.

Therefore

\[
\boxed{
\operatorname*{arg\,max}_t d_Q(t)=t_Q.
}
\]

So the environmentally deepest context is the equal-**metric-distance** point.

## Corollary 1a — normalized metric coordinate

At the unique metric center,

\[
\boxed{\xi_Q(t_Q)=\frac12.}
\]

Under the monotonic assumptions, `xi_Q` increases through one half exactly once.

This is directly analogous to the fitness coordinate `xi_F`, but the two coordinates use different notions of distance.

## Theorem 2 — fitness center and environmental center need not coincide

The fitness-deepest state satisfies

\[
L=\rho,
\]

while the metric-environmental center satisfies

\[
\frac{L}{\|\nabla L\|_{Q^{-1}}}
=
\frac{\rho}{\|\nabla\rho\|_{Q^{-1}}}.
\]

They coincide only under additional conditions, for example equal dual-metric gradient magnitudes at the crossing.

Thus

\[
\boxed{
\text{fitness centrality}\neq\text{environmental robustness centrality}
}
\]

in general.

## Constant-slope one-dimensional special case

Let the environmental path be the physical coordinate `e` with boundaries `e_0<e_2`, and let

\[
L(e)=\ell(e-e_0),
\qquad
\rho(e)=r(e_2-e),
\qquad \ell,r>0.
\]

Under the Euclidean environmental metric,

\[
d_S=e-e_0,
\qquad
d_D=e_2-e.
\]

Hence the environmentally deepest state is simply

\[
\boxed{
e_Q=\frac{e_0+e_2}{2}.}
\]

By contrast, the fitness-deepest state solves `L=rho`:

\[
\boxed{
e_F=\frac{\ell e_0+r e_2}{\ell+r}.}
\]

Therefore

\[
e_F-e_Q
=
\frac{(r-\ell)(e_2-e_0)}{2(\ell+r)}.
\]

The two centers coincide only when `ell=r`.

This gives a directly interpretable asymmetry measure: the displacement between fitness center and environmental center reveals unequal rates at which the two margins change across the domain.

## Empirical consequence

With repeated direct worldline receipts across an ordered environmental axis, Chapter 2 can estimate both:

- `e_F`: where the two **fitness margins** are equal;
- `e_Q`: where the two declared **environmental perturbation distances** are equal.

Their separation is itself an estimand rather than a nuisance. A large separation means the state that is most buffered in fitness terms is not the state requiring the largest environmental displacement to leave BALANCE.

## Claim ceiling

The theorem concerns metric-corrected local boundary distances along a path. If boundary curvature is large relative to the perturbations, local linear distances can deviate from exact geodesic distances. Monotonicity of the two metric distances is an explicit assumption and should be tested rather than inferred from the BALANCE definition alone.

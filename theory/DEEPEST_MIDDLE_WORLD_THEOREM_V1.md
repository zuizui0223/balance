# BALANCE deepest-middle-world theorem v1

## Purpose

Characterize the most interior point of a finite BALANCE domain without assuming the quadratic `sL-K` decomposition.

Work directly with two same-scale positive margins along an ordered environmental axis `e`:

\[
L(e)>0
\]

for distance from the SCH conflict-onset boundary, and

\[
\rho(e)=W_S^*(e)-W_D^*(e)>0
\]

for distance from the architecture crossing on the BITA-facing side.

Inside BALANCE,

\[
d_B(e)=\min\{L(e),\rho(e)\}
\]

is the two-sided depth and

\[
\xi(e)=\frac{L(e)}{L(e)+\rho(e)}
\]

is the normalized interior coordinate.

## Assumptions

On a connected BALANCE path `e in [a,b]`, assume:

1. `L(e)` is continuous and strictly increasing;
2. `rho(e)` is continuous and strictly decreasing;
3. the margins straddle one another across the interval:

\[
L(a)<\rho(a),
\qquad
L(b)>\rho(b).
\]

The endpoints need not be exact mathematical boundaries. Only the straddling condition is required.

## Theorem 1 — unique equal-margin point

Define

\[
g(e)=L(e)-\rho(e).
\]

Because `L` increases and `rho` decreases, `g` is strictly increasing. The endpoint assumptions imply

\[
g(a)<0<g(b).
\]

By continuity there is exactly one point `e_dagger` such that

\[
\boxed{L(e_\dagger)=\rho(e_\dagger)}.
\]

## Theorem 2 — this point uniquely maximizes BALANCE depth

For `e<e_dagger`,

\[
L(e)<\rho(e)
\]

so

\[
d_B(e)=L(e),
\]

which strictly increases toward `e_dagger`.

For `e>e_dagger`,

\[
L(e)>\rho(e)
\]

so

\[
d_B(e)=\rho(e),
\]

which strictly decreases away from `e_dagger`.

Therefore

\[
\boxed{
\operatorname*{arg\,max}_e d_B(e)=e_\dagger
}
\]

and the maximizer is unique.

This gives a general definition of the **deepest BALANCE state**: the point equally far, on the common fitness-margin scale, from the SCH-facing and BITA-facing boundaries.

## Corollary 2a — the deepest point has xi = 1/2

At the equal-margin point,

\[
\xi(e_\dagger)
=
\frac{L}{L+\rho}
=
\boxed{\frac12}.
\]

Thus `xi=1/2` is not an arbitrary visual midpoint. Under the declared monotone-margin assumptions it identifies the unique maximum of the two-sided depth.

## Theorem 3 — xi is monotone across the middle world

Where the margins are differentiable,

\[
\xi'(e)
=
\frac{L'(e)\rho(e)-L(e)\rho'(e)}{[L(e)+\rho(e)]^2}.
\]

With

\[
L'(e)\ge0,
\qquad
\rho'(e)\le0,
\]

and at least one strict inequality, the numerator is positive. Hence

\[
\boxed{\xi'(e)>0}.
\]

So the normalized coordinate moves monotonically from the SCH-facing side toward the BITA-facing side along such an environmental path.

## Corollary 3a — positive fitness-scale invariance

Under a common positive rescaling of the fitness margin,

\[
L'(e)=aL(e),
\qquad
\rho'(e)=a\rho(e),
\qquad a>0,
\]

we have

\[
\xi'_{\rm coord}(e)=\xi(e),
\]

and the equal-margin location `e_dagger` is unchanged, while

\[
d_B'(e)=a d_B(e).
\]

Thus the location and normalized position of the deepest state are invariant to common choice of positive fitness units; its absolute depth retains fitness units.

## Quadratic special case

Under the registered quadratic decomposition with fixed `s` and `K`,

\[
\rho=K-sL.
\]

The deepest-point condition `L=rho` gives

\[
L=K-sL
\]

and therefore

\[
\boxed{L_{\rm deep}=\frac{K}{1+s}}.
\]

So the previously derived quadratic deepest ridge is a special case of the direct worldline theorem.

## Boundary cases

If `L-rho` never crosses zero on the observed interval, no interior equal-margin point is identified there. The observed maximum of `d_B` may then lie at the edge of the sampled range. Do not extrapolate an unobserved deepest state without an explicit path model.

If either margin is nonmonotone, multiple local depth maxima are possible. That is a topology/re-entry problem rather than a failure of the BALANCE definition.

## Empirical consequence

Across ordered environments, Chapter 2 can estimate `L(e)` and direct `rho(e)=W_S^*-W_D^*`. A finite connected BALANCE domain with monotone opposing margins predicts:

- a unique equal-margin context;
- `xi` increasing through `1/2` at that context;
- two-sided depth increasing before and decreasing after it.

This is a BALANCE-domain prediction. PAYOFF frequency dependence is not required.

# BALANCE environmental-distance depth theorem v1

## Purpose

Separate two different meanings of being "deep" inside BALANCE:

1. **fitness-margin depth** — how much fitness margin separates the system from each boundary;
2. **environmental-distance depth** — how far the environment must move, locally, to reach each boundary.

These are not generally the same.

Let environmental context be `e in R^m` and define the BALANCE margins `L(e)>0` and

\[
\rho(e)=W_S^*(e)-W_D^*(e)>0.
\]

The SCH-facing boundary is `L=0`; the SLK-facing architecture-value boundary is `rho=0`.

## Fitness-margin depth

\[
d_F(e)=\min\{L(e),\rho(e)\},
\qquad
\xi_F(e)=\frac{L}{L+\rho}.
\]

This requires the two margins to be expressed on a common fitness scale.

## Local environmental distance to a regular boundary

For a smooth scalar field `f(e)` with regular boundary `f=0`, linearization gives `f(e+delta e) approximately f(e)+grad f(e)^T delta e`. Under the declared Euclidean environmental metric, the smallest first-order displacement needed to reach the boundary has magnitude

\[
\boxed{d_{\rm env}(f)=\frac{|f(e)|}{\|\nabla f(e)\|_2}}.
\]

Therefore inside BALANCE,

\[
d_0(e)=\frac{L(e)}{\|\nabla L(e)\|_2}
\]

is the local environmental distance to the SCH-facing boundary and

\[
d_2(e)=\frac{\rho(e)}{\|\nabla\rho(e)\|_2}
\]

is the local environmental distance to the SLK-facing architecture-value boundary. Define

\[
d_E(e)=\min\{d_0(e),d_2(e)\},
\qquad
\xi_E(e)=\frac{d_0(e)}{d_0(e)+d_2(e)}.
\]

## Theorem 1 — environmental depth is invariant to separate positive margin rescalings

Let `L_tilde=aL` and `rho_tilde=b rho` with `a,b>0`. Then each margin and its gradient scale by the same factor, so `d_0` and `d_2` are unchanged. Therefore

\[
\boxed{d_E\text{ and }\xi_E\text{ are invariant to separate positive rescalings of the two margins}.}
\]

This is stronger than fitness-coordinate `xi_F`, which requires the margins to share a meaningful common scale before they are added.

## Theorem 2 — equal fitness margins need not imply equal environmental distances

The fitness-deep condition is `L=rho`. The environmental equal-distance condition is

\[
\boxed{\frac{L}{\|\nabla L\|}=\frac{\rho}{\|\nabla\rho\|}}.
\]

These conditions coincide only when the two boundary gradients have equal norm at that context. Thus `xi_F=1/2` identifies the deepest state on the fitness-margin scale, not automatically in physical environmental distance.

## Scalar environmental path

For one-dimensional `e`,

\[
d_0=\frac{L}{|L'|},\qquad d_2=\frac{\rho}{|\rho'|}.
\]

If `d_0` increases continuously, `d_2` decreases continuously, and they straddle, then the unique local environmental deepest point satisfies `d_0=d_2` and `xi_E=1/2`. This can occur at a different environmental context from the fitness-deep point `L=rho`.

## Example

If `L(e)=e` and `rho(e)=4-2e` inside `0<e<2`, fitness-margin equality gives `e_F=4/3`, whereas environmental distances are `d_0=e` and `d_2=2-e`, giving `e_E=1`. The two notions of middle-world center are therefore distinct.

## Metric dependence

In multiple environmental dimensions, Euclidean distance depends on coordinate scaling. Under a positive-definite metric matrix `G`, the corresponding first-order distance is

\[
\frac{|f|}{\sqrt{\nabla f^T G^{-1}\nabla f}}.
\]

The conceptual result is unchanged: distance to a boundary is margin divided by gradient magnitude under the chosen metric.

## Empirical consequence

BALANCE can report complementary robustness quantities:

```text
fitness robustness       d_F = min(L,rho)
environmental robustness d_E = min(distance to C0, distance to C2)
```

A system can have a large fitness reserve but sit close to a boundary in environmental space if the relevant margin changes steeply with environment, or the reverse when it changes slowly.

## Claim ceiling

`d_E` is a local first-order boundary-distance approximation. Strong curvature, folds, multiple nearby boundary branches, or topology changes require explicit nearest-boundary calculations. The `rho=0` surface is the SLK-facing architecture-value boundary; no BITA mechanism follows from this geometric distance.

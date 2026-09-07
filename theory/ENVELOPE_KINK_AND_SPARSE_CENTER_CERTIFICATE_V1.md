# BALANCE envelope-kink and sparse-center certificate v1

## Purpose

Characterize two practical features of a multi-alternative middle world:

1. how local environmental sensitivity behaves where the identity of the best competing architecture switches;
2. how many boundaries are needed to certify a globally deepest affine/metric BALANCE center.

## Part I — directional derivative of the alternative envelope

Let architecture reserves be smooth functions

\[
\rho_j(e)=W_S^*(e)-W_{D_j}^*(e),
\]

and define the envelope reserve

\[
\rho_A(e)=\min_j\rho_j(e).
\]

At context `e`, let the active threat set be

\[
A(e)=\{j:\rho_j(e)=\rho_A(e)\}.
\]

### Theorem 1 — envelope directional derivative

For any environmental direction `v`, the one-sided directional derivative of the minimum envelope is

\[
\boxed{
D\rho_A(e;v)
=
\min_{j\in A(e)}\nabla\rho_j(e)^\top v.
}
\]

Therefore when a single architecture is the unique threat, the envelope gradient is simply that architecture's reserve gradient. At a tie, the most rapidly declining active reserve controls the directional loss of shared-world safety.

### Corollary 1a — a threat switch need not be a state boundary

At a context where two reserves tie positively,

\[
\rho_i=\rho_j>0,
\]

`rho_A` may have a kink even though BALANCE remains strictly identified. The kink records a switch in the identity of the nearest architecture threat, not a crossing of `rho_A=0`.

### Theorem 2 — superdifferential at a tie

Because `rho_A` is the pointwise minimum of smooth functions, its local superdifferential at a tie is the convex hull of active gradients:

\[
\boxed{
\partial^+\rho_A(e)
=
\operatorname{conv}\{\nabla\rho_j(e):j\in A(e)\}.
}
\]

This set captures all supporting first-order slopes compatible with the nonsmooth envelope.

## Part II — sparse certificate for affine metric center

Consider environmental dimension `p`, variable `e in R^p`, and metric-normalized affine status constraints

\[
\bar f_k(e)=\frac{a_k^Te+b_k}{s_k}
\ge t,
\qquad
s_k=\sqrt{a_k^TQ^{-1}a_k}.
\]

Let the feasible environmental domain also be represented by affine inequalities. The metric Chebyshev-center problem is an LP in `(e,t) in R^{p+1}`.

### Theorem 3 — at most p+1 independent constraints certify a basic optimum

If a finite optimum exists, linear-programming theory guarantees an optimal basic feasible solution supported by at most `p+1` linearly independent active constraints in the `(e,t)` variables.

Therefore there exists a deepest-center certificate involving no more than

\[
\boxed{p+1}
\]

independent binding status/feasible-region boundaries.

Degenerate optima may have more than `p+1` tight boundaries, but a subset of at most `p+1` independent ones is sufficient to determine an optimal basic certificate.

### Corollary 3a — low-dimensional environment implies sparse robustness bottleneck

In a one-dimensional environmental path (`p=1`), two independent boundaries suffice to certify an interior center.

In a two-dimensional environmental plane (`p=2`), three independent boundaries suffice.

Thus even when many alternative architectures are registered, only a small subset needs to be locally responsible for the deepest environmental robustness state.

## Theorem 4 — status versus feasibility support

The active certificate can contain both:

- biological status boundaries (`L=0`, `rho_j=0`);
- edges of the declared feasible environmental region.

If a region boundary is active, the observed deepest context is partly sampling/accessibility limited rather than purely centered among biological state boundaries.

Therefore a Chapter-2 analysis should report which active constraints are biological and which are imposed by the environmental study domain.

## Empirical consequence

For repeated environmental contexts:

1. estimate the active alternative set and its reserve gradients;
2. at architecture-threat switches, test the predicted one-sided slope rule rather than fitting one smooth derivative through the kink;
3. identify the binding constraints at the metric-deepest context;
4. distinguish a biologically interior center from a center pinned to the sampled environmental boundary.

This makes the geometry of 'what limits BALANCE robustness' directly auditable.

## Claim ceiling

The directional-derivative result assumes smooth component reserves and applies to the minimum envelope. The sparse-center result is exact for affine boundaries/polyhedral feasible regions; nonlinear boundaries require local or nonlinear-programming analogues. Constraint count is a certificate bound, not a claim that only those biological mechanisms exist. PAYOFF frequency dependence remains separate.

# BALANCE Chebyshev dual-support and shadow-price theorem v1

## Purpose

Identify which small subset of boundaries actually determines the globally deepest affine BALANCE context, and quantify how strongly each binding boundary limits robustness.

The existing metric Chebyshev-center formulation is

\[
\max_{e,t} t
\]

subject to

\[
a_k^\top e+b_k\ge t s_k,
\qquad
s_k=\sqrt{a_k^\top Q^{-1}a_k}>0,
\]

for status boundaries indexed by `k`. The present result gives the LP dual and its low-support certificate.

For clarity, first assume the optimum lies in the interior of the declared environmental feasibility region `E`, so no external `E` boundary is active. Hard feasibility boundaries can be added as extra affine constraints with zero `t` coefficient.

## Theorem 1 — dual representation of deepest metric BALANCE depth

Introduce dual multipliers

\[
\mu_k\ge0.
\]

The dual problem is

\[
\boxed{
\min_{\mu\ge0}
\sum_k\mu_k b_k
}
\]

subject to

\[
\boxed{
\sum_k\mu_k a_k=0
}
\]

and

\[
\boxed{
\sum_k\mu_k s_k=1.
}
\]

Under ordinary LP feasibility/boundedness assumptions, strong duality gives

\[
\boxed{
 t^*
 =
 \min_{\mu\ge0:
 \sum\mu_ka_k=0,
 \sum\mu_ks_k=1}
 \sum_k\mu_k b_k.
}
\]

Thus the deepest BALANCE radius has both a primal environmental-center description and a dual boundary-balance description.

## Interpretation of the dual balance equation

The condition

\[
\sum_k\mu_k a_k=0
\]

says that the active normalized boundary pressures balance vectorially at the deepest point.

The normalization

\[
\sum_k\mu_k s_k=1
\]

sets the scale of that balance in the declared environmental metric.

This is a boundary-geometry statement, not a functional-weight statement from SCH.

## Theorem 2 — at most p+1 boundaries are needed for an optimal dual certificate

Environmental state has dimension `p`. The dual equality system contains `p+1` independent scalar equalities:

- `p` components of `sum mu_k a_k=0`;
- one normalization `sum mu_k s_k=1`.

A basic feasible dual optimum therefore has at most

\[
\boxed{p+1}
\]

positive multipliers.

Hence there exists an optimal deepest-radius certificate supported on at most `p+1` status boundaries when no hard environmental boundary is active.

With affine feasibility-region boundaries included in the LP, the same `p+1` support bound applies to the combined set of status and feasibility constraints in a basic dual certificate.

## Corollary 2a — the center can have many ties but a small explanatory certificate

More than `p+1` boundaries may pass through the same optimal center because of degeneracy or symmetry. The theorem does **not** say that only `p+1` boundaries can be tight.

It says there exists an optimal dual explanation using at most `p+1` positive shadow weights.

So a highly complex architecture set can still admit a compact explanation of what limits environmental robustness.

## Theorem 3 — boundary shadow prices

Perturb the intercept of one status margin,

\[
b_k\mapsto b_k+\varepsilon_k,
\]

without changing the active LP basis locally.

The dual envelope theorem gives

\[
\boxed{
\frac{\partial t^*}{\partial b_k}=\mu_k^*.
}
\]

Therefore `mu_k*` is the local shadow price of relaxing boundary `k`:

- `mu_k*=0` means that boundary does not locally limit the deepest radius;
- larger `mu_k*` means a unit outward shift of that boundary buys more BALANCE depth.

This makes the dual coefficients prospectively interpretable as **which biological boundary is worth moving** if the goal is to enlarge the robust middle world.

## Corollary 3a — active architecture alternatives can be ranked by robustness leverage

For architecture reserve constraints

\[
\rho_j(e)\ge t s_j,
\]

the corresponding dual multiplier measures the local gain in deepest environmental robustness from improving the shared-vs-alternative reserve uniformly by one fitness unit in the affine approximation.

This is distinct from asking which alternative has the smallest reserve at one focal context. A boundary can be locally nearest at one point yet carry zero shadow price at the global deepest center if another set of constraints determines `t*`.

## Theorem 4 — relation to Helly obstruction certificates

For any target depth `t>t*`, the shifted intersection is empty. Helly's theorem guarantees an infeasibility certificate involving at most `p+1` convex constraints.

At `t=t*`, the dual support theorem gives an optimality certificate with the same cardinality scale.

Thus Chapter 2 has paired small certificates:

```text
at the optimum      <= p+1 boundaries explain maximal depth
above the optimum   <= p+1 boundaries can certify impossibility
```

under the affine/convex assumptions.

## Tightness

In `p=1`, an interior interval center generally requires two opposing boundaries.

In `p=2`, the incenter of a nondegenerate triangle is supported by all three sides.

Therefore the `p+1` support bound is tight in ordinary geometries.

## Empirical consequence

A multi-environment BALANCE analysis can report, in addition to `t*` and the center `e*`:

1. the binding/positive-dual boundary set;
2. the dual weights `mu_k*`;
3. whether those boundaries are SCH-facing, particular architecture alternatives, or hard environmental feasibility limits;
4. uncertainty in the support set across bootstrap/posterior worldline draws.

This turns the deepest-region result from a location estimate into a mechanistic geometric explanation of **what constrains the middle world**.

## Claim ceiling

The exact LP dual applies to affine/linearized status margins under a fixed declared metric and feasible region. Dual multipliers can change discontinuously at basis switches. Nonlinear nonconvex boundaries require local or convex-program analogues. A shadow price describes static environmental robustness, not evolutionary response, invasion, or PAYOFF dynamics.

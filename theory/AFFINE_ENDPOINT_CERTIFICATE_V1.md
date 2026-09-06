# BALANCE affine endpoint certificate v1

## Purpose

Exploit concavity of the best-alternative reserve to reduce a continuous one-dimensional architecture-ordering claim to an endpoint certificate under the affine-envelope model.

From the affine-envelope theorem,

\[
\rho_A(e)
=
W_S^*(e)-\max_jW_{D_j}^*(e)
\]

is concave on a declared scalar environmental interval whenever the shared and registered alternative optimized worldlines are affine.

## Theorem 1 — the minimum architecture reserve occurs at an endpoint

Let the environmental interval be

\[
E=[e_L,e_R].
\]

For any interior point

\[
e=\theta e_L+(1-\theta)e_R,
\qquad 0\le\theta\le1,
\]

concavity gives

\[
\rho_A(e)
\ge
\theta\rho_A(e_L)+(1-\theta)\rho_A(e_R)
\ge
\min\{\rho_A(e_L),\rho_A(e_R)\}.
\]

Therefore

\[
\boxed{
\min_{e\in[e_L,e_R]}\rho_A(e)
=
\min\{\rho_A(e_L),\rho_A(e_R)\}.
}
\]

So no unobserved interior alternative-architecture crossing can occur if both endpoint reserves are strictly positive and the affine-envelope assumptions hold exactly.

## Corollary 1a — two-endpoint architecture certificate

If

\[
\boxed{
\rho_A(e_L)>0,
\qquad
\rho_A(e_R)>0,
}
\]

then

\[
\boxed{
\rho_A(e)>0
\quad\forall e\in[e_L,e_R].
}
\]

Thus the shared world beats every registered accessible alternative throughout the whole interval.

This is stronger than a generic sample-grid statement: under the affine-envelope theorem, the continuous-domain conclusion follows from the two endpoints.

## Corollary 1b — endpoint lower bound on architecture depth

Define

\[
r_{end}
=
\min\{\rho_A(e_L),\rho_A(e_R)\}.
\]

Then

\[
\boxed{
\rho_A(e)\ge r_{end}
\quad\forall e\in[e_L,e_R].
}
\]

So endpoint reserves provide a conservative lower bound on the architecture-facing fitness margin everywhere inside the interval.

## Theorem 2 — full BALANCE interval from two concave margins

Suppose the SCH conflict margin `L(e)` is also concave on the same interval. Then

\[
\min_E L
=
\min\{L(e_L),L(e_R)\}.
\]

If all four endpoint conditions hold,

\[
L(e_L)>0,
\quad
L(e_R)>0,
\quad
\rho_A(e_L)>0,
\quad
\rho_A(e_R)>0,
\]

then

\[
\boxed{
L(e)>0,
\qquad
\rho_A(e)>0
\quad\forall e\in E.
}
\]

Hence the entire interval is statically inside BALANCE.

If `L` is affine, its concavity condition is automatic.

## Empirical consequence

A repeated-context experiment can use two distinct kinds of inference:

```text
model-free / weak-shape analysis:
    interior contexts are needed to establish the continuous path

affine-envelope registered analysis:
    positive endpoint reserves certify no hidden architecture crossing inside
```

Interior contexts remain valuable for testing whether the affine assumption is correct. The endpoint theorem should therefore be treated as a **model-based certificate**, not a reason to avoid validation of worldline shape.

A useful design is:

1. reserve endpoint contexts for the formal interval certificate;
2. use one or more interior contexts as held-out affine-shape checks;
3. fail closed to sampled-context inference if the affine model is rejected.

## Partial accessibility scope

The theorem applies to whichever alternative envelope is being used.

- using the possible-accessibility envelope gives a robust endpoint certificate against all currently possible alternatives;
- using only the definite-accessibility envelope gives an optimistic certificate conditional on that smaller scope.

The accessibility label must therefore accompany the endpoint conclusion.

## Claim ceiling

The two-endpoint certificate fails if optimized worldlines are materially curved, accessibility changes inside the interval, the same fitness scale is not maintained, or endpoint uncertainty does not establish positive reserve. Positive point estimates alone are insufficient. The result is static Chapter-2 geometry and does not establish switching hysteresis or PAYOFF invasion behavior.

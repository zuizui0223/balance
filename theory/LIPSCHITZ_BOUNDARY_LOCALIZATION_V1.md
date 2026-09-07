# BALANCE Lipschitz boundary localization v1

## Purpose

Localize a critical environmental boundary from one positive and one negative observation using only continuity plus a registered Lipschitz bound.

The result is weaker than an affine interpolation formula but stronger than a mere statement that a crossing occurs somewhere between the two contexts. It produces a guaranteed interval in which every zero crossing must lie.

## Setup

Consider one scalar BALANCE status margin along a registered one-dimensional environmental path parameterized by arc length

\[
t\in[0,D].
\]

Examples include:

- `L(t)` for the SCH-facing conflict onset;
- one architecture reserve `rho_j(t)`;
- the envelope reserve `rho_A(t)` where a valid Lipschitz bound has been registered.

Assume

\[
|f(t)-f(s)|\le K|t-s|
\]

with `K>0`.

Suppose the endpoints straddle the boundary:

\[
f(0)=p>0,
\qquad
f(D)=n<0.
\]

Continuity guarantees at least one zero in `(0,D)`.

## Theorem 1 — every zero lies inside a Lipschitz bracket

Let `t*` satisfy

\[
f(t^*)=0.
\]

From the positive endpoint,

\[
p=|f(0)-f(t^*)|
\le Kt^*,
\]

so

\[
\boxed{t^*\ge p/K.}
\]

From the negative endpoint,

\[
-n=|f(D)-f(t^*)|
\le K(D-t^*),
\]

so

\[
\boxed{t^*\le D+n/K
=D-|n|/K.}
\]

Therefore every zero satisfies

\[
\boxed{
\frac{p}{K}
\le t^*
\le
D-rac{|n|}{K}.
}
\]

This is the **Lipschitz critical-boundary bracket**.

## Theorem 2 — feasibility audit for the registered Lipschitz constant

The bracket is nonempty only if

\[
\frac{p}{K}
\le
D-rac{|n|}{K},
\]

or equivalently

\[
\boxed{p+|n|\le KD.}
\]

But the endpoint Lipschitz condition itself requires

\[
|p-n|=p+|n|\le KD.
\]

Thus an empty bracket is not a biological result; it means the registered `K`, path distance, or endpoint measurements are mutually inconsistent beyond uncertainty.

## Corollary 2a — bracket width

The guaranteed interval width is

\[
\boxed{
W_{crit}
=D-rac{p+|n|}{K}.
}
\]

For fixed endpoint distance, deeper opposite-sign endpoint margins shrink the possible crossing region. A larger conservative `K` widens the interval because faster hidden variation is allowed.

## Theorem 3 — multiple straddling pairs intersect to sharpen localization

Suppose several positive/negative sample pairs along the same ordered path each produce a valid zero bracket `I_r`, and the model additionally asserts a **unique** zero for the focal margin on the registered interval.

Then the unique critical point must lie in

\[
\boxed{I_{joint}=\bigcap_r I_r.}
\]

If the intersection is empty while each pair individually passes its Lipschitz audit, the unique-crossing assumption is falsified or the pairwise samples do not belong to the same static path/context model.

Without a unique-zero assumption, different straddling pairs can refer to different crossings, so their brackets should not be intersected blindly.

## Corollary 3a — relation to no-reentry results

When an independent BALANCE theorem supplies uniqueness/connectedness—for example a declared monotone path or a concave/affine reserve with the appropriate sign structure—the intersection rule can be used safely.

Thus topology and boundary localization play different roles:

```text
shape/topology assumption -> tells whether there is one relevant crossing
Lipschitz magnitude bound -> tells where that crossing can be
```

## Uncertain endpoint margins

Suppose endpoint intervals establish robust signs:

\[
f(0)\in[p^-,p^+],\qquad p^->0,
\]

\[
f(D)\in[n^-,n^+],\qquad n^+<0.
\]

For a conservative bracket containing every crossing compatible with the intervals, use the smallest certified absolute endpoint margins:

\[
\boxed{
t^*\ge p^-/K}
\]

and

\[
\boxed{
t^*\le D-|n^+|/K.}
\]

If `K` is uncertain, use a conservative upper bound `K^+`, which weakens but preserves the guarantee.

## Environmental metric interpretation

If the path is a geodesic or a registered trajectory in a metric environmental space, `D` is its metric arc length. The theorem localizes the crossing **along that path**. It does not claim that the same point is the globally nearest boundary in the full multidimensional environment.

## Empirical consequence

A repeated-context BALANCE study no longer needs to choose between:

```text
linear interpolation of a crossing
```

and

```text
only saying the crossing is somewhere between samples.
```

With a justified Lipschitz bound it can report a nonparametric critical interval. Follow-up sampling can target the midpoint or another design-optimal point inside that interval, then recompute the bracket.

This supplies a sequential critical-region localization route even when affine worldline assumptions are too strong.

## Claim ceiling

The theorem requires a valid Lipschitz bound along the registered path and robust opposite endpoint signs. Multiple-pair intersection additionally requires a unique-crossing/topology assumption. The bracket localizes a static status boundary; it does not identify historical direction, hysteresis or PAYOFF invasion dynamics.
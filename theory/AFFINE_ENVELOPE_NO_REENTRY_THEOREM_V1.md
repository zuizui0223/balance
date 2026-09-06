# BALANCE affine-envelope no-reentry theorem v1

## Purpose

Strengthen the one-dimensional middle-world topology when several accessible alternative architectures compete with the shared world.

The existing multi-alternative definition uses the upper envelope

\[
W_A^*(e)=\max_j W_{D_j}^*(e),
\qquad
\rho_A(e)=W_S^*(e)-W_A^*(e).
\]

Here we show that if optimized worldlines are affine along a declared scalar environmental coordinate, the architecture reserve is automatically concave. This rules out architecture-side BALANCE re-entry without requiring each individual reserve to be monotone.

## Setup

Let `e` vary on an interval `E subset R`. Suppose

\[
W_S^*(e)=a_S e+b_S
\]

and each registered alternative architecture has

\[
W_{D_j}^*(e)=a_j e+b_j,
\qquad j=1,\ldots,m.
\]

Define

\[
\rho_j(e)=W_S^*(e)-W_{D_j}^*(e)
=(a_S-a_j)e+(b_S-b_j).
\]

Then

\[
\rho_A(e)=\min_j\rho_j(e).
\]

## Theorem 1 — architecture reserve is concave

A pointwise minimum of affine functions is concave. Therefore

\[
\boxed{\rho_A(e)\text{ is concave on }E.}
\]

Equivalently, because the alternative upper envelope is a pointwise maximum of affine functions,

\[
W_A^*(e)
\]

is convex, and subtracting it from affine `W_S*` yields a concave reserve.

## Corollary 1a — architecture-favored shared domain is connected

For any concave function, every superlevel set is convex. Hence

\[
\boxed{
\{e\in E:\rho_A(e)>0\}
}
\]

is an interval (possibly empty).

Therefore along an affine one-dimensional environmental worldline, the architecture ordering cannot follow

```text
shared favored -> alternative favored -> shared favored
```

without violating at least one registered assumption.

If the path begins inside the shared-favored architecture domain and later crosses `rho_A=0`, it cannot re-enter the shared-favored domain farther along the same affine path.

This is an architecture-side no-reentry theorem that does **not** require every `rho_j` to be monotone.

## Corollary 1b — connected full BALANCE domain under concave conflict margin

If the SCH conflict margin `L(e)` also has a convex positive superlevel set—for example if `L` is affine or concave on `E`—then

\[
\mathcal B
=
\{L>0\}\cap\{\rho_A>0\}
\]

is the intersection of two intervals and is therefore itself an interval.

Under these conditions the full static BALANCE domain has at most one connected component.

## Theorem 2 — each affine alternative can be active on at most one interval

Let

\[
A_j=
\{e\in E:W_{D_j}^*(e)=W_A^*(e)\}
\]

be the set where alternative `j` lies on the upper envelope.

For every competitor `k`,

\[
W_{D_j}^*(e)-W_{D_k}^*(e)
\]

is affine. If it is nonnegative at two points `e_1<e_3`, it is nonnegative at every point between them. Intersecting this property over all competitors implies

\[
\boxed{A_j\text{ is an interval (possibly empty).}}
\]

Thus an alternative cannot leave the upper envelope and later return on a disjoint interval.

## Corollary 2a — threat-switch complexity bound

After removing alternatives that are never active, each active alternative occupies at most one connected envelope segment. Therefore with `m` registered alternatives,

\[
\boxed{
N_{\rm threat\ switch}\le m-1
}
\]

apart from exact tie intervals, which can be represented as a multi-active segment rather than repeated switching.

This gives a finite complexity bound on architecture-threat identity along an affine environmental gradient.

## Theorem 3 — reserve slope changes in one direction

Because `rho_A` is concave and piecewise affine, its slope is non-increasing as `e` increases. At a threat switch, the active alternative changes to one that makes the reserve slope weakly smaller.

Therefore a sequence of observed reserve slopes that repeatedly increases after exact threat switches is incompatible with the affine-envelope model, beyond uncertainty.

## Empirical consequence

For a repeated-environment BALANCE study, an affine approximation produces three prospective signatures:

1. `rho_A(e)` should be concave/piecewise affine;
2. each alternative architecture should occupy at most one envelope interval;
3. architecture-side shared-favored occupancy should form one connected interval.

Observed re-entry can therefore be localized to a failure of the affine/static/common-scope assumptions rather than being automatically interpreted as evolutionary hysteresis or PAYOFF frequency dependence.

## Relation to earlier no-reentry result

The earlier sufficient no-reentry theorem used monotone changes in `L`, decoupling and cost. The present theorem is different: it uses **affine worldline geometry and the multi-alternative envelope**. Individual architecture reserves may rise or fall, and threat identity may switch, while the best-alternative reserve remains concave and its positive set remains connected.

## Claim ceiling

The theorem is exact only for the declared one-dimensional affine optimized worldlines and fixed registered accessibility scope. Curved worldlines can generate more complex envelopes; changing which architectures are biologically accessible with environment changes the problem itself. Statistical uncertainty near ties can obscure threat identity. The result concerns static optimized fitness, not switching costs, history, invasion, or PAYOFF dynamics.

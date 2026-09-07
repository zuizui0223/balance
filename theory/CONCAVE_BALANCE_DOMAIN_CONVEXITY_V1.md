# BALANCE concave-domain convexity theorem v1

## Purpose

Generalize the one-dimensional affine no-reentry result to a higher-dimensional environmental domain without requiring linear worldlines.

The result is simple but strong: if every positive BALANCE status margin is concave in environment, then the entire static BALANCE region is convex. Hidden exit-and-reentry along any straight environmental interpolation is impossible.

## Setup

Let the environmental state be

\[
e\in E\subset\mathbb R^p,
\]

where `E` is convex.

Let

\[
L(e)
\]

be the positive SCH-facing conflict margin.

For registered accessible alternatives `D_j`, let

\[
\rho_j(e)=W_S^*(e)-W_{D_j}^*(e).
\]

The best-alternative reserve is

\[
\rho_A(e)=\min_j\rho_j(e).
\]

The static BALANCE region is

\[
\mathcal B
=
\{e\in E:L(e)>0,\;\rho_j(e)>0\;\forall j\}.
\]

Equivalently,

\[
\mathcal B
=
\{e\in E:L(e)>0,\;\rho_A(e)>0\}.
\]

Assume `L` and every `rho_j` are concave on `E`.

## Lemma 1 — the architecture envelope reserve is concave

The pointwise minimum of concave functions is concave because its hypograph is the intersection of their convex hypographs.

Therefore

\[
\boxed{
\rho_A(e)=\min_j\rho_j(e)
\text{ is concave on }E.
}
\]

Thus adding multiple alternative architectures does not destroy the concavity structure when every reserve is concave.

## Theorem 1 — the BALANCE region is convex

Take any two BALANCE contexts `e_0,e_1 in B` and any `t in [0,1]`. Let

\[
e_t=(1-t)e_0+te_1.
\]

Concavity gives

\[
L(e_t)
\ge
(1-t)L(e_0)+tL(e_1)>0,
\]

and for every alternative `j`,

\[
\rho_j(e_t)
\ge
(1-t)\rho_j(e_0)+t\rho_j(e_1)>0.
\]

Hence

\[
\boxed{e_t\in\mathcal B.}
\]

Therefore

\[
\boxed{\mathcal B\text{ is convex}.}
\]

Convexity implies connectedness, but is stronger: every straight environmental interpolation between two BALANCE contexts remains BALANCE.

## Corollary 1a — no hidden static re-entry along a chord

If two endpoint contexts on a straight environmental transect are both BALANCE, then under the declared concavity assumptions the entire segment between them is BALANCE.

Therefore a pattern

```text
BALANCE at endpoint A
BITA-side or no-conflict at an interior point
BALANCE at endpoint B
```

falsifies at least one of:

- concavity of `L`;
- concavity of one or more architecture reserves;
- fixed registered accessibility scope;
- common fitness-scale/context matching;
- the static worldline model itself.

This is a higher-dimensional analogue of the one-dimensional affine no-reentry theorem.

## Corollary 1b — endpoint lower bound along a chord

For any margin `f` among `L,rho_1,...,rho_m`, concavity gives

\[
\boxed{
f(e_t)\ge(1-t)f(e_0)+tf(e_1).}
\]

If both endpoint margins are positive, then over the whole segment

\[
f(e_t)\ge\min\{f(e_0),f(e_1)\}>0.
\]

Therefore the segment-wide direct fitness-depth floor is at least

\[
\boxed{
\min_k\min\{f_k(e_0),f_k(e_1)\}.
}
\]

This gives a conservative continuous-segment BALANCE certificate from endpoints once concavity is independently justified.

## Theorem 2 — midpoint/Jensen falsification audit

For an observed interior context `e_t`, define the Jensen residual for margin `f`:

\[
r_f(t)
=
f(e_t)-[(1-t)f(e_0)+tf(e_1)].
\]

Concavity requires

\[
\boxed{r_f(t)\ge0.}
\]

Thus repeated contexts provide a direct shape audit before the convex-domain theorem is used for interpolation.

The strongest fail-closed workflow is:

1. preregister the environmental chord and margin definitions;
2. reserve endpoints for the continuous-domain certificate;
3. use held-out interior contexts to test the Jensen inequalities;
4. only if the concavity gate survives, promote endpoint-positive intervals to continuous BALANCE segments.

## Relation to the affine-envelope theorem

Affine functions are both concave and convex. Therefore the previous one-dimensional affine endpoint/no-reentry results are special cases.

The present theorem allows nonlinear concave margins and arbitrary environmental dimension `p`, but it only controls straight segments inside a convex environmental domain.

## Biological interpretation

A convex BALANCE domain means that once two environmental contexts are known to support the shared architecture against every accessible alternative, intermediate mixtures of those environmental conditions cannot create a hidden static differentiated optimum if all relevant margins bend concavely.

This is a testable geometry of persistence, not a frequency-dependent population result.

## Claim ceiling

Concavity is a biological/model assumption and must not be inferred merely because a few sampled points look smooth. The theorem does not apply if accessibility changes discontinuously, worldline optimization changes feasible sets, margins are nonconcave, or history/frequency dependence changes state. Strict positivity is a static optimized-fitness statement; PAYOFF invasion and coexistence remain separate.

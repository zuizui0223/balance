# BALANCE multi-alternative envelope and metric Chebyshev-center theorem v1

## Purpose

Extend the two-worldline BALANCE definition to systems with **multiple accessible alternative architectures** without changing the canonical logic.

The key move is to replace a single differentiated-accessible worldline by the upper envelope of all registered alternative worldlines.

## Setup

Let

\[
W_S^*(e)
\]

be optimized shared-world fitness in environmental context `e`.

Let `j=1,...,m` index registered alternative architectures with optimized fitness

\[
W_{D_j}^*(e).
\]

Define architecture-specific reserves

\[
\rho_j(e)=W_S^*(e)-W_{D_j}^*(e).
\]

Define the best accessible alternative worldline

\[
W_A^*(e)=\max_j W_{D_j}^*(e)
\]

and its shared-world reserve

\[
\rho_A(e)=W_S^*(e)-W_A^*(e).
\]

## Theorem 1 — envelope reduction

Because subtracting a maximum is the minimum of the subtracted differences,

\[
\boxed{
\rho_A(e)=\min_j\rho_j(e).
}
\]

Therefore the multi-alternative middle world is

\[
\boxed{
L(e)>0,
\qquad
\rho_A(e)>0
}
\]

which is equivalent to

\[
\boxed{
L(e)>0,
\qquad
\rho_j(e)>0\;\text{for every registered alternative }j.
}
\]

Thus the canonical binary BALANCE definition survives exactly if `W_D*` is interpreted as the **best accessible alternative envelope**.

## Theorem 2 — nearest architecture threat

At any BALANCE context, define the active threatening alternatives

\[
A_D(e)=\operatorname*{arg\,min}_j\rho_j(e).
\]

These are exactly the architectures attaining the upper fitness envelope.

The direct fitness depth becomes

\[
\boxed{
d_F(e)=\min\{L(e),\rho_1(e),\ldots,\rho_m(e)\}.}
\]

So Chapter 2 has one SCH-facing boundary and potentially several BITA-facing architecture boundaries. The nearest boundary can switch identity as environment changes.

## Corollary — architecture-envelope kinks are not re-entry by themselves

Even if every `W_{D_j}*` and `W_S*` is smooth, the envelope

\[
W_A^*=\max_jW_{D_j}^*
\]

can be nonsmooth where the identity of the best alternative changes.

Such a kink means

```text
best alternative architecture changed
```

not necessarily

```text
BALANCE disappeared and re-entered.
```

State re-entry still requires the sign of `rho_A` to cross zero and later become positive again.

## Metric environmental depth with several alternatives

Let each positive status margin be denoted

\[
f_k(e),
\]

where the collection contains the SCH conflict margin `L` and every architecture reserve `rho_j`.

Under a positive-definite environmental perturbation metric `Q`, the local distance to affine/linearized boundary `f_k=0` is

\[
d_{k,Q}
=
\frac{f_k}
{\sqrt{\nabla f_k^\top Q^{-1}\nabla f_k}}.
\]

Therefore the local multi-alternative environmental robustness is

\[
\boxed{
d_{B,Q}=\min_k d_{k,Q}.}
\]

The nearest exit can be either conflict loss (`L=0`) or any one of the alternative architecture crossings (`rho_j=0`).

## Theorem 3 — exact metric Chebyshev-center program for affine boundaries

Suppose on a declared environmental region `E` all status margins are affine:

\[
f_k(e)=a_k^\top e+b_k,
\]

and `E` is compact and convex. For affine boundaries the metric distance formula is exact, because the boundaries are hyperplanes.

Define

\[
s_k=\sqrt{a_k^\top Q^{-1}a_k}.
\]

A globally environmentally deepest BALANCE context solves

\[
\boxed{
\max_{e\in E,\;t} t
}
\]

subject to

\[
\boxed{
f_k(e)\ge t s_k\quad\text{for every status boundary }k.}
\]

The optimal value `t*` is the radius of the largest `Q`-metric ball centered in `E` that remains inside every registered BALANCE half-space.

This is the metric Chebyshev-center formulation of the multi-boundary middle world.

If `E` is polyhedral, the constraints are linear in `(e,t)` because each `s_k` is constant, so the problem is a linear program after the metric normalization constants are computed.

## Corollary — support of the environmental center

At a regular optimum, the deepest environmental state is determined by the subset of boundaries whose normalized constraints are tight:

\[
f_k(e^*)=t^*s_k.
\]

These are the **binding boundaries** of environmental robustness.

They need not include every possible alternative architecture. Thus, as in SCH's binding-function geometry, a large candidate set can reduce locally to a smaller set of constraints that actually limit robustness.

## Empirical interpretation

The extension supports systems with several candidate solutions to the same conflict:

```text
shared architecture S
vs
alternative D1
alternative D2
alternative D3
...
```

BALANCE persists only if S still outperforms the best of them all.

This matters for comparative biology because observing that one differentiated state loses to S is insufficient if another accessible differentiated state would win.

A complete Chapter-2 alternative set therefore requires a **registered accessibility scope**: which architectures count as biologically available alternatives in the focal comparison.

## Claim ceiling

The theorem does not identify the complete biological alternative set automatically. Omitted accessible architectures can make an apparent BALANCE state false. The Chebyshev-center result is exact for affine margins and otherwise local/approximate when based on linearized boundaries. The declared environmental metric and feasible region `E` remain biological assumptions. PAYOFF invasion dynamics are separate.

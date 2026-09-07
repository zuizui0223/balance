# BALANCE Helly no-middle-world certificate v1

## Purpose

Show that in a p-dimensional environmental space, failure of the BALANCE region can be certified by a **small subset of boundaries**, even when many alternative architectures are registered.

The multi-alternative BALANCE region is an intersection of convex status sets. Helly's theorem therefore gives a finite low-cardinality obstruction certificate.

## Setup

Let environmental state be

\[
e\in\mathbb R^p.
\]

Let `E` be a declared convex feasible environmental region.

For the SCH-facing condition define

\[
C_0=\{e:L(e)\ge0\}.
\]

For each registered accessible alternative architecture `j`, define

\[
C_j=\{e:\rho_j(e)\ge0\},
\qquad
\rho_j=W_S^*-W_{D_j}^*.
\]

Assume every `C_j` is convex on `E`. This holds, for example, for affine margins or other registered quasiconcave/nonnegative-superlevel models.

The closed nonnegative middle-world feasibility set is

\[
\mathcal B_0=E\cap C_0\cap C_1\cap\cdots\cap C_m.
\]

## Theorem 1 — small infeasibility certificate

If

\[
\boxed{\mathcal B_0=\varnothing,}
\]

then by Helly's theorem there exists a subfamily of at most

\[
\boxed{p+1}
\]

sets among

\[
E,C_0,C_1,\ldots,C_m
\]

whose intersection is already empty.

Therefore a global no-middle-world conclusion in p environmental dimensions always has a certificate involving at most `p+1` binding convex constraints.

The full candidate set can be large, but the obstruction need not be.

## Corollary 1a — interior-domain failure at positive robustness depth

For a declared metric-normalized robustness target `t>0`, define shifted convex sets

\[
C_k(t)=\{e:f_k(e)\ge t s_k\},
\]

where `f_k` ranges over `L` and every registered architecture reserve and `s_k` is the corresponding metric boundary-normalization factor.

If the depth-`t` middle world is empty,

\[
E\cap\bigcap_k C_k(t)=\varnothing,
\]

then some subfamily of at most `p+1` convex constraints already proves that no context achieves robustness depth `t`.

Thus every rejected candidate depth has a small Helly obstruction certificate.

## Corollary 1b — relation to the metric Chebyshev center

Let `t*` be the globally deepest metric BALANCE radius from the affine Chebyshev-center program.

For every

\[
t>t^*,
\]

the depth-`t` intersection is empty, so there exists a certificate with at most `p+1` constraints.

At a regular nondegenerate optimum, the active LP constraints that determine the center supply such a small support directly.

This explains why a high-dimensional list of candidate alternative architectures can still yield a low-cardinality local explanation of why BALANCE cannot be deeper.

## Theorem 2 — the p+1 bound is tight

The cardinality bound cannot generally be reduced.

In two environmental dimensions consider the three affine half-spaces

\[
x\ge1,
\qquad
y\ge1,
\qquad x+y\le1.
\]

Every pair intersects, but the intersection of all three is empty.

Thus in `p=2`, three constraints may be required to certify infeasibility. This attains the Helly bound `p+1=3`.

Analogous simplex constructions make the bound tight in arbitrary dimension.

## Theorem 3 — accessibility scope can change the obstruction set but not the bound

Adding accessible alternative architectures adds convex reserve constraints and can only shrink the BALANCE set.

If the enlarged set becomes empty, a Helly certificate still uses at most `p+1` constraints, though the identity of those constraints may now include newly added architectures.

Hence accessibility-scope fragility has a compact diagnostic:

```text
which <= p+1 boundaries jointly destroy the middle world?
```

This is more informative than only reporting that the full intersection is empty.

## Empirical interpretation

A multi-environment BALANCE analysis can register dozens of candidate differentiated architectures, but a failed middle-world claim may ultimately be explained by a small set such as:

- the SCH conflict boundary;
- one alternative architecture boundary;
- one environmental feasibility boundary.

or, in another system, by several alternative architecture boundaries without the SCH boundary being limiting.

The certificate therefore identifies the **minimal local combination of constraints** that makes compromise unsustainable.

## Claim ceiling

The theorem requires convex status sets in the declared environmental coordinates. For nonlinear nonconvex worldline margins, disconnected accessibility regions, or history-dependent state spaces, Helly's finite-dimensional convex result does not apply directly. The theorem certifies emptiness of the static environmental intersection, not PAYOFF invasion or coexistence dynamics.

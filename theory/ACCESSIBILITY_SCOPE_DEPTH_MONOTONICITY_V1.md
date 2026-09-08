# BALANCE accessibility-scope depth monotonicity theorem v1

## Purpose

Extend accessibility-scope monotonicity from state classification to the **depth and robustness** of the middle-world domain.

The result formalizes a basic but important asymmetry: discovering additional biologically accessible alternative architectures can only make a BALANCE claim harder to sustain. It can shrink the domain or leave it unchanged, but cannot deepen or enlarge it.

## Setup

Let `A` and `B` be registered alternative-architecture sets with

\[
A\subseteq B.
\]

For each alternative `j`, define the shared-world reserve

\[
\rho_j(e)=W_S^*(e)-W_{D_j}^*(e).
\]

Define the envelope reserve for scope `A` by

\[
\rho_A(e)=\min_{j\in A}\rho_j(e),
\]

and analogously `rho_B`.

Let the SCH-facing conflict margin be `L(e)>0` when conflict is active.

## Theorem 1 — reserve monotonicity under scope expansion

Because `A subseteq B`,

\[
\boxed{
\rho_B(e)\le\rho_A(e)
\quad\text{for every }e.
}
\]

Equivalently, the best alternative fitness envelope can only rise when more accessible alternatives are admitted.

## Theorem 2 — BALANCE-domain nesting

Define

\[
\mathcal B_A=\{e:L(e)>0,\;\rho_A(e)>0\}.
\]

Then

\[
\boxed{
\mathcal B_B\subseteq\mathcal B_A.
}
\]

Thus expanding the accessibility scope cannot create a new static BALANCE context that was absent under the smaller scope.

A previously identified BALANCE state can be destroyed by a newly admitted winning alternative, but a newly admitted alternative cannot rescue a non-BALANCE state into BALANCE.

## Theorem 3 — pointwise fitness-depth monotonicity

Define direct fitness depth under scope `A` by

\[
d_F^A(e)=\min\{L(e),\rho_A(e)\}.
\]

Then

\[
\boxed{
d_F^B(e)\le d_F^A(e)\quad\forall e.}
\]

Consequently, over any fixed environmental region `E`,

\[
\boxed{
\sup_{e\in E}d_F^B(e)
\le
\sup_{e\in E}d_F^A(e).
}
\]

So the deepest attainable fitness-margin middle world cannot become deeper after the accessibility set expands.

## Theorem 4 — metric environmental inradius monotonicity

Fix a positive-definite environmental perturbation metric `Q`. Under the declared affine/local boundary model, use **signed inward normalized margins**

\[
d_{L,Q}(e)=
\frac{L(e)}{
\sqrt{\nabla L(e)^\top Q^{-1}\nabla L(e)}
}
\]

and

\[
d_{j,Q}(e)=
\frac{\rho_j(e)}{
\sqrt{\nabla \rho_j(e)^\top Q^{-1}\nabla \rho_j(e)}
}
\]

whenever the relevant gradient is nonzero. These quantities are positive on the corresponding inside half-space and negative after crossing that boundary.

For an inside BALANCE context define

\[
d_Q^A(e)=\min\left\{d_{L,Q}(e),\min_{j\in A}d_{j,Q}(e)\right\}.
\]

Adding boundary constraints gives

\[
\boxed{
d_Q^B(e)\le d_Q^A(e)}
\]

wherever both local signed-distance representations are valid. Since also `B_B subseteq B_A`, the global inradius over a fixed region `E`,

\[
r_Q(A)=\sup_{e\in E\cap\mathcal B_A}d_Q^A(e),
\]

obeys

\[
\boxed{
r_Q(B)\le r_Q(A).}
\]

If the expanded BALANCE domain is empty, set its inradius to zero. This extends scope monotonicity from state membership to environmental robustness.

## Equality condition — dominated additions do nothing

If every newly added alternative is pointwise dominated by the old envelope over `E`, i.e.

\[
\rho_j(e)\ge\rho_A(e)
\quad\forall e\in E,
\quad j\in B\setminus A,
\]

then

\[
\rho_B=\rho_A,
\]

so the BALANCE domain and fitness depths are exactly unchanged.

For the metric inradius, equality also holds whenever an old incenter remains feasible at the old radius after the new boundary constraints are added.

## Corollary — scope fragility has a one-sided interpretation

If a BALANCE claim changes when the accessibility registry is enlarged, the change must be in the direction

```text
BALANCE -> unresolved or alternative-winning
```

never the reverse, holding all worldline estimates and the SCH margin fixed.

This gives a simple audit rule for sensitivity analyses over alternative-architecture scope.

## Empirical consequence

A Chapter-2 analysis can report a **scope-depth curve**:

1. begin with the most defensible minimal alternative set;
2. add plausible alternatives according to a preregistered accessibility hierarchy;
3. recompute domain size, maximum `d_F`, and metric inradius;
4. identify which newly added alternative first becomes binding.

The curve is theoretically non-increasing. An observed increase indicates either a bookkeeping error or that other fitted quantities changed between scope definitions.

## Claim ceiling

The theorem holds only when comparing nested accessibility scopes while keeping the same shared worldline, SCH conflict function, fitness scale, environmental metric and alternative-specific worldlines fixed. Re-fitting models after scope changes can change other quantities and is not the same mathematical comparison. Metric inradius claims additionally require valid local/affine boundary-distance formulas over the region being compared. PAYOFF frequency dependence remains separate.

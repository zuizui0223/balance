# BALANCE interval concave-chord identification theorem v1

## Purpose

Make the concave/strong-concave chord tests fail-closed under interval uncertainty. Point estimates can make a Jensen or curvature signature look exact even when uncertainty is large. This result propagates endpoint and interior intervals algebraically and classifies whether the registered curvature model is identified, violated, or unresolved.

## Setup

For one BALANCE status margin `f`, let endpoint and interior uncertainty intervals be

\[
f_0\in[L_0,U_0],\qquad
f_1\in[L_1,U_1],\qquad
f_t\in[L_t,U_t].
\]

At position `t in [0,1]`, define the true concavity bulge

\[
J=f_t-[(1-t)f_0+t f_1].
\]

Suppose the registered strong-concavity model requires

\[
B_L\le J\le B_U,
\]

where, for curvature bounds `alpha,beta`,

\[
B_L=\frac{\alpha}{2}t(1-t)d_Q^2,
\qquad
B_U=\frac{\beta}{2}t(1-t)d_Q^2.
\]

## Theorem 1 — identified set for the bulge

Because `J` increases with `f_t` and decreases with both endpoints,

\[
\boxed{
J\in[J_L,J_U]
}
\]

with

\[
\boxed{
J_L=L_t-[(1-t)U_0+tU_1]
}
\]

and

\[
\boxed{
J_U=U_t-[(1-t)L_0+tL_1].
}
\]

This is the sharp interval implied by the supplied marginal intervals when no additional dependence information is used.

## Theorem 2 — fail-closed curvature classification

Compare the possible bulge interval `[J_L,J_U]` with the model-required interval `[B_L,B_U]`.

- if `J_U < B_L`, the strong-concavity lower bound is impossible;
- if `J_L > B_U`, the curvature upper bound is impossible;
- if `[J_L,J_U]` lies wholly inside `[B_L,B_U]`, the registered chord signature is interval-identified;
- otherwise the result is unresolved.

Thus

```text
possible interval disjoint below model -> LOWER_BOUND_VIOLATED
possible interval disjoint above model -> UPPER_BOUND_VIOLATED
possible interval contained in model    -> IDENTIFIED_WITHIN_INTERVALS
overlapping partial intervals           -> UNRESOLVED
```

No point estimate is allowed to override the interval classification.

## Corollary 2a — ordinary concavity violation

For concavity alone, the lower requirement is `B_L=0`. If

\[
\boxed{J_U<0,}
\]

then no values inside the supplied intervals can satisfy Jensen concavity.

This is a robust shape falsifier.

## Theorem 3 — robust endpoint-positive segment certificate

If both endpoint lower bounds are positive,

\[
L_0>0,\qquad L_1>0,
\]

then every admissible true endpoint pair is BALANCE-positive for that margin. Under the independently accepted concavity model, every point on the chord satisfies

\[
f(e_t)>0.
\]

For several status margins, the whole segment is robustly BALANCE under concavity if the lower bounds for **every** margin are positive at both endpoints.

This separates uncertainty in measured margins from uncertainty in the concavity model itself.

## Corollary 3a — conservative segment floor

Under concavity, a guaranteed segment-wide lower margin is

\[
\boxed{\min(L_0,L_1).}
\]

For strict interior points with a validated strong-concavity lower curvature `alpha>0`, the pointwise lower bound can be sharpened by adding the corresponding curvature bulge.

## Empirical consequence

Repeated BALANCE experiments should propagate uncertainty in `L`, `rho_j`, or `rho_A` before calling a continuous chord. A useful reporting block is:

```text
endpoint intervals
interior interval
possible Jensen-bulge interval [J_L,J_U]
registered curvature interval [B_L,B_U]
classification
```

This is especially important when direct worldline optima are bootstrap-derived and their uncertainty is not negligible relative to the predicted curvature bulge.

## Claim ceiling

The interval arithmetic assumes only marginal bounds and is therefore conservative when estimates are correlated. A sharper joint confidence region can tighten the identified set, but must be prospectively justified. Robust endpoint positivity does not prove concavity; the shape model remains a separate gate. PAYOFF dynamics remain outside the result.

# BALANCE boundary-sensitivity theorem v1

## Purpose

Quantify how the SCH-facing boundary, the SLK-facing architecture-value boundary, BALANCE width, and the deepest middle-world point move under small perturbations of the two directly measurable margins.

Work on a scalar environmental axis `e`. Let `L(e)` be the SCH-facing conflict margin and

\[
\rho(e)=W_S^*(e)-W_D^*(e)
\]

be the SLK-facing architecture-value reserve. Inside BALANCE, `L>0` and `rho>0`. Assume regular simple roots and differentiability at the relevant points.

## Boundary definitions

Let `e_0` be the SCH-facing boundary:

\[
L(e_0)=0,\qquad L'(e_0)\ne0.
\]

Let `e_2` be the SLK-facing architecture-value boundary:

\[
\rho(e_2)=0,\qquad \rho'(e_2)\ne0.
\]

For the usual monotone orientation, `L'(e_0)>0`, `rho'(e_2)<0`, and `W_e=e_2-e_0`. Let the deepest point `e_d` satisfy `L(e_d)=rho(e_d)` and `L'(e_d)-rho'(e_d) != 0`.

## Perturbation setup

Perturb the margins by

\[
L_\epsilon(e)=L(e)+\epsilon a(e),\qquad
\rho_\epsilon(e)=\rho(e)+\epsilon b(e).
\]

## Theorem 1 — SCH-facing boundary displacement

\[
\boxed{\frac{de_0}{d\epsilon}=-\frac{a(e_0)}{L'(e_0)}}.
\]

Thus the same additive perturbation produces a larger environmental boundary shift where the SCH margin crosses zero shallowly.

## Theorem 2 — SLK-facing architecture-value boundary displacement

\[
\boxed{\frac{de_2}{d\epsilon}=-\frac{b(e_2)}{\rho'(e_2)}}.
\]

When `rho'<0`, a positive perturbation to the shared-architecture reserve moves the architecture-value crossing toward larger `e`.

## Corollary 2a — BALANCE-width sensitivity

\[
\boxed{\frac{dW_e}{d\epsilon}=-\frac{b(e_2)}{\rho'(e_2)}+\frac{a(e_0)}{L'(e_0)}}.
\]

A wider BALANCE domain need not mean that both boundaries moved outward; one side can dominate.

## Theorem 3 — deepest-point displacement

At the deepest point, implicit differentiation of `L-rho=0` gives

\[
\boxed{\frac{de_d}{d\epsilon}=-\frac{a(e_d)-b(e_d)}{L'(e_d)-\rho'(e_d)}}.
\]

Only the difference between perturbations to the two margins moves the equal-margin point. If both margins are shifted equally on the common fitness scale, its location is unchanged to first order.

## Corollary 3a — deepest-depth sensitivity

At `d_*=L(e_d)=rho(e_d)`,

\[
\boxed{\frac{dd_*}{d\epsilon}=\frac{-a(e_d)\rho'(e_d)+b(e_d)L'(e_d)}{L'(e_d)-\rho'(e_d)}}.
\]

Thus location and absolute robustness respond differently to perturbation.

## Special cases

If only SCH-side conflict changes (`b=0`), a positive conflict-margin shift moves the equal-margin point toward the SCH-facing side under the usual orientation. If only the alternative-worldline reserve changes (`a=0`), a positive reserve shift moves the deepest point toward the SLK-facing architecture-value side. If `a=b` at the deepest context, `de_d/d epsilon=0` although absolute depth can change.

## Connection to critical-region uncertainty

These formulas give a local delta-method bridge from uncertainty in fitted margins to uncertainty in conflict-onset location, architecture-value crossing, BALANCE width, and deepest-middle-world location. Shallow crossings are intrinsically difficult to localize because small fitness-margin errors become large environmental-coordinate errors when `|L'|`, `|rho'|`, or `|L'-rho'|` is small.

## Claim ceiling

These are local first-order sensitivity results for regular scalar environmental paths. Multiple roots, nonmonotone paths, discontinuities, or topology changes require the broader BALANCE path framework. The architecture-value boundary is SLK-facing; this theorem does not identify a BITA mechanism.

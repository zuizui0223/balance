# BALANCE boundary-sensitivity theorem v1

## Purpose

Quantify how the SCH-facing boundary, the BITA-facing boundary, the BALANCE width, and the deepest middle-world point move under small perturbations of the two directly measurable margins.

Work on a scalar environmental axis `e`. Let

\[
L(e)
\]

be the SCH-facing conflict margin and

\[
\rho(e)=W_S^*(e)-W_D^*(e)
\]

be the BITA-facing reserve. Inside BALANCE,

\[
L>0,\qquad \rho>0.
\]

Assume regular simple roots and differentiability at the relevant points.

## Boundary definitions

Let `e_0` be the SCH-facing boundary:

\[
L(e_0)=0,\qquad L'(e_0)\ne0.
\]

Let `e_2` be the BITA-facing architecture boundary:

\[
\rho(e_2)=0,\qquad \rho'(e_2)\ne0.
\]

For the usual monotone orientation,

\[
L'(e_0)>0,\qquad \rho'(e_2)<0,
\]

and the finite BALANCE width is

\[
W_e=e_2-e_0.
\]

Let the deepest point `e_d` satisfy

\[
L(e_d)=\rho(e_d),
\qquad
L'(e_d)-\rho'(e_d)\ne0.
\]

## Perturbation setup

Perturb the margins by a small scalar `epsilon`:

\[
L_\epsilon(e)=L(e)+\epsilon a(e),
\]

\[
\rho_\epsilon(e)=\rho(e)+\epsilon b(e).
\]

The functions `a` and `b` can represent a changed ecological context, calibration correction, model parameter shift, or experimentally imposed change in one of the two margins.

## Theorem 1 — SCH-facing boundary displacement

Implicit differentiation of

\[
L_\epsilon(e_0(\epsilon))=0
\]

gives

\[
\boxed{
\frac{de_0}{d\epsilon}
=-\frac{a(e_0)}{L'(e_0)}.
}
\]

Thus the same additive perturbation produces a larger environmental boundary shift where the SCH margin crosses zero shallowly.

## Theorem 2 — BITA-facing boundary displacement

Similarly,

\[
\boxed{
\frac{de_2}{d\epsilon}
=-\frac{b(e_2)}{\rho'(e_2)}.
}
\]

When `rho'<0`, a positive perturbation to the shared-architecture reserve moves the architecture crossing toward larger `e`.

## Corollary 2a — BALANCE-width sensitivity

Because `W_e=e_2-e_0`,

\[
\boxed{
\frac{dW_e}{d\epsilon}
=-\frac{b(e_2)}{\rho'(e_2)}
+\frac{a(e_0)}{L'(e_0)}.
}
\]

So width changes are decomposable into independent movement of the two boundaries. A wider BALANCE domain need not mean that both boundaries moved outward; one side can dominate.

## Theorem 3 — deepest-point displacement

Define

\[
g_\epsilon(e)=L_\epsilon(e)-\rho_\epsilon(e).
\]

At the deepest point `g=0`. Implicit differentiation gives

\[
\boxed{
\frac{de_d}{d\epsilon}
=-\frac{a(e_d)-b(e_d)}
{L'(e_d)-\rho'(e_d)}.
}
\]

Only the **difference** between the perturbations to the two margins moves the equal-margin point. If both margins are shifted by the same amount on the common fitness scale, the deepest location is unchanged to first order.

## Corollary 3a — deepest-depth sensitivity

At the deepest point,

\[
d_* = L(e_d)=\rho(e_d).
\]

Differentiating gives

\[
\boxed{
\frac{dd_*}{d\epsilon}
=
\frac{-a(e_d)\rho'(e_d)+b(e_d)L'(e_d)}
{L'(e_d)-\rho'(e_d)}.
}
\]

Therefore the location and the absolute robustness of the deepest state respond differently to perturbation.

## Special cases

### Only SCH-side conflict changes

If `b=0`,

\[
\frac{de_d}{d\epsilon}
=-\frac{a}{L'-\rho'}.
\]

A positive conflict-margin shift moves the equal-margin point toward the SCH-facing side under the usual orientation.

### Only the alternative-worldline reserve changes

If `a=0`,

\[
\frac{de_d}{d\epsilon}
=\frac{b}{L'-\rho'}.
\]

A positive reserve shift moves the deepest point toward the BITA-facing side.

### Common equal shift

If `a=b` at the deepest context, then

\[
\boxed{de_d/d\epsilon=0}
\]

although the absolute depth can change.

## Connection to critical-region uncertainty

These formulas give a local delta-method bridge from uncertainty in fitted margins to uncertainty in:

- conflict-onset location;
- architecture-crossing location;
- BALANCE width;
- deepest-middle-world location.

The denominators show why shallow crossings are intrinsically difficult to localize: small fitness-margin errors become large environmental-coordinate errors when `|L'|`, `|rho'|`, or `|L'-rho'|` is small.

## Claim ceiling

These are local first-order sensitivity results for regular scalar environmental paths. Multiple roots, nonmonotone paths, discontinuities, or topology changes require the broader BALANCE path framework rather than these formulas alone.

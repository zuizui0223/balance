# BALANCE local certified inside/outside balls v1

## Purpose

Convert each measured environmental context into a geometric region whose BALANCE status is certified without interpolation.

Positive margins generate a guaranteed **inside ball**. A sufficiently negative margin generates a guaranteed **outside ball**. Unions of these balls form finite-sample inner approximations to the BALANCE domain and its complement, leaving an explicitly unresolved band between them.

## Setup

Let the registered BALANCE status margins be

\[
f_0(e)=L(e)
\]

and

\[
f_j(e)=\rho_j(e),\qquad j=1,\ldots,m,
\]

for all retained accessible alternatives. Assume each margin is `K_k`-Lipschitz in environmental metric `d_Q`:

\[
|f_k(e)-f_k(s)|\le K_k d_Q(e,s).
\]

## Theorem 1 — certified BALANCE ball around a positive sample

Suppose at sampled context `s`

\[
f_k(s)>0\quad\forall k.
\]

For each boundary with `K_k>0`, define

\[
r_k^+(s)=\frac{f_k(s)}{K_k}.
\]

A positive constant margin with `K_k=0` imposes no finite radius restriction. Define

\[
\boxed{
r_+(s)=\min_k r_k^+(s)}
\]

with constant-positive boundaries interpreted as `+infinity`.

If

\[
d_Q(e,s)<r_+(s),
\]

then for every status margin

\[
f_k(e)
\ge
f_k(s)-K_kd_Q(e,s)
>0.
\]

Therefore

\[
\boxed{
B_Q(s,r_+(s))\subseteq\mathcal B.
}
\]

Each positive receipt thus certifies a local environmental neighborhood, not merely one point.

## Theorem 2 — certified outside ball around a negative sample

Suppose at least one status margin is negative at `s`. For each such boundary with `K_k>0`, define

\[
r_k^-(s)=\frac{-f_k(s)}{K_k}.
\]

If a negative margin has `K_k=0`, that margin is negative everywhere in the registered domain and the outside radius is infinite.

Define

\[
\boxed{
r_-(s)=\max_{k:f_k(s)<0}r_k^-(s).}
\]

Choose a boundary attaining this maximum. For every

\[
d_Q(e,s)<r_-(s),
\]

that boundary obeys

\[
f_k(e)
\le
f_k(s)+K_kd_Q(e,s)
<0.
\]

Hence

\[
\boxed{
B_Q(s,r_-(s))\subseteq\mathcal B^c.
}
\]

A clearly failed margin therefore certifies a local non-BALANCE region.

## Corollary — finite-sample certified phase map

Given sampled contexts `S`, define

\[
\mathcal B_{in}
=
\bigcup_{s\in S:\,all\ f_k(s)>0}
B_Q(s,r_+(s))
\]

and

\[
\mathcal B_{out}
=
\bigcup_{s\in S:\,some\ f_k(s)<0}
B_Q(s,r_-(s)).
\]

Then

\[
\boxed{
\mathcal B_{in}\subseteq\mathcal B,
\qquad
\mathcal B_{out}\subseteq\mathcal B^c.
}
\]

The remaining environmental region

\[
E\setminus(\mathcal B_{in}\cup\mathcal B_{out})
\]

is explicitly unresolved at the current sampling resolution and Lipschitz bounds.

## Relation to the lower-cone envelope

The positive ball from a sample `s` is exactly the set where all of that sample's individual lower cones remain positive:

\[
f_k(s)-K_kd_Q(e,s)>0\quad\forall k.
\]

The adaptive lower-envelope method takes the maximum over cones from **all** samples and can therefore certify points outside every single-sample positive ball. Local balls are a simple interpretable inner approximation; the full lower envelope is the stronger aggregate certificate.

## Uncertain receipts

For interval-valued sampled margins

\[
f_k(s)\in[f_k^-(s),f_k^+(s)],
\]

use:

- lower endpoints `f_k^-` to construct certified BALANCE balls;
- upper endpoints `f_k^+` to construct certified outside balls.

Thus a positive ball requires

\[
f_k^-(s)>0\quad\forall k,
\]

while an outside ball requires at least one

\[
f_k^+(s)<0.
\]

This prevents point-estimate status from being converted into an unjustified neighborhood claim.

## Corollary — direct critical-region targeting

Samples with small normalized margin

\[
\min_k\frac{|f_k(s)|}{K_k}
\]

sit close to a registered status boundary in the environmental metric. They are natural candidates for denser follow-up sampling.

The identity of the limiting margin also tells which boundary is locally relevant:

```text
L/K_L smallest             -> SCH-facing boundary nearby
rho_j/K_j smallest         -> architecture j is nearest BITA-facing threat
```

## Empirical consequence

A BALANCE field programme can publish a map with three non-overstated regions:

```text
CERTIFIED_BALANCE_INNER_REGION
CERTIFIED_NON_BALANCE_REGION
UNRESOLVED_BETWEEN_CERTIFICATES
```

rather than forcing a continuous state label everywhere from sparse interpolation.

As samples accumulate, the adaptive lower-envelope certificate can shrink the unresolved region while the local balls provide an immediately interpretable geometric receipt for each context.

## Claim ceiling

The balls depend on the registered environmental metric and valid Lipschitz constants over the claimed neighborhood. They are local static certificates. They do not imply historical transition direction, switching hysteresis or PAYOFF invasion behavior.
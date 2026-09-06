# BALANCE threat-switch inverse-gradient theorem v1

## Purpose

Invert the affine threat-stability geometry. Instead of predicting where two alternative architectures tie from known environmental slopes, recover their **relative environmental gradient** from an observed nearest threat-switch displacement.

This is useful when the switch geometry is experimentally/local-environmentally observable but separate high-precision worldline slopes are difficult to estimate.

## Setup

Let the current best alternative be `j*` and a competitor be `k`. Under the affine model,

\[
d(e)
=W_{D_{j^*}}^*(e)-W_{D_k}^*(e)
=a^\top e+b,
\]

where

\[
a=a_{j^*}-a_k.
\]

At current context `e_0`, the pairwise threat gap is

\[
\gamma=d(e_0)>0.
\]

Let environmental perturbation distance be

\[
\|\Delta e\|_Q^2
=\Delta e^\top Q\Delta e,
\qquad Q\succ0.
\]

Suppose `delta*` is the **Q-metric shortest displacement** from `e_0` to the tie hyperplane `d(e)=0`.

## Theorem 1 — inverse relative-gradient recovery

The nearest-point problem is

\[
\min_\delta\frac12\delta^\top Q\delta
\]

subject to

\[
a^\top\delta=-\gamma.
\]

Its first-order condition gives

\[
Q\delta^*+\mu a=0.
\]

Combining this with the tie constraint yields

\[
\boxed{
\delta^*
=-\frac{\gamma}{a^\top Q^{-1}a}
Q^{-1}a.
}
\]

Solving this relation for `a` gives the inverse formula

\[
\boxed{
a
=-\frac{\gamma}{\delta^{*\top}Q\delta^*}
Q\delta^*.}
\]

Therefore the current pairwise fitness gap plus the shortest observed switch vector identifies the full relative environmental gradient vector under the affine model.

## Corollary 1a — norm recovery from switch radius

Let

\[
r_Q=\sqrt{\delta^{*\top}Q\delta^*}.
\]

Then

\[
\boxed{
\|a\|_{Q^{-1}}
=\sqrt{a^\top Q^{-1}a}
=\frac{\gamma}{r_Q}.}
\]

Thus even if the direction of the switch cannot be estimated reliably, the switch radius and current gap identify the metric norm of the pairwise environmental sensitivity.

## Corollary 1b — direction recovery

The relative gradient direction is

\[
\boxed{
a\parallel -Q\delta^*.}
\]

So the environmental direction that most rapidly erodes the current threat gap is the metric-dual of the shortest switch displacement.

## Theorem 2 — reciprocal prediction audit

If the inverse-recovered gradient is

\[
\widehat a
=-\frac{\widehat\gamma}{\widehat\delta^{\top}Q\widehat\delta}
Q\widehat\delta,
\]

then substituting it into the forward affine threat-distance formula must recover

\[
\boxed{
\widehat r_Q
=\sqrt{\widehat\delta^\top Q\widehat\delta}
}
\]

up to propagated uncertainty.

This creates a forward/inverse concordance audit:

```text
current pairwise gap
+ shortest switch displacement
-> inverse relative gradient
-> predicted switch distance
-> must return the observed metric radius
```

Failure beyond uncertainty rejects at least one of:

- affine pairwise worldline difference;
- registered environmental metric;
- assumption that the observed switch displacement is the nearest tie move;
- correct pairing of the two alternative architectures.

## Relation to BALANCE state geometry

This theorem concerns the identity of the best alternative, not the shared-vs-alternative state boundary.

A pairwise alternative tie can occur with

\[
W_{D_{j^*}}^*=W_{D_k}^*<W_S^*
\]

so BALANCE remains positive while the active threat identity changes.

The inverse gradient is therefore a **competitor-geometry quantity**, not a BALANCE occupancy certificate by itself.

## Empirical design implication

For a repeated-context experiment around a robust BALANCE state:

1. estimate the current fitness gap between the top two accessible alternatives;
2. search locally for the nearest environmental perturbation where their optimized fitnesses tie;
3. record the full perturbation vector, not only its scalar distance;
4. use the inverse formula to estimate their relative environmental gradient;
5. verify that independent nearby worldline measurements agree with the reconstructed gradient.

This can reduce the number of dense slope measurements required to characterize the local alternative-envelope geometry.

## Claim ceiling

The inverse formula is exact only for affine pairwise optimized-fitness differences and a correctly specified positive-definite environmental metric. For nonlinear worldlines it is a local tangent approximation only when the observed switch is sufficiently close. Statistical uncertainty in the gap and switch location must be propagated. The result does not infer evolutionary trajectory or PAYOFF frequency dependence.

# BALANCE width-depth bounds v1

## Purpose

Relate the **environmental width** of a finite BALANCE domain to its **maximum two-sided fitness depth**.

Consider a scalar environmental path with boundaries

\[
e_0<e_d<e_2,
\]

where

\[
L(e_0)=0,
\qquad
L(e_d)=\rho(e_d)=d_*,
\qquad
\rho(e_2)=0.
\]

Assume the usual monotone orientation:

\[
L'(e)>0
\]

on the SCH-facing side and

\[
\rho'(e)<0
\]

on the BITA-facing side.

The total environmental width is

\[
W_e=e_2-e_0.
\]

## Slope bounds

Assume on the left segment `[e_0,e_d]`

\[
0<\ell_{\min}\le L'(e)\le\ell_{\max},
\]

and on the right segment `[e_d,e_2]`

\[
0<r_{\min}\le-\rho'(e)\le r_{\max}.
\]

## Theorem 1 — left and right width bounds

Because

\[
d_*=L(e_d)-L(e_0)=\int_{e_0}^{e_d}L'(e)\,de,
\]

we have

\[
\boxed{
\frac{d_*}{\ell_{\max}}
\le e_d-e_0
\le
\frac{d_*}{\ell_{\min}}.
}
\]

Likewise,

\[
d_*=\rho(e_d)-\rho(e_2)
=\int_{e_d}^{e_2}[-\rho'(e)]\,de,
\]

so

\[
\boxed{
\frac{d_*}{r_{\max}}
\le e_2-e_d
\le
\frac{d_*}{r_{\min}}.
}
\]

## Theorem 2 — total BALANCE width bracket

Adding the two sides gives

\[
\boxed{
d_*\left(\frac1{\ell_{\max}}+\frac1{r_{\max}}\right)
\le W_e\le
d_*\left(\frac1{\ell_{\min}}+\frac1{r_{\min}}\right).
}
\]

Equivalently, if width is observed and slope bounds are known,

\[
\boxed{
\frac{W_e}{1/\ell_{\min}+1/r_{\min}}
\le d_*
\le
\frac{W_e}{1/\ell_{\max}+1/r_{\max}}.
}
\]

Thus domain width and maximum fitness robustness constrain one another once the rates at which the two margins change with environment are bounded.

## Corollary 2a — constant-slope exact solution

If

\[
L'(e)=\ell>0,
\qquad
-\rho'(e)=r>0
\]

throughout their respective sides, then

\[
W_e=d_*\left(\frac1\ell+\frac1r\right)
\]

and therefore

\[
\boxed{
d_*=W_e\frac{\ell r}{\ell+r}.}
\]

The maximum fitness reserve equals environmental width multiplied by an effective two-boundary slope.

## Corollary 2b — wide does not necessarily mean deep

For fixed width `W_e`, small boundary slopes imply small `d_*`. A broad BALANCE domain can therefore be fitness-shallow if both margins change slowly with environment.

Conversely, a narrow domain can be fitness-deep if both boundaries are steep.

So two distinct comparative traits of a BALANCE regime are:

```text
environmental extent  W_e
fitness robustness    d_*
```

and neither should be used as a proxy for the other without slope information.

## Corollary 2c — asymmetry of the deepest point

Under constant slopes,

\[
e_d-e_0=\frac{d_*}{\ell},
\qquad
 e_2-e_d=\frac{d_*}{r}.
\]

Hence

\[
\boxed{
\frac{e_d-e_0}{e_2-e_d}=\frac{r}{\ell}.
}
\]

The fitness-deep point is geometrically centered in environmental space only when the two boundary slopes have equal magnitude.

This complements the environmental-distance result: equal fitness margins need not imply equal environmental distances.

## Empirical consequence

Across repeated environments, Chapter 2 can estimate:

- finite domain width `W_e`;
- deepest fitness reserve `d_*`;
- local or conservative slope bounds for `L` and `rho`.

The theorem then supplies internal consistency checks. If observed width and depth violate the slope bracket, at least one fitted margin, boundary, scale match, or monotonicity assumption is inconsistent.

## Claim ceiling

The result assumes one connected finite BALANCE interval and monotone margins on each side of the deepest point. Re-entry, multiple components, or nonregular boundaries require component-wise analysis rather than a single width-depth formula.

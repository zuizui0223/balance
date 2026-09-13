# BALANCE width-depth bounds v1

## Purpose

Relate the **environmental width** of a finite BALANCE domain to its **maximum two-sided fitness depth**.

Consider a scalar environmental path with boundaries `e_0<e_d<e_2`, where

\[
L(e_0)=0,\qquad L(e_d)=\rho(e_d)=d_*,\qquad \rho(e_2)=0.
\]

Assume the usual monotone orientation: `L'(e)>0` on the SCH-facing side and `rho'(e)<0` on the SLK-facing architecture-value side. The total environmental width is `W_e=e_2-e_0`.

## Slope bounds

Assume on `[e_0,e_d]`

\[
0<\ell_{\min}\le L'(e)\le\ell_{\max},
\]

and on `[e_d,e_2]`

\[
0<r_{\min}\le-\rho'(e)\le r_{\max}.
\]

## Theorem 1 — left and right width bounds

Because `d_*=L(e_d)-L(e_0)`,

\[
\boxed{\frac{d_*}{\ell_{\max}}\le e_d-e_0\le\frac{d_*}{\ell_{\min}}}.
\]

Likewise, because `d_*=rho(e_d)-rho(e_2)`,

\[
\boxed{\frac{d_*}{r_{\max}}\le e_2-e_d\le\frac{d_*}{r_{\min}}}.
\]

## Theorem 2 — total BALANCE width bracket

\[
\boxed{d_*\left(\frac1{\ell_{\max}}+\frac1{r_{\max}}\right)\le W_e\le d_*\left(\frac1{\ell_{\min}}+\frac1{r_{\min}}\right)}.
\]

Equivalently,

\[
\boxed{\frac{W_e}{1/\ell_{\min}+1/r_{\min}}\le d_*\le\frac{W_e}{1/\ell_{\max}+1/r_{\max}}}.
\]

Thus domain width and maximum fitness robustness constrain one another once the rates at which the two margins change with environment are bounded.

## Corollary 2a — constant-slope exact solution

If `L'(e)=ell>0` and `-rho'(e)=r>0`, then

\[
W_e=d_*\left(\frac1\ell+\frac1r\right),
\qquad
\boxed{d_*=W_e\frac{\ell r}{\ell+r}}.
\]

## Corollary 2b — wide does not necessarily mean deep

For fixed `W_e`, small boundary slopes imply small `d_*`; a broad BALANCE domain can therefore be fitness-shallow. Conversely, a narrow domain can be fitness-deep if both boundaries are steep. Environmental extent and fitness robustness should not be used as proxies for one another without slope information.

## Corollary 2c — asymmetry of the deepest point

Under constant slopes,

\[
e_d-e_0=\frac{d_*}{\ell},\qquad e_2-e_d=\frac{d_*}{r},
\]

so

\[
\boxed{\frac{e_d-e_0}{e_2-e_d}=\frac{r}{\ell}}.
\]

The fitness-deep point is geometrically centered in environmental space only when the two boundary slopes have equal magnitude.

## Empirical consequence

Across repeated environments, BALANCE can estimate finite domain width `W_e`, deepest fitness reserve `d_*`, and slope bounds for `L` and `rho`. If observed width and depth violate the bracket, at least one fitted margin, boundary, scale match, or monotonicity assumption is inconsistent.

## Claim ceiling

The result assumes one connected finite BALANCE interval and monotone margins on each side of the deepest point. Re-entry, multiple components, or nonregular boundaries require component-wise analysis. The right-hand boundary is the SLK-facing architecture-value boundary; this result does not identify a BITA mechanism.

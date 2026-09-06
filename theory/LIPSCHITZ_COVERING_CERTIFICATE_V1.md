# BALANCE Lipschitz covering certificate v1

## Purpose

Turn a finite environmental sampling design into a rigorous certificate for a continuous BALANCE domain without assuming affine interpolation.

The result is deliberately conservative. It uses only:

- a declared environmental metric;
- a finite sample whose covering radius is known;
- Lipschitz bounds on every status margin.

It therefore supplies a direct bridge from domain geometry to sampling design.

## Setup

Let `E` be a compact environmental domain with metric `d_Q`. BALANCE status is determined by positive margins

\[
f_0(e)=L(e)
\]

and, for registered accessible alternatives,

\[
f_j(e)=\rho_j(e)=W_S^*(e)-W_{D_j}^*(e),\qquad j=1,\ldots,m.
\]

BALANCE at `e` requires

\[
f_k(e)>0\quad\text{for every }k.
\]

Assume each margin is Lipschitz on `E`:

\[
|f_k(e)-f_k(e')|\le K_k d_Q(e,e').
\]

Let the sampled contexts be

\[
S=\{e_1,\ldots,e_N\}.
\]

Define the covering radius

\[
h(S,E)=\sup_{e\in E}\min_{s\in S}d_Q(e,s).
\]

Thus `S` is an `h`-net of `E`.

## Theorem 1 — finite-sample lower certificate for each margin

For any `e in E`, choose a sampled context `s(e)` satisfying

\[
d_Q(e,s(e))\le h.
\]

Lipschitz continuity gives

\[
f_k(e)\ge f_k(s(e))-K_kh.
\]

Since

\[
f_k(s(e))\ge m_k,
\qquad
m_k=\min_{s\in S}f_k(s),
\]

we obtain

\[
\boxed{
\inf_{e\in E}f_k(e)
\ge
m_k-K_kh.
}
\]

This bound requires no interpolation model beyond the registered Lipschitz constant.

## Theorem 2 — whole-domain BALANCE certificate

Define the certified global status margin

\[
\boxed{
\delta_{cert}
=
\min_k\{m_k-K_kh\}.
}
\]

If

\[
\boxed{\delta_{cert}>0,}
\]

then every registered margin is positive at every environmental context in `E`. Therefore

\[
\boxed{E\subseteq\mathcal B}
\]

where `B` is the BALANCE domain for the declared accessibility scope.

Moreover every point has direct fitness depth at least

\[
\boxed{d_F(e)\ge\delta_{cert}.}
\]

Thus a finite sample can certify not just occupancy but a minimum fitness-scale depth over the entire sampled environmental region.

## Corollary 2a — design spacing required for a target certificate

Suppose the observed minimum margin for boundary `k` is `m_k>0`. A sufficient sampling condition for retaining a positive certificate is

\[
\boxed{h<\frac{m_k}{K_k}}
\]

for every status margin.

To guarantee a target global depth `delta_0>0`, require

\[
\boxed{
h\le\min_k\frac{m_k-\delta_0}{K_k}}
\]

for all `k` with `m_k>delta_0`.

This makes environmental sampling density a quantity determined by margin size and environmental sensitivity rather than by an arbitrary number of sites.

## Theorem 3 — fail-closed interpretation of an inconclusive finite grid

If

\[
\delta_{cert}\le0,
\]

no whole-domain conclusion follows. This does **not** imply a boundary crossing exists between samples.

The correct classification is

```text
CONTINUOUS_DOMAIN_NOT_CERTIFIED_AT_REGISTERED_COVERING_RESOLUTION
```

unless an observed sample already crosses a boundary.

Thus the theorem prevents both errors:

- declaring continuous BALANCE merely because every sampled point is positive;
- declaring a hidden crossing merely because the Lipschitz certificate is too weak.

## Corollary — covering-number sample complexity

Let

\[
N(E,h)
\]

denote the metric covering number: the minimum number of radius-`h` balls needed to cover `E`.

Any deterministic design seeking the above certificate needs enough contexts to realize the required covering radius, hence at least the geometry implied by `N(E,h)`.

For a `p`-dimensional rectangular environmental region of characteristic side length `D` under an approximately Euclidean standardized metric, regular-grid covering scales as

\[
\boxed{N=O((D/h)^p).}
\]

Combining with `h < m/K` gives the qualitative scaling

\[
\boxed{N=O((DK/m)^p).}
\]

up to geometry constants.

This exposes a real curse of dimensionality: certifying a continuous middle world becomes rapidly harder as the environmental dimension grows or margins become shallow.

## Uncertain margins

If sampled margins are themselves intervals, use the lower endpoint at each sample:

\[
m_k^{lo}=\min_{s\in S}f_{k,lo}(s).
\]

Then

\[
\boxed{
\inf_E f_k
\ge
m_k^{lo}-K_kh
}
\]

is the fail-closed interval version.

The same logic applies when the Lipschitz constant has a conservative upper bound `K_k^up`.

## Multi-alternative consequence

Because the architecture reserve is the minimum over registered alternatives,

\[
\rho_A(e)=\min_j\rho_j(e),
\]

continuous-domain certification must cover **every nondominated accessible alternative** retained after valid dominance pruning.

Adding a new accessible alternative adds another margin that must pass the covering certificate. It can only weaken or leave unchanged the certified BALANCE region.

## Empirical use

A repeated-context BALANCE study can preregister:

1. environmental metric `Q`;
2. analysis domain `E`;
3. sampling design `S` and computed covering radius `h`;
4. conservative Lipschitz constants for `L` and every retained `rho_j`;
5. sampled lower confidence bounds on all margins.

The output is a continuous-domain certificate rather than a visually interpolated phase map.

## Claim ceiling

The guarantee is only as valid as the Lipschitz bounds, environmental metric, registered accessibility scope and covering-radius calculation. A small sample can still certify a domain if the margins are deep and slowly varying; a dense sample may remain inconclusive if margins are shallow or highly sensitive. The theorem concerns static BALANCE geometry, not switching history or PAYOFF frequency dependence.
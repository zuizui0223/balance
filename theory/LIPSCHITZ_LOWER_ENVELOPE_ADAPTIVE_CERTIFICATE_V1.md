# BALANCE adaptive Lipschitz lower-envelope certificate v1

## Purpose

Strengthen the coarse covering-radius certificate by using the exact information contributed by every sampled context.

A sampled value of a Lipschitz margin creates a lower cone over environmental space. The pointwise maximum of all such cones is the strongest lower bound obtainable from those one-sided Lipschitz inequalities alone. This lower envelope improves monotonically as samples are added and therefore supplies a principled adaptive sampling target.

## Setup

Let a BALANCE status margin `f(e)` be `K`-Lipschitz in the registered environmental metric `d_Q`:

\[
|f(e)-f(s)|\le K d_Q(e,s).
\]

For sampled contexts

\[
S=\{s_1,\ldots,s_N\}
\]

with observed or lower-confidence values `f(s_i)`, define the sample-cone lower envelope

\[
\boxed{
\underline f_S(e)
=
\max_{s\in S}
\left[f(s)-K d_Q(e,s)\right].
}
\]

## Theorem 1 — lower-envelope validity

For every sample `s`, Lipschitz continuity gives

\[
f(e)\ge f(s)-K d_Q(e,s).
\]

Taking the maximum over all samples preserves the inequality:

\[
\boxed{
f(e)\ge\underline f_S(e)\quad\forall e.}
\]

Thus `underline f_S` is a rigorous pointwise lower certificate for the unknown continuous margin.

## Theorem 2 — the cone envelope dominates the coarse covering-radius bound

Let the sample covering radius be `h` and

\[
m_S=\min_{s\in S}f(s).
\]

For every `e`, choose a sample `s_e` with `d(e,s_e)<=h`. Then

\[
\underline f_S(e)
\ge
f(s_e)-Kh
\ge
m_S-Kh.
\]

Therefore

\[
\boxed{
\inf_e\underline f_S(e)
\ge
m_S-Kh.
}
\]

The lower-cone method is never weaker than the global `min(sample)-Kh` certificate and can be substantially stronger when sample values vary across the domain.

## Theorem 3 — adding samples can only improve the certified lower surface

If `S subset T`, then the maximum defining the envelope is taken over a larger set for `T`, so

\[
\boxed{
\underline f_T(e)\ge\underline f_S(e)
\quad\forall e.
}
\]

Hence the global certified minimum

\[
\delta_S=\inf_{e\in E}\underline f_S(e)
\]

obeys

\[
\boxed{
\delta_T\ge\delta_S.
}
\]

This monotonicity is useful because the coarse bound `min(sample)-Kh` need not improve when a new sample reveals a lower local margin. The cone envelope absorbs that observation without losing any previously valid Lipschitz information.

## Multi-margin BALANCE certificate

For status margins

\[
f_0=L,
\qquad
f_j=\rho_j,
\]

build one lower envelope per margin:

\[
\underline f_{k,S}(e).
\]

Define

\[
\boxed{
\underline d_{B,S}(e)
=
\min_k\underline f_{k,S}(e).
}
\]

Then

\[
d_F(e)=\min_kf_k(e)
\ge
\underline d_{B,S}(e).
\]

A whole-domain certificate follows if

\[
\boxed{
\inf_{e\in E}\underline d_{B,S}(e)>0.
}
\]

## Theorem 4 — natural adaptive next-sample target

Let

\[
e^*\in\operatorname*{argmin}_{e\in E}\underline d_{B,S}(e)
\]

be a context where the current continuous-domain certificate is weakest.

Sampling at `e*` is a **maximin certificate-refinement** step: it directly interrogates one of the contexts limiting the current guaranteed lower depth.

After observing the new margin values and adding their cones, the certified surface cannot decrease by Theorem 3. If the new observations lie well above the previous lower envelope, the bottleneck can move elsewhere; if they lie near it, the design has localized a genuinely shallow region.

The theorem does not claim this greedy strategy is globally sample-count optimal. It identifies the current certificate bottleneck without requiring a parametric interpolation model.

## Corollary — boundary-focused sampling emerges automatically

Deep interior samples often generate cones that remain above zero over broad neighborhoods and cease to be limiting. As the certificate improves, minimizers of `underline d_B,S` tend to concentrate near:

- poorly covered regions;
- shallow SCH conflict margins;
- shallow alternative-worldline reserves;
- intersections where several boundaries are simultaneously close.

Thus adaptive design naturally shifts effort toward candidate critical regions rather than continuing uniform sampling after deep regions are already certified.

## Relation to McShane/Whitney Lipschitz extension geometry

The lower envelope

\[
\max_s[f(s)-Kd(e,s)]
\]

is the canonical maximal lower bound implied by individual Lipschitz cones from the samples. No smoothness, affine interpolation or Gaussian-process prior is required.

This makes the certificate suitable as a fail-closed baseline even when a richer statistical spatial model is used for estimation.

## Uncertainty

If each sampled margin has a lower confidence endpoint `f_lo(s)`, replace `f(s)` by `f_lo(s)` in every cone. If the Lipschitz constant is uncertain, use a prospectively justified upper bound `K_up`.

The resulting envelope remains a conservative lower certificate.

## Empirical consequence

A repeated-context BALANCE programme can run sequentially:

```text
initial coarse environmental cover
-> compute lower-cone envelopes for L and every retained rho_j
-> find the weakest certified context
-> sample there
-> update envelopes
-> stop when the preregistered continuous-domain criterion is reached
   or when the data identify a boundary crossing
```

This turns Chapter 2 environmental mapping into a certificate-driven design rather than a fixed dense grid.

## Claim ceiling

Monotone improvement concerns the mathematical lower certificate, not the true unknown margin. The adaptive rule is not claimed globally optimal in number of samples. Its validity requires the registered metric and Lipschitz constants to remain valid over the whole domain and the accessibility scope to remain fixed. Static BALANCE geometry remains separate from historical switching and PAYOFF dynamics.
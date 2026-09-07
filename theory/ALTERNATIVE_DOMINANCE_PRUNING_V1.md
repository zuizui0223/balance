# BALANCE alternative-dominance pruning theorem v1

## Purpose

Reduce a large set of candidate alternative architectures without changing the BALANCE classification or its architecture envelope.

Once Chapter 2 allows multiple alternatives, not every registered alternative needs to remain in every calculation. Some are pointwise dominated by another alternative and can never define the upper competing worldline.

## Setup

For shared world `S` and alternatives `D_i`, define

\[
\rho_i(e)=W_S^*(e)-W_{D_i}^*(e).
\]

The architecture envelope reserve is

\[
\rho_A(e)=\min_i\rho_i(e).
\]

Consider a declared environmental domain `E`.

## Theorem 1 — pointwise dominated alternatives can be removed

Suppose alternatives `i` and `j` satisfy

\[
\boxed{
W_{D_i}^*(e)\le W_{D_j}^*(e)
\quad\text{for every }e\in E.
}
\]

Equivalently,

\[
\boxed{
\rho_i(e)\ge\rho_j(e)
\quad\text{for every }e\in E.
}
\]

Then `D_i` can never exceed `D_j` on the alternative envelope. Removing `D_i` leaves

\[
\max_kW_{D_k}^*(e)
\]

and therefore

\[
\rho_A(e)
\]

unchanged for every `e in E`.

Hence all BALANCE state calls, architecture crossings and envelope-based fitness depths are unchanged.

## Corollary 1a — strict dominance excludes threat activity

If

\[
W_{D_i}^*(e)<W_{D_j}^*(e)
\]

for every `e in E`, then `D_i` is never an active threatening architecture:

\[
i\notin A_D(e)
\quad\text{for all }e\in E.
\]

So strictly dominated alternatives may be removed before threat-switch or boundary-topology analysis.

## Theorem 2 — pruning is transitive

If `D_i` is dominated by `D_j`, and `D_j` is dominated by `D_k` over the same domain, then

\[
W_{D_i}^*\le W_{D_j}^*\le W_{D_k}^*
\]

and `D_i` is dominated by `D_k`.

Therefore the alternative set can be reduced to its pointwise nondominated envelope candidates.

The retained set is not necessarily unique if two alternatives are exactly tied over part or all of the domain, but the resulting envelope is unique.

## Theorem 3 — sampled dominance is weaker than domain dominance

If dominance is observed only at sampled contexts

\[
e_1,\ldots,e_m,
\]

then the valid conclusion is only

```text
D_i is dominated on the registered sample grid.
```

Without a model that controls behavior between samples, this does not prove pointwise dominance over the continuous environmental domain.

Thus sampled pruning is safe only for analyses explicitly restricted to the sampled contexts. Continuous-domain pruning requires either:

- direct analytic dominance;
- interval/shape constraints that guarantee no crossing between samples;
- a prospectively registered interpolation/model class with uncertainty.

## Corollary 3a — affine alternatives can be audited at polytope vertices

Suppose the pairwise difference

\[
W_{D_j}^*(e)-W_{D_i}^*(e)
\]

is affine in `e`, and the declared environmental domain `E` is a compact polytope.

An affine function attains its minimum on a polytope at a vertex. Therefore

\[
W_{D_i}^*(e)\le W_{D_j}^*(e)
\quad\forall e\in E
\]

is certified by checking the inequality at every vertex of `E`.

This supplies an exact finite pruning test for affine worldline models on polyhedral domains.

## Biological interpretation

The theorem formalizes a useful distinction:

```text
registered alternative
!=
active alternative
```

A biologically plausible architecture can remain in the accessibility registry while being mathematically irrelevant to the current domain because another architecture outperforms it everywhere.

Pruning therefore simplifies the Chapter-2 phase diagram without changing the scientific accessibility statement.

It also highlights why alternative-worldline scope matters: adding a newly discovered nondominated architecture can change the envelope and invalidate a previous BALANCE call, whereas adding a dominated architecture cannot.

## Empirical consequence

A multi-alternative BALANCE analysis should report:

1. the full registered biologically accessible alternative set;
2. the subset proven or assumed pointwise dominated over the analysis domain;
3. the retained nondominated envelope candidates;
4. where the identity of the active threat changes.

This separates biological accessibility from mathematical envelope relevance.

## Claim ceiling

Dominance is domain-specific. An architecture dominated in one environmental range can become active outside it. Pruning based on point estimates without uncertainty can be unsafe near ties. PAYOFF invasion or frequency effects can also change population success even when one static optimized worldline is lower, so this theorem remains purely Chapter-2 static geometry.

# BALANCE auxiliary threat-label identification theorem v1

## Purpose

State when architecture identity can be recovered after the static optimized-fitness envelope has been identified.

The envelope observational-equivalence theorem shows that optimized fitness identifies the best-accessible alternative envelope but not necessarily a unique architecture label. The present theorem describes the minimal extra information needed to separate tied or envelope-equivalent alternatives.

## Setup

At context `e`, let the registered active threat set be

\[
T(e)=\operatorname*{arg\,max}_{j\in A}W_{D_j}^*(e).
\]

For each registered alternative `j`, suppose there is an auxiliary observable

\[
h_j(e)\in\mathcal H
\]

measured on the same context and interpreted independently of optimized total fitness. Examples can include a structural marker, loading pattern, developmental state or intervention-specific mechanism readout.

Let the observed auxiliary value of the realized alternative be `h_obs(e)`.

## Theorem 1 — unique active threat from the envelope

If

\[
|T(e)|=1,
\]

then the optimized-fitness registry itself identifies the unique active threat label, conditional on the registered candidate set and valid worldline matching.

No auxiliary observable is mathematically required for label identification at that context, although mechanism claims can still require it biologically.

## Theorem 2 — tie-breaking by an injective auxiliary code

Suppose

\[
|T(e)|>1.
\]

If the auxiliary map is injective on the tied threat set,

\[
j\neq k\in T(e)
\Rightarrow
h_j(e)\neq h_k(e),
\]

and the observed auxiliary value equals one registered code,

\[
h_{obs}(e)=h_{j^*}(e),
\]

then

\[
\boxed{j^*\text{ is uniquely identified within }T(e).}
\]

Thus architecture identity can be recovered by combining the envelope-defined candidate set with a label-separating auxiliary measurement.

## Theorem 3 — partial identification under a noninjective auxiliary code

If several tied threats share the observed auxiliary value, define

\[
T_h(e)=
\{j\in T(e):h_j(e)=h_{obs}(e)\}.
\]

Then the architecture label is identified only to the subset

\[
\boxed{T_h(e).}
\]

No inference using only the envelope and that auxiliary observable can select one member of `T_h` without additional information.

This is a second partial-identification layer nested inside accessibility uncertainty.

## Theorem 4 — an auxiliary variable that is a function of the envelope cannot break envelope equivalence

Suppose the auxiliary observable has the form

\[
h_j(e)=q(W_A^*(e),W_S^*(e),L(e))
\]

for every active alternative `j`, so it depends only on already identified envelope quantities and not on architecture identity.

Then all tied threats receive the same auxiliary value and the observable cannot reduce the active threat set.

Therefore a genuinely separating auxiliary measurement must contain information **not factorizable through the static envelope observables**.

## Corollary — mechanism evidence must be orthogonal to envelope-only evidence

Repeating or transforming the same optimized total-fitness comparison cannot, by itself, resolve an architecture-label tie. Useful mechanism measurements must interrogate a different aspect of the biological system.

This formalizes why Chapter 2 can identify state and reserve directly while stronger claims about what architecture realizes the alternative require structural or mechanism-specific evidence.

## Empirical consequence

A final BALANCE receipt can report:

```text
1. registered accessible alternatives
2. active threat set from optimized-fitness envelope
3. auxiliary label code, if available
4. unique / subset / unresolved threat identity
5. BALANCE state and reserve separately from label certainty
```

State identification need not be discarded merely because architecture identity is unresolved. Conversely, a clean architecture label does not establish BALANCE unless the same-context worldline inequality is also identified.

## Example

Suppose `D1` and `D2` tie at the envelope:

\[
W_{D_1}^*=W_{D_2}^*=2.0.
\]

If a structural assay gives

\[
h_{D_1}=\text{retained},
\qquad
h_{D_2}=\text{drained},
\]

and the realized alternative is observed as `retained`, then `D1` is uniquely identified within the tied threat set.

If both alternatives are `retained` under the assay, the label remains unresolved between `D1` and `D2` despite exact knowledge of the fitness envelope.

## Claim ceiling

The theorem is conditional on the registered candidate set, valid architecture-specific auxiliary codes and context matching. It identifies labels within the active threat set, not unregistered alternatives or historical accessibility. Frequency-dependent invasion remains outside BALANCE and belongs to PAYOFF.
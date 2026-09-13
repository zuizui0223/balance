# BALANCE accessibility-scope partial-identification theorem v1

## Purpose

Turn uncertainty about which alternative architectures are biologically accessible into rigorous inner and outer bounds on the BALANCE domain.

## Setup

Let `A_def` be alternatives definitely accessible, `A_true` the unknown true accessible set, and `A_poss` alternatives plausibly accessible under the registered biological scope, with

\[
A_{def}\subseteq A_{true}\subseteq A_{poss}.
\]

For any alternative set `A`, define

\[
B_A=\{e:L(e)>0,\ W_S^*(e)>\max_{j\in A}W_{D_j}^*(e)\}.
\]

Accessibility-scope monotonicity gives `A subset A' => B_A' subset B_A`.

## Theorem 1 — partial-identification sandwich

\[
\boxed{B_{A_{poss}}\subseteq B_{A_{true}}\subseteq B_{A_{def}}}.
\]

Thus `B_Aposs` is a robust inner BALANCE domain, `B_Adef` is an optimistic outer BALANCE domain, and the true domain lies between them.

## Corollary 1a — three-way context classification

For any context with positive conflict:

- **ROBUST_BALANCE** if `e in B_Aposs`;
- **ROBUST_NON_BALANCE** if `e notin B_Adef`;
- **ACCESSIBILITY_SCOPE_UNRESOLVED** if `e in B_Adef \ B_Aposs`.

The third state is fail-closed: classification depends on whether one or more merely possible alternatives are actually accessible.

## Theorem 2 — reserve interval

Define

\[
\rho_{def}=W_S^*-\max_{j\in A_{def}}W_{D_j}^*,
\qquad
\rho_{poss}=W_S^*-\max_{j\in A_{poss}}W_{D_j}^*.
\]

Then

\[
\boxed{\rho_{poss}\le\rho_{true}\le\rho_{def}}.
\]

Accessibility uncertainty therefore propagates directly into an interval for the **SLK-facing architecture-value reserve**. The corresponding fitness-depth interval is

\[
\boxed{\min(L,\rho_{poss})\le d_{true}\le\min(L,\rho_{def})}.
\]

## Theorem 3 — robust inner domain equals the union-scope comparison

For a family of admissible accessibility sets `mathcal A`, let

\[
A_{union}=\bigcup_{A\in\mathcal A}A.
\]

Then

\[
\boxed{\bigcap_{A\in\mathcal A}B_A=B_{A_{union}}}.
\]

Thus robust BALANCE identification does not require enumeration of every accessibility scenario separately; it is enough to compare the shared world against every alternative appearing in any admissible scenario.

If the admissible family contains a smallest set `A_min`, then

\[
\boxed{\bigcup_{A\in\mathcal A}B_A=B_{A_{min}}}.
\]

## Biological interpretation

```text
worldline uncertainty != accessibility uncertainty
```

Worldline uncertainty concerns fitness estimates for a fixed architecture set. Accessibility uncertainty concerns whether an architecture belongs in the comparison at all. Both can be bounded, but they should not be silently mixed.

## Empirical consequence

A BALANCE receipt can carry definitely accessible alternatives, plausibly accessible alternatives, direct worldline intervals for each, and robust/unresolved/non-BALANCE classification. This allows positive statements without pretending that the full architecture possibility space is known.

## Claim ceiling

The result is set-theoretic and conditional on declared accessibility bounds. If a biologically possible architecture is omitted even from `A_poss`, the robust inner domain may still be too large. Static accessibility is also distinct from frequency-dependent invasion ability: in the closed programme that is a **SLK process-level question**, not a BITA mechanism-identification result.

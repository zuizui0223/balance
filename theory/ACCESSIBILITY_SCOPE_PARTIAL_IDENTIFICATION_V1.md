# BALANCE accessibility-scope partial-identification theorem v1

## Purpose

Turn uncertainty about which alternative architectures are biologically accessible into rigorous inner and outer bounds on the BALANCE domain.

## Setup

Let

- `A_def` = alternatives definitely accessible;
- `A_true` = the unknown true accessible set;
- `A_poss` = alternatives plausibly accessible under the registered biological scope.

Assume

\[
A_{def}\subseteq A_{true}\subseteq A_{poss}.
\]

For any alternative set `A`, define

\[
B_A=\{e:L(e)>0,\ W_S^*(e)>\max_{j\in A}W_{D_j}^*(e)\}.
\]

The accessibility-scope monotonicity theorem gives

\[
A\subseteq A'\Rightarrow B_{A'}\subseteq B_A.
\]

## Theorem 1 — partial-identification sandwich

Applying set monotonicity twice,

\[
\boxed{
B_{A_{poss}}
\subseteq
B_{A_{true}}
\subseteq
B_{A_{def}}.
}
\]

Thus:

- `B_Aposs` is a **robust inner BALANCE domain**: every plausible alternative is beaten by the shared world;
- `B_Adef` is an **optimistic outer BALANCE domain**: only definitely accessible alternatives have been required to lose;
- the true domain lies between them.

## Corollary 1a — three-way context classification

For any context `e` with positive conflict:

### Robust BALANCE

If

\[
e\in B_{A_{poss}},
\]

then `e` is BALANCE for every admissible true accessibility set satisfying the registered bounds.

### Robust non-BALANCE

If

\[
e\notin B_{A_{def}},
\]

then at least one definitely accessible alternative already matches or beats the shared world, so `e` cannot be BALANCE for any admissible true set.

### Scope-unresolved

If

\[
e\in B_{A_{def}}\setminus B_{A_{poss}},
\]

then the state depends on whether one or more merely possible alternatives are actually accessible.

Hence the accessibility uncertainty itself generates a fail-closed state:

```text
ROBUST_BALANCE
ROBUST_NON_BALANCE
ACCESSIBILITY_SCOPE_UNRESOLVED
```

## Theorem 2 — reserve interval

Define envelope reserves

\[
\rho_{def}=W_S^*-\max_{j\in A_{def}}W_{D_j}^*,
\]

\[
\rho_{poss}=W_S^*-\max_{j\in A_{poss}}W_{D_j}^*.
\]

Then

\[
\boxed{
\rho_{poss}
\le
\rho_{true}
\le
\rho_{def}.
}
\]

So accessibility uncertainty propagates directly into an interval for the BITA-facing BALANCE reserve.

The corresponding fitness-depth interval satisfies

\[
\boxed{
\min(L,\rho_{poss})
\le
d_{true}
\le
\min(L,\rho_{def}).
}
\]

## Theorem 3 — robust inner domain equals the union-scope comparison

Suppose uncertainty is represented by a family of admissible accessibility sets

\[
\mathcal A.
\]

Let

\[
A_{union}=\bigcup_{A\in\mathcal A}A.
\]

A context is BALANCE under **every** admissible accessibility set iff it is BALANCE against the union scope:

\[
\boxed{
\bigcap_{A\in\mathcal A}B_A
=
B_{A_{union}}.
}
\]

Thus robust BALANCE identification does not require enumerating every accessibility scenario separately. It is enough to compare the shared world against every alternative that appears in any admissible scenario.

## Corollary 3a — nested-scope outer domain

If the admissible family contains a smallest set

\[
A_{min}\subseteq A
\quad\forall A\in\mathcal A,
\]

then

\[
\boxed{
\bigcup_{A\in\mathcal A}B_A
=
B_{A_{min}}.
}
\]

So the smallest admissible accessibility scope gives the maximal possible BALANCE domain.

## Biological interpretation

This theorem makes an important distinction explicit:

```text
worldline uncertainty
!=
accessibility uncertainty
```

Worldline uncertainty concerns fitness estimates for a fixed architecture set. Accessibility uncertainty concerns whether an architecture belongs in the comparison at all.

Both can be bounded, but they should not be silently mixed.

## Empirical consequence

A Chapter-2 receipt can carry:

- definitely accessible alternatives;
- plausibly accessible alternatives;
- direct worldline intervals for each;
- robust / unresolved / non-BALANCE classification.

This lets comparative studies make positive statements without pretending the full architecture possibility space is known.

## Claim ceiling

The result is set-theoretic and conditional on the declared accessibility bounds. If a biologically possible architecture is omitted even from `A_poss`, the robust inner domain may still be too large. Static accessibility is also distinct from frequency-dependent invasion ability, which belongs to PAYOFF.

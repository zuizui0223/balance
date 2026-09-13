# BALANCE accessibility-envelope observational-equivalence theorem v1

## Purpose

State exactly what static Chapter-2 worldline data can identify about a registry of accessible alternative architectures.

BALANCE already uses the best accessible alternative envelope

\[
W_A^*(e)=\max_{j\in A}W_{D_j}^*(e)
\]

rather than any single alternative in isolation. This theorem shows that the envelope is also the **maximal static object identifiable from shared-vs-alternative optimized-fitness comparisons** unless architecture identity is measured separately.

## Setup

Fix an environmental domain `E`, a shared optimized worldline

\[
W_S^*(e),
\]

and an accessible-alternative registry `A` with optimized alternative worldlines

\[
\{W_{D_j}^*(e):j\in A\}.
\]

Define

\[
W_A^*(e)=\max_{j\in A}W_{D_j}^*(e),
\qquad
\rho_A(e)=W_S^*(e)-W_A^*(e).
\]

The BALANCE state for that registry is

\[
L(e)>0,
\qquad
\rho_A(e)>0.
\]

## Theorem 1 — full static envelope observational equivalence

Two registered alternative families `A` and `B` are **static-envelope observationally equivalent on `E`** iff

\[
\boxed{
W_A^*(e)=W_B^*(e)
\quad\forall e\in E.
}
\]

Under fixed `W_S*` and `L`, this is equivalent to

\[
\boxed{
\rho_A(e)=\rho_B(e)
\quad\forall e\in E.
}
\]

and therefore implies equality of all envelope-derived Chapter-2 quantities on `E`, including:

- BALANCE/non-BALANCE state;
- architecture reserve `rho`;
- direct fitness depth `min(L,rho)`;
- architecture-crossing locations;
- envelope kinks as functions of optimized fitness, though not necessarily their latent architecture labels.

Thus static optimized-fitness data identify the alternative **upper envelope**, not a unique decomposition of that envelope into named architectures.

## Corollary 1a — dominated alternatives are observationally silent

Adding an alternative `D_new` satisfying

\[
W_{D_{new}}^*(e)\le W_A^*(e)
\quad\forall e\in E
\]

leaves the envelope unchanged and is therefore observationally silent for all static BALANCE quantities.

This recovers the dominance-pruning theorem as an observational-equivalence statement.

## Corollary 1b — different registries can generate the same Chapter-2 geometry

Two registries can differ in:

- the number of candidate architectures;
- biological labels;
- dominated worldlines;
- latent worldline decomposition;

while producing the same `W_A*` and therefore the same static BALANCE geometry.

Consequently, the statement

```text
this is the unique alternative architecture causing the BALANCE boundary
```

requires evidence beyond the envelope itself.

## Theorem 2 — binary state equivalence is weaker than envelope equivalence

Suppose two registries produce the same BALANCE/non-BALANCE classification at every context but different positive reserves inside the BALANCE domain.

Then they are **state-equivalent** but not envelope-equivalent.

Therefore observing only the sign of

\[
\rho_A
\]

cannot identify:

- reserve magnitude;
- depth `d_B`;
- nearest threat strength;
- boundary sensitivity away from the zero set.

Direct optimized-fitness values contain strictly more information than state labels alone.

## Theorem 3 — architecture identity is only partially identified on ties

Define the active threat set

\[
T_A(e)=\operatorname*{arg\,max}_{j\in A}W_{D_j}^*(e).
\]

If `T_A(e)` is a singleton, the envelope identifies the active alternative **conditional on the registered candidate set and correctly matched worldlines**.

If several alternatives tie,

\[
|T_A(e)|>1,
\]

then the envelope identifies only the tied threat set. No static optimized-fitness comparison can select one tied member as the unique causal threat without additional architecture-specific information.

A threat-identity switch can therefore be identifiable as a change in the active set even when the exact biological mechanism behind a tied segment remains unresolved.

## Theorem 4 — finite-sample envelope equivalence is only grid-local

For sampled contexts

\[
E_m=\{e_1,\ldots,e_m\},
\]

equality

\[
W_A^*(e_k)=W_B^*(e_k)
\quad k=1,\ldots,m
\]

establishes observational equivalence only on the registered sample grid.

Continuous-domain equivalence requires one of the already registered extensions:

- analytic equality;
- affine/shape restrictions;
- Lipschitz covering certificates;
- interval/uncertainty bounds sufficient to rule out an unsampled envelope crossing.

Thus sampled agreement should never be silently promoted to continuous-domain registry equivalence.

## Theorem 5 — scope expansion is distinguishable only when it pierces the envelope

Let `A subseteq A'`.

The enlarged registry changes static Chapter-2 predictions on `E` iff at least one newly added alternative satisfies

\[
W_{D_{new}}^*(e)>W_A^*(e)
\]

at some context in `E`.

If no added alternative pierces the old envelope, the two scopes are observationally equivalent despite different accessibility registries.

This sharpens accessibility-scope monotonicity: scope expansion can only shrink BALANCE, but it shrinks it **only through envelope-piercing additions**.

## Empirical consequence

A BALANCE evidence package should distinguish three objects:

```text
biological accessibility registry
    = which alternatives are considered possible
static alternative envelope
    = what optimized-fitness comparisons identify directly
architecture identity / mechanism
    = requires alternative-specific causal or structural evidence
```

This prevents two opposite errors:

1. treating a dominated registered architecture as if it altered the Chapter-2 state;
2. treating an observed envelope as if it uniquely identified the architecture generating it.

## Theory -> causal bridge

The theorem gives a direct reason for architecture-specific final causal work.

Worldline comparisons can identify `W_A*`, `rho`, state and depth. But if several biological architectures are observationally envelope-equivalent, mechanism assays or structural interventions are required to decide **which architecture actually realizes the accessible alternative**.

For Pedicularis, the final direct receipt therefore remains about same-context optimized shared versus registered alternative worldlines; any stronger structural claim needs its own evidence lane.

## Claim ceiling

This theorem is conditional on the declared environmental domain, candidate registry and fitness scale. It concerns static optimized worldlines. It does not identify unregistered alternatives, population invasion, frequency dependence or historical accessibility. PAYOFF remains separate.
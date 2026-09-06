# BALANCE accessibility-scope monotonicity theorem v1

## Purpose

Formalize how the BALANCE domain changes when the registered set of biologically accessible alternative architectures is expanded or restricted.

This matters because Chapter 2 compares the shared world against the **best accessible alternative**. A narrow alternative registry can therefore make the middle world look larger than it really is.

## Setup

Let `A` be a registered set of accessible alternatives. Define

\[
W_A^*(e)=\max_{j\in A}W_{D_j}^*(e),
\qquad
\rho_A(e)=W_S^*(e)-W_A^*(e).
\]

The corresponding BALANCE set is

\[
B_A=\{e:L(e)>0,\ \rho_A(e)>0\}.
\]

Its direct fitness depth is

\[
d_A(e)=\min\{L(e),\rho_A(e)\}.
\]

## Theorem 1 — adding accessible alternatives can only reduce reserve

If

\[
A\subseteq A',
\]

then the maximization is over a larger set, so

\[
W_{A'}^*(e)\ge W_A^*(e)
\]

for every context `e`. Therefore

\[
\boxed{\rho_{A'}(e)\le\rho_A(e).}
\]

Thus registering more accessible alternative architectures can never make the shared world look safer on the static worldline comparison.

## Theorem 2 — BALANCE domains are nested downward with accessibility scope

From the reserve ordering,

\[
\rho_{A'}(e)>0
\Rightarrow
\rho_A(e)>0.
\]

Hence

\[
\boxed{B_{A'}\subseteq B_A.}
\]

Adding accessible alternatives can:

- leave a BALANCE call unchanged;
- shrink the BALANCE region;
- eliminate BALANCE at some contexts.

It cannot create a new static BALANCE context that was absent under the smaller alternative set.

## Corollary 2a — incomplete alternative scope is optimistic

If the true accessible set is `A_true` but analysis uses only

\[
A_{obs}\subset A_{true},
\]

then

\[
B_{true}\subseteq B_{obs}.
\]

Therefore a BALANCE domain estimated from an incomplete alternative registry is an **outer bound** on the true static middle world.

A positive BALANCE call under incomplete scope is provisional; a negative call is more robust to adding alternatives.

## Theorem 3 — direct fitness depth is non-increasing with scope

For every context,

\[
\boxed{d_{A'}(e)\le d_A(e).}
\]

because `L` is unchanged while `rho` can only fall.

Consequently, the maximum achievable direct fitness depth also obeys

\[
\boxed{
\sup_e d_{A'}(e)
\le
\sup_e d_A(e).
}
\]

So broadening accessibility scope cannot increase the claimed robustness of the middle world.

## Theorem 4 — dominance-pruned expansions leave BALANCE unchanged

Suppose every newly added alternative in `A'\\A` is pointwise dominated over the declared environmental domain by an alternative already in `A`.

Then the upper architecture envelope does not change, so

\[
\boxed{
W_{A'}^*=W_A^*,\quad
\rho_{A'}=\rho_A,\quad
B_{A'}=B_A,\quad
d_{A'}=d_A.
}
\]

Thus the accessibility-scope theorem and the dominance-pruning theorem fit together cleanly:

```text
add nondominated alternative -> domain may shrink
add dominated alternative    -> no mathematical change
remove dominated alternative -> safe pruning
remove nondominated alternative -> potentially optimistic bias
```

## Corollary 4a — threat-discovery sequence

Consider a sequence of increasingly complete registries

\[
A_1\subseteq A_2\subseteq\cdots\subseteq A_m.
\]

Then the estimated domains form a nested sequence

\[
\boxed{
B_{A_1}\supseteq B_{A_2}\supseteq\cdots\supseteq B_{A_m}.
}
\]

This provides a useful convergence diagnostic for comparative work: if domain calls stabilize as newly audited alternatives are added, remaining scope uncertainty is becoming less consequential.

## Empirical consequence

Chapter 2 should distinguish:

1. **registered accessibility scope** — alternatives considered biologically available;
2. **nondominated envelope scope** — alternatives that can actually define the static competitor envelope;
3. **scope-completeness uncertainty** — plausible but unaudited alternatives.

A strong BALANCE claim should survive reasonable expansion of the registered accessibility set, not merely one chosen differentiated comparison.

## Claim ceiling

The theorem is conditional on a fixed definition of static optimized fitness and on alternatives being compared in the same context and fitness scale. Adding an alternative can also motivate revising the biological state space itself; that is a model-redefinition issue rather than the set-inclusion result above. Frequency-dependent invasion or coexistence remains PAYOFF territory.

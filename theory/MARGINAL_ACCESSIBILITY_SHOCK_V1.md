# BALANCE marginal accessibility shock theorem v1

## Purpose

Give an exact pointwise formula for how much a BALANCE state's bottleneck depth changes when **one newly admitted accessible alternative architecture** is added to an existing registry.

Scope monotonicity establishes direction. This theorem gives magnitude.

## Setup

At one fixed matched context `e`, let the old accessibility scope have envelope reserve

\[
\rho_A=\min_{j\in A}\rho_j.
\]

Let the SCH-facing conflict margin be `L`, and define the old signed bottleneck margin

\[
m_A=\min\{L,\rho_A\}.
\]

When `L>0` and `rho_A>0`, this equals the direct BALANCE fitness depth.

Now add one new accessible alternative `k` with reserve

\[
r=\rho_k.
\]

The expanded scope is `B=A union {k}`.

## Theorem 1 — exact one-alternative update

The new envelope reserve is

\[
\rho_B=\min\{\rho_A,r\}.
\]

Therefore the new signed bottleneck is

\[
\boxed{
m_B=\min\{m_A,r\}.}
\]

The exact loss of bottleneck margin is

\[
\boxed{
\Delta_{scope}(e)
=m_A-m_B
=\max\{0,m_A-r\}.
}
\]

No optimization or approximation is needed at a fixed context.

## Corollary 1a — three biological cases

For an old BALANCE context (`m_A>0`):

1. **irrelevant addition**
   \[
   r\ge m_A
   \]
   gives `Delta_scope=0`;

2. **depth-reducing but still BALANCE**
   \[
   0<r<m_A
   \]
   gives
   \[
   m_B=r>0,
   \quad
   \Delta_{scope}=m_A-r;
   \]

3. **state-destroying alternative**
   \[
   r\le0
   \]
   makes the expanded scope non-BALANCE at that context.

Thus a new alternative matters only when its reserve falls below the old bottleneck.

## Corollary 1b — exact binding criterion

The new alternative becomes the new pointwise bottleneck iff

\[
\boxed{r<m_A.}
\]

At equality it ties the old bottleneck without changing depth.

This cleanly separates biological accessibility from mathematical relevance.

## Theorem 2 — sequential additions telescope

Suppose alternatives are added one at a time with reserves `r_1,...,r_q`. Then

\[
m_q=\min\{m_0,r_1,\ldots,r_q\}.
\]

The cumulative depth loss is

\[
\boxed{
m_0-m_q
=
\sum_{t=1}^q(m_{t-1}-m_t),}
\]

where each increment is

\[
m_{t-1}-m_t
=
\max\{0,m_{t-1}-r_t\}.
\]

Only record-low reserves along the declared addition order generate a positive marginal shock.

The final depth is order-invariant even though the sequence of marginal shocks depends on the chosen order.

## Metric analogue

At one context, under one fixed environmental metric and valid signed inward local/affine distance representation, let `q_A>0` be the old local metric bottleneck and let `q_k` be the signed normalized distance to the newly added architecture boundary.

Then the expanded local bottleneck is exactly

\[
\boxed{q_B=\min\{q_A,q_k\}}
\]

and the local metric-depth shock is

\[
\boxed{
\Delta_Q=\max\{0,q_A-q_k\}.
}
\]

This is pointwise. The **global** Chebyshev incenter may relocate after the scope changes, so global inradius loss is not generally equal to the shock computed at the old incenter.

## Scope-fragility profile

For a set of candidate alternatives not yet admitted, define each alternative's pointwise fragility score

\[
F_k(e)=\max\{0,m_A(e)-\rho_k(e)\}.
\]

This ranks which unregistered candidate architecture would most reduce the current direct depth if admitted, while keeping all worldlines fixed.

A high score does not prove biological accessibility; it identifies where accessibility adjudication matters most for the Chapter-2 state call.

## Empirical consequence

A BALANCE analysis can report, for every candidate alternative:

- its reserve relative to the shared worldline;
- whether it is irrelevant, depth-reducing, or state-destroying;
- the exact pointwise depth shock if admitted;
- environmental contexts where it first becomes binding.

This turns alternative-scope sensitivity from a list of repeated reanalyses into a decomposable quantitative diagnostic.

## Claim ceiling

The exact formulas compare scopes at the same context while holding `L`, shared fitness and every alternative worldline fixed. Refitting models after registry changes is a different operation. The metric formula is local/affine and uses one fixed metric. Accessibility itself remains a biological identification problem, and PAYOFF frequency dependence remains separate.

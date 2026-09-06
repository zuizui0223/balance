# BALANCE domain-existence trichotomy v1

## Purpose

BALANCE is not guaranteed merely because shared-coordinate conflict exists. This note classifies what can happen along an ordered environmental path before any PAYOFF frequency feedback is added.

## Setup

Let `e` be an ordered environmental/control variable. Define:

```text
L(e) >= 0                 shared-coordinate conflict load
Delta(e)=W_D*(e)-W_S*(e)  direct optimized worldline gap.
```

Assume `L` and `Delta` are continuous over the path of interest.

Let `e0` be a conflict-onset point such that:

```text
L(e0)=0
L(e)>0 immediately after e0.
```

BALANCE occupancy is

```text
B = {e : L(e)>0 and Delta(e)<0}.
```

## Case 1 — zero-width / absent BALANCE domain

If the differentiated-accessible worldline is already tied with or above the shared worldline at conflict onset and becomes strictly better immediately after onset, then there is no positive-width BALANCE interval.

A special quadratic example is the zero-extra-cost limit `K=0` with positive recoverability as soon as conflict appears.

Interpretation:

```text
conflict onset and architecture crossing coincide.
```

## Case 2 — finite BALANCE domain

If

```text
Delta(e)<0 immediately after e0
```

and there is a first later crossing `ec>e0` such that

```text
Delta(ec)=0
Delta(e)<0 for e0<e<ec,
```

then

```text
(e0,ec)
```

is a finite positive-width BALANCE domain.

Its environmental width is

```text
W_e = ec-e0
```

when `e` has a meaningful metric scale.

## Case 3 — persistent / no-crossing BALANCE domain

If

```text
Delta(e)<0
```

for every conflict-active `e` in the accessible path, then conflict is real but the differentiated-accessible worldline never overtakes the shared worldline.

This is a persistent BALANCE regime over the observed/accessible path.

In the quadratic weight-path example, this can occur when the recoverable-benefit upper bound remains below architecture cost.

## Monotonic special case

If `Delta(e)` is nondecreasing after conflict onset, the three cases above exhaust the topology:

```text
no positive-width BALANCE
one connected finite BALANCE interval
one connected persistent BALANCE interval.
```

Re-entry requires violation of monotonicity or a change in the effective world definitions / scale.

## Why this belongs to BALANCE rather than PAYOFF

This trichotomy concerns **static optimized worldline order along environment**. PAYOFF asks the separate question of whether an architecture can invade or coexist once frequency-dependent ecological feedback is added.

Thus a finite static BALANCE domain can exist even before any population-game middle region is considered.

## Empirical consequence

To distinguish the three cases, the empirical programme needs:

1. a conflict-onset or conflict-active reference from SCH;
2. direct matched `W_S*` and `W_D*` estimates across environment;
3. enough ordered contexts to determine whether a first crossing exists;
4. uncertainty-aware classification rather than point interpolation alone.

## Claim ceiling

Continuity and any monotonicity assumption must be justified for the focal environmental path. Failure to observe a crossing over a finite sampled range does not prove that no crossing exists outside that range.

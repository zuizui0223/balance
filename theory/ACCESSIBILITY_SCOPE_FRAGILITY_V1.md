# BALANCE accessibility-scope fragility theorem v1

## Purpose

Quantify how much a BALANCE reserve depends on uncertain architecture accessibility scope.

The previous partial-identification theorem gives inner and outer domains. Here we turn the gap between them into a same-fitness-scale sensitivity measure.

## Setup

Let

\[
A_{def}\subseteq A_{poss}
\]

be definitely and plausibly accessible alternative sets. Define

\[
\rho_{def}
=W_S^*-\max_{j\in A_{def}}W_{D_j}^*,
\]

\[
\rho_{poss}
=W_S^*-\max_{j\in A_{poss}}W_{D_j}^*.
\]

By scope monotonicity,

\[
\rho_{poss}\le\rho_{def}.
\]

## Definition — accessibility-scope fragility

Define

\[
\boxed{
\Gamma_A
=
\rho_{def}-\rho_{poss}
\ge0.
}
\]

Equivalently,

\[
\boxed{
\Gamma_A
=
\max_{j\in A_{poss}}W_{D_j}^*
-
\max_{j\in A_{def}}W_{D_j}^*.
}
\]

So `Gamma_A` is exactly the increase in the best alternative worldline produced by admitting the plausible-but-not-definite architecture set.

## Theorem 1 — zero fragility criterion

\[
\boxed{\Gamma_A=0}
\]

if and only if adding the possible-only alternatives does not raise the alternative envelope at that context.

This can occur because:

- every possible-only alternative is dominated by a definitely accessible alternative;
- a possible-only alternative ties but does not exceed the definite envelope.

Thus nonzero registry size does not imply nonzero scope fragility.

## Theorem 2 — true reserve uncertainty width is bounded by fragility

For any true accessibility set satisfying

\[
A_{def}\subseteq A_{true}\subseteq A_{poss},
\]

we have

\[
\rho_{poss}\le\rho_{true}\le\rho_{def}.
\]

Therefore the width of the sharp set-theoretic reserve interval is

\[
\boxed{
\rho_{def}-\rho_{poss}=\Gamma_A.
}
\]

So `Gamma_A` is not merely a heuristic sensitivity score; it is the exact width of the reserve identified set generated solely by accessibility-scope uncertainty.

## Theorem 3 — fitness-depth uncertainty is no larger than scope fragility

Let

\[
d_{def}=\min(L,\rho_{def}),
\qquad
d_{poss}=\min(L,\rho_{poss}).
\]

Because the map `x -> min(L,x)` is 1-Lipschitz,

\[
\boxed{
0\le d_{def}-d_{poss}\le\Gamma_A.
}
\]

Hence uncertainty in direct BALANCE depth induced by architecture scope can never exceed the reserve uncertainty itself.

The inequality can be strict when the SCH-facing margin `L` is the limiting side under both scopes.

## Corollary 3a — scope uncertainty can be irrelevant to current depth

If

\[
L\le\rho_{poss},
\]

then

\[
d_{def}=d_{poss}=L
\]

and accessibility uncertainty does not affect the current two-sided depth even when `Gamma_A>0`.

In that case the middle world is limited by the SCH-facing boundary, not by the uncertain architecture side.

## Theorem 4 — robust-positive condition in fragility form

Since

\[
\rho_{poss}=\rho_{def}-\Gamma_A,
\]

robust BALANCE against all plausible alternatives requires

\[
\boxed{
\rho_{def}>\Gamma_A
}
\]

together with `L>0`.

Thus the definite-scope reserve can be viewed as a budget that must exceed the accessibility fragility penalty.

If

\[
0<\rho_{def}\le\Gamma_A,
\]

the context is positive under definite scope but not robust to plausible architecture expansion.

## Positive-scale behavior

Under a common positive affine fitness transformation, reserve differences scale by the same positive multiplier. Therefore

\[
\Gamma_A' = a\Gamma_A,
\qquad a>0.
\]

State order is unchanged, but `Gamma_A` remains a dimensional fitness quantity. It should not be compared across incompatible fitness semantics merely because the algebra is the same.

## Empirical consequence

A multi-alternative BALANCE receipt can report:

```text
rho_def      reserve under definitely accessible alternatives
rho_poss     reserve under all plausibly accessible alternatives
Gamma_A      exact accessibility-scope uncertainty width
```

This separates three distinct reasons a BALANCE claim may be weak:

- small biological reserve even under definite scope;
- large uncertainty in the alternative worldline estimates;
- large uncertainty about which alternatives belong in the accessibility set.

## Claim ceiling

`Gamma_A` measures only uncertainty induced by the declared accessibility set. It does not include statistical uncertainty in worldline fitness, uncertainty about SCH conflict `L`, or PAYOFF invasion dynamics. Those uncertainty sources should be propagated separately and combined only under an explicit identification model.

# Inverse hysteresis identification under finite forcing resolution

The static BALANCE switching-cost result gives the exact thresholds

```text
Phi_F = C_SD / T
Phi_R = -C_DS / T
```

and exact hysteresis width

```text
W = Phi_F - Phi_R = (C_SD + C_DS) / T.
```

A finite monotone forcing experiment does not generally observe `Phi_F` and
`Phi_R` exactly.  It observes the first sampled values beyond them.

## Forward sweep

If consecutive increasing forcing steps are at most `delta_up` and the first
observed shared->differentiated switch occurs at `F_hat`, then

```text
F_hat - delta_up <= Phi_F < F_hat.
```

## Reverse sweep

If consecutive decreasing forcing steps are at most `delta_down` and the first
observed differentiated->shared switch occurs at `R_hat`, then

```text
R_hat < Phi_R <= R_hat + delta_down.
```

## Width interval

Therefore

```text
max(0, W_hat - delta_up - delta_down)
<= W <= W_hat,
```

where

```text
W_hat = F_hat - R_hat.
```

Finite forcing resolution can only inflate the observed width in this declared
monotone protocol; the inflation is bounded by the sum of the two step sizes.

When the horizon `T` is independently known,

```text
T * max(0, W_hat-delta_up-delta_down)
<= C_SD + C_DS
<= T * W_hat.
```

So the same experiment gives an interval for the total switching-cost burden,
not merely a qualitative hysteresis diagnosis.

Implementation:

```text
balance_domain/hysteresis_interval.py
tests/test_hysteresis_interval.py
```

## Claim boundary

This interval assumes the registered BALANCE finite-horizon switching rule and
monotone forcing with declared maximum increments.  It does not identify the two
switching costs separately, and it does not absorb biological process noise,
measurement error in `Phi`, or time-varying costs into the discretization bound.
Those require separate uncertainty layers.

# Finite forcing resolution and hysteresis-width bias

The existing BALANCE switching-cost result gives the analytic thresholds

```text
Phi_F = C_SD/T
Phi_R = -C_DS/T
```

and exact hysteresis width

```text
Delta_Phi = Phi_F-Phi_R = (C_SD+C_DS)/T.
```

`STEPWISE_FORCING_HYSTERESIS.md` adds an ordered external `Phi` path. This note
asks a narrower measurement question:

> If `Phi` is observed or imposed only at finite increments, how accurately are
> the analytic switching thresholds recovered?

Implementation:

```text
balance_domain/forcing_resolution.py
tests/test_forcing_resolution.py
```

---

## Theorem FR1 — one-sided switch-point error bound

Assume a nondecreasing path starts in the shared architecture and crosses the
forward threshold. Let the observed crossing step satisfy

```text
Phi_{j-1} <= Phi_F < Phi_j
```

with crossing jump

```text
delta_up = Phi_j-Phi_{j-1}.
```

Because BALANCE retains the shared state at equality and switches only for
`Phi>Phi_F`, the first observed forward switch is

```text
hat_Phi_F=Phi_j
```

and therefore

```text
0 < hat_Phi_F-Phi_F <= delta_up.
```

Similarly, for a nonincreasing path starting differentiated and crossing the
reverse threshold,

```text
Phi_j < Phi_R <= Phi_{j-1},
```

so

```text
0 < Phi_R-hat_Phi_R <= delta_down,
```

where

```text
delta_down=Phi_{j-1}-Phi_j.
```

Thus finite forcing resolution moves both observed switch points outward from
the analytic hysteresis band.

---

## Corollary FR2 — discrete hysteresis width is upward biased by a bounded amount

The observed width is

```text
hat_Delta_Phi
=hat_Phi_F-hat_Phi_R.
```

Using FR1,

```text
0
<=(hat_Delta_Phi-Delta_Phi)
<=delta_up+delta_down.
```

If both directions satisfy one common declared forcing-resolution bound

```text
|Delta Phi| <= delta,
```

then

```text
0
<=hat_Delta_Phi-Delta_Phi
<=2 delta.
```

So `max_phi_jump` is not merely a qualitative small-step declaration. Under a
monotone crossing design it directly bounds the discretisation inflation of the
measured hysteresis width.

---

## Registered example

Take

```text
T=10
C_SD=2
C_DS=1.
```

Then

```text
Phi_F=0.2
Phi_R=-0.1
Delta_Phi=0.3.
```

With 0.1-spaced forcing observations, one declared path records

```text
hat_Phi_F=0.3
hat_Phi_R=-0.2
hat_Delta_Phi=0.5.
```

The observed width is inflated by

```text
0.2
```

which exactly equals the sum of the two 0.1 crossing jumps in this example.

Refining both paths to maximum step 0.025 reduces the theorem-level inflation
bound to at most

```text
0.05.
```

The regression tests verify both the one-sided brackets and the refinement
behaviour.

---

## Interpretation

This gives BALANCE a clean distinction between three objects:

```text
analytic hysteresis width
!=
finite-resolution observed hysteresis width
!=
forcing-path validity under a declared small-step bound.
```

A wide observed hysteresis band can therefore contain a known discretisation
component. It should not automatically be interpreted as stronger biological
memory.

Conversely, if the declared maximum forcing step is small relative to the
observed width, the maximum discretisation contribution is quantitatively
bounded.

---

## Claim boundary

FR1/FR2 require monotone paths, one clean crossing in each direction, fixed
per-step horizon `T`, and the current deterministic switching-cost rule. They do
not cover delayed switching, stochastic transition hazards, time-varying costs,
nonmonotone forcing, or continuous-time rate dependence.

In particular, refining the path while holding `horizon_per_step` fixed changes
the total elapsed exposure represented by the full path. This theorem is about
**threshold localisation under the declared per-step decision rule**, not a
claim of physical time-rescaling invariance.

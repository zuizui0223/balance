# Stepwise forcing and the explicit small-step assumption

BALANCE already has an exact finite-horizon switching-cost result for one fixed context:

```text
-C_DS/T <= Phi <= C_SD/T
```

is the history-dependent band in which both shared and differentiated architectures can persist depending on their starting state.

This extension asks a different question:

> What happens when `Phi` is followed along an ordered environmental path, and how explicitly should the assumption of small forcing increments be represented?

## 1. Do not mix two different jump concepts

This note uses **small step** only for the external forcing path

```text
Phi_0, Phi_1, ..., Phi_m.
```

It is not an assumption about mutation size in architecture space. Evolutionary mutation-jump accessibility belongs downstream in PAYOFF.

Define

```text
Delta_Phi_max = max_t |Phi_(t+1)-Phi_t|.
```

A prospectively declared forcing-resolution assumption is

```text
Delta_Phi_max <= delta_forcing.
```

`follow_switching_path(..., max_phi_jump=delta_forcing)` enforces this fail-closed: a path with larger jumps is rejected rather than silently treated as quasi-static.

## 2. Stateful path update

At each path coordinate, the existing `switching_cost_state()` theorem is evaluated without alteration.

If the current state is shared, it remains shared while

```text
Phi <= C_SD/T.
```

It switches to differentiated only after the forward threshold is crossed.

If the current state is differentiated, it remains differentiated while

```text
Phi >= -C_DS/T.
```

It switches back to shared only after the reverse threshold is crossed.

Thus the path implementation composes the registered static result; it does not introduce a new switching rule.

## 3. What the extension now distinguishes

The same static `Phi` can have different realised architecture states because of path history. The code now separately records:

```text
instantaneous Phi,
state before the step,
state after the step,
whether a switch occurred,
forward/reverse thresholds,
observed maximum forcing jump,
declared maximum forcing jump.
```

That makes the resolution assumption auditable instead of implicit.

## 4. Prospective rate extension

The current implementation gives each path coordinate the same declared `horizon_per_step`. A later rate-dependent extension can instead map environmental speed into a coordinate-specific dwell time

```text
T_t = |Delta Phi_t| / |dPhi/dt|,
```

and then evaluate the same switching-cost rule with `T_t`. That would make forcing rate, step size, and switching cost jointly identifiable model inputs. It is not yet claimed here.

## 5. Files

- `balance_domain/stepwise_hysteresis.py`
- `tests/test_stepwise_hysteresis.py`

Run:

```bash
pytest -q tests/test_stepwise_hysteresis.py
```

The tests verify construction of a bounded-increment path, fail-closed rejection of an over-large forcing jump, forward and reverse switch points, and history retention inside the hysteresis band.

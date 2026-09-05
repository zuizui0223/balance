# Direct two-worldline verification

BALANCE is intended to sit between two optimized architecture worldlines, not merely between two labels.

For each registered environment or context `e`, define

```text
W_S*(e) = optimized reproductive fitness under the shared-coordinate architecture
W_D*(e) = optimized reproductive fitness under the differentiated architecture, including its registered architecture cost
```

and

```text
Delta_W(e) = W_D*(e) - W_S*(e).
```

The direct worldline classification is

```text
L(e) = 0                         SCH-facing no-conflict world
L(e) > 0 and Delta_W(e) < 0      BALANCE middle world
L(e) > 0 and Delta_W(e) = 0      architecture critical interface
L(e) > 0 and Delta_W(e) > 0      BITA differentiation world.
```

The programme also has the decomposed bridge

```text
Phi(e) = s(e)L(e) - K(e).
```

On one registered fitness scale and under the declared decomposition,

```text
Delta_W(e) = Phi(e).
```

`balance_domain.worldlines.compare_worldlines` checks this equality when both routes are available.

## Why this matters

A direct worldline crossing and a decomposed `sL-K` crossing can disagree for scientifically meaningful reasons:

- the two experiments are not on the same fitness scale,
- `K` is defined differently across the comparisons,
- relevant ecological channels are omitted from the decomposition,
- the differentiated architecture changes the function optima or functional weights rather than merely recovering the SCH conflict load,
- the two measurements refer to different environments, populations, life-history windows, or generations.

Such disagreement should therefore be exposed as a failed bridge rather than averaged away. It is a candidate signature of a genuine parallel-world shift, but it is not proof of one until scale and design mismatch have been excluded.

## Empirical priority

The strongest Chapter-2 receipt would provide, within matched contexts:

1. an SCH conflict receipt on a common reproductive outcome,
2. direct optimized `W_S*`,
3. direct optimized `W_D*`,
4. independent estimates or bounds for `s` and `K`,
5. uncertainty on both `Delta_W` and `sL-K`.

This allows a direct test of whether BALANCE is genuinely the same middle region when viewed from the SCH and BITA worldlines.

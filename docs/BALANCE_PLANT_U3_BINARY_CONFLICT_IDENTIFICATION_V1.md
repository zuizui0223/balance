# BALANCE U3 binary-conflict nonidentification certificate v1

## Question

Can binary pollen-fate conflict presence distinguish heterantherous cases from their frozen nonheterantherous controls?

The current four-pair lane makes this question answerable as an **identification diagnostic**, even though one control conflict state remains unresolved.

## Observed matched structure

All four heterantherous cases have direct positive pollen-fate conflict evidence.

Three of four nonheterantherous controls are also directly conflict-positive:

- `Solanum lycocarpum`;
- `Senna spectabilis`;
- `Senna covesii`.

Those three positive controls occupy two conservative dependence blocks (`Solanum` and `Senna`). Positive conflict is therefore already demonstrably **not sufficient** for heteranthery.

The remaining control is `Osbeckia chinensis`, whose conflict state is `UNRESOLVED`.

## Exhaustive completion certificate

There are only two registered binary completions of the unresolved Osbeckia state.

### Completion A — Osbeckia is POSITIVE

Every one of the four pairs is conflict-positive on both sides.

```text
within-pair predictor discordance = 0
```

A matched binary conflict coefficient is unidentified because the predictor has no within-pair variation.

### Completion B — Osbeckia is NO_DEMONSTRATED_CONFLICT

Only the Melastoma–Osbeckia pair is conflict-discordant:

```text
case positive / control negative = 1
case negative / control positive = 0
```

The conditional matched log-odds estimate is separated in the positive direction rather than finite.

## Result

Therefore, under **every registered completion** of the remaining binary conflict state:

```text
finite matched binary conflict coefficient = impossible
```

This is stronger and cleaner than repeatedly searching for one more binary conflict label. The binary presence variable is not an identified discriminator of heteranthery in this matched lane.

It does **not** imply that conflict has zero causal relevance. It means that presence/absence is too coarse: nonheterantherous systems can retain the same conflict and route it through different architectures.

## Consequence

The next empirical question is conditional routing:

> given positive pollen-reward versus gamete-transfer conflict, where is that conflict routed?

Current resolved positive controls already show two answers:

- `Solanum lycocarpum` — among-flower module division;
- `Senna spectabilis` — within-flower division of labour despite equal fertile-stamen morphology.

`Senna covesii` has positive conflict but unresolved routing, and `Osbeckia chinensis` remains conflict-unresolved.

## Executable surface

```text
balance_domain/plant_u3_conflict_identification.py
tests/test_plant_u3_conflict_identification.py
```

## Claim ceiling

This is a matched binary-predictor nonidentification certificate. It does not estimate a zero causal effect, population prevalence, conflict strength, or historical transition probability.

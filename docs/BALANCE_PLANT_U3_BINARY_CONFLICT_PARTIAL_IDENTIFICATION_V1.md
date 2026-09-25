# BALANCE U3 binary conflict partial-identification v1

## Question

Does the current unresolved `Osbeckia chinensis` control prevent every conclusion about binary pollen-fate conflict presence?

No. It prevents a complete four-pair point estimate, but it does not prevent a bounded matched-sample statement.

## Current evidence

The four PASS-adjudicated heteranthery cases are all conflict-positive.

Among the four nonheterantherous controls:

- `Solanum lycocarpum` — POSITIVE;
- `Senna spectabilis` — POSITIVE;
- `Senna covesii` — POSITIVE;
- `Osbeckia chinensis` — UNRESOLVED.

Treating the unresolved control as allowed to be either positive or no-demonstrated-conflict gives:

```text
case positive fraction       = [1.00, 1.00]
control positive fraction    = [0.75, 1.00]
case - control difference    = [0.00, 0.25]

case-positive / control-negative matched pairs
                              = [0, 1] of 4
                              = [0.00, 0.25]
```

These are deterministic bounds for this matched sample, not confidence intervals and not population prevalence estimates.

## Biological result

Binary conflict presence already fails as a deterministic separator of heteranthery.

Three independently selected nonheterantherous controls retain direct pollen-reward / gamete-transfer conflict. Resolving `O. chinensis` can only determine whether the observed raw case-control positive-fraction difference is 0 or 0.25 in this four-pair set.

So the more informative BALANCE question is no longer:

> Is conflict present?

It is:

> Given that conflict often persists with or without heteranthery, where and how is it routed, and how strong is it?

The current controls already show different routing states:

- `S. lycocarpum`: among-flower module division;
- `S. spectabilis`: within-flower functional division despite equal fertile-stamen morphology;
- `S. covesii`: conflict present but broader routing architecture unresolved.

This makes morphological heteranthery, conflict presence, and conflict-routing architecture distinct empirical variables.

## Why Osbeckia still matters

The unresolved `O. chinensis` measurement remains necessary for the registered complete four-pair conflict estimand and for any later quantitative comparison.

The partial-identification result does not reclassify it, impute a value, or relax the evidence gate.

## Executable surface

```text
balance_domain/plant_u3_partial_identification.py
tests/test_plant_u3_partial_identification.py
```

## Claim ceiling

These bounds describe the current matched sample only.

They do not estimate natural heteranthery prevalence, population conflict prevalence, a causal effect of conflict on heteranthery, quantitative conflict strength, or historical transition probabilities.

# BALANCE Gymnadenia pollinator-herbivore conflict recovery v1

## Decision

`Gymnadenia conopsea` is admitted to the Chapter-2 reality-pattern ledger as:

```text
CONFLICT_WITHOUT_SPLITTING
```

and the 2015 factorial experiment is added as the fourth current candidate in the quantitative `OPPOSING_FLORAL_SELECTION` stratum.

This promotion is based on **identified pollinator and herbivore selection on the same flowering-phenology coordinate**, not on the separate 2019 scent study's residual nonpollinator selection.

The quantitative effect is **not yet `EFFECT_SIZE_READY`** because the Appendix A2 treatment-group gradients still require reconstruction of the factorial agent contrasts and their joint uncertainty.

---

## Primary source

Sletvold, Moritz & Ågren (2015), *Ecology* 96:214-221, DOI `10.1890/14-0119.1`.

The experiment manipulated the intensity of:

```text
pollination
×
herbivory
```

in a factorial design in one natural `Gymnadenia conopsea` population.

The study measured female reproductive fitness and floral traits including:

```text
flowering phenology
floral display
spur length / morphology
```

Supplemental hand pollination increased female fitness, and approximately one quarter of plants experienced herbivore damage, so both manipulated ecological interactions were consequential in the focal experiment.

---

## Same-trait conflict

The key opposed coordinate is flowering phenology.

The source reports:

```text
pollinator-mediated selection
-> later flowering

herbivore-mediated selection
-> earlier flowering
```

The two effects were similar in strength and approximately additive. Their opposition produced little or no net directional selection on flowering phenology in the combined natural context.

This is especially informative for BALANCE because the zero/weak net result is not an absence of functional selection. It is produced by two non-zero ecological contributions acting in opposite directions on the same trait.

This directly illustrates the Chapter-1/Chapter-2 distinction:

```text
weak net selection
!=
no conflict
```

when component selection is opposed.

The study also recovered a useful internal control: both pollinators and herbivores selected for longer spurs. Thus the same factorial experiment contains both:

```text
conflicting selection on phenology
and
reinforcing selection on spur length.
```

This prevents the programme from treating every two-agent floral effect as automatically antagonistic.

---

## R-layer admission

For the flowering-phenology coordinate:

```text
conflict_present                    yes
shared_architecture_present         yes
alternative_architecture_identified no
pattern_class                       CONFLICT_WITHOUT_SPLITTING
confidence                          high
```

The plant retains one integrated floral/phenological system while pollinator and herbivore contributions favor opposite states.

No differentiated alternative worldline is compared, so this is a reality-pattern receipt rather than direct BALANCE occupancy.

---

## Quantitative Q1 admission

The source is stronger than a generic observational conflict example because it factorially manipulates both agent environments.

Registered Q1 object:

```text
trait = flowering_start / phenology
agent 1 = pollinators
agent 2 = herbivores
relation = opposed
```

Ecological Archives `E096-022-A1` contains:

```text
Table A1: trait means ± SD
Table A2: phenotypic linear selection gradients ± SE
          for all four treatment groups
```

Therefore the source is registered as:

```text
OPPOSED_AGENT_PAIR
APPENDIX_A2_CONTRAST_RECONSTRUCTION_PENDING
```

not as `EFFECT_SIZE_READY`.

---

## Why Appendix beta ± SE is not enough by itself

The meta-analytic target is not merely four treatment-group slopes.

The preregistered Q1 target is an agent-mediated contrast such as:

```text
(beta_pollinator, beta_antagonist)
```

with uncertainty, and optionally:

```text
D = beta_pollinator - beta_antagonist.
```

Because factorial contrasts may share treatment cells or be estimated jointly, the covariance needed for `Var(D)` cannot be assumed to be zero.

Before effect-size promotion, recover one of:

1. the original factorial interaction/trait-by-treatment coefficient covariance from the model;
2. individual-level data enabling a common bootstrap/reanalysis;
3. a source-reported contrast and SE that directly matches the preregistered agent estimand.

Do not compute a pooled effect from treatment-group SEs using an independence assumption unless the design/estimator proves the relevant contrasts are independent.

---

## Relationship to Chapurlat et al. 2019

`Gymnadenia conopsea` also appears in Chapurlat et al. (2019; DOI `10.1111/nph.15747`), where pollinator-mediated selection on scent compounds opposed residual nonpollinator-mediated selection.

A full methods audit of that study found that:

```text
florivore / insect-herbivore damage was not observed
```

and the authors considered antagonistic interactions unlikely to explain the residual scent gradients.

Therefore the two sources have different roles:

```text
Sletvold et al. 2015
identified pollinator × herbivore factorial conflict
-> antagonist-specific Q1 candidate

Chapurlat et al. 2019
pollinator vs residual nonpollinator scent selection
-> NOT antagonist-specific Q1
```

They do **not** count as two independent Gymnadenia system replications.

The R-layer uses one biological cluster:

```text
Gymnadenia conopsea
```

with the 2015 experiment providing the positive conflict admission and the 2019 study serving as a boundary on agent attribution.

---

## Why this is not direct BALANCE occupancy

The direct Chapter-2 object requires matched optimized worldlines:

```text
L > 0
and
W_D* - W_S* < 0.
```

The 2015 factorial changes ecological agent intensity while the flower remains within the same integrated architecture family.

It does not compare:

```text
optimized shared architecture        W_S*
vs
optimized differentiated architecture W_D*.
```

Thus the study does not identify:

```text
rho
Phi
xi
d_B
BALANCE width.
```

---

## Claim allowed

Appropriate:

> In `Gymnadenia conopsea`, a factorial field experiment shows that pollinators and herbivores impose similarly strong but opposite selection on flowering phenology, while the same agents reinforce selection on another floral trait. This provides a high-confidence conflict-without-splitting pattern and a strong quantitative opposed-agent candidate.

Not appropriate:

> The published treatment-group gradients already constitute a pooled-ready BALANCE effect size or direct evidence that a shared worldline outperforms a differentiated alternative.

---

## Next gate

Recover the exact Appendix A2 values and the model/contrast covariance required to estimate pollinator- and herbivore-mediated phenology selection on a common uncertainty scale.

If that reconstruction succeeds, `Gymnadenia conopsea` can become the first `effect_size_ready` Q1 cluster without changing its direct-BALANCE claim ceiling.

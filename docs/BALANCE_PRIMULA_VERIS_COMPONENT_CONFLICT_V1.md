# BALANCE Primula veris component-conflict recovery v1

## Decision

`Primula veris` is admitted to the Chapter-2 reality-pattern ledger as:

```text
CONFLICT_WITHOUT_SPLITTING
```

The admission is based on a same-trait reproductive-component conflict in an integrated floral display. It is **not** promoted to the quantitative pollinator-versus-antagonist stratum because the positive fruit/seed-set pathway is not experimentally isolated as a pollinator-mediated selection coefficient in the focal path-analysis study.

---

## Primary source chain

### Kolb & Ehrlen 2010 — environmental modulation of seed-predator selection

Kolb & Ehrlen (2010; *Evolutionary Ecology* 24:433-445; DOI `10.1007/s10682-009-9316-2`) studied `Primula veris` across 44-52 populations over two years.

They recovered population-level variation in selection on floral display traits, including inflorescence height and flower number. Pre-dispersal seed predation and flower abortion mediated part of this variation, and canopy cover altered selection on inflorescence height through its effect on seed predation.

Admitted role:

```text
SPATIALLY_VARIABLE_SEED_PREDATOR_SELECTION
ENVIRONMENTAL_MODERATOR_OF_TRAIT_CONFLICT
LIFETIME_FITNESS_CONTEXT_AVAILABLE
```

This source demonstrates that antagonist-mediated selection on the display is context dependent, but it does not by itself provide a matched pollinator-mediated coefficient on the same trait.

### Ehrlen, Borg-Karlson & Kolb 2012 — opposite fitness-component paths on one trait

Ehrlen et al. (2012; *Basic and Applied Ecology* 13:509-515; DOI `10.1016/j.baae.2012.08.001`) used selection path analysis to ask how optical and fragrance traits affect total seed production through reproductive success and predator avoidance.

For `inflorescence height`, the study recovered the key Chapter-2 pattern:

```text
increased inflorescence height
-> increased fruit set / seed set

but

increased inflorescence height
-> lower probability of escaping fruit/seed predation.
```

Thus the same floral display trait contributes positively and negatively to total seed production through different fitness components.

The article interprets the broader pattern as simultaneous selection through mutualistic and antagonistic interactions, but the positive reproductive path is not a clean experimental `beta_pollinator` estimate.

Admitted role:

```text
SAME_TRAIT_OPPOSING_FITNESS_COMPONENTS
TOTAL_SEED_PRODUCTION_COMMON_OUTCOME
ANTAGONIST_PATH_EXPLICIT
MUTUALIST_PATH_INTERPRETATION_BOUNDED
```

---

## BALANCE interpretation

The R layer requires a recurrent observable signature, not direct parameter identification.

For this system:

```text
conflict present                    yes
shared/integrated architecture      yes
explicit differentiated worldline   no
shared trait persists               yes
opposed component effects           yes
```

The system therefore supports:

```text
CONFLICT_WITHOUT_SPLITTING
```

at the pattern level.

The result is complementary to the stronger direct-agent cases in `Dalechampia`, `Castilleja`, `Pedicularis`, and `Polemonium` because it shows that the same trait can carry opposing contributions to one downstream fitness measure even when the mutualist channel is not cleanly experimentally separated.

---

## Why this is not a Q1 effect-size-ready pollinator-agent pair

The registered `OPPOSING_FLORAL_SELECTION` quantitative stratum targets a compatible within-study vector such as:

```text
(beta_pollinator, beta_antagonist)
```

with joint uncertainty.

The 2012 Primula path analysis instead decomposes total seed production into component pathways. It does not directly provide a standardized experimentally isolated pollinator-mediated gradient that can be pooled with the current Dalechampia/Castilleja/Pedicularis targets without reanalysis.

Accordingly the quantitative screening ledger retains this source as:

```text
SOURCE_REANALYSIS_REQUIRED
NO_POLLINATOR_AGENT_PAIR_PROMOTION
```

Do not:

- label fruit/seed set automatically as `beta_pollinator`;
- mix path coefficients with standardized selection gradients without a common model;
- infer a missing covariance as zero;
- count the 44-52 populations as independent literature studies.

---

## Why this is not direct BALANCE occupancy

No explicit alternative/differentiated architecture is optimized and compared against the shared Primula display.

The literature therefore does not identify:

```text
W_S*
W_D*
rho
Phi
xi
d_B
```

or a direct Chapter-2 critical threshold.

The proper claim ceiling is:

```text
opposing_component_selection_not_direct_pollinator_beta_or_BALANCE_occupancy
```

---

## Independence contract

`Primula veris` is one biological/system cluster. The 2010 environmental-selection study and the 2012 component-path study are complementary evidence for that cluster.

Do not count them as two independent BALANCE replications.

They are also distinct from the existing `Primula farinosa` cluster, which concerns context-dependent morph-frequency dynamics and remains `UNRESOLVED` for static BALANCE because its strongest evidence is frequency dependent.

---

## Updated claim allowed

Appropriate:

> In `Primula veris`, the same floral display trait can increase fruit and seed production while simultaneously reducing escape from pre-dispersal seed predation, and the strength of seed-predator-mediated selection varies with environmental context. This supports a recurrent conflict-without-splitting pattern in an integrated floral architecture.

Not appropriate:

> Primula veris provides a directly measured pollinator-versus-seed-predator BALANCE worldline or an effect-size-ready pollinator/antagonist coefficient pair.

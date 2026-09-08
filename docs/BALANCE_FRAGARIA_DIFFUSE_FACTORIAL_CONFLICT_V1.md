# BALANCE Fragaria diffuse factorial conflict v1

## Question

Can a shared plant display trait be pulled in opposite directions by pollinators and herbivores while the strength of each selective force depends on the ecological state of the other agent?

This is a stricter object than a simple two-gradient conflict because the agent-mediated selection coefficients are themselves context dependent.

## Primary source

Egan PA, Muola A, Parachnowitsch AL, Stenberg JA. 2021. `Pollinators and herbivores interactively shape selection on strawberry defence and attraction.` Evolution Letters 5:636-643. DOI `10.1002/evl3.262`.

Public data: Dryad DOI `10.5061/dryad.1rn8pk0vn`.

The source supplement `EVL3-5-636-s001.docx` was recovered through the public PMC record. Table S2 reports the mediated-selection contrasts and marginal uncertainty; Table S3 reports the factorial interaction test used by the registered covariance reconstruction.

## Experimental design

The study used woodland strawberry `Fragaria vesca` in a common garden.

The two selective-agent manipulations were crossed factorially:

```text
pollination
  open
  supplemental hand pollination

herbivory
  herbivore addition
  herbivore removal
```

The experiment therefore generated four treatment combinations. Herbivory was manipulated primarily with the strawberry leaf beetle `Galerucella tenella`; herbivore-removal plots received insecticide treatment and addition plots received water controls.

The common downstream female-fitness endpoint was total fertilized seed output per plant.

## Trait coordinate

The strongest BALANCE-relevant shared trait is:

```text
z = inflorescence density
    number of flowers per unit plant volume
```

One visible architecture coordinate can therefore affect both mutualist use and antagonist use.

## Selection analysis

The source standardized traits and relative fitness and estimated multivariate directional selection gradients. Differences among fitness-trait slopes were evaluated with `emmeans::emtrends` to recover four context-specific mediated contrasts:

```text
c1 = pollinator-mediated selection | herbivores present
c2 = pollinator-mediated selection | herbivores absent
c3 = herbivore-mediated selection  | open / pollen-limited pollination
c4 = herbivore-mediated selection  | supplemented pollination
```

For inflorescence density Table S2 reports:

```text
c1 = -0.022 ± 0.314
c2 =  0.572 ± 0.224
c3 = -0.391 ± 0.125
c4 =  0.203 ± 0.365
```

The same table reports the shared diagonal contrast:

```text
OP - HA = 0.181 ± 0.213
```

The factorial paths close at source-reported precision:

```text
c1 + c4 = 0.181
c2 + c3 = 0.181
```

and the interaction contrast is

```text
q = c1 - c2 = c3 - c4 = -0.594.
```

Table S3 reports the one-degree-of-freedom `inflorescence density × pollination × herbivory` interaction `F = 2.366`, giving

```text
SE(q) = sqrt(q^2 / F) = 0.3861704825451837.
```

## Recovered conflict

The source recovers context-dependent opposing selection on the same trait coordinate. In particular, the positive pollinator-mediated contrast when herbivores are absent and the negative herbivore-mediated contrast under open pollination show that the two agents can pull inflorescence density in opposite directions, while the full four-contrast vector shows that neither agent effect is invariant to the other agent's context.

The correct R-layer admission remains:

```text
CONFLICT_WITHOUT_SPLITTING
```

## Why this does not enter the simple Q1 bivariate stratum unchanged

The simple `OPPOSING_FLORAL_SELECTION` stratum targets one bivariate object `(beta_pollinator, beta_antagonist)` with joint uncertainty.

Fragaria is more structured: all four context-specific contrasts are part of the scientific result. Selecting only one pair would be outcome dependent and would discard the diffuse interaction structure.

Fragaria therefore remains in the separate quantitative stratum:

```text
DIFFUSE_FACTORIAL_AGENT_SELECTION
```

## Quantitative promotion is now closed

The earlier gate required the four contrasts plus their full joint covariance. The supplement does not print a 4×4 covariance matrix directly, but it reports enough linearly related sufficient statistics to identify it exactly.

For registered contrasts `a,b,c,d`, the factorial identities are

```text
a + d = b + c = y
a - b = c - d = q.
```

The four marginal variances, the reported variance of `y = OP - HA`, and `Var(q)` recovered from the one-df interaction `F` identify all six off-diagonal covariance terms. The exact null identity `a - b - c + d = 0` supplies the final linear constraints.

The full derivation, reconstructed matrix, PSD check, and deterministic values are frozen in:

- `balance_domain/reported_factorial.py`;
- `data/BALANCE_FRAGARIA_Q1B_RECEIPT_V1.json`;
- `docs/BALANCE_FRAGARIA_Q1B_REPORTED_COVARIANCE_RECEIPT_V1.md`.

No covariance is set to zero by assumption. Several reconstructed off-diagonal terms are materially nonzero.

The covariance is positive semidefinite and rank 3, as expected because the four contrasts obey one exact factorial linear dependence.

## Quantitative status

Fragaria is now the first positive Q1B cluster with registered joint multicontrast uncertainty:

```text
Q1B positive registered clusters:      1
Q1B negative/control reanalyses:       1  (Trifolium)
Q1B effect-size-ready positive:         1  (Fragaria)
minimum independent positives to pool: 3
pooling:                                NOT READY
```

A raw-data bootstrap remains desirable as a sensitivity analysis if the deposited individual-level data are recovered cleanly, but it is no longer required for the source-reported covariance receipt.

## Internal controls

The Fragaria experiment also prevents positive-only screening. Across other traits, agent effects are not universally opposed, and the Trifolium full-factorial study remains a design-matched negative control in which a registered same-trait pollinator-versus-herbivore opposition was not recovered.

## Why this is still not a direct BALANCE receipt

The experiment identifies conflict on one shared trait but does not construct and optimize an explicit differentiated architecture worldline. It therefore does not measure:

```text
W_S*
W_D*
rho
Phi
xi
d_B
```

Q1B effect-size readiness is an R-layer quantitative evidence status, not direct BALANCE occupancy.

## Current status

```text
PRIMARY_SOURCE:                     PEER_REVIEWED_OPEN_ACCESS
RAW_DATA:                           PUBLIC_DRYAD
SOURCE_SUPPLEMENT:                  RECOVERED_VIA_PUBLIC_PMC
FULL_FACTORIAL_AGENT_MANIPULATION:  YES
COMMON_FEMALE_FITNESS:              YES
SAME_TRAIT_AGENT_CONFLICT:          RECOVERED
DIFFUSE_CONTEXT_DEPENDENCE:         RECOVERED
R_PATTERN:                          CONFLICT_WITHOUT_SPLITTING
SIMPLE_Q1_BIVARIATE_READY:          NO
Q1B_DIFFUSE_FACTORIAL_CANDIDATE:    YES
FULL_MULTICONTRAST_COVARIANCE:      RECONSTRUCTED_FROM_REPORTED_SUFFICIENT_STATISTICS
EFFECT_SIZE_READY:                  YES_Q1B
Q1B_POOLING_READY:                  NO_ONE_OF_THREE_REQUIRED
DIRECT_BALANCE_RECEIPT:             NO
```

## Claim ceiling

Appropriate:

> A full-factorial Fragaria experiment recovered context-dependent opposing pollinator- and herbivore-mediated selection on the same inflorescence-density coordinate under a common seed-fitness endpoint, and the source-reported factorial sufficient statistics identify the joint four-contrast covariance required for one Q1B effect-size-ready receipt.

Not appropriate:

> Fragaria directly identifies the BALANCE worldline reserve or by itself establishes a pooled general quantitative effect.

# BALANCE Q1B identification-gap audit v1

## Question

After the first effect-size-ready `Fragaria vesca` Q1B receipt, can the literature already supply two additional independent positive programmes under the **same** quantitative estimand?

The registered Q1B object is deliberately strict. For one continuous trait coordinate and one common reproductive-fitness scale, the study must permit the context-specific agent-selection vector

```text
P | antagonist present
P | antagonist absent
antagonist | pollination limited/open
antagonist | pollination supplemented
```

or an algebraically equivalent joint factorial representation with uncertainty.

The study must also recover a biologically meaningful same-trait conflict rather than merely show that herbivory changes phenotype, that a predator changes pollinator behaviour, or that two treatments interact on reproduction.

## Current result

The targeted primary-source audit currently contains **15 programmes** spanning strict factorial selection studies and high-information near misses.

Deterministic readout:

```text
n_audited_programmes                    = 15
n_strict_q1b_effect_ready              = 1
strict_q1b_effect_ready                = EGAN_FRAGARIA_2021
n_nonpass_programmes                   = 14
n_design_matched_negative_controls     = 2
```

This is a **design-coverage audit**, not a prevalence estimate. The 15 studies were selected because they are unusually informative or close to the registered identification target. They are not a random sample of floral systems and the audit is not claimed to be an exhaustive global systematic review.

The inference is therefore:

> Among the high-information programmes audited so far, `Fragaria vesca` is the only study that currently closes the full continuous-trait diffuse-factorial Q1B effect object with recoverable joint uncertainty.

Not:

> Only one floral system in nature exhibits diffuse pollinator-antagonist conflict.

## The strict pass

### Egan et al. 2021 — `Fragaria vesca`

DOI `10.1002/evl3.262`.

The study crosses pollination and herbivory in a full factorial common-garden experiment and quantifies selection under a common fertilized-seed fitness scale. Inflorescence density experiences opposing pollinator- and herbivore-mediated selection and each agent effect depends on the state of the other agent.

The recovered public supplement reports the four context-specific mediated contrasts, their marginal standard errors, one shared diagonal contrast with standard error, and the one-df interaction F statistic. Exact factorial identities identify the full rank-3 joint covariance without assuming independent standard errors.

Repository receipt:

```text
data/BALANCE_FRAGARIA_Q1B_RECEIPT_V1.json
```

This makes Fragaria **effect-size ready**, but one ready study remains below the registered three-independent-positive pooling gate.

## Near misses by identification gate

### 1. Additive conflict, not diffuse Q1B — `Gymnadenia conopsea`

Sletvold, Moritz & Ågren 2015, DOI `10.1890/14-0119.1`.

This is one of the strongest biological conflict studies in the literature. Pollinators select for later flowering and herbivores for earlier flowering under a factorial manipulation, but no trait × pollination × herbivory interaction is detected. It therefore belongs naturally to simple opposing-agent Q1 rather than being relabelled a diffuse Q1B positive.

The distinction is statistical, not biological: `Gymnadenia` is a strong reality-pattern anchor for opposing selection.

### 2. Full/near factorial designs without a same-trait positive conflict — `Trifolium` and `Lythrum`

`Trifolium repens`, Santangelo et al. 2018/2019, DOI `10.1111/jeb.13392`, has public clean data and a reproducible R analysis. The factorial design identifies real treatment-dependent selection, but no registered same trait receives independent opposing pollinator- and herbivore-mediated selection.

`Lythrum salicaria`, Thomsen & Sargent 2017, DOI `10.1093/aob/mcx026`, shows that simulated herbivory changes direct selection, but pollinator-mediated delta-beta is near zero for the focal floral/architectural traits and pollination × damage × trait interactions are unsupported.

These two systems are valuable **negative controls**, not failed experiments to be discarded.

### 3. Strong opposing selection under a different estimand — `Primula farinosa`

Ågren et al. 2013, DOI `10.1073/pnas.1301421110`.

Pollinators favour long scapes whereas grazers favour short scapes, and spatial variation in interaction intensity is associated with variation in relative morph fitness and morph-frequency evolution.

The focal coordinate, however, is a genetically based **discrete long/short morph**. It is therefore retained in the separate `DISCRETE_MORPH_AGENT_SELECTION` stratum rather than converted to a pseudo-continuous beta.

### 4. Opposing evidence assembled from separate experiments — `Claytonia virginica`

Frey 2004, DOI `10.1111/j.0014-3820.2004.tb00872.x`.

A multiseason field study, pollen-supplementation study and artificial-herbivory experiment collectively support opposing forces on floral redness. The experiments do not form one crossed same-unit factorial design, and the colour phenotype is mainly represented by discrete classes. The system remains an important pattern-level example, not a Q1B receipt.

### 5. Direct trait intervention rather than phenotypic-selection gradient — `Cucurbita pepo` subsp. `texana`

Theis & Adler 2012, DOI `10.1890/11-0825.1`.

Fragrance, pollination and florivores are experimentally manipulated and enhanced fragrance increases florivore attraction and reduces seed production. This is unusually strong evidence for a direct functional trade-off.

But the focal trait value is itself experimentally imposed. The estimand is an intervention contrast on fragrance, not the Q1B continuous-trait selection-gradient vector. This study could support a future **trait-intervention conflict** stratum; it should not be transformed into a beta study by convenience.

### 6. Predator-mediated reversal of pollinator selection — `Lobelia siphilitica`

Benoit & Caruso 2021, DOI `10.1002/ecy.3506`, Dryad `10.5061/dryad.wdbrv15p8`.

Ambush bugs reverse the direction of pollinator-mediated selection on daily display size. The result is highly relevant to context dependence, but the predator acts through pollinator behaviour: it is an indirect tri-trophic modifier, not an independently identified antagonist-mediated plant-fitness selection route on the same trait.

The correct label is `INDIRECT_PREDATOR_CONTEXT_REVERSAL`.

### 7. Herbivory-induced plasticity modifies pollinator selection — `Brassica rapa`

Dorey & Schiestl 2022, DOI `10.1111/evo.14634`.

The design crosses soil and aphid herbivory and compares hand- and bumblebee-pollinated plants. Bumblebee-mediated selection on the morphological PC containing height, flower number and flowering time depends on soil and herbivory context.

However, aphids are removed before pollination and the paper explicitly interprets herbivory as changing the plant phenotype and therefore the pollinator-selection environment. The direct `trait × herbivory` effect is not the registered opposing antagonist-selection route. This is a plasticity-context boundary, not a second Q1B positive.

### 8. Factorial experimental evolution, not a within-generation Q1B selection vector — `Brassica rapa`

Ramos & Schiestl 2019, DOI `10.1126/science.aav6962`.

Bee/hand pollination and caterpillar herbivory are crossed over six generations. Pollination and herbivory interactively alter evolved floral attractiveness, mating system and other traits.

This is strong evidence that mutualist-antagonist interaction changes evolutionary trajectories. Its estimand is **evolutionary response across generations**, not the within-study context-specific phenotypic-selection vector registered for Q1B.

### 9. Pollinator experiment plus observational antagonist null — `Trillium discolor`

Koski 2023, DOI `10.1002/ajb2.16101`, data DOI `10.5281/zenodo.7258367`.

Pollen supplementation identifies pollinator-mediated selection. Natural antagonist damage is also measured, but antagonism is not independently manipulated and antagonist damage does not alter selection on the floral traits. This is a useful one-agent experiment plus antagonist-null boundary.

### 10. Herbivore manipulation without pollination manipulation — `Erysimum mediohispanicum`

Gómez 2003, DOI `10.1086/376574`.

Ungulate exclusion changes the floral-selection regime and herbivory can disrupt pollinator-associated selection. Pollinator preferences are measured, but pollination itself is not experimentally toggled to identify pollinator-mediated beta on the same factorial surface.

### 11. Pollination manipulation plus observational herbivore paths — `Lobelia cardinalis`

Bartkowska & Johnston 2012, DOI `10.1111/j.1469-8137.2011.04013.x`.

Pollination is experimentally manipulated, while herbivore effects are quantified through path analysis. It is informative for multiple selection routes but lacks the crossed antagonist intervention required by Q1B.

### 12. Multi-agent treatment-response experiment rather than trait-selection analysis — `Impatiens capensis`

Soper Gorden & Adler 2018, DOI `10.1002/ajb2.1182`.

Pollination, florivory and nectar robbing are experimentally increased and show non-additive effects on subsequent visitors, plant traits and reproduction. The study therefore establishes genuine multi-agent ecological nonadditivity.

Its primary estimand is treatment response, not agent-mediated phenotypic selection on one continuous trait coordinate.

### 13. Dual-role insect axis — `Brassica rapa`

Knauer & Schiestl 2017, DOI `10.1007/s10682-016-9878-8`.

The system recovers conflicting/nonadditive selection among visitor treatments, but `Pieris brassicae` has both pollinating and herbivore/host-use roles. It cannot be treated as a clean independent antagonist axis against pollination without changing the biology.

## What the failed-gate distribution says

The deterministic readout keeps the first failed gate for every programme. Recurrent failures include:

```text
same_trait_opposition_absent            2
independent_antagonist_selection_absent 2
antagonist_manipulation_absent          2
```

Other programmes fail because the trait is discrete, the selection experiment is not crossed, the focal trait is directly manipulated rather than sampled as a continuous selection coordinate, or the outcome is evolutionary response rather than within-generation selection.

Thus the literature gap is not one missing ingredient. Different programmes occupy different faces of the identification problem.

## Implication for the empirical strategy

The result strengthens rather than weakens the `T -> R -> C -> G` strategy.

The R layer can already show:

- recurring conflict patterns across many systems;
- positive and negative factorial controls;
- discrete-morph selection mosaics;
- context-dependent and trajectory-level effects;
- one fully effect-ready diffuse-factorial continuous-trait receipt.

But the strict Q1B meta-analysis should **not** begin until at least two more independent positive programmes match the same estimand. The current state remains:

```text
positive Q1B clusters       = 1
ready positive Q1B clusters = 1
minimum to pool             = 3
pooling                     = NOT READY
```

The appropriate next search target is therefore not “any study mentioning pollinators and herbivores.” It is specifically:

```text
continuous trait
+ common reproductive fitness
+ crossed pollination intervention
+ crossed independent antagonist intervention
+ same-trait opposing selection
+ context-specific agent contrasts
+ recoverable joint uncertainty
```

## Claim ceiling

Appropriate:

> A targeted audit of 15 high-information programmes finds one currently effect-ready strict Q1B study and numerous near misses that fail for distinct design or estimand reasons. This demonstrates a quantitative identification gap and justifies preserving multiple separate empirical strata.

Not appropriate:

> Only one system in nature exhibits pollinator-antagonist conflict.

Not appropriate:

> The audit is an exhaustive systematic review of all floral-selection literature.

And still not appropriate:

> The Q1B receipt identifies direct BALANCE `W_S*`, `W_D*`, `rho`, `Phi`, `xi`, or `d_B`.

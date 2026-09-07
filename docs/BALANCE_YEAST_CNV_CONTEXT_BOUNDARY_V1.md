# BALANCE yeast CNV context-boundary recovery v1

## Question

Can one experimentally evolving biological system switch between a generalist/shared strategy and a specialist/differentiated strategy as environmental structure changes, without relying on population coexistence as the Chapter-2 object?

## Source

Abdul-Rahman F, Gresham D. 2025. `Copy number variation facilitates rapid toggling between ecological strategies.` bioRxiv. DOI `10.1101/2025.07.22.666191`.

Audit status on 2026-09-07: preprint / not promoted to peer-reviewed evidence.

## Experimental system

The study used `Saccharomyces cerevisiae` dual-fluorescent CNV reporters at nitrogen-transporter loci. The clearest BALANCE-relevant pair is:

```text
GAP1  glutamine-related transporter axis
PUT4  proline-related transporter axis
```

Populations began from a balanced `1:1` copy-number state and evolved in chemostats under either:

```text
static glutamine limitation
static proline limitation
fluctuating glutamine <-> proline limitation
```

The fluctuating treatment alternated nutrient limitation every eight generations.

## Why this is a conflict / generalist-specialist system

Copy number at the two transporter loci has environment-dependent fitness consequences.

The study reports that:

- increased `GAP1` copy number is advantageous in glutamine limitation but can be deleterious in proline limitation;
- increased `PUT4` copy number is advantageous in proline limitation;
- asymmetric `GAP1:PUT4` copy-number ratios produce asymmetric fitness profiles and are classified as specialists;
- balanced ratios such as `1:1`, `2:2`, and `3:3` produce more balanced fitness across the two nitrogen environments and are classified as generalists.

This provides a within-genome trade-off between performance on two environmental tasks rather than a frequency-dependent coexistence object.

## Context-dependent architecture outcome

The same `1:1` generalist ancestral state behaved differently under distinct environmental regimes.

### Static conditions

Under one persistent nitrogen limitation, populations rapidly shifted toward asymmetric copy-number states.

By the final time point:

```text
glutamine limitation -> glutamine specialists dominate
proline limitation    -> proline specialists dominate
```

The authors report approximately 90% glutamine specialists in glutamine limitation and approximately 80% proline specialists in proline limitation across the relevant replicates.

### Fluctuating conditions

Under alternating glutamine/proline limitation, balanced generalist CNV classes were predominant for most of the experiment, although some replicates showed transient or late specialist increases.

Thus the bounded pattern is:

```text
persistent single-resource environment
-> asymmetric copy-number specialization

fluctuating two-resource environment
-> balanced copy-number generalism retained / enriched
```

## BALANCE admission

Pattern class:

```text
BOUNDARY_CROSSING
```

The relevant architecture contrast is:

```text
shared/generalist state
= balanced deployment across both task axes

specialist state
= asymmetric deployment toward one task axis
```

The context axis is:

```text
static vs fluctuating nitrogen limitation
```

This is stronger than a purely comparative generalist-specialist association because:

1. the same laboratory background and reporter architecture are used;
2. the same generalist ancestor seeds the evolution experiments;
3. ecological strategy is tied to measured copy-number genotypes;
4. genotype fitness is estimated from abundance change in the same experimental programme;
5. environmental regime changes which strategy is enriched.

## Why this is not direct BALANCE occupancy

The study does not provide the exact Chapter-2 direct object:

```text
W_S*(e)
vs
W_D*(e)
```

for prospectively optimized shared and differentiated architectures across one registered continuous environmental coordinate.

In particular:

- the fluctuating treatment is an environmental regime rather than one scalar `e`;
- specialist/generalist classes are inferred from copy-number balance and enrichment, not from an explicit optimization of all accessible architectures at each context;
- no bounded direct `rho = W_S* - W_D*` interval is estimated;
- the source is a preprint at the audit date.

Therefore the claim ceiling is:

```text
environment-regime-associated generalist <-> specialist architecture transition
NOT direct BALANCE threshold identification
```

## Why this is not hysteresis

The paper uses separate static and fluctuating evolution treatments. It does not take the same evolved population through a prospectively registered forward and reverse environmental path and estimate distinct transition thresholds.

Therefore:

```text
HYSTERESIS_OR_PATH_DEPENDENCE = NOT PROMOTED
```

The authors describe CNVs as enabling reversible toggling at the mechanistic level, but that language is not converted into a Chapter-2 hysteresis receipt.

## Why this is not PAYOFF substitution

The BALANCE row concerns the architecture state within one yeast genome: balanced versus asymmetric transporter copy number.

It does not require specialist subpopulations to coexist through frequency-dependent ecological interactions. Population frequencies are used as evidence of which within-genome strategy is selected under each environment, not as the theoretical Chapter-2 state itself.

## Relation to the Solanum boundary

The two current `BOUNDARY_CROSSING` rows now provide complementary evidence:

```text
Solanum
phylogenetic repeated transition
shared isomorphic stamens -> within-flower feeding/pollinating division of labour

S. cerevisiae CNV
experimental environmental transition
balanced generalist copy number -> asymmetric specialist copy number
```

Solanum is stronger for repeated natural architecture origins. The yeast CNV system is stronger for direct environmental control and same-background experimental evolution, but weaker because it is currently a preprint and does not identify a continuous common-fitness-scale `W_S* / W_D*` threshold.

## Updated R-layer implication

The boundary class is no longer supported by only one floral transition. A second domain now shows that environmental structure can govern whether an integrated/generalist architecture is retained or a specialist architecture is selected.

This does **not** establish natural prevalence or the quantitative BALANCE boundary. The next upgrade remains a study that directly compares shared and differentiated optimized fitness on the same scale across a graded environmental or cost axis.

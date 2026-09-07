# BALANCE empty-class targeted recovery v1

## Purpose

This audit follows the first bounded `R`-layer expansion and searches specifically for evidence that can close theory-linked pattern classes that were still empty.

The admission question is not whether a study contains words such as `generalist`, `specialist`, `duplication`, `modularity`, or `trade-off`. A study enters a BALANCE pattern class only when the biological unit and architecture contrast match the Chapter-2 object closely enough that the class label does not import a PAYOFF population state or a BITA historical analogy by accident.

Current admission result:

```text
PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE    1 newly admitted
DIRECT_DIFFERENTIATION                               1 newly admitted
BOUNDARY_CROSSING                                    0 remains empty
HYSTERESIS_OR_PATH_DEPENDENCE                        0 remains empty
quantitative pooling                                 0 remains empty
```

The current ledger therefore contains 11 independent clusters, of which four carry a middle-regime signature and six remain explicitly unresolved.

---

## A. Persistent integration with an available differentiation route

### Mihajlovic et al. — coGFP direct duplication experiment

Primary source:

```text
Mihajlovic L et al. 2025
A direct experimental test of Ohno's hypothesis
eLife 13:RP97216
DOI: 10.7554/eLife.97216
Version of Record: 2025-04-02
```

### Why this closes a previously empty pattern class

The experimental system physically instantiated both relevant architecture scopes:

```text
one active cogfp copy
vs
exactly two active cogfp copies
```

The protein has two selectable fluorescence activities. Improvement of green fluorescence can reduce blue fluorescence, providing an experimentally documented functional trade-off. Under selection for both green and blue fluorescence, duplication made copy-specific specialization structurally available: one copy could in principle specialize on green and the other on blue.

That expected differentiation did not occur. The authors report no green/blue copy-specific specialization among analyzed individuals carrying two active copies.

Admitted class:

```text
PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE
```

### Claim ceiling

This is a controlled **non-specialization under dual-function selection** result. It is not a direct natural BALANCE occupancy receipt because the selected output is fluorescence rather than organismal fitness and the experiment does not estimate a same-scale `W_S* - W_A*` worldline gap.

The value of the source is narrower and cleaner: an explicit differentiation route was available, conflict was present, and dual-function selection did not automatically produce functional specialization.

---

## B. Direct differentiation after adaptive conflict

### Hittinger & Carroll — GAL1/GAL3 adaptive-conflict resolution

Primary source:

```text
Hittinger CT, Carroll SB. 2007
Gene duplication and the adaptive evolution of a classic genetic switch
Nature 449:677-681
DOI: 10.1038/nature06151
```

### Why this closes the direct-differentiation class

The pre-duplication architecture is a bifunctional GAL1/3-like gene performing both galactokinase and co-induction functions. In the post-duplication Saccharomyces architecture, GAL1 and GAL3 are specialized paralogues.

The study used precise coding- and non-coding-sequence replacements and measured effects on organismal fitness. Its central inference is that duplication allowed resolution of an adaptive conflict in transcriptional regulation, after which regulatory configurations disfavored in the bifunctional state could evolve separately in the specialized paralogues.

Admitted class:

```text
DIRECT_DIFFERENTIATION
```

### Claim ceiling

This is a reconstructed and experimentally interrogated **differentiation endpoint under adaptive conflict**. It does not show that a middle regime was impossible at every historical or ecological context, and it is not used to estimate BALANCE prevalence or a continuous Chapter-2 critical boundary.

---

## C. Candidates deliberately not promoted

### Sandberg et al. 2017 — alternating-carbon E. coli

Primary source:

```text
Sandberg TE, Lloyd CJ, Palsson BO, Feist AM. 2017
Laboratory Evolution to Alternating Substrate Environments Yields Distinct Phenotypic and Genetic Adaptive Strategies
Applied and Environmental Microbiology 83:e00410-17
DOI: 10.1128/AEM.00410-17
```

The matched experimental programme is attractive because the same ancestor and alternating-substrate protocol produced persistent generalists in some carbon-pair contexts and two specialist subpopulations in another.

However, the specialist outcome is a **population split into separate specialist ecotypes that alternate dominance**, not a differentiated architecture inside the same biological unit. Counting that state as BALANCE `BOUNDARY_CROSSING` would import a frequency-dependent/coexistence object that belongs closer to PAYOFF.

Decision:

```text
NOT_ADMITTED_TO_BALANCE_PATTERN_LEDGER
```

This rejection is intentional and is guarded in `tests/test_balance_pattern_readout.py` by keeping `n_boundary_crossing_clusters == 0`.

### S. cerevisiae transporter-CNV generalist/specialist experiment

A recent experimental-evolution preprint reports balanced transporter copy-number ratios in generalists, imbalanced ratios in specialists, static environments favoring specialists, and fluctuating environments favoring generalists.

This is a strong ecological-strategy boundary candidate, but the architecture is already a two-locus resource-acquisition system rather than a clear shared-coordinate conflict followed by within-unit differentiation. It is therefore retained as a retrieval lead rather than used to close `BOUNDARY_CROSSING`.

### PTE forward/reverse enzyme evolution

Forward evolution of phosphotriesterase toward arylesterase produced specialization, whereas reverse evolution recovered a highly bifunctional enzyme through a different mutational route. This is informative about evolutionary reversibility and path dependence.

It does not, however, provide the Chapter-2 hysteresis test required here: the same registered environmental/control variable was not traversed forward and backward while measuring a BALANCE state threshold.

Decision:

```text
HYSTERESIS_OR_PATH_DEPENDENCE remains 0
```

---

## D. Why HisA/TrpF remains unresolved

The Salmonella HisA/TrpF real-time evolution system is unusually informative. Under continuous selection for both activities it produced:

```text
specialist trajectories
specialists after a generalist intermediate
generalist trajectories improving both activities
```

Some evolved duplicated arrays contained complementary specialists in the same clone, while other trajectories retained/improved bifunctionality.

This mixed result is not a failure. It is almost exactly the architecture-choice problem BALANCE wants to explain. But because multiple outcomes occur under the registered selection regime and the available published comparisons do not define one matched static `W_S* / W_A*` ordering, assigning the whole cluster to either persistent integration or direct differentiation would destroy information.

It therefore stays:

```text
UNRESOLVED
```

and becomes a priority source for extracting an explicit architecture-cost / background / lineage moderator rather than another binary example.

---

## Current deterministic readout

After the two admitted additions:

```text
independent clusters                              11
middle-regime signature clusters                   4
  conflict without splitting                       2
  sandwiched transition mosaic                     1
  persistent integration with available route      1
direct differentiation                             1
unresolved                                          6
boundary crossing                                   0
hysteresis / path dependence                        0
quantitative-pool eligible                          0
```

The middle-regime numerator increased from 3 to 4, but this is **not** interpreted as `4/11` natural prevalence because the ledger is targeted and source-adjudicated rather than an exhaustive sampling frame.

---

## New empirical interpretation

The first targeted empty-class search changes the Chapter-2 picture in a useful way:

1. conflict does not force differentiation even when a differentiation route is experimentally available;
2. differentiation can nevertheless resolve an adaptive conflict in another molecular system and can improve organismal performance;
3. therefore the empirical question is no longer merely whether both integrated and differentiated systems exist;
4. the missing object is the **moderator that switches the ranking of these two architecture states**.

That is a stronger target for the next recovery round than collecting additional compromise examples.

## Next gate

The next search should prioritize a single biological system or closely matched family in which the following can be ordered across contexts:

```text
active conflict
shared/generalist architecture
within-unit differentiated architecture
common performance or fitness scale
context variable that changes their ordering
```

A true `BOUNDARY_CROSSING` should not be registered until that architecture-state ordering changes across a declared environmental, resource, or cost axis. A true hysteresis row additionally requires forward/reverse traversal or another design that separates state persistence from ordinary historical contingency.

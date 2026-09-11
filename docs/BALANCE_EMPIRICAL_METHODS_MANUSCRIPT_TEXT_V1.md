# BALANCE empirical synthesis Methods text v1

## Theory-linked evidence synthesis

We designed the empirical synthesis after fixing the theoretical objects of interest. The purpose was not to estimate the publication frequency of multifunctional conflict, nor to treat any example of multifunctionality as evidence for BALANCE. Instead, we translated the theory into observable signatures and asked which of those signatures could be recovered from source-adjudicated biological systems. The empirical sequence was therefore

```text
mathematical mechanism
-> observable signature
-> source-adjudicated pattern ledger
-> compatible quantitative strata
-> residual direct-identification gap.
```

A direct BALANCE receipt requires active conflict (`L>0`) together with a matched same-context worldline ordering in which the optimized differentiated-accessible alternative remains inferior to the optimized shared architecture (`W_D* - W_S* < 0`). Because most published studies do not provide that matched comparison, we retained lower identification layers rather than backfilling missing worldline quantities from unmatched studies.

## Evidence universe and source adjudication

The current synthesis is a bounded, source-adjudicated evidence synthesis rather than an estimate of natural prevalence. We began with primary studies and evidence already audited in the sister SCH and BITA programmes, because those audits contained explicit information on functional roles, trait coordinates, selection direction, fitness interpretation, and source provenance. We then used targeted retrieval to fill theory-linked empty classes, prioritizing persistent integration with an available alternative, boundary crossing, direct differentiation, path dependence, and quantitatively compatible agent-selection designs. Additional source registries were used as search inventories, including experimental floral-selection databases and public-data studies, but database rows or duplicated analysis records were not counted as independent biological evidence.

The unit of replication was the **independent biological cluster**, not the publication, population, site, year, treatment cell, or measured trait. Multiple papers describing one biological programme could contribute to one cluster, and multiple traits from one cluster could not inflate the independent-cluster count. Each cluster was assigned only the strongest pattern class supported by the underlying source audit and was retained at the corresponding claim ceiling. A cluster was never promoted to direct BALANCE occupancy unless a same-context comparable shared-versus-differentiated worldline analysis existed.

## Pattern classification

For each cluster we recorded, where available, whether conflict was present, whether a shared or integrated architecture persisted, whether an alternative or differentiated architecture was present or experimentally accessible, the environmental or geographic context, evidence for transition or boundary states, history or path dependence, study design, and source-verification state. We classified clusters into seven theory-linked pattern classes:

1. `CONFLICT_WITHOUT_SPLITTING`: opposing demands were supported while one shared or integrated architecture persisted;
2. `PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE`: an alternative architecture was available or experimentally accessible but the integrated state persisted in the focal context;
3. `SANDWICHED_TRANSITION_MOSAIC`: shared, intermediate, or differentiated states occurred along an ordered contextual gradient compatible with a middle regime;
4. `BOUNDARY_CROSSING`: the evidence supported a context-dependent transition from a shared toward a differentiated state;
5. `DIRECT_DIFFERENTIATION`: active conflict was associated with a differentiated outcome without a supported middle regime;
6. `HYSTERESIS_OR_PATH_DEPENDENCE`: forward and reverse transitions or historical dependence differed under an otherwise interpretable control axis;
7. `UNRESOLVED`: relevant conflict or architecture information existed but the relative worldline ordering could not be assigned.

The first three classes were treated as middle-regime signatures. `BOUNDARY_CROSSING` and `DIRECT_DIFFERENTIATION` were retained as neighbouring transition classes rather than as middle-regime positives. `UNRESOLVED` clusters remained visible in all evidence maps. Screening controls with no demonstrated conflict were recorded separately and were not treated as failed BALANCE cases.

## Strict Q1B quantitative lane

We defined a stricter quantitative lane, Q1B, to test one prerequisite of BALANCE: recurrence of opposing agent-mediated selection on the same biological coordinate under compatible experimental designs. Q1B did not measure direct BALANCE occupancy. A design-compatible cluster was eligible for screening only when all of the following conditions were met:

- the biological cluster was independent of all other clusters;
- pollinator and antagonist roles were biologically identified;
- both agents acted on the same defined trait coordinate;
- the study supplied a common reproductive-fitness interpretation across the relevant treatment contexts;
- the factorial design supported the same four context-specific mediated-selection contrasts;
- the joint uncertainty of those contrasts was identified from reported sufficient statistics or a preregistered raw-data resampling analysis.

Positive Q1B admission additionally required the frozen opposing-agent pattern on a predeclared shared coordinate. Design-compatible systems that did not satisfy the positive pattern were retained as specificity controls rather than inserted into the positive numerator. Positive admission is therefore outcome-informed by construction. This distinction is essential: the random-effects summary of positive-admitted Q1B systems is a conditional description of effect magnitude and heterogeneity within that admitted class, not an unbiased estimate of the mean effect across all design-eligible systems and not an independent statistical test that the positive pattern recurs.

The registered contrast vector was

```text
pollinator effect | antagonist present
pollinator effect | antagonist absent
antagonist effect | open pollination
antagonist effect | supplemented pollination.
```

We did not cherry-pick one favourable context-specific contrast from a multicontrast study. All registered contrasts were retained. We also did not treat multiple traits from one biological cluster as independent studies.

## Reconstruction of study-level Q1B effects

For *Fragaria vesca*, source-reported factorial contrasts, their standard errors, the combined contrast, and the one-degree-of-freedom pollination-by-herbivory interaction were sufficient to reconstruct the full rank-three joint covariance matrix without assuming zero covariance among contrasts.

For *Gymnadenia conopsea* (2015), Ecological Archives Table A2 supplied linear selection gradients and standard errors for four distinct factorial treatment groups. Because the treatment-group gradients were estimated from different plants, group-level estimates were treated as independent, and the registered Q1B contrasts and their covariance matrix were obtained by linear transformation of the four reported estimates.

For *Impatiens capensis*, we reanalysed the public randomized Robbing × Florivory × Pollination experiment under a preregistered contract. Before examining the Q1B outcome, the analysis was restricted to `Robbing = N`, leaving the randomized Pollination × Florivory 2 × 2 design. The common outcome was chasmogamous fruit rate. Two traits—early-season flower redness and early-season condensed tannins—were predeclared and both were retained. Treatment-cell selection slopes were recomputed and uncertainty was estimated using 2,000 stratified plant-level bootstrap replicates with a frozen random seed. The full joint covariance matrix was retained. For the cross-study Q1B summary, the two predeclared trait vectors were averaged with equal weight to produce one cluster-level *Impatiens* vector; the two traits were never counted as independent biological replications.

## Pooling rule and conditional summary among positive-admitted systems

Pooling was forbidden until at least three independent effect-size-ready positive clusters existed under the same Q1B estimand. The first permitted conditional summary therefore contained *Fragaria vesca*, *Impatiens capensis*, and *Gymnadenia conopsea* 2015 (`k=3`). For each of the four registered contrast components, we fit a componentwise DerSimonian–Laird random-effects model and used a modified Knapp–Hartung interval with `df=2`. Full within-study covariance matrices were preserved for audit and for construction of the registered contrast vectors, but we did not attempt to estimate a full 4 × 4 between-study covariance matrix from only three independent clusters.

We report the componentwise random-effects mean, modified Knapp–Hartung 95% interval, DerSimonian–Laird `tau^2`, Cochran's `Q`, and `I^2`. These quantities summarize magnitude and heterogeneity **conditional on positive Q1B admission**. Because the admission rule already used the focal conflict pattern, neither the sign nor the confidence interval of this conditional pooled mean is interpreted as an unbiased population-average effect or as an independent test of recurrence. Evidence that the pattern recurs comes from its recovery in three independent biological clusters under the frozen admission contract; evidence that it is not inevitable comes from design-matched negative controls. With `k=3`, even the conditional magnitude summaries are interpreted cautiously.

## Specificity controls and adjacent estimands

We retained design-matched negative controls and biologically adjacent estimands outside the strict Q1B numerator. *Trifolium repens* and *Lythrum salicaria* were retained as negative controls because compatible or near-compatible factorial designs did not produce the required same-coordinate positive pattern. These cases test specificity rather than contributing artificial zero-valued effects to a positive-selected pool. Because the negative controls do not supply the same positive-admission estimand as the three admitted systems, the current synthesis does not claim a single design-universe average across positives and negatives.

We also maintained separate lanes for related but non-equivalent biological objects. *Ipomopsis* was classified as a sequential-filter boundary because pollination-stage and seed-predation-stage selection were temporally ordered rather than forming the registered 2 × 2 agent-intervention vector. *Primula farinosa* was retained as a discrete-morph conflict because the focal estimand was relative fitness of genetically based alternative morphs rather than a continuous standardized selection gradient. A 2019 *Gymnadenia* study was retained as an attribution boundary because statistical opposition between pollinator and residual nonpollinator selection did not identify the residual biological agent as an antagonist. None of these lanes was allowed to increase Q1B `k`.

## Heterogeneity and moderator gate

We froze the first moderator set before adding further positive clusters. The only moderators eligible for the first heterogeneity analysis are antagonist type, focal trait class, reproductive fitness component, pollination-manipulation class, and effect-source class (reported-statistic reconstruction versus preregistered raw-data reanalysis). At `k=3` or `k=4`, moderators are descriptive only: no subgroup test, meta-regression coefficient, or moderator `P` value is permitted. A first exploratory moderator model is allowed only at `k>=5`, and only when at least two levels of a moderator are each represented by at least two independent biological clusters. With fewer than eight clusters, such analyses remain exploratory and cannot support an absence-of-heterogeneity claim.

## Evidence-map summaries

For the broad pattern ledger, we generated deterministic summaries of independent-cluster counts by pattern class, biological domain, confidence, and context axis. These counts were used to visualize recurrence within the screened evidence universe. They were not converted into proportions intended to estimate natural prevalence because the source universe was assembled through bounded source adjudication and targeted theory-linked retrieval rather than probability sampling of natural systems or an exhaustive unbiased publication universe.

We also generated a reality-boundary readout that explicitly separated strict Q1B positives, design-matched negative controls, estimand boundaries, and antagonist-attribution failures. This readout was used to prevent incompatible evidence from entering the same numerical numerator merely because it displayed superficially similar signs or biological narratives.

## Reproducibility and fail-closed promotion

All promoted quantitative receipts, contrast reconstructions, covariance matrices, pooling inputs, and pattern-class counts were stored as machine-readable repository artifacts and guarded by regression tests. Figures were generated from those frozen ledgers rather than from manually entered summary numbers. Promotion rules were fail-closed: missing joint uncertainty, unresolved antagonist identity, an incompatible estimand, or a non-independent biological unit prevented promotion rather than being replaced by a convenient independence assumption or qualitative reinterpretation.

## Claim ceiling and final direct-validation layer

The literature synthesis can test recurrence of conflict-compatible and persistence signatures and can delimit empirical boundary classes. It does not identify direct BALANCE occupancy from unmatched systems. In particular, we did not estimate `W_S*`, `W_D*`, `rho`, `Phi`, `xi`, or `d_B` by combining studies that measured different architectures, contexts, or fitness scales.

The remaining direct empirical target is therefore a same-context, common-fitness-scale comparison of an optimized shared architecture and a registered accessible differentiated alternative, together with independent evidence that conflict is active and joint uncertainty for the worldline difference. Focal experiments such as the registered *Pedicularis* programme are reserved for this final identification problem after literature-based pattern recovery, not used as the initial empirical justification for the general theory.

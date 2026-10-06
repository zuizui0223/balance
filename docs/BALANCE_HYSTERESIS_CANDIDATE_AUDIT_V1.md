# BALANCE strict empirical hysteresis candidate audit v1

## Purpose

Issue #24 requires a real within-unit architecture hysteresis receipt, not generic biological memory.

A candidate is promotable only if the same biological unit can occupy alternative shared/generalist versus differentiated/specialized architecture states along one registered control axis, with forward and reverse histories reaching comparable control values and with a defensible threshold separation plus uncertainty.

This audit records six superficially attractive hysteresis systems and keeps all six below the BALANCE promotion threshold.

Machine-readable ledger:

`data/BALANCE_HYSTERESIS_CANDIDATE_AUDIT_V1.csv`

## Candidate 1 — HL60 DMSO differentiation

Chang et al. (2006), *Multistable and multistep dynamics in neutrophil differentiation*.

- forward experiment: increasing DMSO exposure;
- backward experiment: maximally differentiated cells washed and restimulated across the same DMSO range;
- readout: stationary-state CD11b-high fraction;
- result: response at a given DMSO level depends on treatment history.

This is a strong empirical hysteresis control because the same cell line is driven forward and backward along one experimental stimulus. It is **not** promoted because the observed states are differentiation-marker states, not a registered shared-versus-differentiated multifunctional architecture under one BALANCE conflict coordinate.

## Candidate 2 — yeast phosphate-transporter switching

Wykoff et al. (2007), *Positive Feedback Regulates Switching of Phosphate Transporters in S. cerevisiae*, DOI `10.1016/j.molcel.2007.07.022`.

The PHO network switches between low- and high-affinity phosphate-transporter usage across phosphate availability, with bistability and hysteresis reported for feedback-perturbed cells.

This is biologically closer to an architecture problem because alternative transporter systems are deployed. It is still not promoted:

1. the paper does not provide the registered empirical forward/reverse threshold pair required by Issue #24;
2. the focal hysteresis interpretation is strongest in a feedback-perturbed `pho84Δ` background;
3. high- versus low-affinity uptake states are alternative nutrient-uptake strategies, not yet a demonstrated resolution of one shared multifunctional conflict into differentiated architecture.

## Candidate 3 — locust phase change

Topaz et al. (2012), *Locust Dynamics: Behavioral Phase Change and Swarming*, DOI `10.1371/journal.pcbi.1002642`.

The model predicts a higher density for formation of a gregarious aggregation than for its breakup during density reduction.

This is not promoted because the reported forward/reverse density hysteresis is a numerical-model property at the population/aggregation level. It is not an empirical threshold receipt for one biological unit's architecture.

Experimental locust work does show history-dependent gregarization/solitarization rates, but does not supply the required matched forward/reverse architecture threshold with uncertainty.

## Candidate 4 — tree hydraulic absorption/desorption

Brum et al. (2026), *Employing a Hysteresis Approach to Analyze Shifts in Tree Physiological Thresholds in Response to Drought*, DOI `10.1111/pce.70498`.

This is a strong real-data hysteresis study. The same trees traverse absorption/desorption cycles and the analysis estimates physiological thresholds and hysteresis properties under drought.

It is not a BALANCE architecture receipt because the states are hydraulic flow/storage states rather than shared versus differentiated functional architectures.

## Candidate 5 — cherry-plum dehydration/rehydration

Xu et al. (1999), DOI `10.2503/jjshs.68.228`.

Soil matric potential is traversed through drying and rewetting and water-status variables show hysteresis-like relationships.

Again, this is a useful physiological-history control, not a shared/differentiated architecture transition.

## Candidate 6 — Bacillus subtilis cell-type switching

Tasaki et al. (2025), *Necessary and sufficient condition for hysteresis in the mathematical model of the cell type regulation of Bacillus subtilis*, DOI `10.1007/s00285-025-02316-8`, together with the experimental companion on cyclic colony migration and environmental pH (bioRxiv `10.1101/2020.09.11.292474`).

This is the closest architecture-level candidate in the current audit. Migrating colonies are dominated by motile cells, whereas non-migrating states are dominated by matrix producers, so the system contains a real cell-type division-of-labour axis rather than only a physiological scalar.

It is still **not** promoted. The forward/reverse hysteresis threshold pair is derived for the cell-type regulation model as autoinducing signal varies. The corresponding culture experiments quantify cyclic migration and pH-dependent colony-state transitions, including loss of periodic colony formation at low pH, but do not provide a matched empirical increase/decrease sweep with two architecture thresholds and threshold-separation uncertainty.

So this candidate closes an important loophole:

```text
architecture-like cell-type specialization
+ empirical environmental switching
+ model hysteresis
!= empirical architecture hysteresis receipt
```

## Result

```text
screened named candidates     6
promoted BALANCE hysteresis   0
```

The empirical hysteresis ledger therefore remains at zero.

## Search implication

Future screening should prioritize systems where:

1. the architecture itself changes state, not only a physiological output;
2. both architecture states belong to the same biological unit/family;
3. one graded control variable is traversed in both directions;
4. forward and reverse architecture boundaries can be estimated;
5. threshold uncertainty is recoverable;
6. the phenomenon is not merely population coexistence, collective aggregation, or gene-expression memory.

The strongest remaining target class is therefore an experimentally reversible modularity/specialization system rather than another generic hysteresis paper.

## Claim ceiling

Negative-screen audit only. The cited systems demonstrate biological hysteresis or path dependence at other organizational levels; none is claimed to instantiate BALANCE architecture hysteresis.

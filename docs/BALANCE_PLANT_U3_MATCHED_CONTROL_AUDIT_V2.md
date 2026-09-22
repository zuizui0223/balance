# BALANCE plant U3 matched-control audit v2

## Current state

The six source-resolved U3 heteranthery cases now all have one preregistered PRIMARY control candidate.

```text
registered species cases                  6
cases with SCREENED/ADJUDICATED control   6
cases without any primary control         0
adjudicated primary pairs                 0
case-control layer closed?                NO
```

This closes **control discovery**, not control adjudication.

Canonical registry:

```text
data/BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv
```

## Registered pairs

1. `Solanum rostratum` -> `Solanum lycocarpum`
2. `Melastoma malabathricum` -> `Osbeckia chinensis`
3. `Monochoria korsakowii` -> `Monochoria australasica`
4. `Monochoria vaginalis` -> `Monochoria australasica`
5. `Senna alata` -> `Senna surattensis`
6. `Senna bicapsularis` -> `Senna surattensis`

All remain `SCREENED` and `BLINDED`.

Shared controls are explicit:

- the two `Monochoria` cases share `M. australasica`;
- the two `Senna` cases share `S. surattensis`.

Those pairs cannot be treated as four independent control lineages in later modelling.

## Melastoma pair — newly closed discovery gap

### Case

`Melastoma malabathricum` is the U3 direct division-of-labour case from Luo, Zhang & Renner (2008), with experimentally supported feeding-versus-pollinating anther function.

### Control candidate

`Osbeckia chinensis`.

The control was selected before BALANCE predictor extraction and passes the three discovery criteria from independent source surfaces.

#### Phylogenetic proximity

Chen et al. (2025), TAXON, DOI `10.1002/tax.13349`, recover the `Osbeckia chinensis + O. nepalensis` lineage as sister to `Melastoma` within the Asian Melastomateae.

The match is therefore registered at:

```text
SAME_TRIBE_SUBFAMILY
```

rather than falsely labelled congeneric or species-sister.

#### Absence of case-defining heteranthery

Flora of China describes `Osbeckia` stamens as:

```text
isomorphic
equal or subequal
```

This directly excludes the discrete feeding-versus-pollinating stamen differentiation used to define the `Melastoma malabathricum` case architecture.

#### Animal-pollination eligibility

van der Pijl (1939) directly observed multiple hymenopterans visiting `O. chinensis`.

Bee-sized visitors landed on the stamen bundle; its displacement brought the visitor's abdominal surface into contact with the stigma while pollen was removed from the poricidal anthers.

This is sufficient for the U3 minimal animal-pollination eligibility screen.

## Why all six remain SCREENED

A complete candidate registry is not an adjudicated matched design.

The next gate is pair-by-pair adjudication of:

1. whether the registered control is the closest defensible non-heterantherous comparator under the frozen hierarchy;
2. whether a closer candidate was omitted;
3. whether animal-pollination eligibility and heteranthery absence are source-secure;
4. whether the deterministic tie-break was applied correctly;
5. whether any predictor information leaked into control selection.

Only after that audit can a pair move to `ADJUDICATED`.

## Revised executable readout

`balance_domain/plant_u3_controls.py` now distinguishes:

```text
n_cases_with_registered_primary_control
cases_without_registered_primary_control
screened_control_coverage_complete

from

n_cases_with_adjudicated_primary_control
unmatched_case_taxa
case_control_layer_closed
```

This prevents "we found a plausible control" from being silently equated with matched-design closure.

## Current result

```text
screened_control_coverage_complete = true
case_control_layer_closed          = false
```

The U3 bottleneck has therefore moved from **finding controls** to **adjudicating the six fixed matches**.

## Claim ceiling

U3 remains an outcome-selected case-control development lane.

Even after adjudication it may estimate associations conditional on these heteranthery-positive cases and their registered relatives. It does not estimate heteranthery prevalence or historical transition probabilities.

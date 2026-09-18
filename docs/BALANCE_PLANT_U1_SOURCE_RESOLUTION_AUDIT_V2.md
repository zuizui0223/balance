# BALANCE plant U1 source-resolution audit v2

## Current state

The first outcome-blind U1 surface now has three separately versioned layers:

```text
review universe
-> provisional first-20 taxon-label sample
-> primary-source resolution ledger
```

Files:

- `data/BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv`
- `data/BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv`
- `data/BALANCE_PLANT_U1_SOURCE_RESOLUTION_V1.csv`

The handoff is verified by `balance_domain/plant_u1.py`.

## Review-frame reconciliation

Haas & Lortie (2020) report:

```text
47 plant taxa
59 included studies
```

The current figure-network extraction has:

```text
44 taxon labels
```

Therefore:

```text
reconciliation gap = 3
```

The confirmatory U1 frame is not frozen.

## Provisional double-code sample

The current 20-row sample is the first 20 **raw taxon labels** in lexicographic order.

This is intentionally downgraded from a frozen dependency-group sample because the review supplement has not yet reconciled taxonomic grain.

Hard cases are retained. No taxon is replaced because its primary source is difficult to resolve.

## Primary-source resolution

Current first-20 status:

```text
screen-ready resolved primary sources   10
not yet screen-ready                    10
```

Screen-ready requires:

1. exact primary study identified;
2. primary citation frozen;
3. source status `RESOLVED_PRIMARY`;
4. taxon reconciliation `CLEAR`.

A DOI is preferred but not required when a stable bibliographic primary citation exists.

## Explicit Alstroemeria grain problem

Both of the following labels occur in the provisional extraction/sample:

```text
Alstroemeria ligtu
Alstroemeria ligtu var. Simsii
```

Both currently resolve to:

```text
Botto-Mahan et al. 2011
Floral Herbivory Affects Female Reproductive Success and Pollinator Visitation...
DOI 10.1086/662029
```

The paper title uses `Alstroemeria ligtu`, while the study material is described at the `var. simsii` level.

These two rows therefore remain:

```text
screen_ready = false
```

until the Haas & Lortie supplementary study/taxon mapping establishes whether they are:

- duplicate labels for one biological dependency group;
- two distinct study records at different taxonomic grain;
- or a figure-text extraction artefact.

## Resolved high-information first-20 sources

Examples now frozen in the source ledger include:

- `Aechmea pectinata`: florivory by *Armases* affecting hummingbird visits;
- `Alstroemeria aurea`: flowering-shoot defoliation affecting pollen performance;
- `Alstroemeria umbellata`: aphid × pollinator exclusion study;
- `Brassica nigra`: folivory changing floral chemistry and pollinator behaviour;
- `Calyptrogyne ghiesbreghtiana`: floral herbivory, pollen availability and bat visitation;
- `Castilleja indivisa`: alkaloid uptake changing herbivory and pollinator visitation;
- `Centaurea solstitialis`: biocontrol attack and pollen limitation;
- `Centrosema virginianum`: experimental florivory effects on pollination;
- `Cucumis sativus`: above/below-ground herbivory × pollination experiment;
- `Cucurbita moschata`: leaf/root herbivory × pollination experiment.

These sources make the taxon **screenable**. They do not make it BALANCE-positive.

## Remaining source-resolution classes

Unresolved taxa are not exclusions.

They stay in one of:

```text
SOURCE_RESOLUTION_PENDING
CANDIDATE_SOURCE_FOUND
```

Candidate-source status means a biologically relevant paper was located but its exact linkage to the systematic-review record has not yet been verified.

## Freeze rule

The double-code sample remains unfrozen until all of the following close:

```text
review taxon reconciliation gap == 0
taxon-grain conflicts == 0
all 20 sampled rows have screen_ready == true
```

This is intentionally strict. A smaller convenience sample would undermine the outcome-blind denominator.

# BALANCE macro pilot search protocol v1

## Purpose

Build a screened multifunctionality universe that is independent of the existing BALANCE positive-pattern ledger.

This is a **pilot discovery protocol**, not the confirmatory search freeze. Its purpose is to test whether the macro codebook works across biological domains before the full search strategy is preregistered.

## Pilot strata

The pilot begins with three deliberately different strata.

### P1 — plant reproductive / attraction structures

Target systems in which one plant phenotype or coordinated structure contributes to two functions that can impose conflicting demands.

Priority source families:

- pollination versus herbivory / florivory / seed predation;
- pollination versus abiotic protection or water economy;
- carnivorous-plant pollination versus prey capture;
- differentiated floral modules such as heteranthery;
- shared floral chemical or visual signals with multiple ecological receivers.

Pilot search concept:

```text
(multifunction* OR "functional conflict" OR trade-off OR compromise OR "conflicting selection")
AND
(flower* OR floral OR inflorescence OR trap OR carnivorous)
AND
(pollinat* OR herbiv* OR floriv* OR predat* OR prey OR defence OR defense)
```

Negative/aligned cases are retained.

### P2 — animal feeding / signalling structures

Target structures whose mechanics or morphology serve more than one performance axis.

Priority source families:

- prey capture versus prey processing in jaw systems;
- feeding morphology versus acoustic signalling in bird beaks;
- other repeated structures with evidence for functional decoupling, integration, or division of labour.

Pilot search concept:

```text
("functional decoupling" OR "evolutionary decoupling" OR multifunction* OR trade-off OR "division of labor")
AND
(jaw OR beak OR feeding OR trophic OR appendage)
AND
(capture OR processing OR song OR signal OR performance)
```

The pilot must retain studies that challenge complete decoupling, because residual integration is informative for the BALANCE question.

### P3 — molecular / gene architecture

Target ancestral or extant multifunctional genes/proteins for which duplication, specialization, or retained generalism is documented.

Priority source families:

- escape from adaptive conflict;
- ancestral bifunctionality followed by gene duplication and specialization;
- experimentally accessible duplication without specialization;
- generalist versus specialist molecular architectures under different environments.

Pilot search concept:

```text
("adaptive conflict" OR "escape from adaptive conflict" OR bifunctional OR multifunctional)
AND
(gene duplication OR duplicate* OR specialization OR subfunctionalization)
```

## Anchor sources

The pilot uses high-information reviews and comparative papers as discovery anchors, then follows references backward and forward.

Anchor use is discovery only. Being cited by an anchor does not make a biological system analysis eligible.

### Plant anchors

- Jürgens et al. 2012, *Biological Reviews*: pollinator-prey conflict in carnivorous plants.
- Zamora 1999, *Ecology*: environment-dependent pollinator-prey conflict in *Pinguicula vallisneriifolia*.
- El-Sayed et al. 2016, *Scientific Reports*: spatial, visual and chemical separation of flowers and traps in *Drosera*.
- Kessler et al. 2009, *Functional Ecology*: conflicting pollinator/herbivore selection on floral chemical traits.

### Feeding / signalling anchors

- Ronco et al. 2021, *Evolution Letters*: evolutionary decoupling of oral and pharyngeal jaws across Lake Tanganyika cichlids.
- Conith & Albertson 2021, *Nature Communications*: persistent evolutionary/genetic coupling of cichlid oral and pharyngeal jaws.
- Podos 2001, *Nature*: correlated beak morphology and song evolution in Darwin's finches.
- Friedman et al. 2019, *Proceedings B*: multifunctional beak evolution across foraging, thermoregulation and song.

### Molecular anchors

- Des Marais & Rausher 2008, *Nature*: escape from adaptive conflict after duplication in an anthocyanin-pathway gene.
- Sikosek et al. 2012, *PLoS Genetics*: theory of escape from adaptive conflict, functional trade-offs and mutational robustness.
- the existing BALANCE GAL1/GAL3, HisA/TrpF and coGFP audits are retained as repository-internal discovery seeds.

## Screening sequence

For each candidate:

```text
S0  same declared structure/coordinate serves >=2 functions?
 |
 +-- no -> EXCLUDE_NOT_MULTIFUNCTIONAL
 |
 v
S1  evidence that the functional demands oppose one another?
 |
 +-- aligned -> retain ALIGNED_NO_CONFLICT
 +-- absent/weak -> retain NO_DEMONSTRATED_CONFLICT
 +-- unresolved -> retain UNRESOLVED
 +-- positive -> continue
 |
 v
S2  architecture state identifiable?
 |
 +-- shared/integrated
 +-- regulatory or temporal separation
 +-- spatial compartmentalization
 +-- partial structural differentiation
 +-- separate modules
 +-- polymorphic
 +-- unresolved
 |
 v
S3  code accessibility / coupling / environmental moderators independently of the outcome where possible
```

## Pilot target

Screen approximately 40 clusters before revising the codebook.

Minimum composition target for codebook stress testing:

- >= 15 plant reproductive/attraction systems;
- >= 10 animal feeding/signalling systems;
- >= 10 molecular/gene systems;
- >= 5 aligned, negative, or unresolved conflict controls overall;
- both structurally differentiated and non-differentiated outcomes represented.

These are pilot stress-test targets, not prevalence weights and not confirmatory quotas.

## Duplicate handling

### Same species, same structure, same function pair, same state

Merge papers into one cluster and increment evidence-source count.

### Same species but biologically distinct context changes the conflict or architecture state

Retain separate context rows only if the context contrast is itself part of the comparative estimand. Link them through a shared parent-system identifier in the adjudication notes.

### Comparative radiation papers

Do not automatically create one row per species.

A radiation-level source may be:

- one discovery record;
- multiple species-level rows only when species-level architecture and predictor coding are independently recoverable;
- a phylogenetic comparative dataset handled in a dedicated within-clade analysis instead of flattened into pseudo-independent macro rows.

## Evidence preference

Within each candidate cluster, prioritize:

1. direct experiment / manipulation;
2. phylogenetic comparative test with explicit function mapping;
3. repeated environmental or population comparison;
4. observational selection / performance study;
5. narrative or review-only evidence.

Reviews are discovery tools unless they contain extractable primary evidence.

## Primary exclusion reasons

```text
EXCLUDE_NOT_MULTIFUNCTIONAL
EXCLUDE_DIFFERENT_TRAITS_NO_SHARED_COORDINATE
EXCLUDE_NO_ARCHITECTURE_INFORMATION
EXCLUDE_DUPLICATE_CLUSTER
EXCLUDE_ONLY_THEORETICAL_EXAMPLE
EXCLUDE_NONBIOLOGICAL_CONSTRUCT_OUTSIDE_DECLARED_SCOPE
```

A conflict-negative candidate is not an exclusion merely because BALANCE cannot apply.

## Pilot outputs

After the first 40 screened clusters report:

- conflict-status distribution;
- architecture-state distribution;
- missingness for each predictor;
- fraction reaching the primary outcome gate;
- domain-specific coding failures;
- duplicate-collapse rate;
- disagreement rate under independent double coding;
- whether the five registered macro hypotheses remain measurable without circular coding.

No primary hypothesis test is licensed until the pilot codebook is frozen.

# BALANCE plant U1 provisional source-screening diagnostic v1

## Scope

This diagnostic applies the plant macro codebook to the **provisional first 20 network-visible U1 taxa** after primary-source resolution.

The U1 full 47-taxon review universe is still not reconstructed because three Haas & Lortie (2020) taxa occur outside the Figure 4 network-visible subset.

Therefore:

```text
this is a codebook / specificity diagnostic
!=
the frozen confirmatory U1 sample
```

Every row remains nonconfirmatory.

## Source status

The provisional first 20 are all source-ready:

```text
primary source resolved   20 / 20
```

The screen is stored in:

```text
data/BALANCE_PLANT_U1_SCREENING_PROVISIONAL_V1.csv
```

## S0 — shared reproductive coordinate

The first gate asks a stricter question than the Haas & Lortie review:

> Do the antagonist and pollination functions act through one identifiable shared reproductive structure, trait coordinate, display, or chemical phenotype?

Result:

```text
SCREENED through S0       7
EXCLUDED at S0           13
TOTAL                    20
```

The 13 exclusions are retained in the review denominator with:

```text
EXCLUDE_DIFFERENT_TRAITS_NO_SHARED_REPRODUCTIVE_COORDINATE
```

They are not biological negatives. They answer a different interaction question.

## Why the S0 exclusions matter

Several high-quality herbivory-pollination studies fail the BALANCE shared-coordinate estimand even though they show ecologically important cross-process effects.

Examples:

- *Alstroemeria aurea*: flowering-shoot defoliation changes pollen quality/performance;
- *Brassica nigra*: leaf folivory changes floral chemistry and pollinator behaviour;
- *Cucumis melo*: damage and supplemental pollination jointly determine tolerance;
- *Cucumis sativus*: above/below-ground herbivory interacts with pollination/reproduction;
- *Cucurbita moschata*: leaf/root herbivory changes plant performance but does not alter pollinator visitation or measured floral traits;
- grazing/pollination comparisons in *Aristotelia chilensis*, *Berberis darwinii* and *Cynanchum diemii*.

These systems demonstrate:

```text
herbivory x pollination interaction
!=
shared-coordinate functional conflict
```

This distinction is one of the main empirical reasons the BALANCE macro study needs its own screening layer instead of treating an existing meta-analysis as ready-made data.

## Conflict screen among the provisional 20

No row is promoted to positive conflict.

Across all 20:

```text
POSITIVE                    0
ALIGNED_NO_CONFLICT         1
NO_DEMONSTRATED_CONFLICT    5
UNRESOLVED                 14
```

The 14 unresolved rows include the 13 S0 exclusions, because no statement about shared-coordinate conflict is licensed once the shared-coordinate estimand fails.

## Retained specificity cases

### Castilleja indivisa — aligned multifunctionality

Experimental alkaloid uptake:

- decreases herbivory;
- increases pollinator visitation;
- increases lifetime seed production.

The two ecological interactions point in the same fitness direction.

Therefore:

```text
conflict_status = ALIGNED_NO_CONFLICT
```

This is a particularly useful control against the assumption that every defense-pollination interaction creates antagonistic selection.

### Aechmea pectinata

Florivorous crabs damage flowers and reduce hummingbird visitation.

The same reproductive unit is involved, but the source does not identify a heritable floral coordinate with opposing preferred states.

```text
NO_DEMONSTRATED_CONFLICT
```

### Alstroemeria ligtu var. Simsii

Damage to the nectar-guide tepals lowers attractiveness and reproductive success.

The experiment identifies the pollination function of the guide and the consequence of florivore damage; it does not demonstrate that florivores favour a contrasting guide phenotype.

```text
NO_DEMONSTRATED_CONFLICT
```

### Bouvardia ternifolia

The distylous morphs show similar floral display, antagonist intensity and reproductive output.

The floral polymorphism is retained as an observed architecture, but antagonist effects do not supply a conflict-positive call.

### Centaurea solstitialis

Biocontrol infection reduces inflorescence number and can increase pollen limitation.

Inflorescence display links the processes, but the pathogen does not establish an opposing preferred display state.

### Centrosema virginianum

Florivory damages flowers, reduces pollinator visitation and lowers fruit/seed production.

This is strong same-flower ecological coupling, but damage to an attractive flower is not equivalent to evidence that pollinators and florivores favour opposite trait values.

## One unresolved retained candidate

*Calyptrogyne ghiesbreghtiana* is retained as:

```text
conflict_status = UNRESOLVED
```

because bats and floral herbivores respond to aspects of inflorescence display, but the source does not establish one identical display coordinate with directly opposing optima.

This is exactly the kind of case that should remain visible rather than being promoted or discarded.

## Implication for the plant macro programme

The provisional U1 result is not “BALANCE conflict is rare”.

The licensed conclusion is narrower and more useful:

> A broad herbivory-pollination literature universe has low direct yield for the **shared-coordinate conflict estimand** unless a dedicated source-level screening gate is applied.

U1 and U2 therefore play different roles:

```text
U1:
broad ecological interaction universe
-> strong specificity / estimand screen

U2:
mechanism-targeted sexual-interference universe
-> higher direct conflict yield but many unresolved cases
```

The contrast must not be interpreted as a prevalence comparison because U1 is still provisional and the two review universes use different inclusion criteria.

## Next gate

U1 remains blocked from formal independent double coding until the complete 47-taxon review universe is reconstructed and the deterministic first-20 dependency-group sample is recalculated.

The current 20-row screen remains valuable as a codebook stress test and will be replaced or reconciled—not silently retained—if the full-47 reconstruction changes sample membership.

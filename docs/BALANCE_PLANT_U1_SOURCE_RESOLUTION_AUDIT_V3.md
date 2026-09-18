# BALANCE plant U1 source-resolution audit v3

## Correction to the U1 universe interpretation

The current 44 registered labels are **not a failed extraction of a 47-taxon Figure 4**.

Haas & Lortie (2020) report 47 plant taxa across the full 59-study systematic-review set, but the Figure 4 caption explicitly states that plant species from studies with no actual herbivore or pollinator taxa are omitted from the interaction network—for example, studies using artificially mimicked herbivory and passive or supplemental hand pollination.

Therefore the current registry is correctly described as:

```text
U1 network-visible taxon labels = 44
full review-reported plant taxa = 47
supplement-only taxa to recover = 3
```

The three additional taxa must be recovered from the review supplementary study/taxon mapping, not guessed from Figure 4.

## Current first-20 primary-source resolution

After a second source-resolution pass:

```text
screen-ready primary-source rows = 15 / 20
blocked or pending                = 5 / 20
```

Newly resolved rows:

### Aristotelia chilensis

Vázquez & Simberloff (2004), *Ecological Monographs* 74:281–308, DOI 10.1890/02-4055.

The study compares grazing, pollinator visitation, pollen deposition and reproduction across 11 animal-pollinated understory plant species and explicitly includes *Aristotelia chilensis*.

### Berberis darwinii

The same Vázquez & Simberloff (2004) multi-species primary study explicitly includes *Berberis darwinii* and also reports pollinator-dependence experiments.

One paper can support several species records without turning those records into independent publications; species remain separate biological dependency groups.

### Bouvardia ternifolia

Salinas-Esquivel, Lara & Arizmendi (2018), *Botanical Sciences* 96:1–10, DOI 10.17129/botsci.1031.

The study measures nectar larceny, foliar herbivory, seed predation, floral-morph context and reproductive output.

### Cardus thoermeri

Chalcoff, Lescano & Devegili (2019), *Plant Ecology* 220:125–134, DOI 10.1007/s11258-019-00907-2.

The study combines aphid/ant context with pollinator access and reproductive outcomes.

### Cnidoscolus aconitifolius

Arceo-Gómez, Parra-Tabla & Navarro (2009), *Biotropica* 41:435–441, DOI 10.1111/j.1744-7429.2009.00502.x.

The experiment applies defoliation treatments across three populations and measures sexual expression and pollinator visitation.

## Remaining first-20 unresolved work

Still blocked or not fully source-linked:

- `Alstroemeria ligtu` versus `A. ligtu var. Simsii`: taxon-grain duplication conflict;
- `Brassica napus`: exact review-linked primary source unresolved;
- `Clarkia xantiana ssp. xantiana`: candidate herbivory/pollen-supplementation source requires exact review linkage;
- `Cucumis melo`: pollination source found but exact herbivory-pollination review source unresolved.

Because the two *Alstroemeria* labels currently resolve to the same primary paper and DOI, they remain blocked rather than being counted twice.

## Double-code sample status

The 20-label sample remains provisional:

```text
PROVISIONAL_FIRST_20_TAXON_LABELS_LEXICOGRAPHIC_PENDING_U1_RECONCILIATION
```

Source-ready rows are marked `SOURCE_READY_SAMPLE_NOT_FROZEN`, but independent double coding should not begin as the formal reliability sample until:

1. the three supplement-only taxa are recovered;
2. *Alstroemeria* taxon grain is reconciled;
3. the first-20 dependency-group sample is recomputed from the complete 47-taxon frame;
4. every selected dependency group has an identified primary study.

This preserves the outcome-blind selection rule even when source resolution is inconvenient.

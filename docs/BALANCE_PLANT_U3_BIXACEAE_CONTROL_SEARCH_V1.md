# BALANCE U3 Bixaceae prospective control search v1

## Frozen case

The first prospective routing-expansion case is `Amoreuxia wrightii`.

No conflict-strength or routing-architecture value from any prospective control is used in this search.

## Nearest candidate

Johnson-Fulton & Watson (2017; DOI `10.1600/036364417X695457`) recover monophyletic Amoreuxia within a paraphyletic Cochlospermum and place `C. tetraporum` outside the core Cochlospermum clade; the published topology summary identifies `C. tetraporum` as the sister candidate to Amoreuxia in the relevant analysis.

Flora Neotropica morphology for `C. tetraporum` gives a continuous filament range (5–8 mm) and anther range (2.5–3.5 mm), unlike the discrete dimorphic fertile-stamen sets defining Amoreuxia.

Therefore:

```text
Cochlospermum tetraporum
  phylogenetic proximity    PASS
  heteranthery absence      PASS
  animal pollination        OPEN
  selection                 OPEN
```

Searches under the accepted name and the synonyms `C. argentinense`, `Maximilianea tetrapora`, and `M. argentinensis` recovered no species-level effective-pollination source.

## Fallback candidates

Two farther controls already pass the minimal biological opportunity gate:

### Cochlospermum orinocense

A species-level reproductive-biology study reports roughly 160 fertile poricidal anthers and predominant pollination by solitary `Centris` bees.

### Cochlospermum vitifolium

Roubik et al. (1982; DOI `10.2307/1936792`) identify `Centris` bees as the most important pollinators in a direct species-level study. Core Cochlospermum retains the ancestral uniform-stamen state recovered by Johnson-Fulton & Watson.

Neither fallback is promoted.

The matching protocol ranks phylogenetic proximity before source quality, so stronger ecological documentation cannot let a farther candidate jump over a closer eligibility-OPEN candidate.

## Current blocker

```text
CLOSEST_C_TETRAPORUM_ANIMAL_POLLINATION_ELIGIBILITY_OPEN
```

A public-retrieval ceiling is registered for the missing `C. tetraporum` species-level pollination receipt.

The Bixaceae queue remains `IN_PROGRESS`, and the prospective programme does not advance to Brassicaceae merely because its control search might be easier.

## Claim ceiling

This audit freezes candidate ordering and the current ecological-eligibility blocker. It does not select a control and does not extract conflict strength or routing architecture.

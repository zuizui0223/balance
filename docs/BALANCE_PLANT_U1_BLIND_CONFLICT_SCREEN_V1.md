# BALANCE plant U1 strict blind conflict screen v1

## Purpose

Apply the BALANCE conflict gate to the provisional first 20 outcome-blind U1 review taxa **without promoting herbivore-pollinator interaction into functional conflict by association**.

U1 membership means only that a study jointly considered herbivory and pollination-related outcomes.

BALANCE requires a stronger object:

```text
one shared plant trait / coordinate
+
function-specific demands on that coordinate
+
evidence that those demands oppose one another
```

Damage that reduces pollination is not automatically a functional conflict.

## Provisional first-20 result

The strict screen returns:

```text
POSITIVE                    0
ALIGNED_NO_CONFLICT         1
NO_DEMONSTRATED_CONFLICT   18
UNRESOLVED_CANDIDATE        1
```

Decisions:

```text
FAIL_CONFLICT_GATE   19
HOLD_FOR_FULL_TEXT    1
PASS_CONFLICT_GATE    0
```

This is a provisional blind screen of the current network-visible first 20. It is not the formal independent double-code result because the complete 47-taxon U1 universe is not yet reconstructed.

## Why most U1 systems fail the BALANCE conflict gate

Most primary studies ask questions of the form:

```text
herbivory / florivory
-> pollinator visitation or pollen limitation
-> reproductive success
```

This establishes an ecological interaction pathway.

It does **not** establish:

```text
trait z increases function A
trait z decreases function B
```

or two distinct function-specific optima on the same trait.

Examples:

- florivory in *Aechmea pectinata* damages floral structures and reduces hummingbird visits;
- florivory in *Centrosema virginianum* reduces pollinator visitation and seed production;
- pathogen attack in *Centaurea solstitialis* reduces inflorescence number and can increase pollen limitation;
- supplemental pollination can compensate damage in *Cucumis melo*.

These are biologically important herbivore-pollinator effects, but they do not by themselves identify BALANCE conflict.

## Aligned specificity control

*Castilleja indivisa* is especially informative.

Alkaloid uptake:

```text
herbivory down
pollinator visitation up
lifetime seed production up
```

The same chemical state benefits both interaction channels in the reported experiment.

It is therefore coded:

```text
ALIGNED_NO_CONFLICT
```

rather than being promoted merely because herbivores and pollinators are both involved.

## One unresolved candidate

*Brassica nigra* is retained as:

```text
UNRESOLVED_CANDIDATE
```

because the primary paper explicitly frames a potential trade-off between phytochemical responses to folivory and pollinator interactions.

However, the current screen does not recover a matched fitness-scale demonstration that one phytochemical coordinate is favored in opposite directions by defence and pollination.

It therefore remains held for full-text mechanistic adjudication rather than counted positive.

## Scientific consequence

The outcome-blind U1 universe is turning into a **specificity test** for the BALANCE programme.

A broad literature universe can contain many herbivore-pollinator interactions while yielding few or no systems that satisfy the stricter functional-conflict estimand.

That distinction is valuable:

```text
multiple interacting agents
!=
identified functional conflict
```

and, even more strongly,

```text
identified functional conflict
!=
persistent compromise / architecture resolution
```

U1 therefore protects the macro study from selecting only famous positive examples.

## Architecture claim ceiling

No architecture mode is assigned in this blind conflict screen.

All 20 rows remain:

```text
architecture_status = NOT_IDENTIFIED
```

Architecture coding occurs only after a system passes or survives the conflict screen and the relevant structural evidence is separately adjudicated.

## Next gate

1. reconstruct the full 47-taxon Haas-Lortie universe;
2. recompute the formal first 20 dependency groups;
3. perform independent double coding on that frozen sample;
4. compare the independent coding with this provisional blind screen;
5. repair the codebook if the formal coders systematically disagree.

No U1 coefficient or prevalence estimate is licensed at this stage.

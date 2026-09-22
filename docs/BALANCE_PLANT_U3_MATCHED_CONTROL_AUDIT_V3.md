# BALANCE plant U3 matched-control audit v3

## Current state

U3 now has full **candidate control coverage** and partial **adjudication closure**.

```text
source-resolved heteranthery cases          6
registered PRIMARY control candidates       6
adjudicated PRIMARY pairs                   2
screened PRIMARY pairs still open           4
screened-control coverage complete?        YES
case-control adjudication closed?           NO
```

Canonical machine-readable surfaces:

```text
data/BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv
data/BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv
balance_domain/plant_u3_controls.py
balance_domain/plant_u3_adjudication.py
```

The adjudication ledger separates biological eligibility from the final decision. A pair can be promoted to `ADJUDICATED` only when every registered gate passes.

## PASS — Solanum rostratum -> Solanum lycocarpum

Decision:

```text
PASS
```

The case belongs to heterantherous section Androceras.

The registered control is from section Crinitum, recovered as the sister section in the relevant Solanum phylogenetic context. Crinitum representatives are actinomorphic and isantherous, and `S. lycocarpum` has independent bee/buzz-pollination evidence.

More than one Crinitum candidate can be defended at similar phylogenetic grain, so the preregistered `SOURCE_QUALITY` tie-break is used rather than pretending the control is a unique species sister.

No BALANCE predictor value was used in the match.

## PASS — Melastoma malabathricum -> Osbeckia chinensis

Decision:

```text
PASS
```

Three independent source surfaces close the match:

1. modern Melastomateae phylogenomics places the `O. chinensis/O. nepalensis` lineage sister to `Melastoma`;
2. Flora of China describes `Osbeckia` stamens as isomorphic and equal/subequal, excluding the discrete feeding-versus-pollinating heteranthery that defines the case;
3. direct hymenopteran flower-visitation observations support animal-pollination eligibility.

The registered match level remains `SAME_TRIBE_SUBFAMILY`; no false congeneric or species-sister claim is made.

## OPEN — Monochoria korsakowii -> Monochoria australasica

Decision:

```text
OPEN
```

Closed gates:

- congeneric phylogenetic placement;
- absence of a morphologically distinct pollinating anther in the proposed control;
- predictor blinding;
- registered tie-break.

Open gates:

```text
DIRECT_ANIMAL_POLLINATION_AND_CLOSEST_ELIGIBLE_CONGENER_SEARCH_OPEN
```

The current evidence makes `M. australasica` a strong control candidate, but the programme still requires source-secure direct animal-pollination eligibility and an explicit search excluding a closer eligible nonheterantherous congener.

## OPEN — Monochoria vaginalis -> Monochoria australasica

Decision:

```text
OPEN
```

The same biological control is shared with `M. korsakowii`.

That shared-control dependence is retained explicitly.

The same two gates remain open:

- direct animal-pollination source closure;
- closest-eligible-control closure.

The two Monochoria pairs can therefore never be treated as two independent negative-control lineages merely because there are two case species.

## OPEN — Senna alata -> Senna surattensis

Decision:

```text
OPEN
```

Closed gates:

- congeneric match;
- direct source comparison showing `S. surattensis` lacks the strong feeding/pollinating stamen differentiation of the case;
- Xylocopa visitation / animal-pollination eligibility;
- predictor blinding.

Open gate:

```text
CLOSEST_ELIGIBLE_NONHETERANTHEROUS_CONGENER_SEARCH_OPEN
```

The current pair is source-comparable and biologically valid, but the broad Senna phylogeny has not yet demonstrated that no closer eligible nonheterantherous congener exists.

## OPEN — Senna bicapsularis -> Senna surattensis

Decision:

```text
OPEN
```

The known close relative `S. corymbosa` is itself heterantherous and therefore cannot serve as a negative architecture control.

That exclusion improves the case for `S. surattensis`, but it still does not exhaust the search for the closest eligible nonheterantherous comparator.

The same `S. surattensis` control is shared with `S. alata`, so shared-control dependence must remain explicit.

## Fail-closed contract

The new adjudication validator requires:

```text
decision = PASS
<=>
all six gate fields = PASS
and pair registry selection_status = ADJUDICATED
and blocker = empty
```

For an open pair:

```text
decision = OPEN
<=>
no FAIL gate
and an explicit blocker exists
and pair registry selection_status = SCREENED
```

A documentation edit cannot silently promote a pair.

## Current bottleneck

Control discovery is no longer the U3 bottleneck.

The remaining U3 matching work is now precisely:

1. resolve direct animal-pollination + nearest-eligible search for `M. australasica`;
2. close closest-eligible nonheterantherous comparator search for `S. alata`;
3. close the same search for `S. bicapsularis`;
4. resolve the five Table-S1-dependent U3 family representative identities for broader structural discovery.

## Claim ceiling

Even if all six matched pairs close, U3 remains an outcome-selected case-control lane.

It can compare independently measured conflict/architecture attributes conditional on the registered heteranthery cases and their controls.

It cannot estimate heteranthery prevalence across angiosperms or identify historical transition probabilities.

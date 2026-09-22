# BALANCE plant U3 matched-control audit v3

## Current state

U3 has six species-level case records, but the latest source audit rejects the previously proposed `Senna surattensis` negative controls.

```text
source-resolved heteranthery cases             6
PRIMARY pair records retained                  6
registered eligible PRIMARY controls           4
adjudicated PRIMARY pairs                      2
screened PRIMARY pairs still open              2
rejected PRIMARY control proposals             2
cases needing replacement controls             2
screened-control coverage complete?           NO
case-control adjudication closed?              NO
```

Canonical machine-readable surfaces:

```text
data/BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv
data/BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv
data/BALANCE_PLANT_U3_CONTROL_ALTERNATIVES_V1.csv
balance_domain/plant_u3_controls.py
balance_domain/plant_u3_adjudication.py
balance_domain/plant_u3_alternatives.py
```

The pair record is retained when a proposed control is rejected so the failed comparison remains auditable rather than disappearing from the history.

## Frozen alternative-control search

Replacement/closest-control discovery is now a separate fail-closed registry rather than an informal literature search.

```text
alternative-control receipts    12
OPEN                              6
REJECTED                          6
SCREENED / promoted               0
```

The registry explicitly contains:

- `Monochoria australasica` as the incumbent OPEN candidate for both Monochoria cases;
- `Monochoria cyanea` as an equal-stamen alternative whose direct pollination evidence and relative phylogenetic proximity remain OPEN;
- rejected `Senna surattensis` receipts for both Senna cases;
- rejected `Senna rugosa` receipts after direct morphology contradicted a later "non-heterantherous" synthesis label;
- `Senna siamea` as a phylogenetically close but heterantherous REJECTED candidate for `S. alata`;
- `Senna corymbosa` as a sister but heterantherous REJECTED candidate for `S. bicapsularis`;
- `Senna atomaria` as the first source-secure homomorphic replacement candidate for `S. alata`, still OPEN on direct pollination and closest-eligible placement;
- `Senna armata` as the first source-secure homomorphic replacement candidate for `S. bicapsularis`, still OPEN on direct pollination and closest-eligible placement.

A candidate can become `SCREENED` only when heteranthery absence, animal-pollination eligibility, and phylogenetic proximity all pass. No candidate is promoted merely because it repairs the current design.

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

This closes control selection only. The separate pollen-fate conflict extraction for `O. chinensis` remains unresolved.

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

The current evidence makes `M. australasica` a plausible control candidate, but the programme still requires source-secure direct animal-pollination eligibility and an explicit search excluding a closer eligible nonheterantherous congener.

The latter search must explicitly consider `M. cyanea`, which has been described as lacking the case-defining stamen dimorphism in secondary syntheses but is not placed in the 2021 plastid sampling used for the current control receipt.

## OPEN — Monochoria vaginalis -> Monochoria australasica

Decision:

```text
OPEN
```

The same biological control is shared with `M. korsakowii`; that dependence is retained explicitly.

The same two gates remain open:

- direct animal-pollination source closure;
- closest-eligible-control closure, including the `M. cyanea` candidate.

The two Monochoria pairs cannot be treated as two independent negative-control lineages merely because there are two case species.

## FAIL — Senna alata -> Senna surattensis

Decision:

```text
FAIL
heteranthery_absence_status = FAIL
selection_status = REJECTED
```

The earlier screen over-interpreted the statement that `S. surattensis` has all 10 stamens fertile and similar in size.

Luo et al. (2009) explicitly sampled seven species with heteromorphic stamens. Their Table 1 codes `S. surattensis` as having `long, short` stamen differentiation, and the discussion describes its androecium as having **little** morphological differentiation.

Therefore:

```text
weak differentiation
!=
confirmed heteranthery absence
```

The proposed control is source-comparable and animal-pollinated, but it is not a valid negative architecture control under the frozen U3 protocol.

A replacement nonheterantherous congener or nearest eligible relative must be registered before this case regains control coverage.

## FAIL — Senna bicapsularis -> Senna surattensis

Decision:

```text
FAIL
heteranthery_absence_status = FAIL
selection_status = REJECTED
```

The same source problem applies.

`S. surattensis` is less differentiated than `S. bicapsularis`, but the source still distinguishes long and short stamen sets. It is therefore informative as a low-differentiation comparative state, not as a clean absence control.

The previous shared-control convenience is not retained at the cost of violating the outcome definition.

## Why the Senna rejection improves the design

A case-control study of structural differentiation becomes circular if controls are allowed to be merely "less differentiated" while being labeled "absence."

The fail-closed correction separates two possible future analyses:

```text
primary U3 matched lane:
  heteranthery present
  versus
  independently confirmed heteranthery absent

possible exploratory continuum lane:
  degree / geometry of stamen differentiation
```

The second may ultimately be biologically useful, but it is a different estimand and must not silently replace the preregistered binary control gate.

## Senna replacement-search result

The replacement search now shows a biologically informative pattern: the nearest-looking candidates often retain the very differentiation that the control is meant to lack.

### S. alata

`S. siamea` is phylogenetically close in a recent plastome comparison, but its seven fertile stamens are divided into long and short sets. It therefore fails the heteranthery-absence gate despite good phylogenetic proximity.

`S. rugosa` is also rejected. Direct Irwin-Barneby morphology describes three long and four short fertile stamens with different anther dimensions. A later synthesis calling the species non-heterantherous does not override the directly described discrete fertile-stamen sets.

The first plausible absence candidate is now `S. atomaria`:

```text
heteranthery_absence_status = PASS
animal_pollination_status   = OPEN
phylogenetic_proximity      = OPEN
selection_status            = OPEN
```

Its seven fertile anthers are described as isomorphic, but bee-resource records are not yet equivalent to source-secure effective pollination, and the closest-eligible phylogenetic search is not closed.

### S. bicapsularis

`S. corymbosa` is especially diagnostic: recent ITS evidence recovers it as the sister of `S. bicapsularis`, but direct floral work retains differentiated stamen functions. It is therefore rejected despite excellent phylogenetic proximity.

`S. rugosa` fails for the same direct-morphology reason noted above.

The first plausible absence candidate is now `S. armata`:

```text
heteranthery_absence_status = PASS
animal_pollination_status   = OPEN
phylogenetic_proximity      = OPEN
selection_status            = OPEN
```

Irwin-Barneby morphology explicitly states that the fertile stamens are not differentiated into two sets. The remaining work is to close effective animal-pollination evidence and the closest-eligible comparison within/around the VIIb lineage.

### Biological implication

This search suggests that heteranthery is locally phylogenetically persistent enough that a strict negative control may require moving beyond the closest species.

That is not a reason to relax the control definition. It is itself a result about the architecture landscape and supports keeping a future differentiation-continuum analysis separate from the confirmatory binary case-control estimand.

## Fail-closed contract

The adjudication validator requires:

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

For a rejected pair:

```text
decision = FAIL
=>
at least one biological gate = FAIL
and pair registry selection_status = REJECTED
```

A documentation edit cannot silently promote a pair.

## Current bottleneck

The remaining U3 matching work is now precisely:

1. resolve direct animal-pollination + nearest-eligible search for `M. australasica`, explicitly comparing `M. cyanea`;
2. close effective animal-pollination evidence and closest-eligible placement for the OPEN `S. alata -> S. atomaria` candidate;
3. close effective animal-pollination evidence and closest-eligible placement for the OPEN `S. bicapsularis -> S. armata` candidate;
4. resolve the five Table-S1-dependent U3 family representative identities for broader structural discovery.

Separately, the matched conflict-estimand lane still needs direct pollen-fate evidence for `Osbeckia chinensis`.

## Claim ceiling

Even if all six matched pairs close, U3 remains an outcome-selected case-control lane.

It can compare independently measured conflict/architecture attributes conditional on the registered heteranthery cases and their controls.

It cannot estimate heteranthery prevalence across angiosperms or identify historical transition probabilities.

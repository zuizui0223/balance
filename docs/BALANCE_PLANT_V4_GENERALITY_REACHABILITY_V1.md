# BALANCE plant V4 generality reachability audit v1

## Status

Frozen before independent U2/U6 architecture outcomes are opened.

This audit separates two questions that were previously conflated:

1. is the V4 main model prospectively estimable?
2. can the stronger cross-universe timing-generality gate ever become eligible under the
   already frozen predictor-receipt surface?

The answers are currently:

```text
V4 main model                     viable
strict cross-universe timing G1   unreachable under frozen V4 receipts
```

Machine-readable contract:
`data/BALANCE_PLANT_V4_GENERALITY_REACHABILITY_V1.json`.

## Proof from the frozen receipt surface

The only U2 groups with complete outcome-independent predictor receipts are exactly the
eight current source-screen conflict-positive groups.

Within those eight groups:

```text
shared module stratum = SINGLE

                         U2   U6
SIMULTANEOUS              1   18
ORDERED_OR_ALTERNATING    2    3
```

The frozen G1 gate requires at least two independent blocks at each timing level in each
universe within one shared module stratum.

Predictor adjudication may accept or reject a frozen predictor receipt, but
`reported_value` is immutable. The other 12 U2 reliability-frame groups have
`UNRESOLVED` predictor receipts and cannot be converted to complete receipts by the
current adjudication workflow.

Therefore final licensed U2 rows can only be a subset of the current eight complete
predictor groups. Subsetting cannot increase `SINGLE + SIMULTANEOUS` from one to two.

So final architecture coding can reduce support, but cannot make the strict G1
common-support gate pass.

## Consequence

This does **not** block the V4 main fit. The frozen main design remains full rank.

It does mean that the current publication-reactivation route requiring strict
cross-universe timing generality cannot close under V4 as presently frozen.

This is a design-reachability statement, not a biological result.

## Only admissible reopening route

Because architecture outcomes are still unopened, a future version may prospectively
reopen the route. To prevent selective gap filling, that expansion must not target only a
candidate expected to fill `SINGLE + SIMULTANEOUS`.

The admissible expansion population is all 12 unresolved groups in the frozen U2
20-group reliability frame:

```text
Alpinia_kwangsiensis
Narcissus_assoanus
Narcissus_dubius
Narcissus_triandrus
Pontederia_cordata
Pseudowintera_colorata
Turnera_ulmifolia
Wachendorfia_brachyandra
Wachendorfia_paniculata
Wachendorfia_parviflora
Wachendorfia_thyrsiflora
Wahlenbergia_albomarginata
```

That is 36 predictor slots.

Any reopening requires:

1. a new versioned predictor-coding surface;
2. outcome-independent coding of all 36 slots before architecture outcomes are opened;
3. no architecture output in that coding packet;
4. independent review/adjudication of the expanded predictor receipts;
5. recomputation of the same unchanged common-support gate.

If the same gate still fails, G1 remains unavailable. The threshold is not lowered.

## Frozen implementation of the reopening route

The prospective reopening route is implemented as a separate predictor-coding stage rather
than by editing V1 receipts during adjudication.

Frozen surfaces:

```text
coding template
  data/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv

source packet
  data/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_SOURCE_PACKET_V2.csv

coding protocol
  docs/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_PROTOCOL_V2.md

packet builder
  scripts/build_plant_u2_predictor_expansion_packet.py

manual packet workflow
  .github/workflows/build-plant-u2-predictor-expansion.yml

post-return V2 freeze
  scripts/freeze_plant_u2_predictor_receipts_v2.py
```

The coding worksheet contains exactly the 12 frozen unresolved groups and all 36 predictor
slots. A valid return must review every slot and end each as `CODED` or
`EVIDENCE_CEILING`. `CODED` requires a resolved source-side value with
`outcome_independence=TRUE`; an evidence ceiling remains `UNRESOLVED`.

After return validation, the V2 receipt freeze preserves the 24 already-resolved V1
receipts exactly and overlays only the 36 prospective expansion slots. Every V2 row remains
`SCREENED` until a separate predictor adjudicator reviews it.

Thus predictor coding, predictor adjudication, and architecture/conflict adjudication remain
three distinct stages.

## Current reopening status

The V2 reopening route has now moved beyond a design sketch:

- the 12-group / 36-slot expansion population is frozen;
- the blinded expansion packet has been generated and its artifact provenance recorded;
- no expansion return has yet been received;
- no V2 predictor receipt has yet been independently adjudicated.

A constructive end-to-end regression supplies a **mechanical reachability witness**. It
uses one synthetic admissible completion in which a frozen expansion group is independently
coded as `SINGLE + SIMULTANEOUS` and is later final-adjudicated conflict positive. Under
that configuration, the unchanged common-support and per-universe outcome-support gates
pass and both registered temporal-generality fit wrappers are emitted.

The witness proves only that the registered V2 reopening route is nonempty. It does not
predict the coding of any real group, does not promote a source-screen negative group, and
does not make the real strict-generality gate ready.

Current state:

```text
V1 receipt surface                    unreachable for strict G1
V2 expansion route                    registered and packet generated
V2 mechanical reachability            demonstrated
real V2 expansion return              pending
real V2 independent adjudication      pending
real strict G1 eligibility            unresolved / closed
V4 primary fit                        not blocked by the V2 expansion
```

## Claim ceiling

This audit establishes only the reachability of a preregistered design gate. It does not
establish an architecture effect, a biological generality result, or publication
eligibility.

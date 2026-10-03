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

## Claim ceiling

This audit establishes only the reachability of a preregistered design gate. It does not
establish an architecture effect, a biological generality result, or publication
eligibility.

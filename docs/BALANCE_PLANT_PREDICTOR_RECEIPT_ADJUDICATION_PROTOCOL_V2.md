# BALANCE plant predictor-receipt adjudication protocol v2

## Purpose

Primary-model entry requires more than reproducible predictor coding.

For every admitted U2/U6 dependency group, the three raw predictors must also have an
independently reviewed receipt showing that the value is supported by source evidence
without being inferred from the focal architecture outcome.

The three predictors are:

```text
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

This protocol is separate from the architecture double-coding exercise.

## Reviewer blinding

The predictor-receipt reviewer may see:

- plant codebook;
- this protocol;
- U2/U6 primary-source packets;
- the frozen predictor-receipt rows;
- receipt source identifiers, evidence type, screened value, and notes.

The reviewer must **not** see:

- coder A/B architecture classifications;
- architecture agreement reports;
- post-coding architecture adjudication;
- V4 model coefficients or fitted probabilities;
- publication/reactivation results.

The purpose is to decide whether the predictor receipt itself is source-supported and
outcome-independent.

## Review questions

For every predictor receipt:

1. Is the reported raw predictor value supported by the cited source?
2. Is the source evidence about the conflict-bearing baseline/challenge state rather than
   inferred from the focal resolution architecture?
3. Is the evidence type correctly classified?
4. Does the note explain the source-side basis without referring to a desired V4 result?

## Decisions

Allowed final receipt states:

```text
ADJUDICATED
REJECTED
```

### ADJUDICATED

Use only when:

```text
reported_value != UNRESOLVED
outcome_independence = TRUE
source supports the reported value
source supports the claimed independence
```

### REJECTED

Use when:

- the source does not support the reported value;
- the value depends on the focal architecture outcome;
- the baseline/challenge geometry cannot be separated from the response;
- evidence is too ambiguous to license the predictor.

A rejected receipt is not repaired by copying the architecture code.

## Relationship to architecture coding

Predictor receipt adjudication and architecture adjudication are separate gates.

```text
agreement on predictor category
!= outcome independence

outcome-independent source receipt
!= architecture evidence
```

Both gates must close before a U2/U6 row enters model assembly.

## U2 current frame

```text
8 source-screen conflict-positive groups
3 predictors/group
24 resolved SCREENED receipts among those positive groups
0 independently ADJUDICATED
```

The remaining U2 reliability-frame receipt slots stay unresolved because those groups are
not source-screen conflict positive.

## U2 versioned review surfaces

The default review route remains U2 V1. When the prospectively frozen U2 predictor-expansion
return has been validated and converted into a frozen V2 receipt frame, a separate predictor
review may instead use U2 V2.

The V2 review packet must be built with:

```bash
python scripts/build_plant_predictor_adjudication_packet.py \
  --u2-v2-freeze-dir <IMMUTABLE_V2_FREEZE_WORKSPACE> \
  --out-dir <NEW_PACKET_DIR>
```

The V2 freeze workspace must contain:

```text
BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv
BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json
```

Before packet generation, the builder verifies:

- V2 frame SHA256 against the freeze receipt;
- freeze receipt binding to the current tracked V1 predictor frame;
- freeze receipt binding to the frozen 12-group expansion template.

The V2 packet contains the frozen V2 frame under its V2 basename and includes the freeze
receipt as provenance. It does not include U2 V1 as a competing review surface.

The reviewer returns the U2 frame under the same versioned basename supplied in the packet.
V1 and V2 must never be merged by hand, renamed into one another, or reviewed against the
wrong frozen baseline.

U2 V2 is a prospective predictor-surface expansion. It does not itself admit extra groups
to the V4 model; final model admission still requires independently adjudicated positive
conflict plus architecture and predictor gates.

## U6 current frame

```text
21 conflict-first dependency groups
3 predictors/group
63 resolved SCREENED receipts
0 independently ADJUDICATED
```

## Return rule

The reviewer returns the same receipt CSV with only evidence-review fields changed.

Architecture columns must never be added.

The final validator requires that every model-admitted group has:

```text
3 ADJUDICATED receipts
outcome_independence = TRUE
reported predictor values exactly matching final architecture/predictor adjudication
```

Any mismatch blocks assembly.

## Claim ceiling

Receipt adjudication licenses predictor provenance and independence only. It does not
establish an architecture association and does not make V4 estimable by itself.

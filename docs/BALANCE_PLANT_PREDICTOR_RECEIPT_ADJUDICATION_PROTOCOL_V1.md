# BALANCE plant predictor-receipt adjudication protocol v1

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

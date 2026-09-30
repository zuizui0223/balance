# BALANCE plant architecture adjudication protocol v1

## Purpose

This stage begins only after independent architecture coding has passed the registered
reliability gate.

It resolves coder disagreements by source review. It does not revisit predictor-receipt
independence, fit V4, or inspect publication/reactivation outputs.

## Two independent scopes

### PRIMARY

```text
U2 sexual interference
U6 pollen theft
```

The primary packet is available only when both U2 and U6 reliability pass.

### EXTERNAL

```text
U1 broad interaction specificity validation
```

U1 adjudication is operationally separate and never blocks the U2+U6 primary denominator.

## Packet contents

For each admitted lane the adjudicator receives:

- the frozen plant codebook;
- this protocol;
- the frozen source packet;
- the merged CODER_A/CODER_B ledger;
- the lane agreement report;
- the exact disagreement ledger;
- the canonical adjudication return template.

The packet does not contain:

- predictor-receipt adjudication outputs;
- V4 fit inputs or fitted outputs;
- posterior summaries;
- publication/reactivation outputs.

## Adjudication rule

Every frozen group receives one completed adjudication row.

For fields where CODER_A and CODER_B agree:

```text
adjudicated value = coder consensus
adjudication_basis = CODER_CONSENSUS
```

Consensus may not be overridden by source review.

For fields where coders disagree:

```text
adjudication_basis = SOURCE_REVIEW_OF_DISAGREEMENTS
```

The adjudicator resolves the field from the frozen source evidence and explains the basis
in `notes`.

The final return must contain no PENDING rows.

## Reliability failure

If any registered agreement field is below the frozen raw-agreement threshold:

```text
no adjudication packet
-> codebook repair
-> independent recoding of the same frozen groups
```

Adjudication is not used to hide a failed reliability gate.

## Return validation

The validator reuses the frozen U1/U2/U6 adjudication loaders.

It requires:

- exactly the frozen groups;
- completed independent coder rows;
- the reliability gate already passed;
- `CODER_CONSENSUS` where coders agree;
- `SOURCE_REVIEW_OF_DISAGREEMENTS` where they differ;
- no override of coder-consensus values;
- non-empty notes for every adjudicated row;
- every returned row = `ADJUDICATED`.

A validated return is written to a new immutable workspace together with the corresponding
merged coding ledger.

## Claim ceiling

Architecture adjudication closes a human coding gate only. It establishes no V4 effect,
cross-universe generality, causal transition, or publication eligibility.

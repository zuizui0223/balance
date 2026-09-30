# BALANCE plant architecture adjudication protocol v1

## Purpose

This protocol governs the human step after independent architecture coding has passed the
registered reliability gate.

It is not a third independent coding pass. It is a source review of disagreements only.

## Opening gate

An adjudication packet may be generated for a lane only when every registered agreement
field has:

```text
raw agreement >= 0.80
```

If any field falls below that threshold, no packet is generated for that lane. The action
is:

```text
CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS
```

The frozen groups are not replaced.

## Packet contents

A lane packet contains:

- the frozen plant codebook;
- this adjudication protocol;
- the frozen lane source packet;
- the canonical agreement report;
- a long-format review-context table showing coder A and coder B values for every field;
- one canonical adjudication worksheet.

The packet does not include V4 fitted results, posterior direction labels, predictor-review
decisions, or publication/reactivation outputs.

## Consensus groups

If coder A and coder B agree on every registered field for a group after the reliability
gate passes, that group is mechanically written as:

```text
adjudication_status = ADJUDICATED
adjudication_basis  = CODER_CONSENSUS
notes               = AUTO_CODER_CONSENSUS_AFTER_RELIABILITY_PASS
```

No human source review is required for that group.

Consensus values are frozen and may not be changed later.

## Disagreement groups

If any registered field differs between coder A and coder B, the canonical row remains:

```text
adjudication_status = PENDING
adjudication_basis  = AWAITING_SOURCE_REVIEW_OF_DISAGREEMENTS
all coded fields    = UNRESOLVED
```

The review-context table identifies the exact disagreement fields and also shows consensus
fields for the same group.

The adjudicator reviews the frozen source packet and fills the final canonical row.

When complete:

```text
adjudication_status = ADJUDICATED
adjudication_basis  = SOURCE_REVIEW_OF_DISAGREEMENTS
```

All coded fields must be resolved and notes must record the source-review basis.

## What the adjudicator may not do

The adjudicator must not:

- change a field on which coder A and coder B agreed;
- replace a frozen dependency group;
- use a predictor-review decision as architecture evidence;
- use a fitted V4 coefficient, predicted probability, or posterior label;
- use a desired publication result to resolve ambiguity;
- convert a low-agreement lane into adjudication rather than recoding.

The canonical loader enforces consensus preservation and blocks adjudication while any
lane-wide codebook-repair trigger remains open.

## Lane scope

U2 and U6 are the primary V4 architecture lanes.

U1 is external specificity validation. U1 adjudication may proceed or fail independently
without blocking primary U2+U6 reliability.

## Claim ceiling

Architecture adjudication resolves post-reliability coding disagreements. It establishes no
association, causal transition, cross-universe generality, or publication eligibility.

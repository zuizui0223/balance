# BALANCE plant human-return intake v1

## Purpose

This is the canonical entrypoint after independent human review files begin to return.

It does **not** adjudicate disagreements and it does **not** fit V4. It validates returned
surfaces against the frozen handoff, merges whichever complete architecture stages have
returned, computes agreement for those lanes, and independently validates predictor-receipt
review when that stage has returned.

Machine-readable contract:
`data/BALANCE_PLANT_HUMAN_RETURN_INTAKE_CONTRACT_V1.json`.

Canonical CLI:

```bash
python scripts/audit_plant_human_returns.py --return-dir <RETURN_DIR>
```

Use `--list-required` to print all canonical basenames.

## Independent return stages

The three human-review stages are operationally independent.

### 1. Primary architecture stage

Requires all four files together:

```text
BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv
BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv
BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv
BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv
```

All four may be absent while the primary architecture stage is pending. If any one is
supplied, all four are required.

### 2. External-validation architecture stage

Requires the U1 pair:

```text
BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv
BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv
```

Both may be absent while U1 external validation is pending. If either is supplied, both are
required.

**U1 latency does not block U2/U6 primary reliability.**

### 3. Predictor-review stage

Requires U6 V1 plus **exactly one** U2 receipt version:

```text
U2 V1:
BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv

or

U2 V2:
BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv

and always

U6:
BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv
```

Supplying both U2 versions is ambiguous and fails closed.

A U2 V2 review additionally requires:

```bash
--u2-v2-freeze-dir <V2_FREEZE_WORKSPACE>
```

The freeze workspace must contain the frozen V2 receipt frame and
`BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json`. Its hashes are revalidated against
the current V1 receipt frame and prospective expansion template before the reviewed V2
frame is accepted.

**Architecture-return latency does not block predictor-review validation, and predictor
latency does not block architecture reliability reporting.**

At least one complete stage must be present for intake to run.

## Validation order

For every supplied stage, the intake validates all stage files before persistent output is
written.

Architecture stages:

1. every supplied coder file contains exactly the frozen lane groups for the declared coder;
2. U6 source-reference IDs still match the Pass-1 freeze;
3. coder returns merge into canonical lane order;
4. raw agreement, Cohen kappa, Gwet AC1, and exact disagreements are computed.

Predictor stage:

1. reviewed receipt IDs exactly match the frozen frame of the declared version;
2. U2 V1 is validated against tracked V1; U2 V2 is validated only against its explicit
   hash-bound V2 freeze workspace;
3. reviewed receipts cannot rewrite frozen predictor values, source IDs, or notes;
4. ADJUDICATED receipts must remain source-side and outcome-independent.

A partial stage fails before creating the output directory. Tracked blank worksheets are
never substituted for a missing file inside a supplied stage.

## Primary reliability branching

Primary architecture reliability is U2 + U6.

Every registered agreement field must have:

```text
raw agreement >= 0.80
```

If the primary stage has not returned:

```text
AWAIT_PRIMARY_ARCHITECTURE_RETURNS
```

If any primary field falls below 0.80:

```text
CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS
```

The same frozen groups are recoded independently. Groups are not replaced.

If all U2/U6 fields pass:

```text
SOURCE_ADJUDICATION
```

## U1 external-validation branching

U1 is reported separately because it is external specificity validation.

If U1 has not returned:

```text
AWAIT_U1_EXTERNAL_VALIDATION_RETURNS
```

If U1 reliability passes:

```text
SOURCE_ADJUDICATION
```

A delayed or failed U1 stage never changes the U2/U6 primary reliability result.

## Predictor branching

Primary predictor completion requires:

```text
U2:
every current strict source-screen conflict-positive group
must be a subset of groups with 3 ADJUDICATED outcome-independent receipts

U6:
21 groups x 3 ADJUDICATED outcome-independent receipts
```

The current U2 source-positive set contains eight groups, but V2 may legitimately contain
more than eight complete groups. Extra prospectively resolved/adjudicated U2 groups do not
cause intake failure. Final V4 readiness later switches to the actual final adjudicated
conflict-positive U2 set.

If the predictor stage has not returned:

```text
AWAIT_PREDICTOR_ADJUDICATION_RETURNS
```

If both returned but any required cluster is incomplete or rejected:

```text
RESOLVE_REJECTED_OR_INCOMPLETE_PRIMARY_PREDICTOR_RECEIPTS
```

A rejected frozen receipt is not silently edited into an acceptable one.

## Workspace immutability

An intake output directory is a one-shot evidence workspace.

- one or more complete stages may be supplied;
- all supplied stages must validate before any persistent output is written;
- if the requested output directory already exists, intake fails;
- files are first written to a temporary sibling directory;
- the temporary directory is atomically renamed to the final workspace only after every
  supplied-stage output is complete;
- output paths recorded in the receipt are workspace-relative basenames.

A later stage return or corrected recode therefore uses a new output directory rather than
overwriting an earlier evidence state.

## Outputs

Successful intake writes only outputs for stages actually supplied:

- canonical merged double-coding ledgers for supplied architecture lanes;
- agreement reports and exact-disagreement CSVs for supplied architecture lanes;
- validated U2/U6 reviewed predictor-receipt CSV frames when predictor review is supplied;
- for U2 V2, a copied frozen V2 baseline plus its freeze receipt, each SHA-bound in the
  intake receipt;
- U2/U6 predictor-adjudication readouts when predictor review is supplied;
- one intake receipt with SHA256 values for every supplied human-return file and explicit
  PENDING / RELIABILITY_PASS / RELIABILITY_FAIL / COMPLETE / INCOMPLETE stage status.

The intake receipt always reports:

```text
ready_for_v4_assembly = false
```

because architecture source adjudication remains a separate post-reliability human gate.

## Claim ceiling

The intake licenses only return-file identity, reliability diagnostics, and predictor-review
validation. It establishes no biological association, causal transition, model effect, or
publication eligibility.

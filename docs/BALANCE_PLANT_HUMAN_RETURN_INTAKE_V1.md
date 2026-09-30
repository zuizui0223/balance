# BALANCE plant human-return intake v1

## Purpose

This is the canonical entrypoint after independent human review files begin to return.

It does **not** adjudicate disagreements and it does **not** fit V4. It validates returned
surfaces against the frozen handoff, merges the two architecture coders, computes agreement,
and optionally validates predictor-receipt review when both U2 and U6 predictor files have
returned.

Machine-readable contract:
`data/BALANCE_PLANT_HUMAN_RETURN_INTAKE_CONTRACT_V1.json`.

Canonical CLI:

```bash
python scripts/audit_plant_human_returns.py --return-dir <RETURN_DIR>
```

Use `--list-required` to print the canonical basenames.

## Required architecture returns

All six files are required before persistent architecture-intake outputs are written:

```text
BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv
BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv
BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv
BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv
BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_CODER_A_V1.csv
BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_CODER_B_V1.csv
```

If any of these is absent, intake fails before creating the output directory.

Tracked blank worksheets are never substituted for missing returns.

## Predictor-review returns

The predictor reviewer is an independent gate and is not allowed to delay architecture
agreement reporting.

These two files are therefore optional **as a pair**:

```text
BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv
BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv
```

Allowed states:

```text
neither present -> architecture intake proceeds; predictor status = pending
both present    -> both are validated
only one present -> fail closed
```

## Validation order

The intake performs the following checks before writing persistent outputs:

1. all six coder-return files exist;
2. each file contains exactly the frozen lane groups for the declared coder ID;
3. U6 source-reference IDs still match the Pass-1 freeze;
4. coder returns merge into canonical lane order;
5. raw agreement, Cohen kappa, Gwet AC1, and exact disagreements are computed;
6. if predictor returns are present, reviewed receipt IDs exactly match the frozen frames;
7. reviewed receipts cannot rewrite frozen predictor values, source IDs, or notes;
8. ADJUDICATED predictor receipts must remain source-side and outcome-independent.

## Reliability branching

Primary architecture reliability is U2 + U6.

Every registered agreement field must have:

```text
raw agreement >= 0.80
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

U1 reliability is reported separately because U1 is external specificity validation and
does not block the U2+U6 primary V4 denominator.

## Predictor branching

Primary predictor completion requires:

```text
U2: 8 clusters x 3 ADJUDICATED outcome-independent receipts
U6: 21 clusters x 3 ADJUDICATED outcome-independent receipts
```

If predictor files have not yet returned:

```text
AWAIT_PREDICTOR_ADJUDICATION_RETURNS
```

If both returned but any required cluster is incomplete or rejected:

```text
RESOLVE_REJECTED_OR_INCOMPLETE_PRIMARY_PREDICTOR_RECEIPTS
```

A rejected frozen receipt is not silently edited into an acceptable one.

## Outputs

Successful intake writes one workspace containing:

- canonical merged U1/U2/U6 double-coding ledgers;
- U1/U2/U6 agreement reports;
- exact disagreement CSVs;
- U2/U6 predictor-adjudication readouts when predictor returns are present;
- one intake receipt with SHA256 values for every supplied human-return file.

The intake receipt always reports:

```text
ready_for_v4_assembly = false
```

because architecture source adjudication remains a separate post-reliability human gate.

## Claim ceiling

The intake licenses only return-file identity, reliability diagnostics, and predictor-review
validation. It establishes no biological association, causal transition, model effect, or
publication eligibility.

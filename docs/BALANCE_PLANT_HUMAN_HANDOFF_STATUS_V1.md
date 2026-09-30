# BALANCE plant human-handoff execution v1

## Status

The frozen machine preparation is complete and the independent human-review packets have
been generated.

```text
status = PACKETS_GENERATED_AWAITING_INDEPENDENT_HUMAN_RETURNS
```

Machine-readable provenance:
`data/BALANCE_PLANT_HUMAN_HANDOFF_EXECUTION_V1.json`.

This is an execution receipt, not a biological result.

## Architecture coding packets

Two separate coder packets were generated from the frozen handoff contract.

```text
CODER_A packet SHA256
2701ef155ddffcc97758ee8aa96532d566a077d4a386f760c3ac977e4699b9eb

CODER_B packet SHA256
452330e898ef7f9ab0593ad1f8c20a695854a3f2afd5a16c0e38ad09ebc0eaee
```

The packet audit established:

- identical codebook and protocol bytes for both coders;
- identical U1, U2, and U6 source-packet bytes for both coders;
- U1 = 20 frozen groups;
- U2 = 20 frozen groups, containing all eight source-screen conflict-positive groups;
- U6 = 21 frozen conflict-first groups;
- coder worksheets differ only in `coder_id` and coder-specific filename;
- U1/U2 coding fields are blank;
- U6 coding fields remain `UNRESOLVED` and `coding_status=UNSTARTED`.

Neither coder packet contains the other coder's output, adjudication decisions, agreement
results, predictor-receipt decisions, or publication/reactivation outputs.

## Predictor-receipt adjudication packet

The independent predictor-review packet was also generated.

```text
packet SHA256
dee4c07fd5e9a1e754145f21f5fddfe89881c38720424389ba629eaf79e51e76
```

It contains:

- the same plant codebook used in the architecture handoff;
- the same U2 source packet bytes;
- the same U6 source packet bytes;
- U2 predictor-receipt frame;
- U6 predictor-receipt frame;
- the frozen predictor-adjudication protocol.

It does **not** contain coder A/B architecture outputs or architecture adjudication.

The generated receipt frames remain pre-review:

```text
U2: 60 receipts total
    24 resolved source-screen receipts
    36 unresolved/non-admitted slots
    60 SCREENED, 0 ADJUDICATED

U6: 63 receipts total
    63 resolved source-screen receipts
    63 SCREENED, 0 ADJUDICATED
```

A direct scan of reported values, source identifiers, and receipt notes found zero focal
architecture outcome labels.

## Cross-role evidence identity

The evidence bytes supplied to architecture coders and the predictor reviewer agree for the
surfaces that are intentionally shared:

```text
plant codebook
0429c7aa1dc362cba05deb0fa7072b274853f0413f068df9b7ca9a8072a08ace

U2 source packet
529c2cc94b0421dd25b6eb759a9b9cd656f0b514b0a69e00adbcac019a997ba4

U6 source packet
182f6a74f9834d7be866e176c4b5d1ff450e11aebb56e0fe6d89542c370abd2c
```

Thus the independent reviewers can inspect the same frozen evidence while remaining blind
to each other's judgments.

## Next gate

The remaining primary blockers are genuinely human:

1. coder A completes U1/U2/U6;
2. coder B completes U1/U2/U6 independently;
3. predictor reviewer returns U2/U6 receipt decisions;
4. coder returns are validated and merged;
5. raw agreement, Cohen kappa, Gwet AC1, and exact disagreements are computed;
6. any field below 0.80 raw agreement triggers codebook repair and independent recoding of
   the same frozen groups;
7. only after reliability passes are architecture disagreements adjudicated;
8. predictor receipts are validated separately;
9. licensed U2/U6 rows are assembled;
10. the V4 estimability gate is evaluated.

No missing human judgment is synthesized by the repository.

## Artifact retention

The GitHub Actions artifacts are operational handoff files and have finite retention.
Their run IDs, artifact IDs, expiry timestamps, packet hashes, and source commits are
therefore frozen in the execution receipt. The deterministic builders allow the same
packets to be regenerated from unchanged handoff inputs.

## Claim ceiling

This receipt establishes only that the blinded handoff artifacts were generated and
audited. It establishes no architecture association, effect direction, generality result,
causal transition, or publication eligibility.

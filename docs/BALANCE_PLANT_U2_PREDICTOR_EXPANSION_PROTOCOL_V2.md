# BALANCE U2 predictor expansion coding protocol v2

## Status

Prospectively frozen before independent U2/U6 architecture outcomes are opened.

This protocol implements the only admissible reopening route in
`BALANCE_PLANT_V4_GENERALITY_REACHABILITY_V1`.

It does **not** change the V4 common-support threshold and does not promote any U2 group
into the primary model.

## Population

The coding population is all 12 groups in the frozen U2 20-group reliability frame whose
three V1 predictor receipts are `UNRESOLVED`.

All three predictors are coded for every group:

```text
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

Therefore:

```text
12 groups x 3 predictors = 36 frozen slots
```

Selective coding of only a likely `SINGLE + SIMULTANEOUS` gap-filling group is forbidden.

## Blinding

The predictor coder may see:

- the plant macro codebook;
- this protocol;
- the 12-group U2 source packet;
- the 36-row expansion worksheet.

The predictor coder must not see:

- CODER_A or CODER_B architecture/conflict outputs;
- architecture agreement or disagreement reports;
- post-coding architecture adjudication;
- U2 source-screen conflict classifications;
- V4 fitted coefficients/probabilities;
- publication/reactivation outputs.

## Coding decision

Every frozen slot must end in exactly one of:

```text
CODED
EVIDENCE_CEILING
```

No slot may remain `UNSTARTED`.

### CODED

Use `CODED` only when the primary source supports:

1. one resolved allowed predictor value;
2. a source-side evidence type;
3. `outcome_independence = TRUE`.

The value must be coded from the baseline/challenge geometry rather than inferred from the
focal architecture outcome.

### EVIDENCE_CEILING

Use `EVIDENCE_CEILING` when the source does not support a resolved outcome-independent
predictor value.

Then:

```text
reported_value = UNRESOLVED
notes = non-empty reason
```

An evidence ceiling is a valid completed review. It is not repaired by reading
architecture outputs.

## Freeze after coding

The returned 36-row worksheet is validated against the frozen template.

A V2 predictor-receipt frame is then created:

- the 24 already-resolved V1 receipts are preserved;
- CODED expansion slots receive the prospectively coded source-side value;
- EVIDENCE_CEILING slots remain UNRESOLVED;
- all V2 receipt rows remain `SCREENED`;
- a separate predictor adjudicator must subsequently return `ADJUDICATED` or `REJECTED`.

The expansion coder and predictor adjudicator are different logical roles.

## Relationship to final V4 admission

Predictor expansion does not override the conflict gate.

A newly resolved predictor group can enter final V4 assembly only if independent
architecture/conflict coding and post-reliability adjudication also admit that group as
conflict-positive under the frozen U2 rules.

Thus V2 expands the **possible predictor-support surface**; it does not preselect model
rows.

## Generality rule

After predictor coding is frozen and independently adjudicated, the unchanged V4
common-support gate is recomputed on the final licensed U2/U6 assembly.

If no shared module stratum contains at least:

```text
U2 SIMULTANEOUS >= 2
U2 ORDERED_OR_ALTERNATING >= 2
U6 SIMULTANEOUS >= 2
U6 ORDERED_OR_ALTERNATING >= 2
```

independent dependence blocks, strict G1 temporal generality remains unavailable.

## Claim ceiling

This expansion codes prospective predictor geometry only. It establishes no conflict
status, architecture outcome, association, generality result, or publication eligibility.

# BALANCE plant V4 human-input workspace composition v1

## Purpose

Independent human-review stages can return on different timelines and are stored in separate
immutable evidence workspaces.

The V4 pre-fit builder expects canonical human-mutable basenames in one input directory.
This composition step creates that directory without manual copying.

Machine-readable contract:
`data/BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_CONTRACT_V1.json`.

## Required sources

### Primary architecture adjudication workspace

Must contain a validated PRIMARY adjudication receipt and the canonical U2/U6 merged coding
and adjudication ledgers.

### Predictor-review intake workspace

Must contain a predictor intake receipt with:

```text
predictor_return_status = COMPLETE
predictor_primary_complete = true
```

and the validated reviewed U2/U6 predictor-receipt CSV frames.

For U2, the intake receipt must explicitly declare `V1` or `V2`.

- V1 composition carries the reviewed V1 frame and validates it against the tracked V1
  frozen surface.
- V2 composition carries the reviewed V2 frame **without renaming it**, plus the copied
  frozen V2 baseline and `BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json`.
  The compositor rechecks the V2 frame hash and also verifies that the freeze receipt is
  still bound to the current tracked V1 surface and frozen expansion template.

### Optional external U1 workspace

A validated EXTERNAL architecture-adjudication workspace may be added. Its absence never
blocks the U2+U6 primary workspace.

## Output

The primary composed workspace always contains the five common primary surfaces:

```text
U2 merged coding
U2 final architecture adjudication

U6 merged coding
U6 final architecture adjudication
U6 reviewed predictor receipts
```

and one versioned U2 predictor surface.

For V1:

```text
BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv
```

For V2:

```text
BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv
BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2_FROZEN.csv
BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json
```

The latter two V2 files are provenance surfaces, not additional model inputs.

If external U1 is supplied, the U1 merged coding and adjudication files are added.

Every copied file receives a source SHA256 and composed SHA256 in the workspace receipt.

## Source-receipt hash binding

Every file copied from a validated human-review workspace must match the SHA256 frozen in
that workspace's receipt before it is read or copied.

This applies to:

- U2/U6 merged coding ledgers;
- U2/U6 final architecture-adjudication ledgers;
- U2/U6 reviewed predictor-receipt frames;
- when U2 V2 is active, its copied frozen V2 baseline and V2 freeze receipt;
- optional U1 merged coding/adjudication ledgers.

Semantic CSV validation is not a substitute for this check. Even a change that leaves parsed
rows unchanged, such as trailing whitespace or a blank line, invalidates the immutable
workspace receipt and the compositor fails closed.

The workspace receipt records the active U2 predictor version and the exact reviewed/frozen
basenames. Downstream code must use those receipt-declared names; V2 is never silently
coerced back to V1.

## Final validation

Before the workspace is committed, the compositor reruns
`build_plant_v4_readiness()` using the composed files and frozen repository inputs.

The output is rejected unless:

```text
open primary human gates = 0
primary_model_assembly_ready = true
```

This means a composition receipt cannot be used to bypass an incomplete architecture or
predictor-review gate.

## Immutable workspace

The requested output directory must not already exist. Files are written to a temporary
sibling directory and atomically renamed only after all source and readiness checks pass.

## Next step

```bash
python scripts/build_plant_v4_analysis_inputs.py \
  --input-dir <COMPOSED_WORKSPACE> \
  --build
```

V4 estimability is evaluated only after the licensed assembly is built. A composed human
workspace does not guarantee that the observed architecture classes make the final model
estimable.

## Claim ceiling

Composition establishes provenance and readiness of human inputs only. It contains no fitted
effect, causal result, cross-universe generality conclusion, or publication decision.

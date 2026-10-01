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

### Optional external U1 workspace

A validated EXTERNAL architecture-adjudication workspace may be added. Its absence never
blocks the U2+U6 primary workspace.

## Output

The primary composed workspace contains exactly the six human-mutable primary surfaces:

```text
U2 merged coding
U2 final architecture adjudication
U2 reviewed predictor receipts

U6 merged coding
U6 final architecture adjudication
U6 reviewed predictor receipts
```

If external U1 is supplied, the U1 merged coding and adjudication files are added.

Every copied file receives a source SHA256 and composed SHA256 in the workspace receipt.

## Source-receipt hash binding

Every file copied from a validated human-review workspace must match the SHA256 frozen in
that workspace's receipt before it is read or copied.

This applies to:

- U2/U6 merged coding ledgers;
- U2/U6 final architecture-adjudication ledgers;
- U2/U6 reviewed predictor-receipt frames;
- optional U1 merged coding/adjudication ledgers.

Semantic CSV validation is not a substitute for this check. Even a change that leaves parsed
rows unchanged, such as trailing whitespace or a blank line, invalidates the immutable
workspace receipt and the compositor fails closed.

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
  --out-dir <NEW_ANALYSIS_INPUT_WORKSPACE> \
  --build
```

V4 estimability is evaluated only after the licensed assembly is built. A composed human
workspace does not guarantee that the observed architecture classes make the final model
estimable.

The production builder verifies this workspace receipt and every composed-file hash before
building. It then creates a new immutable analysis-input workspace and writes
`BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json`, which cryptographically links the
pre-fit bundle back to this human-input receipt.

See:
`data/BALANCE_PLANT_V4_ANALYSIS_INPUT_BUNDLE_CONTRACT_V1.json`.

## Claim ceiling

Composition establishes provenance and readiness of human inputs only. It contains no fitted
effect, causal result, cross-universe generality conclusion, or publication decision.

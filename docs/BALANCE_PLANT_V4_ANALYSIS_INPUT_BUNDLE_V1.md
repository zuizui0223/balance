# BALANCE plant V4 analysis-input bundle integrity v1

## Purpose

The human-input compositor produces one immutable directory containing the validated mutable
U2/U6 surfaces. The V4 analysis-input builder converts that human workspace into the licensed
assembly and frozen Stan wrapper JSON files.

This step is itself provenance-bearing. A valid model fit must therefore be traceable back to
one immutable composed human-input workspace rather than merely to a set of files with the
right basenames.

Machine-readable contract:
`data/BALANCE_PLANT_V4_ANALYSIS_INPUT_BUNDLE_CONTRACT_V1.json`.

## Production build input

When `--input-dir` is supplied to:

```bash
python scripts/build_plant_v4_analysis_inputs.py --input-dir <workspace> --build
```

the directory must contain:

```text
BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json
```

The builder verifies:

- receipt schema and analysis identity;
- `primary_model_assembly_ready=true`;
- exact receipt-declared mutable file set;
- every mutable file SHA256 against `composed_sha256`;
- `source_sha256 == composed_sha256`;
- frozen predictor receipt constraints and V4 readiness gates.

The lighter `current_readiness(input_dir=...)` diagnostic remains able to inspect partial
workspaces and does not require a composition receipt.

## Immutable output

The analysis-input output directory must not already exist.

Files are written into a temporary sibling directory and atomically renamed only after all
registered outputs and the bundle receipt are complete.

A corrected or repeated build therefore requires a new output workspace.

## Output receipt

Every successful production build writes:

```text
BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json
```

The bundle copies the canonical source receipt itself as:

`BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json`.

The receipt binds:

- the copied source composed-human-workspace receipt name and SHA256;
- licensed assembly SHA256;
- assembly readout SHA256;
- primary Stan wrapper SHA256;
- primary prior-sensitivity wrapper SHA256;
- both temporal-generality wrapper SHA256 values when that gate is open;
- the frozen generality status.

The optional generality pair must either both exist or both be absent.

## CmdStan boundary

The CmdStan runner independently reloads the licensed assembly, rebuilds the frozen V4 input
objects, and then verifies the analysis-input receipt hashes before any compilation or
sampling.

Thus a valid fit provenance chain is:

```text
human return
-> intake receipt
-> architecture adjudication / predictor review receipts
-> composed human-input workspace receipt
-> analysis-input bundle receipt
-> CmdStan fit execution receipt
```

CmdStan preflight also requires the copied human-workspace receipt to exist inside the
analysis-input directory, verifies its SHA256 against the analysis-input receipt, and
rechecks that it is assembly-ready with no primary human gate open.

Semantic revalidation never substitutes for receipt hash verification.

## Claim ceiling

This contract establishes provenance and immutability of pre-fit inputs only. It does not
establish a fitted effect, causal transition, cross-universe generality, or publication
decision.

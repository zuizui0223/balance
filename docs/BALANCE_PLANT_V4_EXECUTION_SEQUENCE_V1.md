# BALANCE plant V4 end-to-end execution sequence v1

## Status

Frozen before independent human returns are opened.

Machine-readable contract:
`data/BALANCE_PLANT_V4_EXECUTION_SEQUENCE_V1.json`.

This is the one canonical operational path from human-return files to a completed V4 fit.
It does not supply any missing human judgment and does not change the scientific gates.

## 1. Intake returned human review

At least one complete return stage must be present.

```bash
python scripts/audit_plant_human_returns.py \
  --return-dir <RETURN_DIR> \
  --out-dir <NEW_INTAKE_WORKSPACE>
```

The three stages are independent:

- PRIMARY architecture: U2 + U6 coder A/B returns;
- EXTERNAL architecture: U1 coder A/B returns;
- PREDICTOR review: reviewed U2 + U6 predictor-receipt frames.

A partial supplied stage fails closed.

For PRIMARY architecture:

```text
raw agreement < 0.80 in any registered field
-> versioned codebook repair
-> independently recode the SAME frozen groups

all registered U2/U6 fields >= 0.80
-> SOURCE_ADJUDICATION
```

U1 never blocks the primary U2+U6 path.

## 2. Build the PRIMARY architecture adjudication packet

Only after U2 and U6 reliability pass:

```bash
python scripts/build_plant_architecture_adjudication_packet.py \
  --scope PRIMARY \
  --intake-dir <PRIMARY_INTAKE_WORKSPACE> \
  --out-dir <NEW_PRIMARY_ADJUDICATION_PACKET_DIR>
```

The adjudicator may resolve disagreements from source evidence. Coder consensus may not be
overridden.

## 3. Validate the PRIMARY architecture adjudication return

```bash
python scripts/validate_plant_architecture_adjudication.py \
  --scope PRIMARY \
  --intake-dir <PRIMARY_INTAKE_WORKSPACE> \
  --return-dir <PRIMARY_ADJUDICATION_RETURN_DIR> \
  --out-dir <NEW_PRIMARY_ADJUDICATION_WORKSPACE>
```

This creates a new immutable validated architecture-adjudication workspace.

## 4. Optional U1 external validation

If U1 reliability passes, run the same packet/validation sequence with:

```text
--scope EXTERNAL
```

U1 may finish before or after the primary route and never blocks primary V4.

## 5. Compose the V4 human-input workspace

Required:

- validated PRIMARY architecture-adjudication workspace;
- predictor intake workspace with complete primary predictor review.

```bash
python scripts/compose_plant_v4_human_workspace.py \
  --primary-adjudication-dir <PRIMARY_ADJUDICATION_WORKSPACE> \
  --predictor-intake-dir <PREDICTOR_INTAKE_WORKSPACE> \
  --out-dir <NEW_COMPOSED_V4_HUMAN_WORKSPACE>
```

When U1 external validation is available:

```bash
python scripts/compose_plant_v4_human_workspace.py \
  --primary-adjudication-dir <PRIMARY_ADJUDICATION_WORKSPACE> \
  --predictor-intake-dir <PREDICTOR_INTAKE_WORKSPACE> \
  --external-adjudication-dir <U1_ADJUDICATION_WORKSPACE> \
  --out-dir <NEW_COMPOSED_V4_HUMAN_WORKSPACE>
```

The compositor verifies source-receipt hashes, copies only receipt-declared files, reruns the
canonical V4 readiness audit, and requires zero primary human open gates.

## 6. Build immutable V4 analysis inputs

```bash
python scripts/build_plant_v4_analysis_inputs.py \
  --input-dir <COMPOSED_V4_HUMAN_WORKSPACE> \
  --out-dir <NEW_V4_ANALYSIS_INPUT_WORKSPACE> \
  --build
```

This stage:

- builds the licensed U2/U6 assembly;
- evaluates V4 estimability;
- builds the registered primary/prior-sensitivity wrappers;
- builds the generality pair only when its stricter support gate passes;
- copies the canonical human-workspace receipt into the analysis bundle;
- hash-binds assembly, readout, wrappers, and upstream receipt;
- refuses to overwrite an existing output directory.

The GitHub `build-plant-v4-analysis-inputs` workflow is validation-only. Production inputs
are not synthesized in CI.

## 7. Run frozen CmdStan

Use exactly CmdStan 2.40.0:

```bash
python scripts/run_plant_v4_cmdstan.py \
  --cmdstan-dir <CMDSTAN_2_40_0_DIR> \
  --input-dir <V4_ANALYSIS_INPUT_WORKSPACE> \
  --out-dir <NEW_V4_FIT_WORKSPACE>
```

Before sampling, the runner verifies:

- copied human-workspace receipt;
- analysis-input receipt;
- licensed assembly hash;
- assembly readout;
- deterministic wrapper rebuild;
- wrapper hashes;
- generality-pair presence/absence;
- frozen CmdStan version.

Registered sampler diagnostics are fail-closed. Automatic retuning is forbidden.

## 8. Post-fit evidence and publication review

When diagnostics pass, the runner automatically computes the frozen probability estimands
and decision labels.

A completed fit does **not** automatically reactivate the BALANCE paper.

```text
fit/post-fit evidence
-> frozen reactivation evidence gate
-> explicit human publication review
```

The publication status is never changed automatically by the fit runner.

## Immutable-workspace rule

Every persistent evidence stage uses a new output directory:

```text
intake
architecture adjudication
human-input composition
analysis-input build
CmdStan fit
```

Corrections or later stage arrivals create a new workspace. Previous evidence states are not
overwritten.

## Claim ceiling

This sequence freezes operational order and provenance only. It contains no coder judgment,
adjudicated biological state, fitted effect, causal result, cross-universe conclusion, or
publication decision.

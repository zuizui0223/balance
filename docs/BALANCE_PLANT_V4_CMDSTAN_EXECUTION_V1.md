# BALANCE plant V4 CmdStan execution contract v1

## Status

Frozen before independent U2/U6 architecture outcomes are opened.

Machine-readable contract:
`data/BALANCE_PLANT_V4_FIT_EXECUTION_CONTRACT_V1.json`.

Production runner:
`scripts/run_plant_v4_cmdstan.py`.

The runner is intentionally a thin CmdStan CLI wrapper. The repository does not add a
CmdStanPy dependency and CI does not install CmdStan. Actual fitting begins only after the
licensed assembly and V4 pre-fit JSON inputs have been generated from genuine human
returns.

## Frozen CmdStan version

The execution engine is fixed prospectively at:

```text
CmdStan = 2.40.0
```

A fresh official CmdStan source tarball does not necessarily contain an installed
`bin/stanc` entry. The runner therefore first executes CmdStan's own registered target

```text
make bin/stanc
```

when the compiler is absent. It then reads `bin/stanc --version` before model compilation
and refuses to proceed when the installed version differs. Recording a later version in the
fit receipt is not a substitute for this preflight check.

## Frozen sampling configuration

Every registered fit uses:

```text
chains = 4
num_warmup = 1000 per chain
num_samples = 2000 per chain
save_warmup = false
thin = 1
seed = 20260930
metric = diag_e
adapt_delta = 0.99
max_depth = 15
output sig_figs = 18
```

The same random seed is supplied to CmdStan with chain IDs 1–4, so CmdStan applies the
registered chain-specific RNG offset.

No sampling setting is changed after inspecting fitted effect signs.

## Registered fits

The runner fits the following inputs when available:

```text
PRIMARY
  BALANCE_PLANT_V4_STAN_INPUT.json
  BALANCE_PLANT_V4_MULTINOMIAL.stan

PRIMARY_PRIOR_SENSITIVITY
  BALANCE_PLANT_V4_PRIOR_SENSITIVITY_INPUT.json
  BALANCE_PLANT_V4_MULTINOMIAL.stan

TEMPORAL_GENERALITY
  BALANCE_PLANT_V4_TEMPORAL_GENERALITY_INPUT.json
  BALANCE_PLANT_V4_TEMPORAL_GENERALITY.stan

TEMPORAL_GENERALITY_PRIOR_SENSITIVITY
  BALANCE_PLANT_V4_TEMPORAL_GENERALITY_PRIOR_SENSITIVITY_INPUT.json
  BALANCE_PLANT_V4_TEMPORAL_GENERALITY.stan
```

The generality pair is optional only because the stronger frozen support gate can remain
closed while the primary V4 fit is estimable. Exactly one generality input is forbidden:
both must exist together or neither is fit.

## Audited wrapper versus raw Stan data

The pre-fit files are audit wrappers:

```json
{
  "stan_data": { "...": "..." },
  "metadata": { "...": "..." }
}
```

They are not passed directly to CmdStan.

For every fit, the runner:

1. hashes the wrapper;
2. validates that it contains exactly `stan_data` and `metadata`;
3. writes a deterministic raw `stan_data.json`;
4. hashes that raw data file;
5. passes only the raw data to CmdStan.

This prevents audit metadata from accidentally becoming a Stan data variable.

## Fit-input provenance

Before compiling or sampling, the runner reloads
`BALANCE_PLANT_V4_LICENSED_ASSEMBLY.csv` and deterministically rebuilds the frozen V4
pre-fit pipeline in memory.

The supplied wrapper JSON files must exactly equal those rebuilt objects.

This means:

- the primary and primary-prior-sensitivity wrappers must both exist and match the licensed
  assembly exactly;
- if the licensed assembly passes the frozen temporal-generality support gate, both
  generality wrappers must exist and match the deterministic rebuild;
- if the licensed assembly does **not** pass that gate, neither generality wrapper may be
  present;
- wrappers copied from another intake/assembly workspace are rejected even if their Stan
  dimensions happen to be valid;
- the licensed assembly SHA256 and every wrapper SHA256 are written into the execution
  receipt;
- `BALANCE_PLANT_V4_ANALYSIS_INPUTS_RECEIPT_V1.json` is required and every file hash in
  that receipt is verified before compilation;
- the canonical `BALANCE_PLANT_V4_HUMAN_INPUT_WORKSPACE_RECEIPT_V1.json` must be copied
  into the analysis-input bundle; its SHA256, schema, assembly-ready flag, and closed
  primary-human-gate state are revalidated before compilation;
- the analysis-input receipt SHA256 and the copied upstream composed-human-workspace receipt
  path+SHA256 are propagated into the fit execution receipt.

Posterior summaries therefore cannot be standardized over one assembly while being fitted
to another.

## Immutable fit workspace

A V4 fit output directory is a one-run evidence workspace.

- the requested `--out-dir` must not already exist;
- rerunning the same or a corrected fit requires a new output directory;
- previous chain CSVs, diagnostics, receipts, and optional generality summaries are never
  silently overwritten;
- a primary-only run cannot inherit stale generality outputs from an earlier fit.

## Chain and summary completeness

Every registered fit must contain exactly four unique chain CSV files, matching the frozen
chain count. Each chain must contain exactly 2,000 post-warmup draws under the registered
`thin=1` contract, and every chain must report CmdStan version `2.40.0`.

The convergence summary must contain the complete registered parameter set:

```text
PRIMARY / PRIMARY_PRIOR_SENSITIVITY
  alpha: 6 parameters
  beta:  9 parameters
  total: 15

TEMPORAL_GENERALITY / TEMPORAL_GENERALITY_PRIOR_SENSITIVITY
  alpha: 6
  beta:  9
  gamma_u6_ordered: 3
  total: 18
```

Missing, duplicated, or unexpected registered parameters fail closed before diagnostic
thresholds are evaluated. A truncated chain cannot be compensated by pooling the remaining
chains.

## Diagnostics

Posterior reporting is blocked unless every registered fit passes:

```text
divergences = 0
max-depth hits = 0
minimum chain E-BFMI >= 0.30
maximum parameter R-hat <= 1.01
minimum parameter bulk ESS >= 400
minimum parameter tail ESS >= 400
```

R-hat and ESS are read from CmdStan `stansummary`. The diagnostic scope is the fitted
model parameter families:

```text
alpha
beta
gamma_u6_ordered   # generality model only
```

Generated quantities such as `log_lik` and row-level category probabilities do not decide
whether parameter convergence passed.

## No automatic retuning

If any diagnostic gate fails:

```text
FIT_DIAGNOSTICS_FAILED
-> no Delta_T / Delta_M decision
-> no generality decision
-> no automatic change of adapt_delta, max_depth, iterations, priors, or model
```

Any remediation requires an explicit versioned change rather than silent data-dependent
sampler tuning.

## Post-fit bridge

Once all required fit diagnostics pass, the runner reads the chain CSV parameter draws and
calls the prospectively frozen estimand functions:

```text
summarize_v4_primary_postfit
summarize_v4_temporal_generality_postfit
```

The standardization surface remains the one frozen in
`BALANCE_PLANT_V4_ESTIMAND_STANDARDIZATION_V1.json`; raw coefficient signs cannot replace
the registered predicted-probability contrasts.

## Execution

After genuine human returns have closed the V4 assembly gates and the pre-fit builder has
produced inputs:

```bash
python scripts/run_plant_v4_cmdstan.py \
  --cmdstan-dir /path/to/cmdstan \
  --input-dir release/generated/plant_v4_analysis_inputs \
  --out-dir release/generated/plant_v4_fit
```

The runner compiles the two registered Stan programs, executes the registered fits, writes
per-chain logs and CSV files, invokes `stansummary`, writes fit receipts and diagnostics,
and only then writes the post-fit probability-contrast summaries.

## Reproducibility receipt

Every completed fit execution receipt records:

- licensed assembly SHA256;
- analysis-input bundle receipt SHA256;
- upstream composed-human-workspace receipt SHA256;
- every per-job `FIT_RECEIPT.json` SHA256;
- source Stan model SHA256;
- compiled executable SHA256;
- audited input-wrapper SHA256;
- materialized raw-data SHA256;
- CmdStan version recorded in chain output;
- exact command argv for every chain;
- every chain CSV SHA256;
- `stansummary` output SHA256;
- diagnostic gate result;
- primary post-fit summary SHA256;
- temporal-generality post-fit summary SHA256 when that registered fit is active.

Execution status is explicit:

```text
DIAGNOSTIC_FAIL
DIAGNOSTICS_PASS_POSTFIT_PENDING
COMPLETE
```

A diagnostic failure receipt contains no post-fit outputs. `COMPLETE` is written only after
all registered post-fit outputs are present and hash-bound.

## Claim ceiling

This contract fixes execution, diagnostics, and the bridge to the already-registered
post-fit estimands. It contains no observed effect, no biological conclusion, and no
publication decision.

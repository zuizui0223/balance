# BALANCE plant independent-coder packet runbook v1

## Purpose

This runbook converts the frozen coder-handoff contract into two separate downloadable
packets, one for `CODER_A` and one for `CODER_B`.

The packets are evidence-identical. They differ only in which worksheet rows are included.

## Build route

Manual GitHub Actions workflow:

```text
.github/workflows/build-plant-coder-packets.yml
```

The workflow is intentionally `workflow_dispatch` only. It is not triggered on every
commit.

It validates:

- coder-handoff manifest;
- coder-packet blinding;
- U1/U2/U6 frozen worksheet contracts;
- packet determinism.

Then it builds:

```text
balance-plant-coder-a-packet-v1
balance-plant-coder-b-packet-v1
```

as separate GitHub Actions artifacts.

## Packet contents

Each coder receives the same:

```text
plant codebook
double-coding protocol

U1 source packet
U2 source packet
U6 frozen source packet
```

Each coder receives only their own worksheet rows:

```text
CODER_A
or
CODER_B
```

The other coder's rows are absent.

## Explicit exclusions

Packets do not contain:

- U1/U2 source-screen conflict calls;
- U6 candidate-adjudication rationale;
- post-coding adjudication templates;
- agreement reports;
- predictor-receipt ledgers;
- publication/reactivation decisions.

These exclusions are tested by filename class and by the frozen handoff manifest.

## Independence rule

Packets should be distributed separately.

Coders must not exchange:

- worksheets;
- notes;
- interim category decisions;
- questions that reveal a category choice.

Clarification questions should be answered by a neutral coordinator using only the frozen
codebook/protocol. If a clarification changes the codebook materially, both coders must
recode the same frozen reliability frame under the versioned repair protocol.

### U6 completion flag

U6 worksheets have an explicit completion field. Before return, every coder-specific U6 row
must have:

```text
coding_status = CODED
```

A biological field may still be `UNRESOLVED`; that is a legitimate completed judgment.
`UNSTARTED` is not.

Do not alter `dependency_group`, `source_reference_ids`, or `coder_id`.

## Return rule

The returned worksheet must preserve exactly:

```text
CODER_A
CODER_B
```

as coder identifiers.

Relabeling or creating a third coder identifier fails the readiness contract.

After both worksheets are frozen:

1. schema/category validation;
2. raw agreement, Cohen kappa, Gwet AC1, exact disagreement list;
3. if any field has raw agreement < 0.80: codebook repair + independent recoding of the same
   frozen groups;
4. only after the reliability gate passes: source adjudication;
5. predictor outcome-independence is adjudicated separately;
6. only licensed U2/U6 rows may enter V4 assembly.

## Reproducibility

The ZIP writer uses:

- sorted payload paths;
- fixed ZIP timestamp;
- fixed file mode.

Two builds from the same repository state therefore produce byte-identical coder ZIPs.

## Claim ceiling

Packet construction demonstrates blinding and handoff reproducibility only. It does not
adjudicate any biological field and does not create a model-ready dataset.


## Validated return ingestion

Returned coder worksheets are not copied directly over tracked repository files.

For each lane, validate and merge the two returned files:

```bash
python scripts/merge_plant_coder_returns.py \
  --lane U2 \
  --coder-a /path/to/CODER_A_return.csv \
  --coder-b /path/to/CODER_B_return.csv \
  --out-dir /path/to/handoff_workspace
```

The merger requires:

- the exact frozen dependency-group set for the lane;
- exactly one row per frozen group from each coder;
- preserved `CODER_A` / `CODER_B` identifiers;
- the canonical coding schema;
- complete categorical fields.

Missing groups, extra groups, wrong coder identity, partial schemas, or duplicate rows fail
closed.

The merged ledger is written in canonical alternating coder order. It is then used as an
external handoff-workspace override; tracked repository data do not need to be overwritten.

## External handoff workspace

The V4 analysis builder accepts:

```bash
python scripts/build_plant_v4_analysis_inputs.py \
  --input-dir /path/to/handoff_workspace
```

Only human-mutable basenames may override repository defaults:

- U1/U2/U6 completed coding worksheets;
- U1/U2/U6 adjudication files;
- U2/U6 predictor-receipt ledgers.

Frozen source packets, samples, Pass-1 manifests, dependence maps, and model specifications
always remain repository-controlled.

If an override file exists but is malformed, the builder fails closed. It does not silently
fall back to the blank tracked version.

Once all primary human gates close:

```bash
python scripts/build_plant_v4_analysis_inputs.py \
  --input-dir /path/to/handoff_workspace \
  --build
```

This emits the licensed U2/U6 assembly and registered V4 Stan inputs without mutating the
frozen repository inputs.

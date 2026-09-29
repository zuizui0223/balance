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

# BALANCE DOI-module deposition checklist v1

## Release purpose

This checklist governs deposition of the frozen BALANCE technical certification module. It does **not** reactivate BALANCE as a standalone paper and it does not raise the empirical claim ceiling.

The release candidate is built by

```text
python scripts/build_balance_doi_bundle.py
```

and produces

```text
release/generated/BALANCE_DOI_MODULE_V1.zip
release/generated/BALANCE_DOI_MODULE_V1_RELEASE_RECEIPT.json
release/generated/BALANCE_DOI_MODULE_V1.sha256
```

## Scientific gates — must all be green before deposition

- [ ] `docs/PUBLICATION_STATUS.md` still records `STATUS = DOI_MODULE / DORMANT_PAPER_BRANCH`.
- [ ] `ACTIVE_PUBLICATION_QUEUE = false` remains frozen.
- [ ] `manuscript/BALANCE_CANONICAL_MANUSCRIPT_MANIFEST_V1.json` still records `0_direct_matched_receipts`.
- [ ] The canonical claim ceiling still excludes direct BALANCE worldline occupancy.
- [ ] Deterministic manuscript assembly matches the frozen manuscript SHA256, word count and line count.
- [ ] `BALANCE_PATTERN_LEDGER_V1.csv` validates under the canonical one-cluster-per-row contract.
- [ ] Recomputed pattern readout exactly equals `BALANCE_PATTERN_READOUT_V1.json`.
- [ ] Frozen empirical receipts remain 17 independent clusters, 9 middle-regime signatures and 0 direct matched worldline receipts.
- [ ] Figure 3 remains bound to the same validated ledger/readout contract.
- [ ] Full repository tests pass.
- [ ] Dedicated DOI-bundle workflow passes and uploads the release artifact.

A failure at any scientific gate blocks deposition. Do not repair a release failure by widening the claim, relaxing an identification gate, dropping an adverse/negative record, or changing the frozen empirical universe merely to recover a green build.

## Bundle integrity gates

- [ ] `BALANCE_DOI_MODULE_V1.zip` opens successfully.
- [ ] The ZIP contains `RELEASE_RECEIPT.json`.
- [ ] The receipt reports `all_contract_checks_pass = true`.
- [ ] The receipt lists every bundled file with byte size and SHA256.
- [ ] The external `.sha256` file matches the ZIP bytes actually deposited.
- [ ] The release candidate is generated from the intended Git commit.
- [ ] No `.git`, cache, bytecode or previous `release/generated` outputs are bundled.

The release receipt is an audit record. It is not evidence for a stronger biological conclusion.

## Human metadata gates — intentionally not automated

The repository does not infer or choose these values. Complete them manually at deposition time:

- [ ] confirm author list and author order;
- [ ] add ORCID identifiers where desired and verified by each author;
- [ ] choose and confirm the software/data/documentation license(s);
- [ ] write the public deposition description without exceeding the frozen claim ceiling;
- [ ] choose keywords/communities;
- [ ] upload the exact CI-verified ZIP;
- [ ] verify the uploaded checksum against `BALANCE_DOI_MODULE_V1.sha256`;
- [ ] mint the Zenodo DOI;
- [ ] record the minted DOI and release date in a follow-up repository commit or release note.

## Recommended deposition description boundary

A safe description should characterize BALANCE as a reproducible technical module for certifying and quantifying a persistent-conflict middle regime between no conflict and favorable differentiation. It may describe the source-adjudicated 17-cluster pattern synthesis as contextual evidence.

It should **not** say that:

- BALANCE is prevalent in nature;
- the literature directly identifies pooled `Phi`, `rho`, `xi` or `d_B`;
- 17 clusters are a representative prevalence sample;
- any literature case supplies a direct matched shared-versus-differentiated worldline receipt;
- the module establishes accessibility, invasion, fixation or occupancy.

## Post-deposition

After a DOI is minted:

- [ ] preserve the deposited ZIP and checksum unchanged;
- [ ] add the DOI to the repository without rewriting the deposited artifact;
- [ ] cite a version-specific DOI for reproducibility where possible;
- [ ] keep subsequent theory/empirical development on new versions rather than mutating the deposited v1 snapshot.

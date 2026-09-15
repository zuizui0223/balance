# Publication status

## Current role

BALANCE is retained as a **technical certification module / dormant paper branch**, not as an active standalone manuscript.

Its role in the active programme is to support SLK's classification of the persistent-compromise region

```text
L > 0
Phi < 0
```

without competing with the flagship for the same scientific question.

## Retained contributions

The repository remains the canonical home for:

- direct optimized-worldline identification of the middle world;
- two-sided certificate `L>0, Phi<0`;
- position `xi`, depth `d_B`, reserve `rho`;
- environmental width/connectivity/topology diagnostics;
- direct-versus-decomposed worldline concordance;
- no-reentry sufficient conditions;
- switching-cost hysteresis and persistence.

These results remain citable and are now exposed through a self-verifying DOI-module release surface.

## DOI-module release surface

The release contract is defined by

```text
release/BALANCE_DOI_MODULE_MANIFEST_V1.json
docs/BALANCE_TECHNICAL_MODULE_V1.md
docs/ZENODO_RELEASE_CHECKLIST_V1.md
scripts/build_balance_doi_bundle.py
```

The builder fails closed unless the dormant-module status, canonical manuscript contract, empirical claim ceiling and frozen pattern readout remain mutually consistent. A successful build emits a versioned ZIP, a release receipt with per-file SHA256 inventory, and a checksum for the exact ZIP proposed for deposition.

The release surface does **not** infer author order, ORCID identifiers, a license, or a DOI. Those are human deposition metadata and must be confirmed separately before a Zenodo record is minted.

## What is no longer an active paper claim

BALANCE will not currently be developed as a separate full paper whose central claim is simply the geometry of `L>0, Phi<0`. The existence of that state belongs to the SLK flagship; BALANCE supplies the diagnostic and certification machinery underneath it.

The frozen literature-pattern layer is contextual evidence only. It does not identify direct matched BALANCE worldline occupancy, natural prevalence, or pooled `Phi`, `rho`, `xi`, or `d_B` across unmatched systems.

## Reactivation rule

A standalone BALANCE manuscript can be reconsidered only if at least one of the following becomes true:

1. direct empirical worldline data recover a nontrivial middle-world geometry that is itself a biological result;
2. a theorem family emerges that is independent of SLK's state classification and cannot be reduced to diagnostic elaboration;
3. an empirical hysteresis/persistence result establishes a distinct scientific question.

Until then:

```text
STATUS = DOI_MODULE / DORMANT_PAPER_BRANCH
ACTIVE_PUBLICATION_QUEUE = false
```

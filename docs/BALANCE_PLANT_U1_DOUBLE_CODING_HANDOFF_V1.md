# BALANCE plant U1 independent-coder handoff v1

## Status

U1 now has the same operational independent-coder handoff that already existed for U2.

The review universe is source-closed at 47/47 taxa, the deterministic first-20 reliability sample is frozen, and all 20 sampled primary sources are resolved.

Canonical coder packet:

```text
data/BALANCE_PLANT_U1_DOUBLE_CODE_SOURCE_PACKET_V1.csv
```

Blank two-coder worksheet:

```text
data/BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv
```

Executable handoff guard:

```text
balance_domain/plant_u1_double_code.py
tests/test_plant_u1_double_code.py
```

## Blinding rule

Coders receive only:

- sample order;
- taxon / dependency-group identity;
- primary citation;
- DOI when available;
- the shared plant codebook and double-coding protocol.

They must not receive before both sheets are frozen:

```text
data/BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv
data/BALANCE_PLANT_U1_SCREENING_PROVISIONAL_V1.csv
data/BALANCE_PLANT_U1_SCREENING_PROVISIONAL_V1.csv
docs/BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.md
docs/BALANCE_PLANT_U1_PROVISIONAL_SCREENING_DIAGNOSTIC_V1.md
```

The source-resolution ledger's `evidence_surface` and notes are also excluded from the coder packet.

## Worksheet contract

Each of the 20 frozen groups has exactly two blank rows:

```text
CODER_A
CODER_B
```

Each coder independently assigns:

```text
conflict_status
architecture_mode
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

The worksheet uses the canonical agreement schema directly, so once both coders freeze their entries it can be passed without reformatting to `balance_domain.plant_macro_agreement`.

## Agreement gate

For each core field the canonical report returns:

- raw agreement;
- Cohen's kappa;
- Gwet's AC1;
- category marginals;
- exact disagreement groups.

Any raw agreement below 0.80 triggers codebook repair before confirmatory freeze.

## Current blocker

No source reconstruction or packet-building work remains for U1.

The gate is now genuinely external to the assistant-generated development artifacts:

> two independently produced coder classifications must be completed without access to the provisional BALANCE calls.

## Claim ceiling

This handoff establishes source closure, sample identity and coder blinding only. It does not make any U1 biological classification adjudicated or primary-model eligible.

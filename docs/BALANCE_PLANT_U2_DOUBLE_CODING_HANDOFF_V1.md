# BALANCE plant U2 independent-coder handoff v1

## Status

U2 is the first plant review universe that satisfies the programme's source-closure requirement for a formal reliability sample.

The source universe is:

```text
Barrett 2002 sexual-interference review
22 dependency groups
37 review references fully classified
22 / 22 dependency groups linked to primary evidence
```

The provisional BALANCE coding already exists, but it is **not part of the coder packet**.

## Deterministic reliability sample

The double-coding protocol requires the first 20 unique dependency groups from an outcome-blind frozen screening frame.

For U2, record IDs are frozen before the provisional conflict/architecture screen. Therefore the formal reliability sample is:

```text
U2_001
...
U2_020
```

Selection is independent of:

- conflict status;
- architecture mode;
- evidence quality after screening;
- whether a case is positive, null or unresolved.

U2_021 and U2_022 are outside the sample only because they are records 21 and 22. They are not outcome-based exclusions.

Canonical sample:

```text
data/BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv
```

Blank coder worksheet:

```text
data/BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv
```

## Blinding rule

Independent coders may receive:

- taxon/dependency-group identity;
- the review-linked primary citation(s);
- DOI(s) when available;
- the plant macro codebook;
- the double-coding protocol.

They must **not** receive:

```text
data/BALANCE_PLANT_U2_SCREENING_PROVISIONAL_V1.csv
docs/BALANCE_PLANT_U2_PROVISIONAL_SCREENING_DIAGNOSTIC_V1.md
```

before both coder sheets are frozen.

The provisional screen is a first-pass development artifact, not a gold standard.

## Fields to code

Each coder independently assigns:

```text
conflict_status
architecture_mode
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

`UNRESOLVED` is valid and should be used rather than inferred values.

## Agreement gate

After both coder sheets are frozen, the existing canonical agreement module reports:

- raw agreement;
- Cohen's kappa;
- Gwet's AC1;
- category marginals;
- exact disagreement groups.

Any core field with:

```text
raw agreement < 0.80
```

triggers codebook repair before confirmatory freeze.

## Relationship to U1

U1 remains useful as a broad-interaction specificity universe, but its formal 47-taxon frame is still blocked by three supplement-only taxa.

U2 does not wait on that reconstruction because U2 is independently review-defined and source-closed.

Thus the programme now has:

```text
U1 = broad ecological-interaction specificity lane, formal sample still open
U2 = mechanism-targeted sexual-interference lane, formal coder sample ready
```

This is not a comparison of natural prevalence.

## Claim ceiling

Freezing this sample establishes only that the reliability exercise is outcome-blind and reproducible.

It does not make the provisional U2 biological calls adjudicated, nor does it make any row primary-model eligible.

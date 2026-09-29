# BALANCE plant macro independent double-coding protocol v1

## Purpose

The plant macro programme cannot move from pilot screening to confirmatory analysis unless the core conflict and architecture variables are reproducible across independent coders.

The first agreement exercise therefore treats coding reproducibility as an empirical gate.

## Pilot sample

Double-code the first **20 unique dependency groups** drawn from the outcome-blind plant screening frame.

Selection rule:

1. order groups by the frozen screening-frame record identifier;
2. take the first 20 groups after duplicate clustering;
3. do not replace difficult or ambiguous systems with easier examples;
4. if fewer than 20 groups are available in an early extraction batch, code all available and continue when the next batch is frozen.

The current hand-built 29-record plant pilot can be used only to test the agreement machinery. It is not the confirmatory agreement sample because it was not outcome-blind.

## Independent coding

Each coder receives:

- source PDFs / source links;
- the plant codebook;
- the same cluster definition;
- no access to the other coder's classifications.

Coders independently assign:

```text
conflict_status
architecture_mode
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

They may add notes and mark `UNRESOLVED`.

`UNRESOLVED` is a legitimate category, not a failure to be hidden.

## Agreement metrics

For every field report:

1. exact raw agreement;
2. Cohen's kappa;
3. Gwet's AC1;
4. category marginals;
5. exact dependency groups in disagreement.

Why report both kappa and AC1:

- kappa is familiar but can behave poorly under highly imbalanced categories;
- AC1 provides a prevalence-robust companion;
- neither coefficient substitutes for the raw disagreement table.

## Codebook-repair trigger

Before confirmatory freeze:

```text
raw agreement < 0.80
on any core field
-> REPAIR_REQUIRED
-> no source adjudication yet
-> versioned codebook repair
-> new independent recoding round on the SAME frozen reliability groups
-> recompute agreement
```

The 0.80 value is a workflow trigger, not a claim that 0.80 has universal statistical meaning.

The biological sample is **not** replaced after seeing disagreement. Difficult groups remain
in the frozen reliability frame; otherwise the repair process could select easier systems
and inflate apparent reproducibility.

No disagreement is resolved merely by letting one coder overrule the other. Source
adjudication opens only after the repaired coding round clears the reliability gate.

## Adjudication after independent coding

After metrics are frozen:

1. reveal disagreements;
2. return to the exact source evidence;
3. record an adjudicated value;
4. record why the original wording permitted disagreement;
5. update the codebook only by a versioned change;
6. if codebook wording changes materially, independently recode the same frozen reliability
   frame under the new codebook version and recompute agreement before adjudication.

The final analysis ledger uses adjudicated values but preserves the pre-adjudication coder receipts.

## Independence from outcome

For predictor fields, disagreement adjudication must not use architecture outcome as a shortcut.

Exposure geometry is coded from the integrated/challenge state, not from the focal
resolution architecture. Thus observed dichogamy/herkogamy cannot by itself establish
`conflict_timing_geometry` or `conflict_spatial_geometry`.

For example:

```text
heteranthery observed
!=>
module_substrate was SERIAL_WITHIN_FLOWER
```

unless serial stamen architecture is independently documented.

Likewise:

```text
dichogamy observed
!=>
conflict_timing_geometry was SEQUENTIAL_WITHIN_UNIT
```

unless the functional demand timing itself is documented rather than inferred from dichogamy.

## Two distinct predictor gates

Reproducibility and outcome-independence are different requirements.

### Gate A — independent-coder reproducibility

The double-coding exercise asks whether two blinded coders can assign the same predictor
category from the same primary evidence.

### Gate B — outcome-independent predictor receipt

Even perfect coder agreement does not license a predictor if the evidence used to assign it
was inferred from the focal architecture outcome.

Therefore every confirmatory row additionally requires a separate adjudicated receipt for:

```text
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

The receipt records source, evidence type, and whether the predictor value is logically
independent of the focal architecture outcome.

The frozen predictor-receipt frames are:

- `data/BALANCE_PLANT_U1_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv`
  — 20 reliability groups x 3 predictors = 60 slots; still an empty outcome-blind frame
  until U1 conflict-positive adjudication exists;
- `data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv`
  — 60 slots total; the eight source-screen conflict-positive groups already have all three
  predictor values source-screened outcome-independently, but none is independently
  adjudicated;
- `data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv`
  — 21 conflict-first groups x 3 predictors = 63 slots; all 63 are source-screened
  outcome-independently, but none is independently adjudicated.

These receipt frames contain no focal architecture outcome as a licensing shortcut.

A predictor enters the model only after **both Gate A and Gate B** are closed.

## Worksheet completion semantics

For every frozen row, coders must enter an explicit value for each coding field.

For U1/U2:

```text
conflict_status
architecture_mode
module_substrate
conflict_timing_geometry
conflict_spatial_geometry
```

For U6, the same four architecture/predictor fields are coded and the returned row must also
set:

```text
coding_status = CODED
```

The identifiers are immutable:

```text
cluster_id / dependency_group
coder_id
U6 source_reference_ids
```

Do not edit those fields.

`UNRESOLVED` is an allowed **completed biological code** when the evidence does not support
a more specific category. A blank cell or U6 `coding_status=UNSTARTED` means the coding task
is not complete.

Therefore:

```text
UNRESOLVED != UNSTARTED
```

A returned U6 worksheet with any `UNSTARTED` row fails the return-ingestion contract even
if the category columns contain text.

## Architecture-versus-resolution language

Coders always score `architecture_mode`.

Only after `conflict_status=POSITIVE` is independently established may the analysis describe that architecture as a candidate conflict-resolution mode.

## Confirmatory freeze gate

The plant macro search frame cannot be declared analysis-ready until:

- the double-coded sample is complete;
- agreement metrics are generated by the canonical script;
- every field below the workflow threshold has undergone codebook repair;
- adjudication provenance is retained;
- no coder output has been silently overwritten.

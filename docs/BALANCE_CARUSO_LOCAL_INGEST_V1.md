# BALANCE Caruso non-duplicated workbook local ingest v1

## Status

```text
public Dryad landing metadata      VERIFIED
source-of-truth filename           VERIFIED
source-of-truth record count       VERIFIED = 755
local/programmatic bytes           NOT YET ACQUIRED
local ingest implementation        READY
biological re-screen               NOT STARTED FROM DATABASE BYTES
```

This is deliberately an acquisition/identity boundary, not a BALANCE result.

## Frozen public source

Caruso et al. 2019:

```text
publication DOI  10.1111/evo.13639
Dryad DOI        10.5061/dryad.2v8c5g0
```

The current Dryad landing page exposes two files:

```text
Exp_stud_NOTdup_Dryad.xls   451.58 KB   file_stream 21862
Exp_stud_dup_Dryad.xlsx     231.08 KB   file_stream 21863
```

The first is the source-of-truth inventory. Dryad describes it as 755 records with
directional selection gradients and associated standard errors, plus a second worksheet
describing the database columns.

The duplicated workbook exists only to reconstruct the published pair construction and
must never create additional biological replication.

## Current transport boundary

The landing page is publicly visible, but direct file-stream retrieval from the current
execution environment returns HTTP 403. Earlier API-based download attempts also encountered
an authenticated-download boundary.

Therefore:

```text
transport failure != missing dataset
transport failure != negative scientific result
```

The analysis no longer depends on solving that transport problem programmatically. One
local copy of the exact non-duplicated workbook is sufficient to enter the deterministic
Stage-A ingest below.

## Local ingest

Install the optional legacy Excel reader:

```bash
python -m pip install -e '.[caruso]'
```

Then run:

```bash
python scripts/ingest_caruso_nondedup.py \
  Exp_stud_NOTdup_Dryad.xls \
  release/generated/caruso_nondedup_ingest_v1
```

The input basename is intentionally exact. A renamed duplicated workbook or a modern
`.xlsx` file is rejected rather than guessed.

## Fail-closed source checks

The ingest requires:

1. exact basename `Exp_stud_NOTdup_Dryad.xls`;
2. legacy `.xls` format;
3. exactly two worksheets;
4. exactly one worksheet/header combination producing 755 non-empty records;
5. a unique nonblank database header;
6. exactly one companion worksheet retained as the column-dictionary inventory.

The 755-row rule is detected before any BALANCE conflict screening.

## Outputs

```text
BALANCE_CARUSO_NONDUP_SOURCE_RECEIPT_V1.json
BALANCE_CARUSO_NONDUP_ROW_INVENTORY_V1.csv
BALANCE_CARUSO_NONDUP_COLUMN_DICTIONARY_V1.csv
```

The receipt records:

- source SHA256;
- byte count;
- Dryad DOI and public file-stream ID;
- worksheet names;
- detected data sheet;
- header row number and original field names;
- exact 755-record count;
- companion dictionary sheet;
- claim ceiling.

The row inventory preserves original workbook row numbers and signed values as normalized
text. It does not classify conflict.

## Next gate

Only after the Stage-A receipt passes should the inventory be grouped into frozen
article / experiment / population / trait units and screened for biological agent identity,
same-trait compatibility, signed opposition, and uncertainty.

No row is promoted because it makes an existing BALANCE result stronger.

## Claim ceiling

```text
immutable_source_inventory_only_no_BALANCE_conflict_result
```

This ingest can establish what the public database contains. It cannot establish an
opposed-agent pair, an effect-size-ready cluster, or direct BALANCE occupancy.

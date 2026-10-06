# Peucedanum raw-data reanalysis contract v1

## Purpose

This contract turns the current published-summary `Peucedanum multivittatum` critical-region anchor into a reproducible individual/population-data reanalysis without allowing a new criticality claim before the source analysis is reproduced.

The Chapter-2 target remains observational. This contract does **not** turn the Peucedanum datasets into a causal `W_S*` versus `W_D*` experiment.

## Registered public sources

### 2021 population dataset

```text
DOI: 10.5061/dryad.b5mkkwhcq
file: Kudo&Shibata_Ecol&Evol_DataSet.xlsx
period: 2017-2019
populations: 9
```

Dryad states that the workbook contains notes, plot locations, population reproductive data across 2017-2019, and individual size/sex-allocation/reproductive-performance data for 2017.

### later Peucedanum dataset

```text
DOI: 10.5061/dryad.w3r2280v5
files:
  Data1_FloralGender.xls
  Data2_basedata20-21.xls
  Data3_FitnessAnal.xls
  README.md
```

### 2025 critical-region archive

```text
article DOI: 10.1111/1365-2745.70130
repository DOI: 10.14943/hu95572
handle: 2115/95572
Wiley supplement: jec70130-sup-0001-supinfo.zip
```

The Hokkaido repository is the preferred source for the 2025 raw data + reproducible code. Transport failure is tracked separately in issue #5.

## Published-summary verification baseline

Before raw-data recovery, the current publisher article surface was independently
rechecked and frozen in:

```text
empirical/peucedanum/PEUCEDANUM_2025_PUBLISHED_SUMMARY_RECEIPT_V1.json
```

This receipt contains the five-plot estimates and standard errors for final-fruit
selection differential and gradient, plus the five female-gain exponents and their
reported uncertainties. It matches the pre-existing BALANCE point-estimate fixtures.

The receipt is the R1 numeric target surface. It is **not** a substitute for the raw-data
reanalysis; year/individual dependence, source-model reproduction, and robustness still
require the public archive bytes.

## Stage R0 — source inventory and semantic mapping

Do not infer spreadsheet columns from names alone. For every source file/sheet, record:

```text
source_doi
source_file
source_sheet
row_count
column_names
mapping_status
```

Map source-specific columns into the normalized semantics below only after visual inspection of the workbook notes / README.

Core normalized fields:

```text
dataset_id
source_doi
year
population_id
plant_id
flowering_day
perfect_flower_count
male_flower_count
initial_fruit_count
intact_fruit_count
predator_egg_count
seed_predation_rate
flower_stem_height
```

Derived fields may include:

```text
total_flower_count = perfect + male
male_fraction = male / total
final_fruit_set_rate = intact_fruit_count / perfect_flower_count
```

Optional male-function / paternity variables are retained when present but are not required for the female-fitness critical-region reproduction.

Missing source values remain missing. Do not impute values merely to complete a plot-year cell.

### Deterministic local R0 ingest

Once any registered public source bytes are available locally, inventory them before
assigning biological semantics:

```bash
python scripts/ingest_peucedanum_raw.py inventory \
  <source-file-1> [<source-file-2> ...] \
  --out-dir release/generated/peucedanum_source_inventory_v1
```

For Excel workbooks install the optional readers:

```bash
python -m pip install -e '.[peucedanum]'
```

The inventory records exact source byte count/SHA256 plus file, sheet, row, and column
dimensions. It does **not** infer a header or a biological variable from a column name.

ZIP archives are accepted as provenance containers. The outer ZIP SHA256 and every member
SHA256 are frozen. Safe tabular members are exposed to the mapping contract as:

```text
<archive basename>::<member/path.csv>
```

Only CSV/TSV/XLS/XLSX members are decoded as tables; code/README members remain in the
archive inventory. Absolute paths, parent traversal, backslash path separators, and
duplicate member names fail closed.

After visually checking the source workbook notes/README, populate
`empirical/peucedanum/PEUCEDANUM_RAW_SEMANTIC_MAPPING_TEMPLATE_V1.json` with explicit
`source_file`, `source_sheet`, one-based `header_row`, and exact
`normalized_field -> source column` mappings. Only then change its status from

```text
TEMPLATE_NOT_SOURCE_VERIFIED
```

to

```text
SOURCE_VERIFIED_MAPPING
```

and run:

```bash
python scripts/ingest_peucedanum_raw.py normalize \
  <source-file-1> [<source-file-2> ...] \
  --mapping empirical/peucedanum/PEUCEDANUM_RAW_SEMANTIC_MAPPING_TEMPLATE_V1.json \
  --out-dir release/generated/peucedanum_normalized_v1
```

Normalization fails closed if the verified source table, header, or exact mapped column is
absent; if a required normalized semantic is unspecified; or if a derived field is supplied
rather than recomputed. Sheet-level constants such as year/population are allowed only when
they are explicitly frozen in the reviewed mapping.

Outputs:

```text
inventory:
  BALANCE_PEUCEDANUM_RAW_SOURCE_INVENTORY_V1.json

normalization:
  BALANCE_PEUCEDANUM_NORMALIZED_ROWS_V1.csv
  BALANCE_PEUCEDANUM_NORMALIZATION_RECEIPT_V1.json
```

The normalized rows are passed through the same fail-closed semantic validator used by the
downstream reanalysis contract. R0 therefore cannot silently promote guessed spreadsheet
semantics into R1.

## Stage R1 — reproduce before extending

No raw-data criticality result may be promoted until the reanalysis reproduces the published qualitative and quantitative targets sufficiently closely.

### Registered 2025 final-fruit selection targets

Plot order:

```text
HA, HL, HC, KD, HD
```

Linear selection differential `S`:

```text
-0.027, -0.051, +0.036, +0.021, +0.024
```

Linear selection gradient `beta`:

```text
-0.035, -0.029, +0.034, +0.008, +0.026
```

Female-gain exponents `b`:

```text
0.63, 0.45, 1.15, 1.26, 1.55
```

The key reproduction target is not only coefficient proximity but the published regime ordering:

```text
HA / HL: negative final-fruit selection and b < 1
HC / KD / HD: non-negative-to-positive final-fruit selection and b > 1
```

The source paper's model structure, standardisation, year handling and error family must be reproduced from the archived analysis code before setting numeric tolerances for coefficient equality.

## Stage R2 — individual-data critical region

Only after R1 passes, estimate the transition across the ordered context axis.

Minimum outputs:

```text
plot-specific signed margins
critical bracket(s)
bootstrap / model-based uncertainty
whether HL--HC remains the unique crossing region
```

If an explicit continuous antagonist-pressure axis is available, estimate a numeric crossing and propagate uncertainty in both the response coefficient and the axis. The current published-summary analysis propagates coefficient uncertainty only and is therefore weaker.

## Stage R3 — robustness

Run at minimum:

```text
leave-one-year-out
leave-one-plot-out where the estimand remains defined
alternative standardisation consistent with the source model
published-model reproduction vs minimal reanalysis comparison
```

A critical region is called stable only if the same broad transition is not driven by one year or one exceptional population.

## Stage R4 — three-world interpretation

Even a perfect R1-R3 reproduction remains an observational Chapter-2 anchor unless matched optimized worldlines exist.

Do not infer from Peucedanum alone:

```text
SCH causal conflict load L
shared-world optimum fitness W_S*
differentiated-world optimum fitness W_D*
architecture cost K
causal BALANCE occupancy
historical differentiation
```

The strongest allowed result before a matched worldline experiment is:

```text
MULTI_DEFINITION_OBSERVATIONAL_CRITICAL_REGION_REPRODUCED_FROM_RAW_DATA
```

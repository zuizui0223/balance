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

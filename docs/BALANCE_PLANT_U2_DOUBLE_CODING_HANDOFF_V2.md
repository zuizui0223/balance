# BALANCE plant U2 independent-coder handoff v2

## Status

U2 is source-closed at 22 dependency groups and has a formal 20-group reliability sample.

This version records and repairs a sampling-rule deviation **before any independent coding was performed**.

## Preregistered rule

The shared double-coding protocol was committed on 2026-09-18:

```text
commit b14770c74bd3545047c8168637c103c16e7b011a
order groups by frozen screening-frame record identifier
take the first 20 groups
```

The canonical U2 reliability sample is therefore:

```text
U2_001 ... U2_020
```

with `U2_021` and `U2_022` outside the reliability sample.

## Deviation and repair

On 2026-09-21 the sample was explicitly aligned to the record-ID protocol.

On 2026-09-22 commit `5f6b1c256e1a81238c77f6da96fecdee8eb1dbe5` recomputed it by lexicographic taxon order, replacing:

```text
U2_009  Wahlenbergia albomarginata
U2_020  Wachendorfia thyrsiflora
```

with:

```text
U2_021  Solanum rostratum historical
U2_022  Chamaecrista fasciculata historical
```

That change conflicts with the earlier frozen protocol.

No independent coder worksheet had been filled before this repair, so the correct action is to restore the preregistered record-ID sample rather than rewrite the protocol after the fact.

Machine-readable deviation receipt:

```text
data/BALANCE_PLANT_U2_SAMPLE_DEVIATION_REPAIR_V1.json
```

## Blinded source packet

Canonical sample:

```text
data/BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv
```

Coder source packet:

```text
data/BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv
```

Blank worksheet:

```text
data/BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv
```

The packet contains taxon identity, primary citation and DOI only. It does not expose evidence-family labels, provisional conflict calls or architecture calls.

## Agreement gate

Each of the 20 groups has exactly two blank rows, CODER_A and CODER_B, using the canonical agreement schema.

After both coders freeze entries, report raw agreement, Cohen's kappa and Gwet's AC1 for the five core fields. Any raw agreement below 0.80 triggers codebook repair.

## Relationship to U1

U1 is now also source-closed, has a frozen first-20 sample, and has its own blinded source packet and blank two-coder worksheet.

Thus both outcome-blind review universes are operationally ready for genuinely independent coding.

## Claim ceiling

This repair restores protocol compliance before reliability data exist. It does not adjudicate any biological field or make U2 primary-model eligible.

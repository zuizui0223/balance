# BALANCE plant U1 double-code protocol alignment v1

## Issue

The shared double-coding protocol was registered at commit
`b14770c74bd3545047c8168637c103c16e7b011a` before the first U1 sample was created.

That protocol specifies:

```text
order by frozen screening-frame record identifier
take the first 20 dependency groups
```

After full-47 reconstruction, the U1 sample file carried a lexicographic-taxonomy rule label instead.

## Why this is not a sample change

For U1 the two rules select exactly the same records:

```text
U1_001 ... U1_020
```

The three supplement-only taxa recovered later are `U1_045`–`U1_047` and all sort after the twentieth taxon. No row enters or leaves the reliability sample.

The repair therefore changes only:

1. the rule label;
2. the executable validator.

No independent coding existed before this alignment.

## Canonical rule

```text
FIRST_20_DEPENDENCY_GROUPS_BY_FROZEN_U1_RECORD_ID
```

Machine-readable receipt:

```text
data/BALANCE_PLANT_U1_PROTOCOL_ALIGNMENT_V1.json
```

## Claim ceiling

This is sampling-protocol alignment only. It does not change any biological coding or agreement result.

# BALANCE U3 prospective routing expansion queue v2

## Purpose

Freeze case order before prospective control conflict or routing outcomes are examined, while allowing the programme to continue when a case reaches a **matching-stage public evidence ceiling**.

## Frozen order

```text
1  Bixaceae        Amoreuxia wrightii
2  Brassicaceae    Brassica rapa
3  Lythraceae      Lagerstroemia indica
4  Malvaceae       Mollia lepidota
```

## Progression rule

A case is never deleted because matching is difficult.

The queue may advance only after every preceding row has one of three frozen pre-outcome states:

```text
CLOSED
FAILED
EVIDENCE_CEILING_BLOCKED
```

`EVIDENCE_CEILING_BLOCKED` means the matching-stage source gate has reached a registered public-retrieval ceiling. The dependence block remains in the queue as missingness. It is not converted to a negative biological outcome and is not removed from the programme.

Rows after the single `IN_PROGRESS` row must remain `NOT_STARTED`.

## Bixaceae disposition

`Amoreuxia wrightii` remains the first queued case.

Its closest nonheterantherous candidate is `Cochlospermum tetraporum`, but species-level animal-pollination eligibility remains unresolved under the registered public evidence ceiling. Farther controls with strong bee-pollination evidence are not substituted because phylogenetic proximity has higher matching priority.

Therefore:

```text
Bixaceae
  status = EVIDENCE_CEILING_BLOCKED
  block retained = U3_DEP_BIXACEAE_01
```

No conflict or routing outcome from Bixaceae was used to set this status.

## Active case

The next active row is now:

```text
Brassicaceae
Brassica rapa
U3_DEP_BRASSICACEAE_01
status = IN_PROGRESS
```

The existing matched-control hierarchy and predictor-blinding rules remain unchanged.

## Claim ceiling

This queue controls prospective acquisition and missingness handling. It does not establish control eligibility, conflict state, routing architecture, effect size, or prevalence.

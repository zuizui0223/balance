# BALANCE: pre-outcome U2 sampling-cell strategy (2026-11-19)

**Status: hypothetical design-only comparison, NOT a biological result or a change in source admission.**

The frozen V4 predictor dataset (U2=8, U6=21) is source-screened only. Human A/B architecture classifications, conflict adjudications, predictor receipts and multinomial V4 outcome fits are not available. The independent 12-group / 36-slot V2 U2 predictor expansion remains unfinished, and source coding must cover **every** frozen expansion slot, not just plausible favorable candidates.

## Two distinct goals for additional independent source data

1. **Reduce optimistic model uncertainty:** each future conflict-positive U2 group would add a row to the same five-column V4 predictor matrix. An idealized hypothetical independent Bernoulli outcome gives a lower bound on unpenalized logistic SE (NOT observed architecture effect and NOT actual four-class V4 power). All six U2 module × timing cells can be compared without response data.
2. **Open the preregistered G1 predictor common-support gate:** within the common SINGLE module stratum, U2 has one SIMULTANEOUS and two ORDERED/ALTERNATING groups, versus U6 18 and three. The G1 registered minimum is two per level in each universe. This is a stronger logical criterion than simple pooled-model rank or lower SE.

## Exact comparison of **one hypothetical additional qualified U2 group**

The six rows below are *design profiles only*. No new species has been identified, independently coded, admitted or analyzed. They would have to pass all genuine blind predictor, source, conflict and architecture gates.

| Hypothetical U2 profile | Idealized ordered-timing SE floor | Change from 1.0801 baseline | Idealized module SE floor | Would source-side G1 predictor **counts only** reach minimum? |
|---|---:|---:|---:|---|
| MODULAR + ORDERED/ALTERNATING | **1.0055** | **−6.9%** | **1.3784** | No |
| SINGLE + SIMULTANEOUS | **1.0422** | **−3.5%** | **1.4563** | **Yes, if genuinely qualified** |
| SINGLE + ORDERED/ALTERNATING | 1.0583 | −2.0% | 1.5100 | No |
| MODULAR + VARIABLE_CONTEXT | 1.0720 | −0.7% | 1.4036 | No |
| SINGLE + VARIABLE_CONTEXT | 1.0778 | −0.2% | 1.4989 | No |
| MODULAR + SIMULTANEOUS | 1.0778 | −0.2% | 1.4469 | No |

**Non-obvious design conflict:** maximizing improvement in an optimistic slope-information benchmark favors the currently empty U2 MODULAR+ORDERED cell. Repairing strict G1 cross-universe predictor common support requires **SINGLE+SIMULTANEOUS** instead. A research programme should not silently use one objective's apparent advantage as evidence for the other.

### Example of combined scenarios

If one **genuinely independent** and conflict-positive U2 SINGLE+SIMULTANEOUS group and one MODULAR+ORDERED/ALTERNATING group were added, then the illustrative ordered SE floor would change from 1.0801 to **0.9700**, while the modular SE floor would change from 1.5353 to **1.3014**. The single-stratum G1 *predictor counts* would meet the pre-outcome minimum, but the outcome-support, direction, prior-sensitivity and source-dependence gates would still be required.

To maintain G1 predictor counts after losing any single group, the currently frozen SINGLE-stratum categories would need at least three per timing × universe: example additions to U2 are two SINGLE+SIMULTANEOUS and one SINGLE+ORDERED. Those illustrative rows give ordered SE floor 0.9774. This is a **new optional robustness diagnostic**, not a higher preregistered G1 threshold.

## What to actually do

- Preserve the V2 U2 12-group expansion as an **all-groups blind coding task**, not a targeted outcome-chasing search. The source and coder may return EVIDENCE_CEILING for any slot. A resolved predictor alone does not promote a candidate to conflict-positive.
- After independent returns and conflict/architecture adjudication, check which cells actually acquired eligible independent groups. No real new values are assumed from the six hypothetical rows.
- Do not increase U6 SINGLE+SIMULTANEOUS preferentially just because that category is easy to find: the 18-group U6 abundance cannot fix the specific U2 common-stratum deficiency.
- If none of the 12 U2 groups qualifies as SINGLE+SIMULTANEOUS, report strict G1 as unsupported under the frozen frame. A new, separately preregistered source-independent discovery universe would be needed before stronger claims, without treating selected positive cases as a representative denominator.

## Reproducibility and evidence ceiling

```bash
python scripts/audit_plant_v4_preoutcome_u2_planner.py
python -m pytest -q tests/test_plant_v4_preoutcome_u2_planner.py
```

The implementation uses `_design_matrices` from the existing registered V4 model, reads **only pre-outcome source-side predictor CSVs**, and calculates hypothetical design profiles with exact rational Gram inverses. It does not touch `U2` V2 expansion worksheets, the 21 U6 groups, 42 unopened architecture coder rows, V4 priors, source analyses, fitted results, or flagship manuscripts.

**None of the displayed hypothetical profiles is an actual new species or biological association.**

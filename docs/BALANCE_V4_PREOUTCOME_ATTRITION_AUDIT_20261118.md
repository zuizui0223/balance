# BALANCE V4 pre-outcome exact attrition audit (2026-11-18)

## Status and allowed inference

**New read-only source-screen design audit.** This is not a fitted architecture model, an effect-size meta-analysis, evidence that BALANCE is occupied, or a general biological law. The U2/U6 predictor receipts are SCREENED, not independently ADJUDICATED. The two architecture coders have not returned the frozen blinded U2/U6 response labels.

This audit deliberately reads only the frozen U2 source conflict screen and the frozen U2/U6 V1 source-side predictor receipt CSVs. It does not open 42 U6 architecture coding entries, coder A/B outputs, V4 outcome assemblies, U3 discovery outcomes or other exploratory effect data.

Run from the repository root:

```bash
python scripts/audit_plant_v4_preoutcome_attrition.py
python -m pytest -q tests/test_plant_v4_preoutcome_attrition.py
```

## Scientific question

Can a small number of independent biological-group exclusions destroy the prospectively defined V4 predictor design, even before response classes are observed? Distinguish (i) **linear-algebra rank** from (ii) **the predeclared minimum of two groups for every included primary predictor level**. Neither implies outcome-class support or precise fitted associations.

The frozen predictor-only surface contains **29 source-screened groups**: eight strict-conflict-positive U2 groups and 21 conflict-first U6 groups. V4 has five design columns: separate U2/U6 intercepts, MODULAR substrate, ORDERED/ALTERNATING timing and VARIABLE_CONTEXT timing. Spatial exposure remains secondary, with one source-screened DISTRIBUTED group.

## Exact deletion enumeration

All group-removal subsets of sizes zero, one, two and three were enumerated. Rank is calculated exactly using the repository's fraction-based V4 rank engine on the distinct predictor vectors. The primary-level check requires >=2 remaining source-screened groups at each of SINGLE/MODULAR and SIMULTANEOUS/ORDERED_OR_ALTERNATING/VARIABLE_CONTEXT.

| Removed groups | Subsets enumerated | Rank <5 | Any primary-level support <2 |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 0 |
| 1 | 29 | 0 | 0 |
| 2 | 406 | 0 | 6 |
| 3 | 3,654 | 2 | 154 |

Exactly **two triple deletions** destroy rank:

1. Removing *Asclepias exaltata*, *Mimulus aurantiacus*, and *Eichhornia paniculata* removes every pre-outcome MODULAR group.
2. Removing *Campsis radicans*, *Asclepias exaltata*, and *Epilobium obcordatum* removes every VARIABLE_CONTEXT group.

The **six two-group subsets that lose >=2 primary-level support** comprise three pairs drawn from the three MODULAR groups and three pairs drawn from the three VARIABLE_CONTEXT groups. Rank remains full in all six; numerical estimability and the preregistered support criterion therefore diverge.

Across triple deletions, 79 subsets fail module-level support, 79 fail timing-level support, and 4 fail both, giving 154 distinct support failures. These are counts of deterministic exclusion scenarios, not probabilities of ecological events and not p-values.

## Strict generality and a more stringent robustness target

The same source-side joint module/timing counts that govern the previously frozen G1 timing generality gate are:

| SINGLE substrate only | U2 SIMULTANEOUS | U2 ORDERED | U6 SIMULTANEOUS | U6 ORDERED |
|---|---:|---:|---:|---:|
| Current frozen V1 | 1 | 2 | 18 | 3 |
| Registered G1 minimum | 2 | 2 | 2 | 2 |
| Extra qualifying groups for G1 feasibility | **1** | 0 | 0 | 0 |
| Extra groups for a *new, optional* one-deletion-robust G1 sensitivity target | **2** | **1** | 0 | 0 |

The last line is **not** a change to the preregistered G1 rule. It is a prospective diagnostic: if every eligible module-by-timing cell has at least three independent groups, losing any one group still leaves at least two. This is not achieved by the currently unresolved U2 V2 expansion and must not be represented as an observed result.

The existing expansion packet already covers **all 12 U2 groups with unresolved V1 predictors** (36 slots) and has not received real independent source-side coding or adjudication. It cannot be completed using the focal architecture outcome, nor by selectively coding a promising subset. Even an added SINGLE+SIMULTANEOUS group must independently pass the strict U2 conflict gate.

## Interpretation

**Positive design result:** the five-column V4 predictor matrix remains full rank after any one or two source-screened groups are dropped. **Important fragility:** six two-group exclusions already remove the minimum primary-level support; cross-universe G1 temporal generality is still unavailable under the V1 surface. Thus the full-rank result does **not** warrant fitting a confirmatory biological architecture effect or claiming generality.

The 29 rows are selected source-screened biological groups, not 29 independently randomized trials; shared papers, phylogeny, and function-family ascertainment remain separate uncertainty/dependence issues. Group-deletion enumeration does not replace original-source validation or independent double coding.

## Next empirical decision

1. Complete the genuine frozen A/B architecture double coding, and the independent source-side U2/U6 predictor receipt adjudication.
2. If G1 is important, finish the full 12-group U2 V2 *predictor-only* expansion before any architecture unblinding; keep the registered >=2 criterion untouched.
3. After human returns, apply the frozen outcome-class support checks and V4 model execution diagnostics, then repeat an appropriately clustered influence analysis on **observed** responses. Report null and reversed results as well as positive contrasts.

**Files added by this draft only:** `balance_domain/plant_v4_preoutcome_attrition.py`, `scripts/audit_plant_v4_preoutcome_attrition.py`, `tests/test_plant_v4_preoutcome_attrition.py`, and this document. All frozen CSVs, architecture outcomes, existing manuscripts and default-branch inference remain unchanged.

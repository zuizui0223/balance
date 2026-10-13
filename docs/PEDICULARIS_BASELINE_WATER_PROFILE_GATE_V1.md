# Pedicularis SCH ↔ Experiment-B water-baseline gate v1

**Status: pre-outcome method screening contract only; no field records or empirical BALANCE worldlines.**
Companion to [PR #225](https://github.com/zuizui0223/balance/pull/225) and
the frozen comparator amendment \`data/PEDICULARIS_BALANCE_COMPARATOR_AMENDMENT_V2.json\`.

## The missing empirical equivalence

The SCH V2 primary surface verifies that water depth is kept **approximately fixed**
across its z × P × G treatment cells. Its current
\`THREE_WORLD_CONFLICT_HANDOFF_V1\` carries population/season/fitness scale and L,
but **not whether this fixed water state equals y0 (dry) or y1 (wet)**.
This matters because the archived BITA experiment-B design compares two
fixed function states:

\`\`\`text
Delta_state = max_x W(x, water=y1) - max_x W(x, water=y0).
y0 = dry/disabled water protection
y1 = wet/active water protection
\`\`\`

The SCH surface may have been held at *either* water state. The literal
\`context_id\` and \`fitness_scale_id\` matching cannot certify a water-state
equivalence that neither handoff records.

In particular, when natural SCH flowers remain wet, one cannot relabel that
SCH baseline y0 solely to obtain a desired direct gap. A prospective true
dry-y0 SCH protocol is a **hypothesis/feasibility decision**, not a
retroactive statistical recoding.

## Pre-outcome method-only screen

\`balance_domain.pedicularis_baseline.evaluate_pedicularis_baseline_method\`
and \`scripts/evaluate_pedicularis_baseline.py\` implement an intentionally
narrow geometric method screen.

Inputs must exclude *all reproductive outcomes*. Freeze the intended baseline
\`expected_sch_water_state=XY_Y0_DRY\` and method thresholds before opening
biological data. Record early/late bract-compartment water depth (millimetres)
for three independently assigned sets of plants:

| arm | role | required water state |
|---|---|---|
| \`SCH_FIXED\` | SCH V2 P2 surface baseline, water-y fixed | dry y0 |
| \`XY_Y0_DRY\` | Experiment-B lower water state | dry y0 |
| \`XY_Y1_WET\` | Experiment-B protected state | wet y1 |

This method gate is **only applicable to the design whose SCH baseline was
predeclared dry**. If SCH has a wet baseline, it should return a HOLD and the
experiment must be redesigned / prospectively re-specified; do not change
which arm is called shared after inspecting outcomes.

The gate checks:

1. Exact population/season/context/protocol identities in every source row;
2. one independently assigned water compartment per plant (no pseudoreplication);
3. plant counts in all three arms against a frozen minimum;
4. observed dry depth <= frozen maximum in SCH and XY y0;
5. observed wet depth >= frozen minimum in XY y1;
6. each arm's total early/late water-depth range within a frozen maximum;
7. SCH-vs-XY-y0 profile **minimum/maximum endpoint gaps** within a frozen tolerance.

The endpoint gap is deliberately only a conservative *support comparison*:
a matching minimum/maximum does not establish equality of the entire
depth distribution, intervention exchangeability, causal selectivity, plant
condition, field timing, or true experimental source linkage. More detailed
distributional/causal analysis requires a separate precommitted design.

Two valid machine outcomes:

- \`BASELINE_METHOD_PROFILE_SCREEN_PASSED_NOT_CAUSAL\`: supplied method-only
  profiles are numerically compatible with the registered dry-y0 baseline;
  **neither the original source datasets nor external preregistration timing
  are independently verified by this screen**.
- \`BASELINE_METHOD_HOLD\`: at least one support, identity, wet/dry,
  profile-match or range requirement failed.

Malformed, outcome-contaminated or nonfinite inputs **raise an error**
rather than receiving a guessed score.

## Templates and execution

\`\`\`text
data/PEDICULARIS_SCH_XY_BASELINE_METHOD_TEMPLATE_V1.csv
data/PEDICULARIS_SCH_XY_BASELINE_THRESHOLDS_TEMPLATE_V1.json
\`\`\`

Both files are unusable until actual field method profiles and prospective
thresholds are supplied. In particular the JSON contains
\`NOT_FROZEN_REQUIRED_BEFORE_USE\` and invalid threshold placeholders.

After a defensible pre-outcome freeze and subsequent method measurements:

\`\`\`bash
python scripts/evaluate_pedicularis_baseline.py \
  --pilot /path/to/outcome-free-method-profiles.csv \
  --thresholds /path/to/prospectively-frozen-thresholds.json \
  --out /path/to/baseline-method-receipt.json
\`\`\`

The runner enforces an exact, **method-only** CSV header, hashes both files
and refuses to overwrite a prior receipt. Its hashes identify the supplied
files but do **not**, without an additional independent file-lineage audit,
prove that the method-only profiles came from the same SCH P2 and BITA
Experiment-B source records used to fit the worldlines. It does not verify
the chronology of the freeze itself.

Before any real biological claim, additionally check the source plant IDs,
randomization schedule and raw-file hashes against the actual source
producer receipts, the B0 water/perforation selectivity method gate,
the independent SCH P0/P/G qualifications, and the common viable-seed
fitness-scale definition.

## Scope ceiling

Even a positive method-only screen identifies **no** functional-state effect,
no structural architecture-value cost, no BALANCE occupancy, no BITA
mechanism and no historical differentiation.

A subsequent negative fixed-state \`Delta_state\` with a positive SCH
conflict may license a *functional-state* comparison **only after** complete
source/protocol validation and joint uncertainty. It does not make the
uncosted superset
\`max_{x,y in {y0,y1}}W(x,y) - max_xW(x,y0)\` negative (impossible by set
inclusion), nor does it supply net structural costs/constraints.

The BITA Experiment-B producer in PR #181 remains **closed unmerged**,
and its power wrapper in PR #182 remains **closed unmerged** as of
2026-10-13. Thus no source-linked field-positive receipt is available
from that archived branch. This module creates *no* such evidence.

## Reproduce the regression guard

\`\`\`bash
python -m pytest -q tests/test_pedicularis_baseline_method.py
\`\`\`

Synthetic tests cover dry method-screen pass without biological promotion,
SCH-wet mismatch, y1-not-wet, profile mismatch despite both labels saying dry,
duplicate plants or water compartments, outcome-contaminated columns,
post-outcome threshold status, unfrozen intended baseline, and nonnumeric
measurements. **Synthetic tests do not constitute field validation.**

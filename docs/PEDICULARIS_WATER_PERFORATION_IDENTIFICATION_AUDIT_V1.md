# Pedicularis rex: separate water-defence state from perforation/handling

Status: SOURCE-METHOD-AUDITED / NEW EXPERIMENT NOT EXECUTED  
Date: 2026-10-08  
Programme gate: before Experiment B's water-state worldline is assigned a causal interpretation.

## Source-verified reason for the audit

Sun & Huang (2015), *AoB PLANTS* 7:plv019, DOI 10.1093/aobpla/plv019, manipulated water retention by **making a hole at the base of the cupulate bract with scissors**, comparing water-drained treated inflorescences to intact controls. The published methods describe 40–60 tagged inflorescences per each of six populations, 20–30 drained per population, with at least six capsules counted per individual. The paper reports no detectable drain-treatment difference in pollinator/robber visitation and a significant increase in seed predation in five of six populations; initial seed set was not detectably affected, whereas final seed set was.

Primary source: https://academic.oup.com/aobpla/article/doi/10.1093/aobpla/plv019/200213 (Methods: Seed predation; Results: Table 2).

**Identification warning, not a refutation:** in the reported treatment contrast, water removal and physical perforation co-occur. No water-retained/perforated or water-removed/nonperforated factorial contrast is documented in those reported methods. Hence the experimental treatment identifies the *joint intervention package*, not an isolated causal `water-depth` effect. Puncture/handling could potentially change oviposition access, bract microclimate, flower damage or another pathway. This possibility is a rival mechanism requiring direct controls; it is not proof that the historical conclusion was false. The point cannot be solved by fitting a more complicated regression to the same two treatment labels.

The 2016 *Annals of Botany* study, DOI 10.1093/aob/mcw097 (source: https://pmc.ncbi.nlm.nih.gov/articles/PMC4970362/), reports pollinator-favoured floral exsertion alongside predator-associated selection for reduced exsertion across populations. It is observational evidence of opposing trait associations, **not** a randomized `x × water × puncture` landscape and not a direct BALANCE worldline receipt.

## Competing ecological mechanisms with discriminating predictions

| Hypothesis | Water retained vs experimentally removed, at fixed bract integrity | Perforated vs not, at fixed water state | Interpretation |
| --- | --- | --- | --- |
| H_W: water barrier | Water retention reduces predator attack and improves viable seed fitness under predator exposure | No residual perforation effect after equivalent microclimate and handling | Water-mediated functional defence |
| H_B: structural breach/handling | Little or no water effect after integrity controlled | Perforation/handling changes predation or fitness | Apparent water effect could be manipulation-mediated |
| H_WB: interacting water and integrity | Water effect exists only under some integrity states | Perforation effect depends on water depth | Bract integrity and water are joint defensive components |
| H_0: neither survives controls | No reproducible effect on attack or final seeds | No reproducible effect | Historical contrast context-specific, noisy or operationally distinct |

These alternatives are **not** assumed equiprobable. The physical route by which a basal hole would alter oviposition is an empirical question, not an established mechanism.

## Stage B0 — manipulation feasibility before biological outcomes

Aim for *orthogonal* manipulation of (A) water retained vs removed and (B) intact vs standardized basal perforation. The four intended arms are:

1. intact + retained water (matched handling/sham),
2. intact + dry (aspirate water without perforation, repeat as required),
3. perforated + retained water (a validated retention/refill protocol **without changing the relevant access route**),
4. perforated + dry (historical hole/drain approach).

The third arm is mechanically challenging: sealing a hole could itself block insect access, while leaving it open can prevent water retention. **If water and perforation cannot actually be separated, declare orthogonal identification infeasible.** Never call a sealed-plug intervention an identical "open puncture" treatment without validating access, or fill in the missing design cell using regression extrapolation. An intact+dry versus intact+wet experiment can still test a *water-state* contrast if handling is balanced, but cannot estimate the independent perforation effect.

All arms need standardized contact/manipulation effort, repeated water-depth measurements during the oviposition window, recorded damage, bract opening/size, realized exsertion, nectar accessibility, pollen load, visitor counts, predator egg/early attack and mature undamaged seed count. Do not assign a functional water effect from labels if realized water-depth distributions overlap materially.

Experimental unit: focal plant or predeclared within-plant flower block; preserve `plant_id` dependence and `flower_id`. Randomize arms before outcomes. Do not treat repeated flowers on a plant as independent. Predeclare handling failure, leakage and attrition before seed outcomes are opened.

## Stage B1 — ecological contrast, not an architecture comparison

Under matched pollinator and predator exposure, compare **within the validated manipulations**:
- `Delta_water = E[W | retained, integrity] - E[W | dry, integrity]`,
- `Delta_breach = E[W | perforated, water-state] - E[W | intact, water-state]`,
- the water × perforation interaction, if the full four-cell factorial is genuinely feasible.

Primary `W` is undamaged mature seeds per focal flower (same population, season, counting and censoring rules). Predator attack, damaged seeds, oviposition and pollen are distinct **mechanism outcomes**, not interchangeable fitness scales.

A positive water effect identifies an experimental functional-state benefit in that ecology; it **does not** measure the developmental/maintenance cost of building a cupulate bract or show that a differentiated morphology is favoured. If puncture unexpectedly harms seed production, investigate direct damage rather than silently subtracting it from the water-benefit estimate as architecture cost.

## Stage B2 — eligibility for BALANCE / SCH / SLK

The registered Experiment A still needs independently qualified P/G interventions and a positive same-context SCH conflict `L` on a matched fitness scale. The `x × water-y` Experiment B (≥5 x levels × 2 validated water states) then estimates distinct functional-state optima `W_S^*` and `W_D^*` with joint uncertainty.

Only `L.lower95 > 0` plus `(W_D^*-W_S^*).upper95 < 0` justifies a **FUNCTIONAL_STATE_BALANCE** receipt. Those two water states retain the same bract architecture. No statement about selection for historical modularization, structural-architecture fitness ordering, architecture cost `K`, or the evolutionary maintenance of undifferentiated architecture follows.

Structural promotion requires an independently realized and biologically accessible architectural alternative, repeatable/feasible costs and final reproductive fitness on the same scale; the hole treatment is not a substitute. If the architecture condition fails, route the structural-BALANCE claim to another system while keeping the qualified functional-state experiment useful.

## Concrete decision before expensive full-factorial sampling

- **B0 PASS**: water state and perforation can both be varied without confounded handling/access and off-target failures, or a qualified nonperforating water-only contrast is explicitly declared; advance only the corresponding licensed contrasts.
- **B0 PARTIAL**: water-only state is valid but integrity cannot be orthogonalized; promote at most functional-state inference, no puncture effect.
- **B0 HOLD**: every effective draining method alters access/geometry/damage or states cannot be maintained; redesign before (x × y) power calculations.
- **B0 NO NEW FIELD DATA**: published 2015 data remain a positive historical functional defence anchor only; no claim of a newly executed intervention.

This audit changes no frozen tests, original source coefficients or BALANCE/SLK/BITA ownership.

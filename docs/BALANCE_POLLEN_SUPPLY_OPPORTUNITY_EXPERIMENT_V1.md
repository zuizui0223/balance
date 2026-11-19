# BALANCE: pollen-supply and service-opportunity gates with controlled visit order

**2026-11-19 | Prospective, model-generated predictions; zero new empirical effect estimates.**

## Motivation and provenance

The previous source-only U6 audit (draft [PR #273](https://github.com/zuizui0223/balance/pull/273)) identified three incompatible pollen-loss coordinates and two opposing visitor orders inside the three sequentially screened U6 systems. This analysis does **not** change the frozen U6 roster, the U2/U6 V4 four-class architecture model, its two registered directional hypotheses, the original blind architecture coding, or the previous drafts.

An **independent real published biological case** makes an important distinction worth formalizing:

> Brody, Burnham & Smith (2021), *Annals of Botany*, doi:[10.1093/aob/mcab050](https://doi.org/10.1093/aob/mcab050), studied *Polemonium foliosissimum* experimentally in one research programme. Muscid flies removed abundant pollen and were less effective pollen depositors than bumblebees. Removing approximately half the anthers in pollen-source neighbourhoods did **not** detectably exacerbate female reproductive pollen limitation, while hand supplementation increased seeds per fruit (published overall means 5.50 to 6.46; P<0.001). The authors describe a likely bottleneck in effective pollinator service rather than a simple absence of pollen. The original article is not a new 2026 discovery.

This is a **published-results-only source anchor**, not a new replicate-level workbook reanalysis. In particular:

- The flies' and bees' reported pollen remaining on anthers (9,700 versus 16,900 grains after single visits) cannot be treated as *pollen removed* without comparably measured starting stocks.
- Reported pollen deposited after single visits (266 versus 352 grains) did **not** differ significantly in that comparison (P=0.189); pollen deposited is not assigned genetic paternity.
- The roughly 50% anther-removal manipulation is not proof that 50% of all *available pollen* was lost.
- Non-detection of extra seed limitation is not equivalence, and the original study did not manipulate legitimate visit *capacity* in a fully factorial source-stock×service design.
- One biological programme means **one** independent study, not separate independent studies for its experimental endpoints.
- *Polemonium foliosissimum* is **not admitted to the frozen BALANCE U6 universe**. The source transcript and the hypothetical models have separate provenance and were not fitted together.

The complete source-only note is `data/BALANCE_POLEMONIUM_2021_SOURCE_ONLY_ANCHOR_V1.json`. The scripts do not use the published effect sizes to select parameters.

## Model A — independently test supply and service constraints

For fixed available donor pollen `P`, fractional loss `r`, legitimate visit count `n`, per-visit pickup capacity `c`, eventual delivery success `eta`, and a *hypothetical* saturating recipient response:

```
Q(P,r,n)   = min[(1-r)*P, n*c]
D(P,r,n,H) = eta*Q(P,r,n) + H
Y_proxy    = Ymax * [1-exp(-D/kappa)]
```

`H` is pollen applied directly to a recipient stigma (hand supplementation): it bypasses visitor-delivery and donor-pollen gates. **Y_proxy is not an actual measured seed count** and its exponential shape is a falsifiable modeling assumption. It is not a structural alternative fitness worldline.

Two mechanisms are observationally confusable from marginal seed success alone:

1. **Service-limited:** `n*c <= (1-r)*P`. Source reduction does not change `Q`, but a separate hand-pollination intervention can increase `Y_proxy`. Thus true recipient pollen limitation can coexist with little observed source-pollen-reduction effect.
2. **Source-limited:** `(1-r)*P < n*c`. Source reduction changes `Q`; its effect on `Y_proxy` may still be hard to see if the output response is near saturation.

Both predictions are *not* universally true without fixed visitor behavior, the capacity ceiling, and the response model. An observed negative effect of removal in a well-verified service-limited stratum would falsify this restricted fixed-service model or imply unmeasured behavioral, qualitative or other pathways.

### Synthetic illustration — not calibrated to any botanical species

Fixed arbitrary illustration: `P=100` pollen units, `r=0.5`, `c=10` units per visit, `eta=1`, `kappa=50`, `Ymax=10`, `H=20` for hand supplementation.

| Effective visits | No-removal output proxy | Source-halved output proxy | Source-reduction loss | Hand supplementation gain (no removal) |
|---|---:|---:|---:|---:|
| 2 (service limited) | 3.2968 | 3.2968 | **0** | **2.2099** |
| 7 (source threshold crossed) | 7.5340 | 6.3212 | **1.2128** | 0.8130 |

The values are deterministic predictions of the assumed functions, not empirical estimates or SEs. A change in stock, visitor quality, plant sex, pollen quality or saturation function changes the numeric predictions.

## Model B — the same visitors can reverse the value of delayed pollen release

Consider a **closed donor pollen stock** with total 100 grain-equivalent units and no replenishment except an explicitly scheduled second release. Two effective visitor opportunities (`L`) each remove fraction `alpha=0.3` of currently exposed stock; one thief (`T`) removes fraction `beta=0.5`. Effective exported pollen is `eta=1` times legitimate removal. This is a maximally simplified *pollen-export proxy*, not genetic paternity.

Two exposure programmes release the **same total** pollen:
- `BURST`: release all 100 before the first visitor;
- `DELAYED`: release 50 before the first visitor, then 50 immediately after that visit.

The number and identity of visits are held fixed. Only their order differs.

| Event order | Burst exported | Delayed exported | Delayed − burst |
|---|---:|---:|---:|
| **T→L→L**: thief first | 25.50 | 38.25 | **+12.75** |
| **L→T→L**: legitimate first | 40.50 | 27.75 | **−12.75** |

The **program ranking reverses** because delayed pollen release shields some pollen from an early thief, but withholding pollen at an early legitimate visit carries an opportunity cost. The raw contrast is *an algebraic consequence of this constructed finite-stock model*, **not a new observed evolutionary law or proof of architecture selection**.

Crucially, with `beta=0` (matched no-theft sham), T→L→L has zero delayed-programme difference but L→T→L has a **−10.50** delayed cost, *even without pollen theft*. Therefore a raw timed-release difference confounds early legitimate-opportunity cost with thief-specific protection.

An additional **three-way difference-in-differences** isolates the model's thief-dependent shift in release-program advantage:

```
G(order, thief) = export(DELAYED) - export(BURST)

Gamma = [G(TLL, theft) - G(TLL, sham)]
      - [G(LTL, theft) - G(LTL, sham)]

illustrative Gamma = (12.75 - 0) - (-12.75 - (-10.50)) = +15.00
```

Again, +15 is synthetic, has no experimental uncertainty, and must not be interpreted as a population or fitness effect. Failure of donor pollen conservation or reversed order dependence under verified conditions would reject the closed-stock, fixed-removal mechanism; a nonzero difference in full viable paternity would be a distinct inference with separate assumptions.

### Distinguish three clocks

- **External visitor clock:** which insect or vertebrate arrives first;
- **Plant dispensing clock:** when newly viable pollen becomes exposed on the anthers;
- **Recipient reproductive clock:** when stigma pollen can fertilize ovules and when stored pollen is degraded or removed.

A visitor's earlier legitimate service does not mean the entire pollen reservoir was exported, and a late thief cannot retroactively remove pollen that has already successfully left the source. Theft on a **recipient stigma** belongs to the third clock and is excluded from the donor-stock model.

### Fixed-grid robustness — model-internal only

A prospective 3×3×3×3 parameter grid tests three legitimate pickup fractions (0.1/0.3/0.6), three thief fractions (0.2/0.5/0.8), three delayed-release fractions (0.25/0.50/0.75), and three eventual transfer efficiencies (0.25/0.50/1.00). Within the *same closed-stock fractional-removal assumptions*, **81/81** scenarios favor delayed release when theft precedes both legitimate visits; **81/81** disfavor it when a legitimate visit precedes theft and the delayed release; **81/81** yield a positive sham-adjusted three-way export-proxy interaction (range **0.25–72** in the arbitrary 100-unit pollen scale). This is a deterministic grid, not 81 biological replicates, not 81 experiments, not a null distribution, and not evidence of ecological universality. All sign claims are conditional on model structure, not measured `K`, `Phi`, or genetic paternity.

## Registered empirical design to test the predictions, without changing V4

**Experiment A: stock × service capacity.** Randomize independently replicated source-pollen reduction (intact/sham versus reduction) × experimentally controlled effective-visitor opportunity (low/high or prespecified quantitative exposure). Keep legitimate species/size, visit windows, donor age and handling comparable. Independently count donor pollen availability, visitor removal and recipient deposition. Hand pollination is a **separate saturation diagnostic**, not a substitute for controlling legitimate visitors. Randomize at a whole plant/enclosure/patch level where cross-treatment pollen movement otherwise causes interference; clustered flowers are not independent donor replicates.

Primary interaction of interest (on a prechosen fitness scale) is the contrast in source-reduction effects between measured service strata. The model predicts low or zero depletion effect only where supply capacity truly exceeds service capacity; source-reduction effects may appear as legitimate service increases. Failure to observe that contrast under good intervention fidelity falsifies the proposed gate, not all effects of pollen theft.

**Experiment B: controlled order × pollen release × thief treatment.** A prospective 2 (TLL/LTL) × 2 (burst/half-late) × 2 (real pollen-removal exposure/sham) factorial with constant total available pollen, visitor counts and observation windows. Randomize at independent donor plants or isolated matched experimental blocks; a technical sham must control physical interference and artificial masking. Record flower age, timing of exposure, quantity and viability of released pollen, visitor-body pollen load, subsequent stigma deposition, residual source pollen and independent seed paternity. Include a **source-pollen conservation check** and unbiased no-thief control. Repeated observations on flowers of the same mother or within the same enclosure are clustered measurements.

The mechanistic primary estimand is `Gamma` above on a *measured source-export* scale. A distinct reproductive estimand uses genetically verified viable offspring/paternity at the recipient, with uncertainty clustered at the randomized unit. **Never substitute pollen-body load or fluorescence for genetic siring.**

A timed manual masking/release treatment establishes a **functional-state** alternative; an evolved additional pollen module has not thereby been constructed or costed. To claim BALANCE structural persistence, separately measure optimized shared and differentiated-accessible architectures on a matched common reproductive-fitness horizon together with net structural cost `K`. Positive `Gamma` does not identify `L`, `K`, `Phi`, or evolutionary historical differentiation.

## Falsifiers and reporting

- If the actual donor stock remains comfortably above measured service capacity yet reduction lowers recipient fitness, the fixed-service gate is inadequate: test pollinator avoidance, pollen quality, injury and stochastic delivery rather than rebranding it as a new structural effect.
- If treatment responses follow source stock but not the controlled number/quality of effective visits, reject the independent two-capacity interpretation.
- If delayed release fails to protect pollen under TLL with verified donor stock and equal pollinator access, the fixed-fraction stock model fails.
- If the hypothesized interaction is reversed or absent after experimental controls, report it; the synthetic `Gamma=+15` is not a target to force.
- If the distinct treatment cohorts cannot be followed to donor siring or recipient seed viability, keep the result at pollen-export/receipt level.
- Pre-register the randomization unit, sample size, primary reproductive endpoint, pollen baseline calibration, fixed treatment schedules and leakage/noncompliance exclusion rules before field data collection. Do not perform outcome-driven sample or response-category selection.

## Reproduce

```bash
python scripts/audit_pollen_supply_opportunity.py
python -m pytest -q tests/test_pollen_supply_opportunity.py
```

The independent Python model uses only standard-library arithmetic and fixed synthetic parameters, with fail-closed input guards, mass-conservation assertions, sham/real theft contrasts, and no source-data interpolation. It is **not** a fitted meta-analysis, a new Polemonium effect, a new U6 taxon admission, a V4 confirmatory result, or a revised BALANCE worldline.

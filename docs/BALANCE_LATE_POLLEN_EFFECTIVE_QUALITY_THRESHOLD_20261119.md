# BALANCE — delayed pollen contribution threshold and independent source-audit ceiling
**2026-11-19 | Draft extension to PR #274. Prospective model mechanics, not new empirical effects.**

## What was actually verified in the primary Polemonium article

Brody, Burnham & Smith (2021), *Annals of Botany* 128:127–134, DOI [10.1093/aob/mcab050](https://doi.org/10.1093/aob/mcab050). The publisher article was read again, with original methods, results, and the supplementary list checked. One independent biological research programme; **no row-level original dataset was recovered or refitted**.

The year-specific design is important:

| Source year | Manipulated context | Reported result | What cannot be inferred |
|---|---|---|---|
| 2015 | Four pollen-source neighbourhoods; anther reduction | Pollen receipt fell 32.2% in females and 28.9% in hermaphrodites, source test F(1,93)=4.20, p=0.04 | No hand-supplementation interaction estimated in this year |
| 2016 | Ten neighbourhoods; rotated odd/even pollen-source treatments; hand supplementation on matched plants/stalks | Seed number per fruit 5.50±0.28 (natural) vs 6.46±0.31 (hand); chi²=13.07, p<0.001 | It does NOT independently randomize pollinator-service capacity |
| 2016 | Same design | Source reduction × hand supplementation, seeds/fruit chi²=0.083, p=0.773; fruit set chi²=0.33, p=0.568 | Nonsignificance is NOT evidence of equivalence; not proof of zero donor fitness cost |

2016 pollen receipt showed no significant reduction in the reported overall test (chi²=0.334, p>0.563), even though hermaphrodites had a numeric 20% lower stigma load. Do not call both years negative. The primary article lists **four supplementary figure images (S1–S4) and a legend file**. Individual neighbourhood-week or pollen-source records were not located in the checked supplementary listing or targeted archive searches. This is a *limited search report*, not proof that underlying data do not exist.

Original authors did **not** measure male genetic paternity, independently randomize effective visitor number/quality, or experimentally compare two accessible structural flower architectures with common-fitness costs. Therefore an independent pollen source × effective-service causal interaction, `L`, `K`, `Phi`, `W_S^*-W_D^*`, and flower-architecture adaptation remain unidentified.

The source-only, reproducible provenance note is `data/BALANCE_POLEMONIUM_2021_PRIMARY_DESIGN_AUDIT_V1.json`. It is intentionally independent of all synthetic parameter choices.

## Why the previous 81/81 grid is not a general theorem about flowers

The previous synthetic source-stock model treats all pollen grains exported by an effective visitor as contributing equally, regardless of whether they were available immediately or released after the first visit. Its 81/81 positive early-thief result remains correct **conditional on that equality assumption**. It should not be used to assert that staged anther release is universally adaptive.

Introduce a new *hypothetical* dimensionless weight `q>=0`: the later-released cohort's effective contribution per grain relative to the earlier cohort. This weight may reflect later visits actually reaching a compatible stigma, pollen quality, post-pickup transport or fertilization, or post-deposition competition. It is **not itself the probability that a grain is viable**, and may exceed 1 when the later cohort has a higher relative effective contribution. Neither `q` nor the other model parameters were measured in the 2021 Polemonium experiment.

The model still assumes total pollen `P`, a delayed fraction `d`, legitimate per-visit pollen removal `a`, thief per-visit removal `b`, a common unweighted service-transfer efficiency `eta`, and exactly two legitimate visits `L` with one `T`. The first visitor is followed by the delayed release. Both visitors remove the same fractions of *both exposed cohorts*. The physical pollen stock remains closed and conserved.

### Conditional analytic results, not novel discoveries from algebra alone

Let `D_seq` denote the difference in **quality-weighted legitimate export proxy** between delayed release and all-at-once release for the given visitor sequence.

For an early thief `TLL`:
```
D_TLL = P * eta * (2a-a²) * d * [q-(1-b)].
```
For positive `P,eta,a,d`, the sign changes at:
```
delayed pollen release favorable <=> q > 1-b .
```
This is the key **falsifiable sign boundary**; the algebraic expression itself is model arithmetic, not evidence of a newly evolved biological mechanism.

For a legitimate first visitor `LTL`:
```
D_LTL = P * eta * a * d * [q(1-b) - 1 -(1-b)(1-a)].
```
This is negative for most `q<=1` scenarios with positive removal; at sufficiently high `q>1`, even the legitimate-first order may favor delayed release. Thus **the raw directional reversal is not a universal property** of all possible pollen-quality regimes.

The original 2×2×2 **no-theft-sham-adjusted three-way interaction** remains algebraically positive under the new model:
```
Gamma = P * eta * a * b * d * (1+q),
```
for positive `P,eta,a,b,d`. This is **not** proof that delaying pollen is fitness-beneficial, since the raw delayed-minus-burst difference `D_TLL` can be negative even while `Gamma>0`. This distinguishes an interaction from the actual rank of competing functional programmes.

### Explicit synthetic falsifier of the old headline

Using the same *arbitrary* settings as previous PR #274 (`P=100, a=0.3, b=0.5, d=0.5, eta=1`) with only the new relative contribution varied:

| Later-cohort relative contribution q | TLL delayed − burst | LTL delayed − burst | Sham-adjusted Gamma |
|---:|---:|---:|---:|
| 0 | −12.750 | −20.250 | +7.500 |
| 0.25 | −6.375 | −18.375 | +9.375 |
| 0.50 | 0.000 | −16.500 | +11.250 |
| 0.75 | +6.375 | −14.625 | +13.125 |
| 1.00 | +12.750 | −12.750 | +15.000 |
| 1.50 | +25.500 | −9.000 | +18.750 |

At `q=.25` the original **early-thief delayed-is-better sign reverses**, even though the adjusted three-way interaction is still positive. `q=1` reproduces the exact original simple model. High `q>1` is a relative quality scale, not a violation of physical pollen conservation, and weighted export is no longer a literal grain count.

**These are deterministic counterexamples, not observed reproductive fitness, genetic siring or support for new modules.** Biological significance requires prospectively measuring quality-weighted export or, preferably, genotype-assigned mature progeny.

## Why this is biologically worth measuring

Published floral studies already show that pollen presentation schedules vary with visitor assemblages, and that exposed/presented anthers can alter insect visitation and contact to subsequently dehiscing anthers. For background, see:
- *Epimedium* pollen packaging/dispensing study, PMID 23614841.
- *Parnassia palustris* anther-anther interference manipulations, PMC3903572.
- *Penstemon* anther dehiscence/temperature/humidity study (Journal of Pollination Ecology, article 703).

These are independent **prior literature mechanisms**, not measurements of the specific `q` parameter here. Late release may protect fresh pollen, increasing relative efficacy, or miss receptive flowers/legitimate visitors, decreasing effective contribution. Do **not** assume universal decline in intrinsic pollen viability merely because pollen is released later.

## Registered experiment needed to identify this boundary

Use a randomized source-level `2 visitor orders (TLL/LTL) × 2 release programmes (burst/delayed) × 2 thief regimes (real/sham)` design with equal donor pollen production and pre-measured availability. For each donor and batch, independently measure **pollen grain survival/exposure, legitimate pickup, delivered grains and viable donor paternity**. Distinguish true delayed-cohort contribution from visitor timing and recipient floral phase, keeping the randomized plant or enclosure as the true experimental unit. The source-pollen release programme could itself affect pollinator visitation, so any detection of altered visitor numbers requires a different mechanistic model or a controlled visitor protocol.

The primary raw-advantage estimand compares staged-versus-burst **same-scale viable male fitness** at each visitor order; the three-way adjusted interaction is a distinct contrast and must **not** be mistaken for an absolute architecture benefit. The actual net cost of a novel anther architecture `K` remains unmeasured. Only after accessible shared and differentiated structural alternatives are evaluated on common fitness scale can a BALANCE-C1 or SLK architectural value claim be made.

## Reproduce

```bash
python scripts/audit_pollen_two_cohort_quality.py
pytest -q tests/test_pollen_two_cohort_quality.py tests/test_polemonium_2021_primary_design_audit.py
```

All code paths are stdlib-only, fail closed for invalid proportions, compare algebra to independent cohort accounting, match the old unweighted model at `q=1`, test conservation across a parameter grid, and retain no original response labels or invented field rows.

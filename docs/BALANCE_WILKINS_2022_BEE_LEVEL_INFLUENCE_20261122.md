# Wilkins 2022: bee-level and colony-deletion robustness (2026-11-22)

**Status: post-open / exploratory robustness audit, not another preregistered outcome.**
This audit follows the independently authenticated Wilkins et al. (2022) source
study [doi:10.1007/s00442-022-05246-0](https://doi.org/10.1007/s00442-022-05246-0),
whose original 60 bee trials, archived model reproductions and fixed body-only
endpoint definitions are already recorded in BALANCE draft PR #279.

## Specific concern

The original (replayed) body-only-versus-basket binomial mixed model,
`cbind(BodyPollen, CorbiculaPollen)`, showed a Treatment×HeadWidth Type II
chi-square of **13.2182**, p=0.000277. Its sampling unit is **one bee** (59 with
complete size data), not the hundreds of thousands of pollen grains making up
the binomial count. The original random-effects term includes a bee-level
intercept, but there are only **three colonies**, and the pollen-grain
likelihood can still be a consequential modeling assumption. The genotype of
the pollen donor and source-plant treatment block are not available in the
archive. This audit asks whether the original interaction's **direction** is
robust under equal-bee weighting and omission of a bee or an entire colony.

## Frozen design before seeing new results

Use the original source CSV only when its SHA256 matches the existing pinned
`0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62`.
Count the 60 original bees once each. Require complete HeadWidth, VisitTime,
BodyPollen and CorbiculaPollen: expected **59** records.

Analysis response is the *single-bee log ratio*:

```
logratio_i = log(BodyPollen_i / CorbiculaPollen_i)
```

Positive values indicate more terminal nonbasket body pollen relative to
pollen in that bee's basket. They do **not** identify eventual transfer to a
stigma or viable donor offspring. No pseudocount is required because both
counts are nonzero for complete source trials.

Treat Cone (joined) as reference and Sham (free) as the contrast. Subtract
the **pooled original 59-bee** mean from HeadWidth and VisitTime before any
deletion. Centering fixes the meaning of the two-way contrast at a shared
observation time; it is not selected from resulting p-values. Two predefined
**bee-equal-weighted** linear model specifications are fitted independently:

- Full original three-way structure with colony fixed intercepts:
  `logratio ~ Treatment * centered_width * centered_time + ColonyID`.
- Reduced two-way sensitivity with a time adjustment and colony fixed intercepts:
  `logratio ~ Treatment * centered_width + centered_time + ColonyID`.

Report the **Sham−Cone difference in the HeadWidth slope at the original mean
VisitTime**, its bee-level HC3 standard error, and a t-based approximate
95% CI/p-value using n-p residual degrees of freedom. The two estimates
do **not** have the same biological meaning as the original Type II interaction
test with all terms fitted; do not compare their p-values as if they were
independent tests or interpret discrepancies as formal heterogeneity.

Repeat the same design and global centering after **each colony is removed**
(three fits per specification; only two colonies remain in each) and after
**each of the 59 bees is removed** (59 fits per specification).
Record the signed interaction, range of leave-one-out estimates and count of
sign-preserving deletions; these are *stability diagnostics*, not 59 biological
replicates or 3 independent tests of a null hypothesis. No post-hoc
selection of the model with the lowest p-value is permitted.

The HC3 covariance calculation uses independent **bee rows** to address
heteroskedasticity. It is **not a valid colony-cluster-robust inference
procedure with just three colonies**, nor does it resolve unobserved repeated
source plants. Every step fails closed on unexpected source hashes,
missingness, nonfull-rank design, or nearly-perfect leverage.

## Reproducible output

```bash
Rscript scripts/check_wilkins_2022_bee_level_robustness.R \
  /path/to/442_2022_5246_MOESM3_ESM.csv /tmp/wilkins-robustness
```

The existing authenticated-source GitHub Actions workflow runs the script
after the original five-model/two-sensitivity replay, uploading:

- `bee_level_hc3_contrasts.csv`: two full-sample bee-equal models;
- `leave_one_colony_out.csv`: three deletions per model;
- `leave_one_bee_out_summary.csv`: all 59 deletion summary ranges;
- `bee_level_scope.csv`: original source identity, sample definition,
  centralization and inferential ceiling.

**Interpretive gate:** if both bee-level model specifications and all three
colony omissions preserve the interaction direction, call it *directionally
stable within this source*, **not** proven general to new colonies, flowers,
plants or taxa. If signs flip, label the original result *colony-dependent*
and maintain the original positive published inference separately. In
neither case can the source infer experimental genetic paternity, reproductive
fitness or a net BALANCE `Phi` structural alternative.

The source was obtained from one original study; this robustness exercise does
not create extra studies, evolutionary transitions, or independent biological
worldlines. U2/U6/V4 and architecture A/B human coder inputs remain untouched.


## Actual R reanalysis results (2026-11-22)

The authenticated original source was re-read in
[GitHub Actions #45013279220](https://github.com/zuizui0223/balance/actions/runs/45013279220).
Both fixed post-open models completed with 59 equal-weighted bees, and the
original five-model reference replay still matched all 37 published test
statistics (maximum original chi-square deviation 0.00169969).

The reported `TreatmentSham:width_centered` coefficient is **free minus
joined in the head-width slope per millimetre**, evaluated at the original
complete-bee mean handling time. These are HC3 standard errors and approximate
t-based intervals on the **bee-row** scale, not 3-colony cluster-robust CIs:

| Locked exploratory specification | Slope difference, per mm | HC3 SE | Approx. 95% interval | Approx. p |
|---|---:|---:|---:|---:|
| Full original 3-way structure + colony fixed effect | +3.525543 | 1.475394 | [0.560628, 6.490459] | 0.020761 |
| Reduced 2-way interaction + handling time + colony fixed effect | +3.175466 | 1.106602 | [0.954907, 5.396025] | 0.005929 |

**Stability, not independent effect confirmation:** both fitted slopes remained
positive under **59/59 one-bee deletions** and **3/3 one-colony deletions**.
The full 3-way coefficient ranged from **+1.855975 to +4.318321** when one
colony was omitted; the reduced two-way coefficient ranged from **+2.761527
to +3.449744**. The deleted-colony datasets have only two colonies and cannot
support valid generalization to the population of colonies.

This establishes a more specific **within-study positive result**: the
architecture×bee-size interaction in the allocation of **terminal body pollen
versus pollen basket** is not solely due to the published composite that
also contains stigma pollen; it remains directionally stable when each bee
receives one outcome and when any one of three colonies is deleted. It does
**not** demonstrate an architecture-by-size interaction in *actual stigma
deposition* (published-source replay p=0.49192) or viability of exported
pollen. Nor does it remove treatment-order bias, unmeasured source-plant
clustering, survivor bias from seven excluded noncollectors, or possible
post-treatment covariate bias.

The full provenance and exact model readout are committed in
[`results/wilkins_2022/BEE_LEVEL_ROBUSTNESS_SUMMARY_20261122.json`](../results/wilkins_2022/BEE_LEVEL_ROBUSTNESS_SUMMARY_20261122.json).
Its source is the real Actions artifact
`wilkins-2022-architecture-model-replay`, ID 14750741539, ZIP SHA-256
`bceafeb74283bee7eabdc0315768b9f694ab25b19bf768b1a53cbcfa78fe87a8`,
and its derived CSV diagnostics include all three colony-deletion rows.
The artifact is temporary, but the source-locked R code and summary record
are versioned in this branch.

The original five-model source quantities, proposed BALANCE structural
fitness and the frozen U2/U6/V4 architecture inference are **unchanged**.

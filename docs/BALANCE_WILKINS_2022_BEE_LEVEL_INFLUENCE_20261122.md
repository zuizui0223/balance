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

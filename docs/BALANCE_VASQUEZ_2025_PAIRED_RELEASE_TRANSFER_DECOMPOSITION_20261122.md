# 2026-11-22 post-open: paired source release × conditional transfer decomposition

**Evidence: authentic Zenodo 17102653 data.csv, 15 donor-bee trials (6 `S.rostratum`, 9 `S.dulcamara`) with four recipient stigmas per donor.** This is a post-open source-level sensitivity on the original 2025 biological study, not a prospectively registered plant experiment or an independent evolutionary replication.

## Why this specific audit is necessary

The completed PR #280 analysis reported:
- Mean released proportion (`R_i=B_i/A_i`): 0.13547 versus 0.37768;
- Mean transfer of released pollen (`T_i=H_i/B_i`): 0.008611 versus 0.010007;
- Actual mean full produced-to-recipient transfer (`Y_i=H_i/A_i`): 0.00064957 versus 0.00313750.

Hence the source-group product `E[R]E[T]` overpredicts the actual group mean `E[RT]` for *both* species. We want to quantify the **within-species pairing term** and establish whether that apparent negative coupling is fragile to a single trial.

Crucial: `R_i=B_i/A_i`, `T_i=H_i/B_i` share `B_i` in opposite numerator/denominator positions. Therefore **a negative covariance is a descriptive joint-data pattern, not causal evidence that more pollen release decreases transfer efficiency**. The same algebra can produce a negative association when measured total H is fixed or poorly related to B; the denominator structure itself can induce anticorrelation. This is the main inferential gate, not a footnote.

## Fixed decomposition on real trial pairs

For each species s, use only the 15 authenticated source original trials; do not multiply 4 nested recipient rows into 60 independent donor units. Let `R`, `T` and `Y=R*T` be unit fractions, not percentages. Calculate:

```
mu_R,s = (1/n_s) * sum R_i
mu_T,s = (1/n_s) * sum T_i
mu_Y,s = (1/n_s) * sum Y_i

C_s = mu_Y,s - mu_R,s * mu_T,s
    = (1/n_s) * sum (R_i-mu_R,s)*(T_i-mu_T,s)

mu_Y,d - mu_Y,r =
  (mu_R,d - mu_R,r)*(mu_T,d + mu_T,r)/2
+ (mu_T,d - mu_T,r)*(mu_R,d + mu_R,r)/2
+ (C_d - C_r).
```

Three signed contributions sum EXACTLY to the true observed difference, conditional on this symmetric reference decomposition. Multiply unit-fraction contributions by **100 to express percentage points**. Report these as *arithmetic attribution* or *standardized source-stage components*, **NOT causal paths or independent experimental effects**.

For each species also report `C_s` in produced-pollen percentage-point units, sample Pearson and Spearman correlations as exploratory diagnostics, and the range/number of positive/negative covariance signs under **each single-donor deletion within that species**. Do not add correlation p-values under a null of biological independence, because `R` and `T` share a source denominator.

Use a fixed seed 20261122 and 20,000 within-species paired trial bootstrap resamples to obtain **descriptive percentile intervals** for the three between-species arithmetic components and each species covariance. Importantly, resample **(R_i,T_i) pairs together**, not the two factors independently: independently shuffling or independently resampling the factors destroys the covariance term we are trying to quantify. No clustering-robust 2-hive inference is possible; the bootstrap treats within-species trials as exchangeable solely for exploratory precision.

### Additional denominator-independent guard

To distinguish arithmetic coupling from a genuine organism-mediated transfer bottleneck, report a *descriptive* Spearman association between **actual delivered stigma pollen count `H_i`** and **actual donor released grains `B_i`** within species (no common B in opposite numerator/denominator). This does not remove confounding by donor production, recipient visit duration, bee size or species. It is only an observational guard against claiming that a ratio anticorrelation proves reduced absolute delivery.

No new fitted causal coefficients, new source species, new pollen-fate compartments, genetic fatherhood, seed fitness, or optimized alternative architectures are identified. This analysis must not re-open frozen U2/U6/V4 blind flower-architecture labels.

## Interpretation gates fixed at analysis authoring time

- If `C_s` is negative for both species but signs reverse under many donor deletions, call it **sample-sensitive denominator coupling**, not universal physiological compensation.
- If `C_s` stays negative under most deletions, report *descriptive negative coupling in these source trials*, retaining the algebraic shared-denominator caveat and no p-value-based causal statement.
- Compare the size and sign of the **release, conditional PTE, covariance** components. They are exact accounting contributions to one source contrast, not independent causal mediators.
- If `H_i` versus `B_i` is not negatively associated, that would further caution against treating `C_s<0` as an ecological cost of larger pollen release.
- Even if `H_i` versus `B_i` is negative, it remains observational, not an effect of experimentally changing accessible pollen stock.

## Reproduce

```bash
python -m scripts.audit_vasquez_2025_trial_structure --source-dir /tmp/vasquez-original
python -m scripts.decompose_vasquez_2025_release_transfer --original-csv /tmp/vasquez-original/data.csv --out /tmp/vasquez-decomposition.json
python -m pytest -q tests/test_vasquez_2025_covariance_decomposition.py
```

The workflow uses hash-verified Zenodo 2025 public source CSV and uploads *only* source-aggregate JSON, not individual trial records. It does not merge the PR or update main.

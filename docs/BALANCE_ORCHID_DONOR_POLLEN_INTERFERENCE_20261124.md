# Orchid pollen interference: authentic source audit and 31-vs-32 trial ambiguity

**2026-11-24 — draft research record, independent empirical programme; source-only plus original coded-group sensitivity, not a reproduced published 31-trial model.**

## Primary original experiment and an important positive ecological result

Harder, Richards, Ågren & Johnson (2021), *The American Naturalist* 197:250–265, [DOI 10.1086/712378](https://doi.org/10.1086/712378), manipulated whether stained donor pollen from **Anacamptis morio** (Orchidaceae) travelled with potentially interfering pollinaria from recipient flowers:

- **Recipient flowers emasculated** (no competing pollinaria pickup) versus **recipient flowers intact** (new competitor pollinaria can be picked up).
- Source Methods state **16 emasculated versus 15 intact donor trials**, with alternating rather than strictly randomized trial order.
- Each bumblebee carried a stained donor flower's pollinaria through a chain of recipient flowers; the number of stained donor massulae reaching stigmas was counted after each visit. The original paper reports competing pollen doubled the share of donor pollen lost in transit and reduced donor massula export by **27%**.
- **These published numbers are not direct genetic paternity, offspring seed production, a plant's total lifetime male fitness, or an estimate of fitness costs of anther modularity.** Orchid massulae are donor-labelled pollen packages, not comparable individual granular Solanum pollen grains.

This is genuinely a separate primary experimental study from the preceding Solanum original studies. Its distinguishing causal manipulation concerns *competition after donor pickup* rather than *anther release/accessibility*. It is still one original source, not numerous independent evolved plant architectures.

## Authentic mirror data, data availability and provenance

The original Dryad [doi:10.5061/dryad.41ns1rnc0](https://doi.org/10.5061/dryad.41ns1rnc0) is mirrored at [Zenodo record 4072200](https://zenodo.org/records/4072200). The mirror retains the **Dryad DOI**, so it is **not an independent replication**.

The official Zenodo API and file were downloaded by the [source-authenticated GitHub Actions run #45241393794](https://github.com/zuizui0223/balance/actions/runs/45241393794). The genuine original `Data_for_AmNat.csv` has:

- **8041 bytes**, original published MD5 `650e40ae7ebb41bdfb333dcf63c63c71`;
- SHA256 `303428b859bcba4756ac78c4ffd4b42121a6efce5b0cd2cc2030834705f62cbc`;
- **383** individual recipient-flower observations, six columns: `Trial_type, Trial, M_init, R, Visit, Deposition`;
- **16 `Emasc` and 16 `Intact` distinct `Trial` source codes: 32 coded groups**, in conflict with the *published manuscript's 16/15*.

The source is internally inconsistent with the literal paper design. Moreover, `Emasc` trial codes 2 and 3 have consecutive Visit 1–10 and 11–17, respectively, identical initial `M_init=201` and `R=0`. These are suggestive of a single continued source-donor sequence split into two record codes, but there is **no unique bee ID or plant ID** in the CSV to prove it. Merging the groups would make **15 emasculated and 16 intact**, the *opposite* allocation from the paper's stated 16/15. It cannot automatically be adopted as the actual original inclusion rule.

Additionally, **four coded trial groups have more than one recorded `R` value** even though the original Data Description calls `R` final retained donor pollinaria. Hence this independent audit does not use `R` to calculate transport loss or pretend to reproduce the reported *doubling of massula loss*. Two source code groups contain fewer than six recipient records, whereas the manuscript describes the minimum of six flowers for published experimental trials. These differences are recorded as **source-stage unresolved issues**, not repaired by selecting particular rows after seeing their outcomes.

Exact source trial IDs, visit minima/maxima, M_init and R consistency flags are in [`results/harder_2021/ORIGINAL_ORCHID_TRIAL_ADMISSION_RECEIPT_20261124.json`](../results/harder_2021/ORIGINAL_ORCHID_TRIAL_ADMISSION_RECEIPT_20261124.json).

## Real source-coded donor massula deposition: bounded alternative records

The original trial-coded source supports an unambiguous *descriptive* endpoint for each coded group: `sum(Deposition)` across that group's recorded recipient stigmas, divided by its unique `M_init` source initial massula count estimated from a neighboring donor flower. This is massula **deposition relative to estimated initial donor massulae**, not fertilization. Longer visit sequences provide more deposition opportunities, so the analysis additionally considers a fixed early-visit window.

| Assumption explicitly kept separate | Emasculated (no competitor) | Intact (competitor possible) | Intact / emasculated |
|---|---:|---:|---:|
| Every source-coded trial group (16 vs 16) | **52.15%** | **39.30%** | **0.754** (24.6% less) |
| Hypothetical continuity merger of Emasc2 and Emasc3 (15 vs 16) | **55.63%** | **39.30%** | **0.707** (29.3% less) |
| Six-recipient common-position window, qualifying code groups only (14 vs 15) | **49.90%** | **36.03%** | **0.722** (27.8% less) |

To avoid the unsupported assumption that one specific intact source code should be removed to match the paper, we also evaluated **all 16 possible single-intact-code omissions**, yielding 16 alternatives with 16 source `Emasc` groups and 15 `Intact` groups. **All 16** retain lower export in the intact treatment; the intact/emasculated ratio spans **0.707–0.803**, corresponding to approximately **19.7–29.3% less donor massula deposition**.

However, this is an **exclusion sensitivity envelope**, not a data-driven reconstruction of the actual authors' 31 donor trials. Emasc2–3 may remain pseudoreplicated in these scenarios. The original *coded-group* n=16+16 descriptive 20,000-resample bootstrap interval for the intact-minus-emasculated difference is **[−0.2684,+0.0118]** in fractional units (i.e., −26.84 to +1.18 percentage points), **including zero**. Treating all 32 code IDs as independent biological donors is not verified; this interval is **not** a valid species-wide, bee-population, or original manuscript 31-trial inferential confidence interval.

The actual source group and sensitivity envelope plus the mirrored-file digest are saved in [`results/harder_2021/ORIGINAL_ORCHID_32_GROUP_EXPORT_SENSITIVITY_20261124.json`](../results/harder_2021/ORIGINAL_ORCHID_32_GROUP_EXPORT_SENSITIVITY_20261124.json). Reproducible scripts are `scripts/audit_harder_2021_zenodo_mirror.py` and `scripts/audit_harder_2021_export_sensitivity.py`. Raw original recipient CSV bytes are not committed.

## Relation to the BALANCE mechanistic programme: distinct barriers, not fitted grand theory

The original Solanum programme in [PR #280](https://github.com/zuizui0223/balance/pull/280) showed **source accessibility/removal** and conditional donor-to-stigma transfer are separate observational bottlenecks, using 15 original donor-bee trials in two species. The author interventions in this **independent orchid experiment** target the *competing-pollen transport stage after donor pickup*, and show source-coded deposition is consistently lower in the treatment with competitor pollinaria under several transparent coding choices.

The joint scientific interpretation is **not** that floral anther structural differentiation is now demonstrated to evolve from this interference. It is that **male pollen transport opportunities can be limited after successful pickup by pollen carried from other donors**. Importantly, this impairment cannot be inferred from anther pollen production or flower-architecture geometry alone.

Neither source identifies a total plant genotype-verified siring rate, a net shared-versus-differentiated structural alternative under common conditions, nor `K` and `Phi`. Orchid intact/emasculated recipient manipulation is not a randomized trial of new floral modules. No outcome coder data from frozen U2/U6/V4 are opened or recoded; the source should not be introduced into larceny-only U6 just because competing male pollen interferes with dispersal.

### Next adjudication needed before stronger statistical claims

1. Reconcile published 16/15 versus archived 16/16 `Trial` codes through an original-paper code or explicit author correspondence, not a trial deletion chosen by p-value or closeness to 27%.
2. Resolve whether Emasc2 and Emasc3 are segments of one donor sequence and why four coded groups vary `R`.
3. Once original donor trial identity is verified, fit a trial-unit model accounting for number and order of recipient visits, both source initial massula counts and trial dispersion; report a source-supported effect rather than importing p-values from the published result.
4. To advance toward male fitness rather than transport, collect parentage/genotype-identified offspring in a new experiment, independent of recipient stigma count.
5. Before claiming broad ecological universality, repeat analogous competitor-pollen experiments for nonpollinarium granular pollen systems with standardized endpoints.

**Current epistemic status:** authentic positive *source-coded* transport interference direction under multiple bounded data choices, but published original biological trial membership unresolved and no independent paternity result.


## Original journal analysis-code access check

The paper explicitly links a supplementary ZIP with Excel/R model code:
[official supplement file](https://www.journals.uchicago.edu/doi/suppl/10.1086/712378/suppl_file/59424Supplements.zip).
A separate, one-time bounded publisher file-access check was added to
`scripts/audit_harder_2021_publisher_supplements.py` and ran in
[GitHub Actions #45242551944](https://github.com/zuizui0223/balance/actions/runs/45242551944).
The exact official publisher endpoint returned **HTTP 403**, so the
author code's source-trial inclusion/exclusion rules **could not be examined**.
The metadata-only access artifact is **14850824249**, ZIP SHA-256
`4b5b71bdb856bea07f363a5ca2f2ebaa0108df4d9188595750ec76e5474b7af9`.
This is a retrieval blocker, **not proof that author code is unavailable
globally**.

Crucially, **successful Zenodo 383-row source-data authentication does not
resolve the Methods' 31 donor trial membership**. As long as the publisher
code is inaccessible and no independently justified inclusion rule is
available, the manuscript's 31-trial inferential analysis remains an
unreproduced result. All coded-group effect estimates above retain their
post-open exploratory label and no source-specific exclusion was chosen.

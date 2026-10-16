# Dalechampia 2015: source-authenticated blossom-level maternal-robust sensitivity

**Evidence ceiling:** post hoc alternative statistical analysis, NOT the published mixed-effects model, NOT a seed-carbon mechanism and NOT structural BALANCE occupancy.

## Main biological question and original source

Does an apparent benefit of retaining involucre bracts after anthesis remain precise when each experimentally manipulated blossom, rather than each seed, is the observational unit?

Pélabon et al. (2015, Functional Ecology, DOI 10.1111/1365-2435.12427) manipulated hand-pollinated Dalechampia scandens blossoms within maternal plants. The foil treatment obscured the **entire blossom**, including fruits; it was not a selective bract-only shade treatment. The study reported seed-mass treatment coefficients of approximately −2.03 ± 0.32 mg (foil-covered), −1.34 ± 0.32 mg (bracts removed), and +0.29 ± 0.32 mg (bract-edge-cut control), relative to intact blossom. Those values come from an adjusted maternal-random-effect source model that is **not** reproduced here.

Open data: https://doi.org/10.5061/dryad.nb675. Both original source file lengths and MD5 hashes are checked before analysis. The archived seed file contains 1,221 records, one missing mass, 142 blossoms nested in 37 mothers. A numeric <20-mg exclusion gives the source-reported 117 aborted-seed count, but does **not independently reproduce embryo/seed-coat morphology**. The numeric ≥20-mg sample retains 1,103 measured seed masses from 132 blossoms and 36 mothers.

## New independent estimator

One response per blossom: average nonmissing seed weights in that blossom, then fit a linear model with treatment versus intact control, blossom peduncle diameter and maternal-plant fixed effects. Uncertainty is a **mother-cluster-robust covariance with a finite-cluster correction**; intervals are asymptotic normal 95% Wald intervals, not exact small-sample t intervals. An optional seed-set covariate and an alternative all-mass analysis are presented together to prevent favorable posthoc model selection.

All numbers below are treatment minus intact control, in mg per seed as **blossom means**. Each bracket is a mother-cluster-robust asymptotic Wald 95% interval.

### Primary source-compatible numeric ≥20-mg subset (36 mothers, 132 blossoms)

| Treatment | Peduncle + maternal fixed effects | Additional seed-set adjustment |
|---|---:|---:|
| Entire-blossom foil cover | −1.841 [−3.862, +0.179] | −1.749 [−3.856, +0.358] |
| Both bracts removed | −1.158 [−3.298, +0.981] | −1.120 [−3.271, +1.032] |
| Bract-edge-cut sham | +0.687 [−1.558, +2.933] | +0.737 [−1.615, +3.088] |

All three primary intervals include zero. The **direction** of foil-cover and removal estimates largely agrees with the paper, but their precision is substantially lower. This cannot be described as a failure of exact numerical reproduction or proof that the source model was erroneous: the estimator, unit weighting and covariance structure differ.

### All nonmissing seed masses (37 mothers, 142 blossoms)

| Treatment | Peduncle + maternal fixed effects | Additional seed-set adjustment |
|---|---:|---:|
| Entire-blossom foil cover | −2.178 [−4.730, +0.374] | −2.731 [−5.143, −0.319] |
| Both bracts removed | −1.869 [−4.184, +0.447] | −1.833 [−3.910, +0.245] |
| Bract-edge-cut sham | +0.404 [−2.131, +2.939] | −0.320 [−3.151, +2.512] |

One exploratory foil-cover interval excludes zero only when both **all seed masses and seed-set adjustment** are included; that single favorable variant must **not** be selectively promoted to a confirmatory discovery. Both excluding low-mass seeds and including them can condition interpretation on developmental-stage outcomes. Neither version identifies mature reproductive fitness or morphological abortion independently.

## Source and inference separation

The six-plant physiological assay independently supports stronger green-bract area-based carbon fixation, but those plants are **different** from the maternal seed-mass experimental cohort. Bract-cover or removal treatments also alter fruit light, temperature, handling and potentially physical protection. No isotope-labelled carbon transfer to seeds was established.

Do not combine the 2012 resin or 2013 wild selection papers with the 2015 experiment to calculate causal SCH conflict L, architecture construction cost K, net alternative fitness, Phi or BALANCE occupancy. No independent biological cluster was added.

## Reproduction

The public archived two-file Dryad download is matched by source IDs, lengths and MD5 before fitting. The dedicated workflow runs the independent source model and verifies the frozen source SHA256, biological support and registered coefficient/interval outputs. The original published nlme AIC and all male-plus-female structural architecture worldlines are **not** claimed as replicated.

Components:
- balance_domain/dalechampia_blossom_clustered.py
- scripts/analyze_dalechampia_2015_blossom_clustered.py
- scripts/verify_dalechampia_blossom_clustered.py
- data/DALECHAMPIA_2015_BLOSSOM_CLUSTERED_FROZEN_V1.json
- .github/workflows/dalechampia-2015-blossom-clustered.yml

**Next experiment:** under a prospectively validated procedure, independently suppress bract-local photosynthetic assimilation while preserving fruit light, bract protection, heat/humidity, and handling; follow carbon uptake and mature viable-seed performance. If that physical separation is impossible, retain a mixed postanthesis blossom-treatment effect rather than assigning a bract-carbon mechanism.

# Wilkins 2022: within-colony slopes and downstream stigma-stage audit

**Analysis class: exploratory, post-open, same-source robustness only.**
This extension to PR #279 addresses a distinct gap in the earlier
[bee-level leave-one-colony analysis](BALANCE_WILKINS_2022_BEE_LEVEL_INFLUENCE_20261122.md).
A positive coefficient after deleting any whole colony does **not** establish
that the coefficient is positive **inside each original colony**.

The raw trial source and 2022 original R supplement were authenticated by
SHA-256 before reuse (CSV `0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62`,
[Wilkins et al. 2022 DOI 10.1007/s00442-022-05246-0](https://doi.org/10.1007/s00442-022-05246-0)).
Exactly 60 pollen-collecting bees are recorded in the source; 59 have
complete bee head width and pollen-stage measurements across Blue,
Orange and Red colonies. Anther architecture was altered alternately
between joined Cone and free Sham. Neither architecture assignment nor
the observed bee sizes establishes randomized body-size-by-architecture
factorial causality.

## Two prespecified readout families

**1. Same-colony architecture×bee-size:** For Blue, Orange and Red separately,
fit one bee-equal-weighted linear model

```r
log(BodyPollen/CorbiculaPollen) ~ Treatment*centered_HeadWidth + centered_VisitTime
```

with the original whole-study mean for centering. Report the free-minus-joined
size slope, *within-colony descriptive* standard error and 95% interval,
the n of Cone and Sham bees, and treatment-arm common observed size support.
There are **only three source colonies** and some within-colony arms are small;
these three slopes cannot establish species-wide or colony-population variation.
Do not use the prior leave-one-colony sign result in place of these slopes.

**2. Independent downstream observational endpoints:** On the **same 59 bees**
fit separately:

```
log_body_basket = log(BodyPollen / CorbiculaPollen)
log_stigma_body = log(StigmaPollen / BodyPollen)
log_stigma_count = log(StigmaPollen)
```

For each, the two fixed alternative source models are

```r
response ~ Treatment*centered_HeadWidth + centered_VisitTime + ColonyID
response ~ Treatment*centered_HeadWidth + ColonyID
```

The first conditions on observed visit time (a potential post-treatment
variable); the second omits this adjustment. They are model-specification
sensitivities **not sequential multiplicity-free tests**. For each report
the free-minus-joined head-width interaction coefficient and
heteroskedasticity-robust **bee-row HC3** approximate interval. The
`log_body_basket` time-adjusted slope must reproduce the prior independently
run estimate of +3.17546609 within 0.002, or the pipeline fails.

**Meaning:** `log_stigma_body` is a ratio of **pollen currently counted
on pooled stigmas versus pollen remaining on the bee's body**. It does not
measure the true fraction of all produced pollen deposited, because loss,
grooming, unrecovered pollen, donor pollen produced, and pollen on previously
visited stigmas are not exhaustively followed. `log_stigma_count` records
stigma-grain numbers, not viable donor genetic paternity or seed production.
The same terminal-body pool appears in more than one endpoint, so these
responses are mathematically dependent; two different individual p-values
are not a test of an endpoint-effect difference. These analyses do **not**
estimate a new mediator by multiplying across separate outcomes.

The source manuscript's published stigma model, conditioning on
`log(BodyPollen)`, gave a nonsignificant architecture×head-width term
(p=0.4919) and a significant architecture×terminal-body-load term
(p=0.0213). The new stigma-count models condition on a different set
of variables and therefore do not overwrite that published estimand.

## Threats and interpretation

The data include 7 recruited bees that never collected basket pollen and
were excluded from the original archive: these outcomes cannot be
recovered or assumed to be zeros. Only three bee colonies are represented;
the 2022 source plants were reused but their IDs are not available in the
CSV. Head width and visit time may correlate with pollen handling, and
time is measured after treatment. HC3 CIs assume bee-row independence and
are **not robust to unmeasured colony/source-plant clusters**.

Before observing added outcomes, the following interpretive ceiling is fixed:

- If colony-specific signs differ, state that **pooled positive evidence is
  not uniformly present in the three observed colonies**, despite deletion
  stability. Do not choose one favorable colony.
- If downstream stigma response is null, state **no supported transmission
  of the body/basket routing interaction to observed stigma deposits** under
  those specifications; null is not equivalence.
- If stigma response is non-null, state a within-study **stigma-deposition
  association**, not genetic siring, maternal seeds or structural net fitness.
  The two staging outcomes cannot establish mediation or a causal relay.
- No result from this extension is a preregistered V4 architecture outcome,
  an independent evolutionary transition or an experimental estimate of
  `L`, `K`, or `Phi`.

## Execution and verification

The original source-authenticated R workflow now adds:

```bash
Rscript scripts/check_wilkins_2022_colony_and_stigma_stages.R \
  /path/to/442_2022_5246_MOESM3_ESM.csv \
  /tmp/wilkins-2022-checks
```

The run exports `colony_specific_size_slopes.csv` (three colonies),
`pollen_stage_bee_hc3.csv` (six fixed endpoint × model combinations) and
`colony_stage_inference_scope.csv`. This is an **explicitly post-open
exploratory** source reanalysis. No raw publisher CSV or original
copyrighted author code is committed to the repository, and the existing
U2/U6/V4 coder surfaces are unchanged.

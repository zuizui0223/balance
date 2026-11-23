# Harder 2021 — paper-aligned original row count and six-visit hurdle audit

**Post-open original-source sensitivity, recorded before this additional
statistic is computed.** Source: Harder et al. (2021), doi:10.1086/712378;
the authenticated original `Data_for_AmNat.csv` is SHA-256
`303428b859bcba4756ac78c4ffd4b42121a6efce5b0cd2cc2030834705f62cbc`,
383 recipient-level rows, 32 distinct source `(Trial_type,Trial)` codes.

## Corrected original publication-level ambiguity

In the *same published paper*, the general experimental Methods say **16
emasculated and 15 intact trials**, minimum **six** flowers (section Data
Collection). However, the process-based dispersal model Methods say
**379 individual recipients from 31 trials: 15 emasculated and 16 intact**
(section Model Fitting). These two reported treatment allocations are
**internally contradictory**, independently of the 32-coded-group CSV.

Original source `Intact` code `4` has exactly **four** recipient records
(visits 1–4). Excluding only these four from the 383-row original file yields
**379 recipient records and 31 source groups: 16 Emasc + 15 Intact**.
This *simultaneously matches* the paper's general Methods allocation and
modeling section **recipient-row count**, but **does not match** the
modeling section's reversed group allocation. It also remains inconsistent
with the manuscript's claimed ≥6 visits for every trial, because source
`Emasc` trial `7` has only two recorded visits.

This makes the unique four-row source `Intact4` exclusion a useful
**paper-alignment candidate**, *not an externally confirmed author
inclusion/exclusion rule*. The original author supplementary ZIP returned
HTTP 403; no published code or donor identity establishes why
Intact4 exists, why Emasc7 has two visits, or whether source Emasc2
and Emasc3 are truly separate donors. Do **not** silently correct
the article's own group counts or announce a successfully replicated
original 31-trial model.

## Locked quantitative diagnostics on the same stained donor source

1. Compare source group effects on
   `sum(Deposition)/M_init` for:
   - All original 32 coded groups (16/16).
   - Paper-aligned *candidate* removing only source Intact4: 379 recipient
     rows, 31 coded groups, 16/15, **no unspecified removal**.
   - Exploratory merge of consecutive Emasc2 + Emasc3 (15/16; 383
     recipient rows) which recovers the *opposite* author paragraph.
   All comparisons report group means and ratios as **coded-group
   descriptive estimates**, not certified 31 independent donor trials.
   Cross-check the paper-aligned candidate is one of all 16 intact-code
   leave-one-out sensitivity scenarios already recorded in PR #281.
2. Restrict to **the common recorded early six recipient positions**.
   A source coded donor unit is eligible iff it records visit positions
   1,2,3,4,5,6; this excludes Emasc3 (starts at visit 11), Emasc7
   (two visits) and Intact4 (four visits), leaving 14 Emasc + 15 Intact
   coded groups, with 174 individual recipient observations.
   This window prevents groups with longer recipient chains from
   automatically contributing more deposited massulae. Each eligible
   coded group contributes exactly **six** recipients, and the group
   remains the experimental unit.
3. Within that common six-visit window, calculate:
   - Fraction of the six stigmas receiving **at least one stained donor
     massula**, equal weight to each donor-code group.
   - **Mean number of stained massulae per positive stigma** within
     each donor code group, divided by its fixed initial donor massula
     count `M_init`; do not estimate this if all six stigmas are zero.
   - Mean deposited stained massulae on all six stigmas divided
     by `M_init`.
   - First-six recipient position-specific zero-deposition fractions,
     with one observation per group at each position.
   These are descriptive observed-zero and positive-deposition stages.
   **Zero massulae on a stigma does not identify lack of stigma contact;
   it may also reflect lack of available pollen or zero transfer on
   contact.** No separate mechanistic contact probability `c` is
   claimed without directly observed contact events.
4. Report 20,000 **within-treatment code-group bootstrap** percentile
   intervals for the difference (Intact−Emasc) of the common-six
   source massula export fraction, any-stained-massula fraction and
   conditional positive-stigma normalized deposition amount. The
   bootstrap is an **exploratory coded-group** interval, and may
   overstate statistical independence if Emasc2/E3 or other code groups
   are repeated portions of one bee donor.
5. Audit the number of fixed six-stigma groups with *zero* positive
   recipients; these cannot support a conditional-positive mean.
   Report the sample sizes for that component explicitly rather than
   silently discarding them from the source count.

## Interpretation gate and scientific value

If Intact/Emasc still differs when each group is standardized to six
recipient opportunities, the group-level effect is **not solely a
consequence of different numbers of visited flowers**. It could
still arise from treatment alternating with day/bee characteristics,
underlying source massula stock, pollen residence, stigma contact,
within-trial pollen depletion or other unmeasured confounding.

If the any-stained-massula frequency differs but positive-load does not,
call the data **compatible** with a zero-versus-positive exchange
bottleneck; do not identify it as physical stigma contact.
If positive-load differs but not nonzero frequency, call the difference
**compatible** with a conditional load bottleneck, not proof of
reduced pollen viability or physiological male fitness.
If both differ, report both observable components as separate,
potentially dependent stages.

The original published experiment remains **independent of prior
Solanum studies** at the research programme/plant-family level,
but is not a test of flower architecture evolution, fathered offspring,
seed production or BALANCE structural cost `K` / `Phi`.
Frozen U2/U6/V4 source admissions and blinded human architecture
outcomes are unaffected.

## Reproduce

```bash
python -m scripts.audit_harder_2021_zenodo_mirror --source-dir /tmp/orchid-source
python -m scripts.check_harder_2021_visit_window_hurdle \
  --original-csv /tmp/orchid-source/Data_for_AmNat.csv \
  --out /tmp/orchid-early-six-summary.json
pytest -q tests/test_harder_2021_visit_window_hurdle.py
```

Output artifacts contain **only code-group aggregate summaries and source
membership counts**, not raw donor/recipient data and not final genetic
paternity or independent evolved lineage effects.

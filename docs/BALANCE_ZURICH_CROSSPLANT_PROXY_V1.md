# Same-garden cross-plant visitor composition: exposure proxy diagnostic

**2026-11-15; post-open exploration, not a causal negative control or new experimental replication.**

Original source: [Zurich 2025 EnviDat DOI 10.16904/envidat.676](https://doi.org/10.16904/envidat.676). This retains all 24 study gardens and verifies the same original ZIP SHA256 via the upstream Zurich analysis. *Daucus carota* and *Raphanus sativus* were selected after the first 4-species analysis because both use compatible Apis / other-bee / nonbee guild categories.

For each focal plant, preserve its **own total recorded captures per observer-hour** as the baseline predictor. Add two visit-guild shares from (A) that plant or (B) the other plant measured in **the same garden**. Train on 23 whole gardens, predict the omitted garden, repeat for all 24. Evaluate four covariate settings without dropping null or unfavorable outcomes.

| Outcome | Source of composition | No extra covariates | Mean flower exposure | Latitude & longitude |
| --- | --- | ---: | ---: | ---: |
| Carrot seeds | Own Carrot | +19.40% | +19.33% | +12.93% |
| Carrot seeds | Radish, same garden | −18.41% | −17.37% | −15.02% |
| Radish fruit formation | Own Radish | −0.10% | +2.50% | +0.31% |
| Radish fruit formation | Carrot, same garden | +18.05% | +14.99% | +16.09% |

Positive percentage is held-out garden RMSE reduction compared with the same focal baseline and matching nuisance covariates. A fifth sensitivity contrast uses flower-positive survey time; all directional results are retained in the full machine readout.

**Interpretation:** The fact that Carrot composition predicts Radish fruit better than Radish's own composition in the examined models means composition can carry information about garden-wide exposure, sampled visitor movement or shared biotic/abiotic conditions. It does not identify *which* of those mechanisms acts, and does not rule out genuine cross-plant interactions. The borrowed plant's guild shares are not a randomized negative control; co-planted phytometers share real visitors. Thus this comparison is a post-open diagnostic, not confirmation of an independently transferable biological mechanism.

One Zurich field programme still counts as ONE study. Neither morphology nor matched architecture construction costs or net shared-vs-differentiated reproductive fitness were measured. No U2/U6 architecture coder rows, original V4 estimands or source admissions are changed.

Reproduction from original verified ZIP:

    python scripts/audit_zurich_crossplant_proxy.py --source /path/to/EnviDat_2025_four_species_original.zip --out-dir /tmp/zurich_proxy
    BALANCE_ZURICH_ORIGINAL_ARCHIVE=/path/to/EnviDat_2025_four_species_original.zip python -m pytest -q tests/test_zurich_crossplant_proxy.py

See also the independent Wisconsin orchard source and frost-adjusted prediction in docs/BALANCE_WISCONSIN_APPLE_CONTEXT_CONDITIONALITY_V1.md.

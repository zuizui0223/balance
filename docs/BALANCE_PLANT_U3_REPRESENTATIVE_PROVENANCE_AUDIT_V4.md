# BALANCE U3 representative provenance audit v4

## Two different questions are now frozen separately

Earlier U3 notes used representative identity for two different objects. That ambiguity is now removed.

### A. Canonical family representative coverage

Question: do all 16 Figure-2 heteranthery-positive families have at least one source-secure representative taxon at an explicit provenance level?

Answer: 16 / 16 CLOSED.

The three families formerly lacking body-text/Table-S1 access are represented independently as:

- Malvaceae — Mollia lepidota
- Bixaceae — Amoreuxia wrightii
- Scrophulariaceae — Verbascum phoeniceum

The provenance levels are not identical. Mollia lepidota and Amoreuxia wrightii have pre-2010 independent morphology evidence. Verbascum phoeniceum is deliberately marked post-review independent evidence.

None is asserted to be the species printed in the inaccessible 2010 Supporting Table S1.

### B. Exact Supporting Table S1 reconstruction

Question: what exact species did Vallejo-Marín et al. (2010) print in Table S1 for Malvaceae, Bixaceae and Scrophulariaceae?

Answer: ARCHIVAL OPEN.

Live Wiley supplement routes return HTTP 403. The registered Wayback audit found no usable saved copy. Candidate reduction has narrowed the historical search space, but exact original-row identity is not recovered.

This archival question does not block the current U3 programme. Figure-2 family membership is source-closed, the matched species cases are independently sourced, and canonical family representative coverage is complete.

## Machine-readable contract

- data/BALANCE_PLANT_U3_REPRESENTATIVE_RESOLUTION_V3.json
- balance_domain/plant_u3_representative_resolution.py
- tests/test_plant_u3_representative_resolution.py

The validator fails closed if canonical coverage falls below 16, if any of the three representative taxa/provenance classes drift, if exact Table-S1 identity is silently marked closed, or if archival identity is reintroduced as a current analysis blocker.

## Claim ceiling

BALANCE can state that all 16 U3 families have source-resolved representative coverage at explicit provenance levels.

BALANCE cannot state that Mollia lepidota, Amoreuxia wrightii, or Verbascum phoeniceum are the exact species printed in the inaccessible 2010 Table S1.

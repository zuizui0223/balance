# Alpinia: site-level confounding and a fixed-quality visitor-efficiency diagnostic

**2026-11-17, post-open exploratory SOURCE audit. One species, one biological study, no new U6 architecture outcomes.**

## A stronger limitation than previously foregrounded: the effective exposure unit

The original Deng et al. (2015) [PLOS ONE methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC4687006/) describe a **two-by-Four-Directional-Plot (FDP)** comparison: **one squirrel-exposed and one guarded FDP**, ~**300 m apart**, each with **four compass-direction transects / 60 spatial subplots**. Four on-site observers actively guarded the unrobbed FDP. Subplots, distance bins, or sampled flowers inside an FDP **are not independently randomized FDP-scale robbery exposures**. One guarded versus one exposed FDP leaves robbery status perfectly tied to the **specific plot location**. Even a spatial CAR model or repeated measurements within these two plots does not separately identify the top-level robbery-versus-location effect. The abstract's shorthand about randomly established plots does not supersede the detailed two-FDP layout.

Original **S1** [DOC supplement](https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0144585.s001&type=supplementary) provides 32 published direction × distance-bin dye-positive stigma **means**, not 32 separate treatment-site replicates. Original **S2** [DOC supplement](https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0144585.s002&type=supplementary) provides 16 year × direction × exposure **aggregates**, not individual flowers or independently randomized sites. This applies simultaneously to the purported three-stage chain (visits → fluorescent dye → fruit formation), and the three stages were not measured on the same flowers at matched times.

## A sharply scoped falsifiable *mean-based arithmetic* check (not statistical rejection)

Published six-day visit rates, visits/h: squirrel-exposed *Bombus eximius* **6.15 ±0.82 SE**, *Apis cerana* **3.06 ±0.81 SE**; guarded **7.86 ±0.94** and **1.33 ±0.34**, respectively. Summing only these two reported means gives 9.21 versus 9.19, but this is **not all visitor taxa or a statistical equivalence claim**. Relative Bombus fraction within the two groups falls from 85.53% to 66.78%.

Define a hypothetical linear effective-visit index with fixed per-visit *Bombus* effectiveness 1 and fixed *Apis* effectiveness \`a\` where \`0 <= a <= 1\`: exposed/guarded index \`(6.15+3.06*a)/(7.86+1.33*a)\`.

| Assumed Apis/Bombus efficiency a | Plug-in effective visit ratio (exposed/guarded) |
|---:|---:|
| 0 (Apis contributes nothing) | 0.78244 |
| 0.25 | 0.84406 |
| 0.50 | 0.90088 |
| 0.75 | 0.95343 |
| 1 (equal quality) | 1.00218 |

Original S2 fruit-set ratio \`(5174/17231)/(7001/16845)\` is **0.72248**: lower than the **plug-in** envelope [0.78244, 1.00218]. Solving exact plug-in equality for \`a\` gives **−0.22452**, disallowed by the hypothetical nonnegative weighting. This only means that the **rounded published means** do not algebraically reproduce the observed fruit ratio *under all these strong model assumptions*. It is NOT evidence that visitor composition failed, that other mechanisms have been identified, or that any formal null hypothesis was rejected.

In fact, using *only an illustrative ±1 published SE shift* to the two Bombus means yields \`(6.15-0.82)/(7.86+0.94)=0.60568\` to \`(6.15+0.82)/(7.86-0.94)=1.00723\`. The fruit ratio 0.72248 falls inside. **This is a sensitivity scenario, NOT a confidence interval**, because published summary errors do not reveal the covariance or full sampling distribution of the two-guild index.

Crucial omitted channels: **floral damage and discarded flowers**, pollen/visitor behavior per flower, altered visit timing, pollinator-quality plasticity, nonlinear fruit initiation, unrecorded visitors and a confounded 300-m plot contrast. Six-day bee observations are not matched in time or individual floral identity to the 2005/2007 fruit-set measurements. The source explicitly reports style damage and complete floral removal.

## Consequences for BALANCE

What survives: a **within-one-study ecological signature** of altered bee-guild composition, a lower fluorescent dye-transfer proxy within 0–14 m, and lower plot fruit-set fractions. None identifies **causal mediation**, genetic male siring or net structural trade-off/cost (\`L\`, \`K\`, \`Phi\`, optimized \`W_D^* - W_S^*\`). No multiplication or pooled statistical significance across the nonindependent S1/S2 cells. **Do not count 60 subplots as 60 independent randomized FDPs.**

To test mechanism: independently replicate site-level squirrel exposure (or matched longitudinal natural experiments with defensible identification), orthogonally manipulate nectar removal and stigma/style/corolla damage, track the same flowers through effective visitor events, genuine pollen deposition, fruit initiation, mature viable seeds and paternity. To claim evolved differentiation, separately compare viable shared versus differentiated architectures at matched total fitness scales.

## Reproduction

\`\`\`bash
python -m pytest -q tests/test_alpinia_dye_visitation_bridge.py tests/test_alpinia_fixed_efficiency_envelope.py
python scripts/audit_alpinia_fixed_efficiency_envelope.py \
  --s1-original-doc /path/to/pone.0144585.s001.doc \
  --s1-antiword-text /path/to/S1_TEXT.txt \
  --output /tmp/alpinia_fixed_efficiency_plot_gate.json
\`\`\`

The parent bridge SHA256-checks original S1/S2 normalized rows; the official original S1 DOC is checked if supplied. FDP design counts are independently sourced from the **published field methods** (not claimed to be original S1/S2 row columns). Original U6's 21 taxa, 42 independent A/B forms, V4 sealed outcomes and SLK work remain untouched. This PR stays draft.

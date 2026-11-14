# U6 original source ecology: final six preselected taxa and eligibility/fitness ceilings

**Date:** 2026-10-28. **Status:** original-paper abstract/full-text source observations and explicit source-access uncertainty; **not** independent U6 architecture coding, a causal experiment, matched architecture fitness, or historical origin. This is an exploratory source-extractor lane stacked above [the immediately preceding six](BALANCE_U6_NEXT6_ORIGINAL_FUNCTION_LOCATION_AUDIT_V1.md); it must not be supplied to the independent source-blinded coders.

## Fixed selection and coverage

U6's [Pass-1 frozen 21-group conflict-first universe](../data/BALANCE_PLANT_U6_PASS1_FREEZE_V1.json) has **18 SIMULTANEOUS** and **3 SEQUENTIAL_WITHIN_UNIT** source timing tags. After the original main ecology six (all three sequential + simultaneous alphabetic ranks 1–3) and the prior additional simultaneous ranks 7–12, the final remaining source-extractor-only lane examines **simultaneous alphabetic ranks 13–18**:

*Nothofagus pumilio*, *Passiflora foetida*, *Prockia crucis*, *Pseudobombax ellipticum*, *Theobroma cacao*, and *Zea mays*.

The separate earlier first-six ecological clock branch contains simultaneous ranks 1–6 and overlaps the main original-six pilot in three; it remains **unmerged**. Consequently:
- On the **stacked ecology branches**, source notes exist for **18/21** biological U6 taxa. The remaining 3 are *Banksia menziesii*, *Bromelia antiacantha*, *Campanula americana* (already described only on the separate first-six clock branch).
- Across these source-extraction branches, 21/21 distinct taxa have **some provisional ecological description**, but this is **not one merged, independently adjudicated source dataset**. Original source identity and quality differ greatly. No 21/21 original full-article quantitative outcome analysis is claimed.
- Original U6 42 independent A/B coder rows remain **UNSTARTED/UNRESOLVED**; predictor adjudication and sealed V4 outcomes have not been opened.
- Original references are not independent evolutionary origins. Two *Theobroma cacao* admission studies belong to **one biological taxon/dependence group**, not two taxa.

## Six published source accounts with distinct functional levels

| Frozen taxon | Original article | Source-supported ecological phenomenon | Boundary / source limitation |
| --- | --- | --- | --- |
| *Nothofagus pumilio* | [Díaz & Kitzberger 2006](https://doi.org/10.1111/j.1442-9993.2006.01637.x) | Parakeets eat **wind-pollinated flowers** as a seasonal food resource, removing reproductive structures and pollen while tracking flowering/altitude | Flower consumption is not a measured male-siring penalty of 65%; no tested alternative reproductive organ |
| *Passiflora foetida* | [Amela García & Hoc 1998](https://www.scielo.sa.cr/scielo.php?pid=S0034-77441998000200002&script=sci_arttext) | Pollen-collecting bees can avoid stigma contact, whereas effective nectar-foraging visitors contact both male and female parts; nectar puncturing is a **distinct** robbery pathway. Stigmas move through successive flower phases | The three morphological phases are not a reversible within-genotype cue-policy experiment or a de novo structure |
| *Prockia crucis* | [Bullock, Martínez del Río & Ayala 1989](https://pubmed.ncbi.nlm.nih.gov/28312586/) | Pollen is the floral reward; the balance of efficient and inefficient pollen-consuming bee visitors changes over the day | Source records visitor timing and flower display, not a direct genetic architecture alternative or combined reproductive fitness; original U6 evidence ceiling retained |
| *Pseudobombax ellipticum* | [Eguiarte, Martínez del Río & Arita 1987](https://pascal-francis.inist.fr/vibad/index.php?action=getRecordDetail&idt=7640827) | Nectar bats visit at night as major pollinators, while orioles, bees and hummingbirds use flowers by day with different transfer implications | Visitor chronology is not proof of programmed novel pollen-dosing organs; original full PDF is linked for later verification but not analyzed as primary raw data here |
| *Theobroma cacao* | [Young 1981](https://doi.org/10.2307/2402485), [Young 1985](https://doi.org/10.1007/BF02012584) | Stingless bees collect cacao pollen without sufficient stigma contact; low field fruit set and flower handling are source observations | Different source years/experiments are not equivalent controlled population interventions. Single U6 taxon and unresolved complete siring/structure cost |
| *Zea mays* | [Lundgren, Razzak & Wiedenmann 2004](https://doi.org/10.1603/0046-225X-33.4.958) | Predatory ladybird beetles use wind-dispersed corn pollen as an alternate food resource while also feeding on aphids | **New eligibility concern:** beetle diet/pollen capture from the field does not, by itself, establish a male gamete-export loss, maternal seed change, or consumptive emasculation of plants. Flag for independent original-source admission review, **without retroactively excluding the frozen Zea group** |

These source observations have individual locators, numerical/source-availability qualifications, and non-coder status in [the frozen selection-order extractor ledger](../data/BALANCE_U6_LAST6_SOURCE_FUNCTION_ECOLOGY_V1.csv). The *Nothofagus* consumer-removal observation does not provide plant siring, and the *Zea* predator diet study does not quantify a cost to maize reproduction. Some sources were accessible as original abstracts/indexed author summaries rather than complete article datasets; data lacking from the original source remain missing, not biological zero.

## Main scientific implication

The **source locus** and the **clock** must be distinguished from (and independently quantified before) a proposed architectural response:

1. Pre-deposition pollen removal from anther: consumer can eat reward pollen without effective export.
2. Post-deposition pollen removal on recipient stigma: already-delivered gametes are taken, as previously found in [*Melastoma affine*](BALANCE_U6_NEXT6_ORIGINAL_FUNCTION_LOCATION_AUDIT_V1.md), rather than being removed from source anthers.
3. Destructive consumption of an entire wind-pollinated flower, and ingestion of pollen already dispersed into a predator's environment, may not be equivalent to competing pollen reward/export functions within a flower.
4. Time-of-visit (night/dawn/day), pollen exposure timing, stigma receptivity and irreversible developmental flower phases are biologically different timescales. Nor is any of them the PAYOFF parameter `rho` without repeated true environmental state observations.

**Do not fit** the hypothesized new architecture-value effect using these observation labels as SLK `L`, PAYOFF same-coordinate conflict `C`, reversible plasticity `W_P`, or an inherited new module. The original inclusion is not changed; it is *audited*. For Zea, an admissibility doubt is an independent review task, not a retroactive source-based decision to remove an inconvenient taxon.

## Source audit and next legitimate step

Run:

```bash
python -m pytest -q tests/test_u6_last6_source_function_ecology.py
python scripts/audit_u6_last6_source_function_ecology.py --out /tmp/u6_last6_ecology.json
```

The implementation reads the original 21-taxon freeze, 63 original predictor receipts, original source packet, earlier merged-six pilot, previous extra six source pilot, taxonomy dependence and 42 double-coder placeholders. It validates the final-six membership, original U6_REF links, evidence gaps and biological process/locus types; source hashes are recorded.

**Unresolved scientific gates:** independently blinded `CODER_A` / `CODER_B` architectural and predictor coding (0/42 formally complete), no source-verified matching of `W_S,W_P,W_D`, no independently measured structural cost `K`, no nuclear genetic architecture/path, no independent dated origin, no causal evidence that a trade-off historically evolved a new structural module. SLK/BITA sister projects retain the original mechanism/fitness boundaries; this document is **source ecology only**.

## Post-open source-stage comparability stress test (2026-11-14)

**Exploratory scientific extension, not frozen V4 input or an independent source adjudication.** The source-first U6 roster includes observations from different reproductive stages and even different biological fitness pathways. A pooled label `POLLEN_THEFT` therefore does not license pooling their effect estimates as a shared anther-coordinate conflict, nor infer that any floral module was selected by theft. These distinctions are testable **eligibility hypotheses**, not findings about architecture fitness.

| Biological location of documented event | Original evidence example | What can be inferred | What a causal contrast would still require |
| --- | --- | --- | --- |
| Before dispersal, at a donor anther or floral pollen pool | *Grevillea barklyana*, Vaughton (1996), [author abstract](https://aff.org.au/results/grants-awarded/aff-vaughton-grevillea-publication/): bees gather male-phase pollen, and bird exclusion with bee access reduces fruit set by >50% relative to combined access | Floral visitor identity and access can affect reproductive performance; exclusion is an intervention on the visitor assemblage | Matched anther-level pollen-fate and siring measurements, separate controls for loss of bird service, and comparison to a viable differentiated source architecture |
| After pollination, on a recipient stigma | *Melastoma affine*, Gross & Mackay (1998), [original article](https://doi.org/10.1016/S0006-3207(98)00010-X): honeybees remove **previously deposited stigma pollen**; late honeybee visits lower seed set | An independently supported recipient-stage reproductive interference mechanism | Recipient-side pollen-retention/deposition interventions; anther-level pollen partitioning alone cannot be assumed to solve a recipient-side loss |
| Whole flowers and their pollen removed | *Nothofagus pumilio*, Díaz & Kitzberger (2006), [original article](https://doi.org/10.1111/j.1442-9993.2006.01637.x): parakeets harvest wind-pollinated flowers | A destructive consumer interaction with reproductive structures | Measured counterfactual pollen export/siring and seed production under harvest versus control, not a numerical conversion of percent pollen eaten into percent fitness lost |
| After pollen has entered the external wind-dispersed environment | *Zea mays*, Lundgren, Razzak & Wiedenmann (2004), [original article](https://doi.org/10.1603/0046-225X-33.4.958): coccinellid predators eat corn pollen shed into the field | Pollen is a subsidy to predator diets; source quality warrants a primary eligibility flag | Evidence that beetles remove pollen **before successful gamete export** and thereby change maize siring or seed fitness, not simply predator diet and anthesis overlap |

**Falsifiable stage-match restriction (post-open hypothesis):** a source-anther architectural manipulation should be evaluated against source-anther removal and pollen export, whereas recipient-stigma removal must be evaluated against deposition/retention and subsequent fertilization. The location of resource uptake alone does not imply a fitness conflict if the uptake occurs after the plant's relevant pollen-export opportunity. If matched manipulations show that an anther-only change protects fertilization from purely recipient-side removal without altering recipient exposure, or that post-export predator feeding causes measured donor fitness loss despite no pre-export pollen limitation, the simple stage-local mechanism must be revised rather than imposed on the data.

For a **future study**, measure (i) pre-visit donor pollen availability, (ii) exported pollen, (iii) delivered and subsequently removed recipient pollen, (iv) paternity and mature seed success, and (v) independent fitness costs of an accessible anatomical alternative, with plant/population identifiers and temporally synchronized exposure. Use controls for visitor assemblage change, stigma damage, animal displacement, wind flow, fruit/flower removal and environmental confounding as appropriate. Not every system permits every intervention. Biological replicates are independent plant/study programmes, not rows, visit events, article citations or multiple pollen stages from the same flower.

**Analytical firewall:** preserve all 21 preselected U6 taxa and both independent architecture coder sheets unchanged. Do **not** retroactively exclude *Zea* or *Melastoma* based on their ecological outcome or source quality; instead tag source-side fitness-link eligibility as `NOT_TESTED`, `EVIDENCE_CEILING`, or independently verified when an appropriate future audit exists. Stratify any *new* exploratory stage-specific synthesis **after** source-identity review; never backfill `L`, `R`, `K`, `Phi`, structural mode, historically evolved modules or V4 responses from these notes. Existing locked V4 predictors and estimands remain untouched. No new data, experiment or causal BALANCE receipt was generated by this addendum.

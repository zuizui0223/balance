# BALANCE U3 prospective routing expansion queue v5

## Queue exhausted

The prospectively frozen four-family expansion has completed its matching-stage acquisition pass.

```text
1  Bixaceae        Amoreuxia wrightii    EVIDENCE_CEILING_BLOCKED
2  Brassicaceae    Brassica rapa          EVIDENCE_CEILING_BLOCKED
3  Lythraceae      Lagerstroemia indica   EVIDENCE_CEILING_BLOCKED
4  Malvaceae       Mollia lepidota        EVIDENCE_CEILING_BLOCKED
```

No row was removed, replaced by an easier case, or converted to a negative biological result.

## Why this is a result

The expansion was deliberately frozen before prospective control conflict or routing outcomes were observed. Under that design, every added heteranthery-positive case encountered a distinct negative-control identification limit:

- Bixaceae: nearest nonheterantherous candidate has unresolved species-level animal-pollination eligibility.
- Brassicaceae: close relatives retain tetradynamy; biologically eligible equal-stamen family candidates cannot be source-ranked as the closest eligible relative.
- Lythraceae: close relatives retain dimorphic stamens; a monomorphic congener remains unranked on the common phylogenetic surface and incompletely resolved for effective pollination.
- Malvaceae: source-resolved Mollia congeners retain differentiated stamen cohorts, while a newly described divergent congener and the accepted species remainder are not source-closed for morphology or intrageneric ranking.

Therefore:

```text
prospective_queue_exhausted = true
new dependence blocks        = 4
closed controls              = 0
evidence-ceiling missing     = 4
```

This is not evidence that valid controls do not exist. It is evidence that strict, blinded matched-control construction is currently identification-limited on the public source surface.

## Consequence

The programme should not respond by widening controls until a desired contrast appears. The four blocked dependence units remain explicit missingness. Any later reopening must be triggered by genuinely new morphology, pollination, or phylogenetic evidence and must preserve the frozen candidate history.

## Claim ceiling

This queue result concerns matched-control identifiability. It does not estimate heteranthery prevalence, conflict effects, routing effects, or historical transition probabilities.

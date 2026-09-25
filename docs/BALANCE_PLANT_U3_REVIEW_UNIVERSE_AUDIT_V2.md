# BALANCE plant U3 heteranthery review universe v2

## Current state

The Figure-2 family universe remains exactly 16 families / 12 APG III orders and remains outcome-selected positive discovery evidence, not a prevalence denominator.

Representative provenance is now:

```text
BODY_TEXT_NAMED                         11
SOURCE_RESOLVED_INDEPENDENTLY            3
SOURCE_RESOLVED_INDEPENDENTLY_POST_REVIEW 1
TABLE_S1_REPRESENTATIVE_PENDING          1
TOTAL RESOLVED                          15 / 16
```

The inaccessible Wiley Table S1 was audited reproducibly in workflow run `36077393929` (artifact `10840830354`). The article page and four registered supplement URL forms all returned HTTP 403. The repository therefore preserves a retrieval-failure receipt rather than pretending the table was read.

## Bixaceae closed independently

`Amoreuxia wrightii` is now the independent representative.

Authoritative North American flora treatment describes `Amoreuxia` as having two dimorphic fertile stamen sets. The species description for `A. wrightii` resolves the sets concretely: shorter distal filaments with yellow anthers versus longer proximal filaments with usually dark-red anthers.

This also fits the review's taxonomic handling: Vallejo-Marín et al. explicitly note that APG III merges former Cochlospermaceae into Bixaceae.

This is **not** a claim that Table S1 named `A. wrightii`.

## Scrophulariaceae closed as post-review independent representative

`Verbascum phoeniceum` is now registered under the separate provenance class `SOURCE_RESOLVED_INDEPENDENTLY_POST_REVIEW`.

Lunau et al. (2017) explicitly figure `V. phoeniceum` (Scrophulariaceae) as having within-flower heteranthery. This is excellent species-level confirmation that the family contains a valid heterantherous representative, but it postdates the 2010 review.

Therefore it closes the **independent representative** need only. It does not reconstruct the inaccessible 2010 Table S1 row.

## Malvaceae deliberately remains open

The historical evidence strongly narrows the relevant lineage to `Mollia`.

Darwin (1877) reports that in several `Mollia` species the five outer stamen cohorts are longer and carry green pollen while the five inner cohorts are shorter and carry yellow pollen; he explicitly says he obtained specimens of `M. lepidota` and `M. speciosa`. Müller (1883) independently summarizes the same pattern.

However, Vallejo-Marín et al. (2010) state that Malvaceae contributed **one** reported heterantherous species. The historical sources expose more than one plausible `Mollia` species, so choosing one would manufacture precision.

Thus:

```text
Malvaceae exact representative = OPEN
candidate lineage              = Mollia
```

until the exact single-species source can be recovered.

## Claim ceiling

U3 now has 15/16 family representatives source-resolved at explicitly separated provenance levels. It still cannot claim the inaccessible Table S1 was read, cannot estimate heteranthery prevalence, and cannot use the post-review Scrophulariaceae representative as evidence of what the 2010 supplement specifically listed.

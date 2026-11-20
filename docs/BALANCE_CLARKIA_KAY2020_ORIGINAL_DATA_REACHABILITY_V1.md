# Clarkia Kay et al. (2020): original-data audit and BALANCE testability

**Status (2026-11-19): independently located original public research and Dryad files; NO downloaded microdata or new effect estimates yet.** This is an original-source and archived-file availability audit, separate from the model-only PR #274 and frozen V4.

## Primary research, not a new result

Kay, Jogesh, Tataru & Akiba (2020), *Proceedings of the Royal Society B* 287:20202593, [doi:10.1098/rspb.2020.2593](https://doi.org/10.1098/rspb.2020.2593). Open full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC7779490/

Original released data and code: Kay et al. (2020), [Dryad doi:10.5061/dryad.8cz8w9gmp](https://datadryad.org/dataset/doi:10.5061/dryad.8cz8w9gmp), Dec 26 2020. The public landing page lists 29 files totalling 12.95 MB. This is **one primary biological research programme** comprising multiple distinct experiments and two species, not 29 biological replicates or multiple independent confirmations.

### 2018 greenhouse: strongest pollen-presentation/export data

*C. unguiculata*, 13 dosing arrays versus 15 fully dehisced no-dosing arrays. Each array had 20 male-phase source flowers, five emasculated receptive female-phase flowers and one *Bombus impatiens* visitor. All inner anthers were removed; outer anthers were just beginning to open in the dosing treatment and fully dehisced in no-dosing. **No-dosing flowers were approximately one day older**, a potentially relevant biological confound.

| Reported outcome | Dosing | No dosing | Source inference |
|---|---:|---:|---|
| Exposed pollen measured along anther length | 1.9 mm | 4.6 mm | F(1,38)=483.17, p<0.001; **this is exposed length, not counted grains** |
| Stigma pollen | reference | ~30% lower no-dosing point estimate | treatment coefficient −0.3507, p=0.27; **not significant** |
| Bumblebee corbicula collected pollen | 6.7 mg | 6.5 mg | F(1,25)=0.01, p=.923; not significant |

The original article interprets these results as supporting the *potential* for gradually exposing pollen to increase its efficiency of export, but **does not measure paternal genetic success** and does not establish equivalence of pollen deposition. The study does not randomize the order of a legitimate visitor versus a thief as in PR #274, nor directly estimate the relative late-cohort contribution `q` or removal fraction `b`.

### 2017 field: visitation versus female-seed endpoints

*C. unguiculata*: field manipulation in 17 patches, five floral removal treatments, morning/afternoon observations over two days, patch-structured analysis. The source reports ~50% reduced morning visitation after inner-anther removal and ~45% reduced afternoon visitation after outer-anther removal, compared with controls, under their observed time-of-day changes. The later ripe-fruit subset gave female **seeds per fruit** mean 34 (control), 28 (inner removed), 30 (outer removed): F(2,78)=0.43, p=.65. This is **not a test of male fitness**, proof that the male role is absent, or an equivalence test. Even if plant/flower ID keys permit combining these source tables, their analysis may need patch/date clustered inference rather than individual rows as independent replicates.

### 2017 field: anther-origin pollen fate in C. cylindrica

The two differently coloured pollen origins were observed on captured bee scopae and neighbouring stigmas. Original source reports no statistically detected difference in relative pollen source between the two destinations (t=−1.401, p=.17); this does not establish equal reproductive contribution or genetic siring. These observations are not the same flowers/experimental arrays as the 2017/2018 C. unguiculata manipulations.

### Across Clarkia species

Eleven species were time-lapse monitored for dehiscence; six classified heterantherous, five not. The source reports timing differences associated with heteranthery (phylogenetic ANOVA F=75.71, p=.002), but the phylogenetic analysis describes approximately **one origin with two losses**; this is not 11 independent evolutionary transitions or 11 replicated species-level causal adaptation tests.

## Original Dryad file availability and a reproducibility defect

The landing page includes the source-linked filenames:

| Purpose | Publicly listed file(s) | Eligibility |
|---|---|---|
| 2017 field visitor counts / female seeds | `CungManipulative.csv`, `CungSeeds.csv`, `FieldManipulationsCung.R` | candidate original-row analysis, only after validating flower/patch keys and author R model |
| 2018 greenhouse export | `BombusTrials2018.R`, `pollen_available.csv` | exposed-pollen data & analysis code, **but greenhouse exported stigma/corbicula raw table is not listed** |
| 2017 species pollen fate | `pollen_data.csv`, `cylindrica.R` | scopa/stigma pollen stage, not paternal siring |
| Dehiscence timing | `time_lapse_data.csv` | greenhouse timing, not visitor-order randomization |
| Greenhouse central raw input | **`BombusTrials2018.csv`** | The Dryad usage notes explicitly describe this file, but it is absent among the 29 names; **missing-input HOLD** pending confirmed retrieval or author clarification |

The exact public file_stream links returned **403** from web access here; the local container also could not reach the Dryad hostname. This is an **access blocker in the current environment**, not evidence that nobody can download the public data. The official Dryad API documents `/api/v2/files/{id}/download`. This PR creates a separate GitHub Actions source-access test that attempts official public API retrieval and reports exact statuses; it never asks for or fabricates credentials.

The code retrieves only the small listed file types (nine filenames; never 12.4 MB phylogeny), checks source format and SHA256, and emits **metadata only**: status, columns, rows, byte counts, hashes. Even if two CSVs are available, a matching `treatment` label or shared `patch` alone **does not license a row join**; join keys require confirming identity/row grain in the author R script. No raw data are committed, no paternity inference is produced, and the greenhouse missing-file gate remains closed regardless of availability of its R code.

If the download workflow reports `HTTP_401_DOWNLOAD_HOLD`, `HTTP_403_DOWNLOAD_HOLD`, or `DOWNLOAD_FAILED_HOLD`, the result is **no data obtained**. Green CI means the *fail-closed source audit worked*; it must never be described as a successful source-data reanalysis.

## Exact evidence boundary against the BALANCE q-threshold

The model-only PR #274 derived `q>1-b` from a closed-stock, fixed-fraction treatment-order model. Kay et al.'s original data cannot presently be used to fit that boundary because:

1. No recorded thief-before-legitimate versus legitimate-before-thief randomized visitation order;
2. Dosing and fully dehisced male flowers differed in age and exposed pollen, rather than independent manipulation of `b` and `q`;
3. Recipient stigma counts are a **pollen deposition endpoint**, not viable donor paternity;
4. A q-stratum (late versus early cohort realized male contribution) was not genetically assigned;
5. No optimized shared-versus-differentiated architecture cost `K` was identified.

**Strongest defensible synthesis:** original experimental research supports the biological relevance of gradual pollen presentation to pollinator attraction and pollen transport, but neither supports a new quantified BALANCE threshold nor shows ecological universality.

## Reproduce (source-only)

```bash
python scripts/audit_clarkia_kay2020_dryad.py
python scripts/audit_clarkia_kay2020_dryad.py --download --json-out /tmp/clarkia-source-access.json
pytest -q tests/test_clarkia_kay2020_dryad_source_access.py
```

The CI workflow `.github/workflows/audit-clarkia-kay2020-dryad.yml` triggers the public retrieval attempt in a network-enabled GitHub runner; the metadata-only artifact expires after 14 days. Review its statuses before making any claim about downloaded records. All BALANCE original V4 analyses, U6 blind coders, review admissions and manuscript files are unchanged.

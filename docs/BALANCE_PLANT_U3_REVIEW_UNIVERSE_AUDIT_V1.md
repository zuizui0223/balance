# BALANCE plant U3 heteranthery review universe v1

## Purpose

U3 adds a third literature family to the BALANCE plant programme using Vallejo-Marín et al. (2010), *Trait correlates and functional significance of heteranthery in flowering plants* (New Phytologist 188:418–425; DOI 10.1111/j.1469-8137.2010.03430.x).

Unlike U1 and U2, U3 is **not outcome-independent with respect to architecture**. The review intentionally identifies families containing heterantherous species.

Therefore U3 is registered only as a structural-division positive discovery surface and cannot be used as a prevalence denominator or as a direct confirmatory case sample without a separate comparator design.

## Exact review-defined family set

Figure 2 of the primary review contains exactly 16 heteranthery-positive families spanning 12 orders:

Pontederiaceae; Haemodoraceae; Commelinaceae; Tecophilaeaceae; Dilleniaceae; Lythraceae; Melastomataceae; Anacardiaceae; Malvaceae; Bixaceae; Brassicaceae; Fabaceae; Malpighiaceae; Lecythidaceae; Solanaceae; Scrophulariaceae.

The Figure-2 extraction matters because later reviews often mention Bignoniaceae as a heteranthery family, but Bignoniaceae is **not** one of the 16 families in the 2010 phylogenetic analysis. Scrophulariaceae is.

## Representative-taxon status

The accessible article body names representative genera/species for 11 families.

The Wiley page exposes the supporting-file identity (`NPH_3430_sm_TableS1.doc`) but the file itself is not retrievable through the current public access path. The repository therefore does **not** claim that Supporting Table S1 was inspected.

Two of the five previously pending families can nevertheless be resolved independently from pre-2010 primary literature plus the review's statement that each contributes a single reported heterantherous species:

```text
Lythraceae     Lagerstroemia indica
  Nepi, Guarnieri & Pacini 2003
  Plant Biology 5:311-314
  DOI 10.1055/s-2003-40797
  direct heteranthery: long reproductive stamens + short feed-pollen stamens

Brassicaceae   Brassica rapa
  Kudo 2003
  Functional Ecology 17:349-355
  DOI 10.1046/j.1365-2435.2003.00736.x
  direct manipulation of long vs short stamens with different pollination contributions
```

These rows are coded `SOURCE_RESOLVED_INDEPENDENTLY`, not `TABLE_S1_RESOLVED`.

Three families remain genuinely pending because the accessible evidence does not yet identify the exact 2010 representative without ambiguity:

```text
Malvaceae
Bixaceae
Scrophulariaceae
```

No species name is guessed for those three.

## Biological role in BALANCE

The review interprets heteranthery as a likely response to the conflict created when pollen is simultaneously male gamete and pollinator food. The 2009 Solanum rostratum experiment provides direct functional evidence that feeding anthers are preferentially manipulated while pollinating anthers export more pollen.

That makes U3 highly relevant as a **structural division-of-labour anchor**, but it also creates outcome-selection risk.

## Anti-bias rule

U3 rows all carry `analysis_role = POSITIVE_ARCHITECTURE_DISCOVERY_ONLY` and `matched_control_status = CONTROL_NOT_REGISTERED`.

They may not enter the primary binary architecture model until a separately registered comparator layer is built.

## Matched-control next gate

The next U3 design step is a within-family matched comparator protocol, not simply more heterantherous cases.

For each family case, a comparator must be selected by a rule fixed before predictor extraction, preferably a non-heterantherous close relative with comparable pollen-reward ecology. If congeneric matching is impossible, the widening rule must be explicit and versioned.

This creates a case-control estimand for correlates of structural pollen-function partitioning. It does not estimate the natural prevalence of heteranthery.

## Prior-art boundary

Vallejo-Marín et al. (2010) already showed family-level phylogenetic associations of heteranthery with poricidal anthers, absence/loss of nectaries and enantiostyly.

BALANCE must therefore not repackage those same correlates as its novelty. U3 is useful only if the later species-level matched analysis asks a distinct architecture-resolution question or serves as a structural-positive anchor inside the broader plant macro synthesis.

# BALANCE Q1B heterogeneity analysis contract v1

## Purpose

The first allowed Q1B pool contains three independent effect-size-ready positive clusters and shows component-specific heterogeneity. This contract freezes the next-stage moderator analysis **before** adding further positive clusters.

## Frozen moderators

Only the following study-level moderators may be examined in the first heterogeneity analysis:

1. antagonist type;
2. focal trait class;
3. reproductive fitness component;
4. pollination manipulation class;
5. effect-source class (reported-statistic reconstruction vs preregistered raw-data reanalysis).

No new moderator may be introduced after inspecting the k>=5 pooled residuals without a versioned secondary/exploratory analysis.

## Sample-size gate

At k=3, moderator information is descriptive only. No meta-regression, subgroup mean comparison, or moderator p-value is allowed.

At k=4, moderator information remains descriptive only.

At k>=5, a first exploratory moderator fit may be run only if at least two levels of the moderator contain >=2 independent biological clusters. With k<8, results remain exploratory and no absence-of-heterogeneity claim is allowed.

## Independence rule

The biological cluster, not the trait, treatment cell, population, site, or year, is the independent replication unit. Multiple traits from one cluster must not be counted as separate moderator observations.

## Q1B expansion gate

A fourth or fifth cluster enters the positive numerator only if it satisfies the existing Q1B effect-size-ready contract on a common reproductive-fitness estimand with identified joint uncertainty. Design-matched null/negative studies remain controls and do not enter the positive numerator.

## Current candidate adjudication

`Campbell et al. 2022 / Ipomopsis` is retained as a sequential-filter raw-data candidate, not automatically Q1B-compatible. It compares pollination-stage and seed-predation-stage selection, but does not by itself instantiate the same 2x2 factorial intervention estimand as Fragaria, Impatiens, and Gymnadenia. It may only enter Q1B after a versioned estimand-compatibility audit; otherwise it remains a separate sequential-filter stratum.

`Trifolium repens 2018` and `Lythrum salicaria 2017` remain design-matched negative controls under the frozen adjudication and must not be promoted solely to increase k.

## Claim ceiling

The Q1B pool concerns recurrence and context dependence of opposing agent-mediated selection on a shared coordinate. It does not identify direct BALANCE occupancy, optimized shared-versus-differentiated worldlines, or the theory parameters `rho`, `Phi`, `xi`, or `d_B`.

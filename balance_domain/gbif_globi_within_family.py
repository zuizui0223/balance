"""Post-open, within-family RECORD-DOCUMENTATION association for 48 plants.

Source: actual 2026-10-24 GBIF occurrence/search counts joined to the
2026-10-19 frozen GloBI exact-target-name documentation snapshot.  The
species panel was selected before GloBI inspection, but the statistic here
is exploratory/post-open after looking at descriptive group differences.

We condition on 4 selected species per convenience-chosen family and the
observed number of GloBI-documented species in each family, then enumerate
all relabelings of which species are documented. We ask how exceptional the
observed within-family *ranks* of GBIF observation counts are under artificial
within-family LABEL EXCHANGEABILITY. Labels WERE NOT RANDOMIZED: this
reference distribution must not be called a design-based ecological test,
a causal observation-effort effect, or global interaction-conflict prevalence.

GBIF indexed occurrence-search records are at most a correlated public
documentation/observability proxy (not verified field effort or abundance).
GloBI "undocumented" is NEVER ecological absence of interactions.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
from math import comb
from pathlib import Path

from .gbif_occurrence_effort import (
    source_effort_audit_from_files,
    READOUT as SOURCE_READOUT,
)

SCHEMA="BALANCE_GBIF_GLOBI_WITHIN_FAMILY_EFFORT_REFERENCE_V1"
MANIFEST="data/BALANCE_GBIF_OCCURRENCE_EFFORT_48_SOURCE_MANIFEST_V1.json"
SOURCES=("gbif_occurrence_search_count",
         "gbif_occurrence_search_has_coordinates_count")
EXPECTED_MIXED={
    "Brassicaceae":2,
    "Ericaceae":1,
    "Fabaceae":3,
    "Rosaceae":1,
    "Rubiaceae":1,
}
EXPECTED= {
    "n_species":48,
    "n_families":12,
    "n_GloBI_documented":16,
    "n_GloBI_undocumented":32,
    "n_mixed_families":5,
    "n_mixed_species":20,
    "mixed_independent_concordant_pairs":16,
    "mixed_discordant_pairs":0,
    "mixed_tied_pairs":0,
    "n_conditional_assignments":1536,
    "max_rank_sum":28,
    "expected_rank_sum":20,
    "upper_tail_count":1,
    "two_sided_tail_count":2,
}


def _nonnegative(value, label):
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be original nonnegative indexed count")
    return value


def _source_species(source: dict) -> dict[str,list[dict]]:
    if source.get("schema_version")!=SOURCE_READOUT or (
        source.get("status")!=
        "ACTUAL_OCCURRENCE_DOCUMENTATION_EFFORT_ASSOCIATION_NOT_FITNESS"
    ):
        raise ValueError("authenticated source audit status or version changed")
    if (source.get("source_GBIF_date")!="2026-10-24"
        or source.get("source_GloBI_date")!="2026-10-19"
        or source.get("n_species_first_selected")!=48):
        raise ValueError("original two-date species-first source panel changed")
    for key,expected in (
        ("GBIF_count_includes_indexed_occurrences_not_unique_effort_or_abundance",True),
        ("cross_date_and_taxonomic_index_limitations",True),
        ("source_taxa_not_globally_representative",True),
        ("GloBI_absence_is_not_ecological_interaction_absence",True),
        ("pollinator_antagonist_conflict_not_identified",True),
        ("fitness_impact_or_SCH_L_identified",False),
        ("net_structural_BALANCE_occupancy_identified",False),
        ("additional_independent_biological_clusters",0),
    ):
        actual=source.get(key)
        if type(expected) is bool:
            if actual is not expected:
                raise ValueError("source ecological evidence boundary changed: "+key)
        elif type(actual) is not int or actual!=expected:
            raise ValueError("source biological cluster counter changed")
    species=source.get("species")
    if not isinstance(species,list) or len(species)!=48:
        raise ValueError("all 48 original source taxa must be retained")
    groups=defaultdict(list)
    seen=set()
    for row in species:
        if not isinstance(row,dict):
            raise ValueError("original source species row invalid")
        key=row.get("gbif_species_key")
        if type(key) is not int or key in seen:
            raise ValueError("duplicated/missing original species GBIF key")
        seen.add(key)
        if not isinstance(row.get("species"),str) or not row["species"]:
            raise ValueError("source species taxon name missing")
        family=row.get("family")
        if not isinstance(family,str) or not family:
            raise ValueError("source family identity missing")
        if type(row.get("globi_name_recorded")) is not bool:
            raise ValueError("GloBI label must be source-verified boolean")
        if (row["globi_name_recorded"] !=
            (_nonnegative(row.get("globi_exact_target_name_relation_rows"),
                          "GloBI exact relation rows")>0)):
            raise ValueError("GloBI source label and row count inconsistent")
        for field in SOURCES:
            _nonnegative(row.get(field),field)
        if (row[SOURCES[1]]>row[SOURCES[0]]):
            raise ValueError("GBIF coordinate count exceeds indexed occurrence count")
        groups[family].append(row)
    if len(groups)!=12 or any(len(v)!=4 for v in groups.values()):
        raise ValueError("all twelve original four-species family strata required")
    if sum(row["globi_name_recorded"] for row in species)!=16:
        raise ValueError("original GloBI coverage group counts changed")
    return dict(sorted(groups.items()))


def _rank2_with_ties(members: list[dict], field:str)->dict[int,int]:
    """Twice the 1..4 ascending midrank; ties cannot be split arbitrarily."""
    ordered=sorted(members,key=lambda row:(row[field],row["gbif_species_key"]))
    ranks={}
    cursor=0
    while cursor<len(ordered):
        end=cursor
        while (end+1<len(ordered) and
               ordered[end+1][field]==ordered[cursor][field]):
            end+=1
        # Ranks cursor+1 through end+1, twice their mean.
        rank2=cursor+end+2
        for pos in range(cursor,end+1):
            ranks[ordered[pos]["gbif_species_key"]]=rank2
        cursor=end+1
    return ranks


def _reference_by_family(groups:dict[str,list[dict]],field:str)->dict:
    per_family=[]
    distributions=[(0,)]
    observed_rank2=0
    expected_rank2=0
    eligible=0
    concordant=discordant=tied=0
    all_concordant=True
    for family,members in groups.items():
        ranks=_rank2_with_ties(members,field)
        n_doc=sum(x["globi_name_recorded"] for x in members)
        doc=[r for r in members if r["globi_name_recorded"]]
        nondoc=[r for r in members if not r["globi_name_recorded"]]
        raw_pairs=[(a[field],b[field]) for a in doc for b in nondoc]
        cc=sum(a>b for a,b in raw_pairs)
        dd=sum(a<b for a,b in raw_pairs)
        tt=sum(a==b for a,b in raw_pairs)
        concordant+=cc
        discordant+=dd
        tied+=tt
        scores=[ranks[r["gbif_species_key"]] for r in members]
        observed=sum(ranks[r["gbif_species_key"]] for r in doc)
        # Expected doubled rank under fixed-m family label relabeling.
        expected2=n_doc * sum(scores)/len(members)
        if not expected2.is_integer():
            raise ValueError("source family midrank expectation is noninteger")
        expected2=int(expected2)
        # Report rank only within informative mixed-documentation families.
        if 0<n_doc<len(members):
            eligible+=1
            all_concordant=all_concordant and dd==tt==0
            observed_rank2+=observed
            expected_rank2+=expected2
            options=tuple(
                sum(scores[i] for i in idx)
                for idx in combinations(range(4),n_doc)
            )
            if len(options)!=comb(4,n_doc):
                raise ValueError("incorrect conditional family label count")
            distributions.append(options)
        else:
            options=(observed,)
        per_family.append({
            "family":family,
            "n_species":4,
            "n_name_documented":n_doc,
            "all_four_sampled_species_same_genus":(
                len({r["species"].split()[0] for r in members})==1
            ),
            "contributes_to_within_family_reference":0<n_doc<4,
            "documented_rank_sum":observed/2,
            "conditional_rank_sum_expectation":expected2/2,
            "pairwise_documented_higher":cc,
            "pairwise_documented_lower":dd,
            "pairwise_ties":tt,
            "n_possible_fixed_label_allocations":len(options),
            "documented_species":[r["species"] for r in doc],
            "undocumented_species":[r["species"] for r in nondoc],
        })
    # combinations over 5 independent FAMILY label permutations, holding
    # observed number of documented plants fixed *in each family*.
    options=[]
    for choices in product(*distributions):
        options.append(sum(choices))
    obs=observed_rank2
    center=expected_rank2
    high=sum(x>=obs for x in options)
    low=sum(x<=obs for x in options)
    two=sum(abs(x-center)>=abs(obs-center) for x in options)
    return {
        "GBIF_count_field":field,
        "statistic":"sum_twice_midrank_of_GloBI_documented_species_in_mixed_families",
        "within_family_ties_use_average_ranks":True,
        "n_informative_mixed_families":eligible,
        "n_species_in_informative_families":eligible*4,
        "n_distinct_documented_undocumented_family_pairs":
            concordant+discordant+tied,
        "n_pairs_documented_has_higher_GBIF_count":concordant,
        "n_pairs_documented_has_lower_GBIF_count":discordant,
        "n_pairs_tied_GBIF_count":tied,
        "all_informative_documented_vs_undocumented_pairs_higher":all_concordant,
        "observed_documented_rank_sum":obs/2,
        "conditional_exchangeability_expected_rank_sum":center/2,
        "conditional_reference_assignments":len(options),
        "upper_tail_assignments":high,
        "lower_tail_assignments":low,
        "two_sided_absolute_deviation_assignments":two,
        "conditional_one_sided_upper_reference_fraction":high/len(options),
        "conditional_two_sided_reference_fraction":two/len(options),
        "not_randomized_labels_or_confirmatory_p_value":True,
        "family_data":per_family,
    }


def analyze_effort_family_rank_reference(source:dict)->dict:
    groups=_source_species(source)
    primary=_reference_by_family(groups,SOURCES[0])
    sensitivity=_reference_by_family(groups,SOURCES[1])
    original=source["source_source_aggregate"]
    if original["n_families_with_both_GloBI_documented_and_not"]!=5 or (
        original["n_families_with_higher_documented_median_GBIF_occurrences"]!=5
    ):
        raise ValueError("source original within-family rank signal changed")
    for key,data in (
        ("occurrence_search_count",primary),
        ("occurrence_search_has_coordinates_count",sensitivity),
    ):
        facts={
            "n_species":source["n_species_first_selected"],
            "n_families":len(groups),
            "n_GloBI_documented":original["n_with_GloBI_exact_target_name"],
            "n_GloBI_undocumented":original["n_without_GloBI_exact_target_name"],
            "n_mixed_families":data["n_informative_mixed_families"],
            "n_mixed_species":data["n_species_in_informative_families"],
            "mixed_independent_concordant_pairs":
                data["n_pairs_documented_has_higher_GBIF_count"],
            "mixed_discordant_pairs":
                data["n_pairs_documented_has_lower_GBIF_count"],
            "mixed_tied_pairs":data["n_pairs_tied_GBIF_count"],
            "n_conditional_assignments":data["conditional_reference_assignments"],
            "max_rank_sum":data["observed_documented_rank_sum"],
            "expected_rank_sum":data["conditional_exchangeability_expected_rank_sum"],
            "upper_tail_count":data["upper_tail_assignments"],
            "two_sided_tail_count":data["two_sided_absolute_deviation_assignments"],
        }
        if facts!=EXPECTED:
            raise ValueError(
                f"original 48-species {key} conditional rank signal changed"
            )
        actual_mixed={r["family"]:r["n_name_documented"]
                      for r in data["family_data"]
                      if r["contributes_to_within_family_reference"]}
        if actual_mixed!=EXPECTED_MIXED:
            raise ValueError("original 5 mixed families/coverages changed")
    return {
        "schema_version":SCHEMA,
        "status":"POSTOPEN_PUBLIC_RECORD_DOCUMENTATION_BIAS_STRATIFIED_REFERENCE_NOT_CONFLICT",
        "GBIF_snapshot_date":"2026-10-24",
        "GloBI_snapshot_date":"2026-10-19",
        "original_48_species_source_manifest_sha256":
            source["effort_source_manifest_sha256"],
        "source_family_convenience_stratification_not_random_global_sample":True,
        "within_family_label_exchangeability_is_hypothetical_unverified":True,
        "primary_statistic_chosen_post_open_not_preregistered":True,
        "family_conditioning_on_observed_GloBI_documentation_count":True,
        "family_stratification_does_not_control_genus_phylogeny_or_gbif_taxonomic_bias":True,
        "all_original_source_species_retained":48,
        "primary_indexed_occurrence_counts":primary,
        "georeferenced_occurrence_counts_sensitivity":sensitivity,
        "GBIF_occurrences_are_public_indexed_records_not_effective_field_effort":True,
        "GloBI_records_are_source_documentation_not_all_biotic_interactions":True,
        "non_detected_GloBI_is_not_absence_of_real_interactions":True,
        "no_direct_floral_fitness_or_functional_conflict_studied":True,
        "structural_BALANCE_occupancy_identified":False,
        "additional_independent_biological_clusters":0,
        "ecological_claim_ceiling":(
            "within five documentation-mixed convenience families, high "
            "GBIF indexed occurrence ranks perfectly track exact target-name "
            "GloBI record status; conditional exchangeability reference is "
            "post-open descriptive, not a causal effort, phylogenetic or "
            "functional conflict result"
        ),
    }


def analyze_effort_family_rank_from_source(root:Path,manifest:Path)->dict:
    original=source_effort_audit_from_files(root,manifest)
    return analyze_effort_family_rank_reference(original)

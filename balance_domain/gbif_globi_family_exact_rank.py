"""Post-open family-conditional association in real GBIF/GloBI source coverage.

This is an EXTRACTION/REPORTING-BIAS finding, not a biological interaction
frequency, direct functional conflict L, or architecture value. The 48 GBIF
species were chosen independently of GloBI labels within 12 PRESELECTED family
strata (four taxa each); families themselves are a convenience selection.

For each family with 0 < k < 4 GloBI-recorded species, retain the k observed
documentation labels and consider all C(4,k) conditional placements of these
labels among the original GBIF occurrence-ranked taxa. Across the five mixed
families there are exactly 1,536 possible assignments. Our statistic is the
number of within-family documented-versus-undocumented species pairs in which
the documented species has more GBIF indexed occurrences (ties score 1/2).
This is an EXACT CONDITIONAL COMBINATORIAL REFERENCE UNDER AN UNVERIFIED
WITHIN-FAMILY EXCHANGEABILITY NULL, not a randomized-treatment p-value or
proof that observation effort causes documented interactions.

Sensitivity 1 uses georeferenced GBIF occurrence indices.
Sensitivity 2 switches from name-only GloBI to strict matching of GBIF
taxon-key identifiers (only TWO taxa). This dramatically shrinks source
coverage; a name-matched ecological association cannot be automatically
generalized to key-verified botanical concepts.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math

from .gbif_occurrence_effort import source_effort_audit_from_files, git_blob_sha1

SCHEMA="BALANCE_GBIF_GLOBI_FAMILY_CONDITIONAL_RANK_V1"
ORIGINAL_MANIFEST="data/BALANCE_GBIF_OCCURRENCE_EFFORT_48_SOURCE_MANIFEST_V1.json"
EXPECTED_GLOBI_COVERAGE="BALANCE_GBIF_GLOBI_SPECIES_FIRST_STATIC_COVERAGE_V1"
EXPECTED_N=48


def _strict_int(x,name):
    if type(x) is not int or x<0:
        raise ValueError(f"{name}: expected exact nonnegative original source count")
    return x


def _pair_wins_twice(items:list[dict], labels:set[int],measure:str) -> tuple[int,int]:
    """Use integer 2x-score: winner 2, tie 1, loser 0; no float ties."""
    total=0
    eligible=0
    for i in range(len(items)):
        for j in range(i+1,len(items)):
            if (i in labels)==(j in labels):
                continue
            yes=items[i] if i in labels else items[j]
            no=items[j] if i in labels else items[i]
            p=_strict_int(yes[measure],measure)
            q=_strict_int(no[measure],measure)
            total+=2 if p>q else 1 if p==q else 0
            eligible+=1
    return total,eligible


def exact_family_label_reference(
    observations:list[dict], *, label_field:str, measure_field:str,
)->dict:
    """Exact conditional rank association, keeping per-family GloBI k fixed.

    This is a post-open descriptive inferential reference, NOT an exchangeably
    randomized experiment. One species is a source-coverage unit, not a
    reproductive plant/flower experimental replicate.
    """
    if not isinstance(observations,list) or len(observations)!=EXPECTED_N:
        raise ValueError("frozen 48 species-first outcome-independent roster required")
    families=defaultdict(list)
    seen=set()
    for x in observations:
        if not isinstance(x,dict):
            raise ValueError("family observation must be a source-linked record")
        key=x.get("gbif_species_key")
        if type(key) is not int or key in seen:
            raise ValueError("GBIF accepted species taxon key missing/duplicated")
        seen.add(key)
        family=x.get("family")
        if not isinstance(family,str) or not family:
            raise ValueError("original botanical family missing")
        if type(x.get(label_field)) is not bool:
            raise ValueError("GloBI source-coverage label must be boolean, not fitness")
        _strict_int(x.get(measure_field),measure_field)
        families[family].append(x)
    if len(families)!=12 or any(len(v)!=4 for v in families.values()):
        raise ValueError("twelve selected 4-species family strata must be retained")
    active=[]
    family_rows=[]
    observed_score=0
    source_pairs=0
    possible_assignments=1
    for family,rr in sorted(families.items()):
        # Rank using descending occurrence count, with frozen accepted GBIF
        # species key as deterministic tie-break. Ties score half a concordance.
        ordered=sorted(rr,key=lambda z:(-z[measure_field],z["gbif_species_key"]))
        labels={i for i,x in enumerate(ordered) if x[label_field]}
        k=len(labels)
        if 0<k<4:
            score,npair=_pair_wins_twice(ordered,labels,measure_field)
            cases=[]
            for comb in combinations(range(4),k):
                s,nn=_pair_wins_twice(ordered,set(comb),measure_field)
                if nn!=npair:
                    raise ValueError("conditional reference sample pair dimension changed")
                cases.append(s)
            active.append(cases)
            observed_score+=score
            source_pairs+=npair
            possible_assignments*=math.comb(4,k)
            family_rows.append({
                "family":family,
                "n_source_species":4,
                "n_GloBI_label_documented":k,
                "GBIF_occurrence_count_per_rank_desc":[r[measure_field] for r in ordered],
                "documented_label_per_rank_desc":[r[label_field] for r in ordered],
                "source_taxon_key_per_rank_desc":[r["gbif_species_key"] for r in ordered],
                "n_eligible_documented_undocumented_pairs":npair,
                "observed_concordant_pair_score_twice":score,
                "all_GloBI_documented_species_above_undocumented_by_index":score==2*npair,
                "conditional_label_placements":len(cases),
            })
    # Families with k=0 or k=4 contribute ZERO rank evidence but still
    # belong to the exact 48-species denominator and remain in the audit.
    histogram=Counter()
    if active:
        for arrangement in product(*active):
            histogram[sum(arrangement)]+=1
    else:
        histogram[0]=1
    if sum(histogram.values())!=possible_assignments:
        raise ValueError("finite conditional GloBI-label permutation support incomplete")
    right=sum(n for t,n in histogram.items() if t>=observed_score)
    left=sum(n for t,n in histogram.items() if t<=observed_score)
    p_upper=right/possible_assignments
    p_lower=left/possible_assignments
    return {
        "status":"POSTOPEN_CONDITIONAL_ASSOCIATION_NULL_NOT_RANDOMIZED_EXPERIMENT",
        "source_GloBI_label_definition":label_field,
        "source_GBIF_occurrence_measure":measure_field,
        "n_families_source_roster":len(families),
        "n_informative_mixed_documentation_families":len(active),
        "n_species_source_roster":len(observations),
        "n_documented_species_source_roster":sum(x[label_field] for x in observations),
        "family_detail_mixed_only":family_rows,
        "n_within_family_documented_undocumented_pairs":source_pairs,
        "observed_concordant_pairs_equivalent":observed_score/2,
        "max_concordant_pairs_equivalent":source_pairs,
        "exact_conditional_label_assignments":possible_assignments,
        "right_tail_arrangement_count":right,
        "left_tail_arrangement_count":left,
        "right_tail_conditional_p":p_upper,
        "two_sided_doubled_tail_conditional_p":min(1.0,2*min(p_upper,p_lower)),
        "all_informative_families_perfectly_rank_separated":bool(active) and all(
            r["all_GloBI_documented_species_above_undocumented_by_index"]
            for r in family_rows
        ),
        "source_selected_families_not_exchangeable_beyond_frame":True,
        "within_family_source_label_exchangeability_not_verified":True,
        "post_open_exploratory_statistic_not_confirmatory":True,
        "no_causal_documentation_impact_identified":True,
        "no_true_biological_noninteraction_identified":True,
        "no_SHC_fitness_or_structural_BALANCE_identified":True,
    }


def real_source_rank_audit(root:Path) -> dict:
    """Start with exact-hash authenticated 96 GBIF occurrence API responses."""
    manifest=root/ORIGINAL_MANIFEST
    full=source_effort_audit_from_files(root,manifest)
    if (full.get("status")!="ACTUAL_OCCURRENCE_DOCUMENTATION_EFFORT_ASSOCIATION_NOT_FITNESS"
            or full.get("n_species_first_selected")!=48):
        raise ValueError("original 48-species GBIF effort audit is not source-qualified")
    source_manifest=json.loads(manifest.read_text(encoding="utf-8"))
    coverage_path=root/source_manifest["original_GloBI_static_coverage_path"]
    original=coverage_path.read_bytes()
    if git_blob_sha1(original)!=source_manifest["original_GloBI_static_coverage_git_blob_sha1"]:
        raise ValueError("original immutable GloBI species coverage source has changed")
    summary=json.loads(original)
    if summary.get("schema_version")!=EXPECTED_GLOBI_COVERAGE:
        raise ValueError("original GloBI selected-name source coverage schema changed")
    keys={r["gbif_species_key"]:r for r in summary["species"]}
    src=full["species"]
    if len(keys)!=48 or len(src)!=48:
        raise ValueError("original 48 species name and identifier records required")
    enriched=[]
    for r in src:
        gid=r["gbif_species_key"]
        match=keys[gid]
        if bool(match["exact_GloBI_target_name_rows"]>0)!=r["globi_name_recorded"]:
            raise ValueError("name-only GloBI original cover label changed")
        id_rows=_strict_int(match.get("matching_GBIF_species_key_rows"),"GloBI matched GBIF-key records")
        if id_rows>match["exact_GloBI_target_name_rows"]:
            raise ValueError("source taxon key match cannot exceed GloBI target-name rows")
        enriched.append({
            "gbif_species_key":gid,
            "species":r["species"],
            "family":r["family"],
            "gbif_occurrence_search_count":r["gbif_occurrence_search_count"],
            "gbif_occurrence_search_has_coordinates_count":
                r["gbif_occurrence_search_has_coordinates_count"],
            "name_documented":r["globi_name_recorded"],
            "GBIF_key_documented":id_rows>0,
            "GloBI_direct_key_matched_rows":id_rows,
        })
    if sum(x["GBIF_key_documented"] for x in enriched)!=2:
        raise ValueError("only two original source taxa were directly GBIF-key matched")
    checks={
        "name_exact_all_occurrence":exact_family_label_reference(
            enriched,label_field="name_documented",
            measure_field="gbif_occurrence_search_count"),
        "name_exact_georeferenced":exact_family_label_reference(
            enriched,label_field="name_documented",
            measure_field="gbif_occurrence_search_has_coordinates_count"),
        "direct_GBIF_key_all_occurrence":exact_family_label_reference(
            enriched,label_field="GBIF_key_documented",
            measure_field="gbif_occurrence_search_count"),
    }
    a=checks["name_exact_all_occurrence"]
    b=checks["name_exact_georeferenced"]
    if not (
        a["n_informative_mixed_documentation_families"]==5
        and a["n_within_family_documented_undocumented_pairs"]==16
        and a["observed_concordant_pairs_equivalent"]==16
        and a["exact_conditional_label_assignments"]==1536
        and a["right_tail_arrangement_count"]==1
        and b["observed_concordant_pairs_equivalent"]==16
        and b["right_tail_arrangement_count"]==1
    ):
        raise ValueError("source family-conditioned matched association outcome changed")
    strict=checks["direct_GBIF_key_all_occurrence"]
    if strict["n_documented_species_source_roster"]!=2:
        raise ValueError("direct identifier validated source support changed")
    return {
        "schema_version":SCHEMA,
        "status":"SOURCE_VERIFIED_POSTOPEN_FAMILY_CONDITIONAL_REPORTING_BIAS_ASSOCIATION",
        "GBIF_snapshot_date":"2026-10-24",
        "GloBI_snapshot_date":"2026-10-19",
        "n_species":48,
        "n_family_strata":12,
        "source_taxonomic_sampling":"twelve deliberately chosen angiosperm families, four GBIF species each, preselected without GloBI outcome",
        "source_manifests_sha256":{
            "original_GBIF_effort_manifest":hashlib.sha256(manifest.read_bytes()).hexdigest(),
            "original_GloBI_selected_coverage":hashlib.sha256(original).hexdigest(),
        },
        "n_GloBI_name_documented":16,
        "n_GloBI_direct_GBIF_key_documented":2,
        "family_conditional_source_analyses":checks,
        "primary_qualifier":"conditional exact association reference under exchangeable within-family GloBI documentation labels; post-open, not causal",
        "name_vs_key_support_is_severely_different":True,
        "family_ranks_do_not_control_species_abundance_or_taxonomic_genus":True,
        "index_counts_not_number_of_independent_field_observation_events":True,
        "never_treat_no_GloBI_rows_as_no_biological_interactions":True,
        "actual_pollinator_or_antagonist_fitness_not_measured":True,
        "new_independent_flora_selection_transition_or_BALANCE_worldline":False,
        "additional_independent_biological_clusters":0,
    }

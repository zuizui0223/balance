"""Source-verified species-first GBIF → GloBI *opportunity* coverage audit.

Read original publicly acquired GBIF taxonomy JSON and GloBI CSV bytes;
validate full selected-species sampling denominator and original source SHA256.

This does NOT establish same-trait antagonistic selection, pollination success,
loss of an ecological guild, natural frequency of any plant interaction, or
the BALANCE net structural accessible alternative.
"""
from __future__ import annotations

from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

SCHEMA="BALANCE_GBIF_GLOBI_SPECIES_FIRST_COVERAGE_V1"
GBIF_SCHEMA="BALANCE_GBIF_SPECIES_FIRST_SELECTED_V1"
GLOBI_SCHEMA="BALANCE_GBIF_GLOBI_SPECIES_FIRST_OPPORTUNITY_V1"
FLORAL_INTERACTION_LABELS=("pollinates","visitsFlowersOf","flowersVisitedBy")
GLOBI_EXPECTED_COUNT=188
SELECTED_SPECIES_EXPECTED=48
SELECTED_WITH_ANY_EXPECTED=16
DIRECT_ID_MATCH_EXPECTED=88
GLIBI_SOURCE_TEXT_HOLDS_EXPECTED=0


def _sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def _json_bytes(b:bytes,label:str)->dict:
    try:
        return json.loads(b)
    except (ValueError,UnicodeDecodeError) as exc:
        raise ValueError(f"{label} source JSON invalid") from exc


def _parse_csv(b:bytes)->list[dict]:
    try:
        text=b.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("GloBI original text not UTF-8") from exc
    reader=csv.DictReader(io.StringIO(text))
    needed={"source_taxon_name","source_taxon_external_id",
            "interaction_type","target_taxon_name","target_taxon_external_id"}
    if not needed.issubset(reader.fieldnames or []):
        raise ValueError("GloBI original source columns missing")
    rows=list(reader)
    if any(None in r or not r["interaction_type"] for r in rows):
        raise ValueError("GloBI original source relation row malformed")
    return rows


def audit_real_species_first_coverage(
    sampling_contract:dict, species:dict, network:dict,
    original_files:dict[str,bytes],
) -> dict:
    """Revalidate the 12 GBIF taxonomy pages + 48 GloBI response files."""
    if sampling_contract.get("schema_version")!="BALANCE_GBIF_SPECIES_FIRST_CROSS_ORDER_PANEL_V1":
        raise ValueError("species-first family frame missing")
    if species.get("schema_version")!=GBIF_SCHEMA or network.get("schema_version")!=GLOBI_SCHEMA:
        raise ValueError("original taxonomy and opportunity manifest mismatch")
    if (species["n_species_selected"]!=SELECTED_SPECIES_EXPECTED
        or species["n_family_strata"]!=12 or
        species["n_families_with_complete_quota"]!=12 or
        network["n_queries_completed"]!=48 or network["n_GloBI_fetch_holds"]!=0
        or len(network["per_species"])!=48):
        raise ValueError("GBIF/GloBI original species-first sample incomplete")
    if sampling_contract.get("species_selection_independent_of_GloBI_interaction_records") is not True:
        raise ValueError("sampling not recorded as blind to interaction outcomes")
    if (species.get("selection_rule_frozen_before_GloBI_interactions") is not True
        or network.get("study_frame_selected_without_examining_GloBI_data") is not True):
        raise ValueError("source-first selection independence claim missing")
    if network.get("no_direct_plant_fitness_selection_result") is not True:
        raise ValueError("GloBI relations cannot become plant fitness conflict evidence")
    if network.get("strict_structural_BALANCE_occupancy_identified") is not False:
        raise ValueError("GloBI cannot be relabelled strict structural BALANCE")
    if network.get("n_gbif_taxa_selected")!=len(species["species"]):
        raise ValueError("selected versus source GloBI denominator drift")
    expected_frame_hash=hashlib.sha256(json.dumps(
        sampling_contract,sort_keys=True
    ).encode()).hexdigest()
    if species.get("frame_sha256")!=expected_frame_hash:
        raise ValueError("GBIF pre-interaction selection contract digest mismatch")
    by_key={x["gbif_species_key"]:x for x in species["species"]}
    if len(by_key)!=48:
        raise ValueError("GBIF selected keys not unique")
    by_retrieval={r["GBIF_species_key"]:r for r in network["per_species"]}
    if len(by_retrieval)!=48 or set(by_key)!=set(by_retrieval):
        raise ValueError("complete original species denominator not retained")
    expected_files={
        f["source_snapshot_path"] for f in species["family_counts"]
    }|{r["source_path"] for r in network["per_species"]}
    if set(original_files)!=expected_files:
        raise ValueError("12+48 authenticated original public files required")
    for f in species["family_counts"]:
        if f["status"]!="SELECTED_FIXED_WINDOW":
            raise ValueError("source family incomplete; cannot claim 48 completed")
        raw=original_files[f["source_snapshot_path"]]
        original=_json_bytes(raw,"original GBIF")
        if (original.get("count") != next(
            x["accepted_species_search_count_at_freeze"]
            for x in sampling_contract["family_strata"]
            if x["family"]==f["family"]
        ) or str(original.get("offset"))!=f["query_url"].split("offset=")[-1]):
            raise ValueError("GBIF original family page source altered")
        if original.get("limit")!=20 or len(original.get("results",[]))!=20:
            raise ValueError("GBIF page size unexpectedly changed")

        family=f["family"]
        source_candidates=[]
        for item in original["results"]:
            canonical=item.get("canonicalName")
            parts=canonical.split(" ") if isinstance(canonical,str) else []
            eligible=(
                item.get("taxonomicStatus")=="ACCEPTED" and
                item.get("rank")=="SPECIES" and
                item.get("nameType")=="SCIENTIFIC" and
                item.get("kingdom")=="Plantae" and
                item.get("family")==family and
                item.get("familyKey")==f["gbif_family_key"] and
                item.get("synonym") is False and
                item.get("extinct") is not True and
                type(item.get("key")) is int and
                item.get("speciesKey")==item["key"] and
                len(parts)==2 and parts[0].isalpha() and
                parts[0][0].isupper() and parts[0][1:].islower() and
                parts[1].isalpha() and parts[1].islower()
            )
            if eligible:
                source_candidates.append(item)
        seed=sampling_contract["deterministic_seed"]
        ranked=sorted(source_candidates,key=lambda x:hashlib.sha256(
            f"{seed}:SPECIES:{family}:{x['key']}".encode("ascii")
        ).hexdigest())
        expected=ranked[:4]
        actual=[x for x in species["species"] if x["family"]==family]
        if len(actual)!=4 or f["selected_species"]!=4:
            raise ValueError("GBIF species quota/source sample changed")
        for original_item,derived in zip(expected,actual):
            if (original_item["key"]!=derived["gbif_species_key"] or
                original_item["canonicalName"]!=derived["canonical_name"] or
                derived.get("authorship")!=original_item.get("authorship")):
                raise ValueError("species selection differs from original GBIF source page SHA256 ranking")
        # Source hash is computed from genuine original HTTP response bytes;
        # not TinyFish or markdown text extracted from JSON.
        if not isinstance(raw,bytes) or not raw:
            raise ValueError("GBIF taxonomy original source bytes unavailable")
    total_type_counts=Counter()
    family_table=defaultdict(lambda:{
        "n_species":0,"n_with_exact_GloBI_target_name":0,
        "n_with_direct_GBIF_key_link":0,
        "exact_name_GloBI_relation_rows":0,
        "same_GBIF_key_relation_rows":0,
        "other_or_unresolved_identifier_relation_rows":0,
        "floral_visitation_or_pollination_label_rows":0,
    })
    per_species=[]
    all_direct=0
    name_matched=0
    target_mismatch=0
    observed_species=0
    direct_species=0
    for gbif_key,sample in sorted(by_key.items()):
        r=by_retrieval[gbif_key]
        if (r["GBIF_canonical_name"]!=sample["canonical_name"]
            or r["family"]!=sample["family"]
            or r["retrieval_status"]=="GLOBI_SOURCE_HOLD"):
            raise ValueError("GBIF–GloBI sampled name, family or retrieval status drift")
        raw=original_files[r["source_path"]]
        if _sha(raw)!=r["original_source_sha256"]:
            raise ValueError("GloBI source original byte digest altered")
        relations=_parse_csv(raw)
        exact=[x for x in relations if x["target_taxon_name"]==sample["canonical_name"]]
        if (len(relations)!=r["original_relation_rows"] or
            len(exact)!=r["exact_target_name_rows"] or
            len(relations)-len(exact)!=r["other_target_name_rows"]):
            raise ValueError("GloBI exact source target counts diverged from original")
        direct=[x for x in exact if x["target_taxon_external_id"]==f"GBIF:{gbif_key}"]
        conflicting=[x for x in exact if (
            (x["target_taxon_external_id"] or "").startswith("GBIF:") and
            x["target_taxon_external_id"]!=f"GBIF:{gbif_key}"
        )]
        if conflicting:
            raise ValueError("literal target-name matched another explicit GBIF species key")
        literal=Counter(x["interaction_type"] for x in exact)
        if dict(sorted(literal.items()))!=r["exact_target_relation_counts"]:
            raise ValueError("source interaction categories changed")
        labeled=sum(literal.get(x,0) for x in FLORAL_INTERACTION_LABELS)
        fam=family_table[sample["family"]]
        fam["n_species"]+=1
        fam["n_with_exact_GloBI_target_name"]+=bool(exact)
        fam["n_with_direct_GBIF_key_link"]+=bool(direct)
        fam["exact_name_GloBI_relation_rows"]+=len(exact)
        fam["same_GBIF_key_relation_rows"]+=len(direct)
        fam["other_or_unresolved_identifier_relation_rows"]+=len(exact)-len(direct)
        fam["floral_visitation_or_pollination_label_rows"]+=labeled
        total_type_counts.update(literal)
        observed_species+=bool(exact)
        direct_species+=bool(direct)
        name_matched+=len(exact)
        all_direct+=len(direct)
        target_mismatch+=len(relations)-len(exact)
        per_species.append({
            "gbif_species_key":gbif_key,
            "gbif_accepted_species_name":sample["canonical_name"],
            "family":sample["family"],
            "GBIF_search_numOccurrences_field":sample.get("GBIF_numOccurrences_field"),
            "original_GloBI_rows":len(relations),
            "GloBI_exact_target_name_rows":len(exact),
            "GloBI_direct_identical_GBIF_key_rows":len(direct),
            "GloBI_name_only_other_identifier_rows":len(exact)-len(direct),
            "GloBI_other_taxon_target_rows":len(relations)-len(exact),
            "literal_flower_visit_or_pollinate_rows":labeled,
            "verbatim_exact_target_relation_types":dict(sorted(literal.items())),
            "actual_independent_pollinator_visit_success_measured":False,
            "absence_of_ecological_interaction_measured":False,
            "direct_fitness_conflict_measured":False,
        })
    if name_matched!=GLOBI_EXPECTED_COUNT or observed_species!=SELECTED_WITH_ANY_EXPECTED:
        raise ValueError("archived public GloBI source relationship coverage drift")
    if all_direct!=DIRECT_ID_MATCH_EXPECTED or direct_species!=2:
        raise ValueError("source author-qualified GBIF key identity distribution drift")
    if total_type_counts.get("pollinates",0)!=0 or total_type_counts.get("visitsFlowersOf",0)!=2:
        raise ValueError("actual original floral interaction text label coverage changed")
    if name_matched!=sum(r["exact_target_name_rows"] for r in network["per_species"]):
        raise ValueError("GloBI original result source/summary mismatch")
    concentration=max(x["GloBI_exact_target_name_rows"] for x in per_species)
    return {
        "schema_version":SCHEMA,
        "status":"REAL_PUBLIC_SPECIES_FIRST_INTERACTION_COVERAGE_NOT_BIOLOGICAL_CONFLICT",
        "n_gbif_accepted_taxa_selected":48,
        "n_families_12_distinct_orders":12,
        "n_GloBI_queries_succeeded":48,
        "n_species_with_exact_target_name_relation":observed_species,
        "n_species_without_exact_target_name_relation":48-observed_species,
        "n_families_without_any_exact_target_name_relation":sum(
            x["n_with_exact_GloBI_target_name"]==0 for x in family_table.values()
        ),
        "n_GloBI_original_relation_rows":name_matched+target_mismatch,
        "n_exact_target_name_rows":name_matched,
        "n_target_taxon_mismatch_rows":target_mismatch,
        "n_exact_target_and_direct_GBIF_key_rows":all_direct,
        "n_exact_target_but_non_GBIF_identifier_rows":name_matched-all_direct,
        "n_taxa_with_direct_GBIF_species_key":direct_species,
        "largest_single_species_relation_rows":concentration,
        "largest_single_species_share_of_exact_rows":round(concentration/name_matched,6),
        "by_original_GloBI_relation_type":dict(sorted(total_type_counts.items())),
        "flower_visitation_or_pollination_literal_record_rows":sum(
            total_type_counts.get(k,0) for k in FLORAL_INTERACTION_LABELS
        ),
        "n_taxa_with_flower_visit_or_pollinate_label":sum(
            x["literal_flower_visit_or_pollinate_rows"]>0 for x in per_species
        ),
        "family_coverage":dict(sorted(family_table.items())),
        "species_coverage":per_species,
        "author_level_taxon_link_verified_from_GloBI":False,
        "GBIF_search_numOccurrences_field_independently_confirms_zero_occurrences":False,
        "missing_GloBI_record_means_ecological_absence":False,
        "index_target_guild_richness_estimable_from_broad_taxon_rows":False,
        "pollinator_guild_competition_measured":False,
        "opposing_trait_fitness_gradient_identified":False,
        "interaction_data_unbiased_across_species_or_families":False,
        "species_first_sampled_families_globally_representative":False,
        "strict_structural_BALANCE_occupancy_identified":False,
        "additional_independent_biological_clusters":0,
    }


def audit_source_files(root:Path)->dict:
    frame=json.loads((root/"data/BALANCE_GBIF_SPECIES_FIRST_CROSS_ORDER_PANEL_V1.json").read_text())
    selected=json.loads((root/"data/BALANCE_GBIF_SPECIES_FIRST_SELECTED_V1.json").read_text())
    network=json.loads((root/"data/BALANCE_GBIF_GLOBI_SPECIES_FIRST_READOUT_V1.json").read_text())
    names={x["source_snapshot_path"] for x in selected["family_counts"]}|{
        x["source_path"] for x in network["per_species"]
    }
    return audit_real_species_first_coverage(
        frame,selected,network,
        {name:(root/name).read_bytes() for name in names},
    )

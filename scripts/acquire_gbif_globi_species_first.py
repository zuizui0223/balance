#!/usr/bin/env python3
"""Retrieve a predeclared 12-order GBIF species panel and GloBI opportunities.

This is a REAL PUBLIC TAXONOMY/ASSOCIATION DATA pipeline, but it never treats
a GloBI relation as experimentally demonstrated floral fitness conflict.

Sampling frame and SHA256-ranking rules were committed before consulting
interactions on the sampled species. Family selection is a CONVENIENCE
cross-order panel, not a representative sample of all flowering plants.

No replacement of taxa after discovering few/no interactions. Request failures
and source taxon mismatch are reported, NEVER silently coded ecological zero.
"""
from __future__ import annotations

from collections import Counter
import argparse
import csv
import hashlib
import io
import json
import random
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

SCHEMA = "BALANCE_GBIF_SPECIES_FIRST_CROSS_ORDER_PANEL_V1"
SPECIES_SCHEMA = "BALANCE_GBIF_SPECIES_FIRST_SELECTED_V1"
NETWORK_SCHEMA = "BALANCE_GBIF_GLOBI_SPECIES_FIRST_OPPORTUNITY_V1"
MAX_GBIF_BYTES = 1_500_000
MAX_GLOBI_BYTES = 2_000_000
TIMEOUT_SECONDS = 16
EXPECTED_FAMILIES = 12
GLOBI_LIMIT = 500
GLOBI_RELATIONS = {
    "pollinates", "visitsFlowersOf", "flowersVisitedBy",
    "visits", "eats", "preysOn", "hasHost", "parasiteOf",
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _page_offset(seed: str, fam: str, key: int, count: int, size: int) -> int:
    if count < size:
        raise ValueError("family population smaller than fixed page")
    h = hashlib.sha256(f"{seed}:PAGE:{fam}:{key}".encode("ascii")).digest()
    return size * (int.from_bytes(h[:8], "big") % (count // size))


def _species_score(seed: str, family: str, key: int) -> str:
    return _sha256(f"{seed}:SPECIES:{family}:{key}".encode("ascii"))


def _read_https(url: str, limit: int, attempts: int = 2) -> bytes:
    if not (url.startswith("https://api.gbif.org/v1/") or
            url.startswith("https://api.globalbioticinteractions.org/interaction.csv?")):
        raise ValueError("remote biological source outside approved API domains")
    last = None
    for i in range(attempts):
        try:
            request = Request(url, headers={
                "Accept": "application/json,text/csv,text/plain,*/*",
                "User-Agent": "balance-species-first-sampling/1.0 (public data audit)",
            })
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                if response.headers.get("Content-Length") and int(
                    response.headers["Content-Length"]
                ) > limit:
                    raise ValueError("public source response exceeds bounded size")
                data = response.read(limit + 1)
            if len(data) > limit:
                raise ValueError("public source response exceeded safe limit")
            return data
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            last = f"{type(exc).__name__}: {exc}"
            if i + 1 < attempts:
                time.sleep(.35)
    raise ValueError(f"public source unavailable ({last})")


def select_species(frame: dict[str, Any], fetch=_read_https) -> tuple[dict, dict]:
    """Unbiased with respect to interaction *outcomes* within fixed families."""
    if frame.get("schema_version") != SCHEMA or not (
        frame.get("status") ==
        "FAMILY_STRATUM_AND_SAMPLING_RULE_FROZEN_BEFORE_SELECTED_GLOBI_LOOKUPS"
    ):
        raise ValueError("GBIF species-first pre-interaction contract missing")
    seed = frame["deterministic_seed"]
    if seed != "BALANCE_GBIF_20261019_MACRO_PILOT_SEED_V1":
        raise ValueError("taxon lottery seed differs from preregistered contract")
    fams = frame["family_strata"]
    if len(fams) != EXPECTED_FAMILIES or len({
        f["gbif_family_key"] for f in fams
    }) != EXPECTED_FAMILIES:
        raise ValueError("family/phylogenetic sampling frame incomplete")
    if frame.get("family_frame_is_random_sample_of_all_angiosperm_families") is not False:
        raise ValueError("this is NOT a representative global flora family sample")
    if frame.get("species_selection_independent_of_GloBI_interaction_records") is not True:
        raise ValueError("interactions cannot affect species selection")
    selected = []
    provenance = {}
    summaries = []
    for f in fams:
        family = f["family"]
        key = f["gbif_family_key"]
        expected = f["accepted_species_search_count_at_freeze"]
        size = frame["page_size"]
        offset = f["fixed_offset"]
        if _page_offset(seed, family, key, expected, size) != offset:
            raise ValueError(f"{family} source GBIF sampling offset drift")
        url = f["page_url"]
        expected_url = (f"https://api.gbif.org/v1/species/search?"
                        f"rank=SPECIES&status=ACCEPTED&higherTaxonKey={key}"
                        f"&limit={size}&offset={offset}")
        if url != expected_url:
            raise ValueError(f"{family} GBIF original URL changed")
        path = f"data/external/gbif/2026-10-19/species_first_{family}.json"
        result = {
            "family": family, "gbif_family_key": key, "order": f["order"],
            "query_url": url, "source_snapshot_path": path,
            "eligible_candidates_in_fixed_page": None,
            "selected_species": 0, "n_page_rows": None,
            "status": "GBIF_TAXONOMY_HOLD", "failure": None,
        }
        try:
            raw = fetch(url, MAX_GBIF_BYTES)
            parsed = json.loads(raw)
            if (parsed.get("offset") != offset or parsed.get("limit") != size
                    or parsed.get("count") != expected
                    or len(parsed.get("results", [])) != size):
                raise ValueError("GBIF taxonomy version/count/window drifted")
            provenance[path] = raw
            candidates = []
            for x in parsed["results"]:
                name = x.get("canonicalName")
                if not (isinstance(name, str) and
                        x.get("taxonomicStatus") == "ACCEPTED"
                        and x.get("rank") == "SPECIES"
                        and x.get("nameType") == "SCIENTIFIC"
                        and x.get("kingdom") == "Plantae"
                        and x.get("family") == family
                        and x.get("familyKey") == key
                        and x.get("synonym") is False
                        and x.get("extinct") is not True
                        and isinstance(x.get("key"), int)
                        and x.get("speciesKey") == x["key"]
                        and _is_plain_binomial(name)):
                    continue
                candidates.append(x)
            ranked = sorted(candidates, key=lambda x: _species_score(
                seed, family, x["key"]
            ))
            for x in ranked[:f["species_quota"]]:
                selected.append({
                    "family": family,
                    "order": x.get("order"),
                    "gbif_family_key": key,
                    "gbif_species_key": x["key"],
                    "canonical_name": x["canonicalName"],
                    "scientific_name_with_authorship": x.get("scientificName"),
                    "authorship": x.get("authorship"),
                    "GBIF_numOccurrences_field": x.get("numOccurrences"),
                    "GBIF_extinct_field": (
                        "NOT_REPORTED" if "extinct" not in x else "FALSE"
                    ),
                    "source_page_path": path,
                    "score_sha256": _species_score(seed, family, x["key"]),
                })
            result["eligible_candidates_in_fixed_page"] = len(candidates)
            result["n_page_rows"] = len(parsed["results"])
            result["selected_species"] = min(len(ranked),f["species_quota"])
            result["status"] = (
                "SELECTED_FIXED_WINDOW" if len(ranked)>=f["species_quota"]
                else "GBIF_SPECIES_SHORTFALL_NO_REPLACEMENT"
            )
        except (ValueError, OSError, KeyError, TypeError) as exc:
            result["failure"] = f"{type(exc).__name__}: {str(exc)[:150]}"
        summaries.append(result)
    if len({x["gbif_species_key"] for x in selected}) != len(selected):
        raise ValueError("duplicate original GBIF taxon key in selection")
    readout = {
        "schema_version": SPECIES_SCHEMA,
        "status": "TAXONOMY_SELECTED_WITH_EXPLICIT_SOURCE_HOLDS",
        "selection_rule_frozen_before_GloBI_interactions": True,
        "frame_sha256": _sha256(json.dumps(frame,sort_keys=True).encode()),
        "seed": seed, "family_counts": summaries,
        "n_family_strata": len(fams),
        "n_families_with_complete_quota": sum(
            x["status"]=="SELECTED_FIXED_WINDOW" for x in summaries),
        "n_species_planned": sum(x["species_quota"] for x in fams),
        "n_species_selected": len(selected),
        "species": selected,
        "taxon_selection_independent_of_interaction_availability": True,
        "unselected_family_shortfall_never_filled_from_GloBI": True,
        "nonrepresentative_fixed_family_set": True,
        "no_multiplex_conflict_identified": True,
        "strict_structural_BALANCE_identified": False,
    }
    return readout,provenance


def _is_plain_binomial(name: str) -> bool:
    parts = name.split(" ")
    return len(parts)==2 and parts[0].isalpha() and (
        parts[0][0].isupper() and parts[0][1:].islower()
    ) and parts[1].isalpha() and parts[1].islower()


def retrieve_globi(selected: dict, fetch=_read_https) -> tuple[dict,dict]:
    """Every selected species generates one GloBI query or a FETCH_HOLD."""
    if selected.get("schema_version") != SPECIES_SCHEMA or (
        selected.get("selection_rule_frozen_before_GloBI_interactions") is not True
    ):
        raise ValueError("source species frame not separately frozen")
    raw_files = {}
    rows = []
    for species in selected["species"]:
        name = species["canonical_name"]
        key = species["gbif_species_key"]
        url = ("https://api.globalbioticinteractions.org/interaction.csv?"
               f"targetTaxon={quote(name)}&limit={GLOBI_LIMIT}")
        path = f"data/external/globi/2026-10-19/species_first_{key}.csv"
        item = {
            "GBIF_species_key":key,"GBIF_canonical_name":name,
            "family":species["family"],"query_url":url,"source_path":path,
            "retrieval_status":"GLOBI_SOURCE_HOLD",
            "original_relation_rows":None,
            "exact_target_name_rows":None,
            "other_target_name_rows":None,
            "exact_target_relation_counts":{},
            "original_source_sha256":None,
            "source_target_author_match_verified":False,
            "biotic_interaction_absence_identified":False,
            "functional_fitness_tradeoff_identified":False,
            "retrieval_problem":None,
        }
        try:
            raw = fetch(url, MAX_GLOBI_BYTES)
            text = raw.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            if not {"source_taxon_name","target_taxon_name",
                    "target_taxon_external_id","interaction_type"}.issubset(
                        reader.fieldnames or []
                    ):
                raise ValueError("GloBI interaction CSV schema changed")
            original = list(reader)
            if any(None in x or x["interaction_type"] is None for x in original):
                raise ValueError("GloBI CSV malformed relation row")
            match = [r for r in original if r["target_taxon_name"]==name]
            count_by = Counter(r["interaction_type"] for r in match)
            # Author name and GBIF taxon key are not guaranteed on GloBI's
            # source/target string records; name-only != accepted concept.
            raw_files[path] = raw
            item.update({
                "retrieval_status":"EXACT_TARGET_NAME_ASSOCIATIONS_FOUND"
                    if match else "NO_EXACT_TARGET_NAME_ASSOCIATIONS_IN_RESPONSE",
                "original_relation_rows":len(original),
                "exact_target_name_rows":len(match),
                "other_target_name_rows":len(original)-len(match),
                "exact_target_relation_counts":dict(sorted(count_by.items())),
                "original_source_sha256":_sha256(raw),
                "result_at_GloBI_limit_possible_truncation":len(original)>=GLOBI_LIMIT,
            })
        except (ValueError,UnicodeError,OSError,KeyError,TypeError) as exc:
            item["retrieval_problem"] = f"{type(exc).__name__}: {str(exc)[:150]}"
        rows.append(item)
    n_success=sum(x["retrieval_status"]!="GLOBI_SOURCE_HOLD" for x in rows)
    n_exact=sum(x["exact_target_name_rows"] or 0 for x in rows)
    return {
        "schema_version":NETWORK_SCHEMA,
        "status":"PUBLIC_GLOBI_SPECIES_FIRST_OPPORTUNITY_DATA_NOT_DIRECT_CONFLICT",
        "sampling_species_source_schema":SPECIES_SCHEMA,
        "n_gbif_taxa_selected":len(selected["species"]),
        "n_queries_completed":n_success,
        "n_GloBI_fetch_holds":len(rows)-n_success,
        "n_GloBI_queries_with_exact_target_name":sum(
            (x["exact_target_name_rows"] or 0)>0 for x in rows
        ),
        "total_exact_target_name_relation_rows":n_exact,
        "per_species":rows,
        "zero_source_rows_do_NOT_identify_absent_interactions":True,
        "GloBI_target_name_not_author_authenticated":True,
        "source_name_matches_not_ecological_conflicts":True,
        "source_broad_taxon_relation_labels_not_independent_agent_species":True,
        "study_frame_selected_without_examining_GloBI_data":True,
        "family_coverage_not_global_sampling_weights":True,
        "no_direct_plant_fitness_selection_result":True,
        "strict_structural_BALANCE_occupancy_identified":False,
        "additional_independent_biological_clusters":0,
    },raw_files


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--frame",type=Path,required=True)
    parser.add_argument("--output-root",type=Path,required=True)
    args=parser.parse_args()
    frame=json.loads(args.frame.read_text(encoding="utf-8"))
    selected,gbif_source=select_species(frame)
    root=args.output_root
    for path,data in gbif_source.items():
        output=root/path
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(data)
    selected_path=root/"data/BALANCE_GBIF_SPECIES_FIRST_SELECTED_V1.json"
    selected_path.parent.mkdir(parents=True,exist_ok=True)
    selected_path.write_text(json.dumps(selected,indent=2,sort_keys=True)+"\n")
    # Phase boundary: selected species are in an immutable frozen local
    # snapshot before any queries for those species are made.
    opportunity,globi_source=retrieve_globi(selected)
    for path,data in globi_source.items():
        output=root/path
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(data)
    output=root/"data/BALANCE_GBIF_GLOBI_SPECIES_FIRST_READOUT_V1.json"
    output.write_text(json.dumps(opportunity,indent=2,sort_keys=True)+"\n")
    report={
        "n_families":len(frame["family_strata"]),
        "n_species_selected":selected["n_species_selected"],
        "n_family_holds":len(frame["family_strata"])-
                         selected["n_families_with_complete_quota"],
        "n_GloBI_success":opportunity["n_queries_completed"],
        "n_GloBI_hold":opportunity["n_GloBI_fetch_holds"],
        "n_exact_target_name_species":opportunity[
            "n_GloBI_queries_with_exact_target_name"],
        "n_exact_target_name_relations":opportunity[
            "total_exact_target_name_relation_rows"],
        "selected_species":[x["canonical_name"] for x in selected["species"]],
        "species_opportunity":[
            [r["GBIF_canonical_name"],r["exact_target_name_rows"],
             r["original_relation_rows"],r["retrieval_status"]]
            for r in opportunity["per_species"]
        ],
        "no_conflict_fitness_inference":True,
    }
    print("BALANCE_SPECIES_FIRST_SOURCE_SUMMARY="+json.dumps(
        report,sort_keys=True,separators=(",",":")
    ))


if __name__=="__main__":
    main()

"""Synthetic tests of a PRE-FROZEN taxonomy-first sample, never field results."""
from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from scripts.acquire_gbif_globi_species_first import (
    SCHEMA, SPECIES_SCHEMA, NETWORK_SCHEMA,
    _page_offset, _species_score, _is_plain_binomial,
    select_species, retrieve_globi,
)

ROOT=Path(__file__).resolve().parents[1]
FRAME=ROOT/"data/BALANCE_GBIF_SPECIES_FIRST_CROSS_ORDER_PANEL_V1.json"


def frame():
    return json.loads(FRAME.read_text(encoding="utf-8"))


def fake_accepted_taxonomy_fetch(frame_doc):
    observed=[]
    def fetch(url,limit):
        observed.append(url)
        match=next((f for f in frame_doc["family_strata"]
                    if url==f["page_url"]),None)
        if not match:
            raise AssertionError("outcome information requested before freezing taxonomy")
        # Real GBIF records include name + speciesKey identity, and some
        # extinct fields are missing, not False; missing remains UNKNOWN.
        vals=[]
        for i in range(20):
            latin=("alfa","beta","gamma","delta","epsilon","zeta",
                   "eta","theta","iota","kappa","lambda","mu","nu",
                   "omicron","pi","rho","sigma","tau","upsilon","omega")[i]
            key=match["gbif_family_key"]*1000+i
            vals.append({
                "key":key,"speciesKey":key,
                "canonicalName":"G"+match["family"].lower()+" "+latin,
                "family":match["family"],
                "familyKey":match["gbif_family_key"],
                "rank":"SPECIES","kingdom":"Plantae",
                "taxonomicStatus":"ACCEPTED",
                "nameType":"SCIENTIFIC","synonym":False,
                "scientificName":"G"+match["family"].lower()+" "+latin+" Mock.","authorship":"Mock.",
                "numOccurrences":0,"order":match["order"],
            })
        vals[0]["extinct"]=True
        vals[1]["extinct"]=False
        obj={"offset":match["fixed_offset"],
             "limit":frame_doc["page_size"],
             "count":match["accepted_species_search_count_at_freeze"],
             "results":vals}
        return json.dumps(obj).encode("utf-8")
    return fetch,observed


def fake_globi_fetch(sampled):
    seen=[]
    keybyname={x["canonical_name"]:x["gbif_species_key"]
               for x in sampled["species"]}
    def fetch(url,limit):
        seen.append(url)
        name=next((n for n in keybyname if
            "targetTaxon="+n.replace(" ","%20")+"&limit=500" in url),None)
        if not name:
            raise AssertionError("unregistered GloBI species query")
        out=io.StringIO()
        w=csv.DictWriter(out,fieldnames=[
            "source_taxon_name","target_taxon_name",
            "target_taxon_external_id","interaction_type"
        ],lineterminator="\n")
        w.writeheader()
        # Half the selected taxa get a labelled association; remaining
        # taxa have either only a wrong taxon or no source records.
        key=keybyname[name]
        if key%2==0:
            w.writerow({
                "source_taxon_name":"Bombus",
                "target_taxon_name":name,
                "target_taxon_external_id":"",
                "interaction_type":"pollinates",
            })
        else:
            w.writerow({
                "source_taxon_name":"Unrelated visitor",
                "target_taxon_name":"Other plant",
                "target_taxon_external_id":"",
                "interaction_type":"interactsWith",
            })
        return out.getvalue().encode()
    return fetch,seen


def test_exact_precommitted_page_offsets_and_twelve_distinct_orders():
    c=frame()
    assert c["schema_version"]==SCHEMA
    assert c["species_selection_independent_of_GloBI_interaction_records"] is True
    assert c["family_frame_is_random_sample_of_all_angiosperm_families"] is False
    assert len(c["family_strata"])==12
    assert len({x["order"] for x in c["family_strata"]})==12
    for x in c["family_strata"]:
        assert _page_offset(
            c["deterministic_seed"],x["family"],x["gbif_family_key"],
            x["accepted_species_search_count_at_freeze"],c["page_size"],
        )==x["fixed_offset"]
    assert len(_species_score("seed","Fabaceae",1234))==64
    assert _is_plain_binomial("Fictiva alfa")
    assert not _is_plain_binomial("Fictiva alfa subsp. delta")


def test_species_sample_determined_before_and_independent_of_network_data():
    c=frame()
    fetch,urls=fake_accepted_taxonomy_fetch(c)
    sample,raw=select_species(c,fetch=fetch)
    other,_=select_species(c,fetch=fetch)
    assert sample==other
    assert sample["schema_version"]==SPECIES_SCHEMA
    assert sample["n_family_strata"]==12
    assert sample["n_species_planned"]==48
    assert sample["n_species_selected"]==48
    assert sample["n_families_with_complete_quota"]==12
    assert len(raw)==12
    assert len(urls)==24
    assert {s["family"] for s in sample["species"]}=={
        x["family"] for x in c["family_strata"]
    }
    assert all(s["GBIF_extinct_field"]!="TRUE" for s in sample["species"])
    assert all(s["source_page_path"].startswith("data/external/gbif/")
               for s in sample["species"])


def test_missing_GBIF_taxa_never_replaced_with_known_positive_species():
    c=frame()
    fetch,_=fake_accepted_taxonomy_fetch(c)
    missing=c["family_strata"][0]["page_url"]
    def broken(url,limit):
        if url==missing:
            raise ValueError("source 429")
        return fetch(url,limit)
    sample,raw=select_species(c,fetch=broken)
    assert sample["n_species_selected"]==44
    assert sample["n_families_with_complete_quota"]==11
    assert sample["family_counts"][0]["status"]=="GBIF_TAXONOMY_HOLD"
    assert sample["family_counts"][0]["failure"].endswith("source 429")
    assert len(raw)==11
    assert all(r["family"]!="Asteraceae" for r in sample["species"])


def test_globi_query_retains_empty_or_wrong_species_as_missing_not_biological_absence():
    c=frame()
    sel,_=select_species(c,fetch=fake_accepted_taxonomy_fetch(c)[0])
    fetch,calls=fake_globi_fetch(sel)
    result,raw=retrieve_globi(sel,fetch=fetch)
    assert result["schema_version"]==NETWORK_SCHEMA
    assert result["n_gbif_taxa_selected"]==48
    assert result["n_queries_completed"]==48
    assert result["n_GloBI_fetch_holds"]==0
    assert len(calls)==48
    assert len(raw)==48
    assert result["n_GloBI_queries_with_exact_target_name"] in (20,21,22,23,24,25,26,27,28)
    assert result["zero_source_rows_do_NOT_identify_absent_interactions"] is True
    assert result["GloBI_target_name_not_author_authenticated"] is True
    assert result["source_name_matches_not_ecological_conflicts"] is True
    assert result["strict_structural_BALANCE_occupancy_identified"] is False
    for row in result["per_species"]:
        assert row["functional_fitness_tradeoff_identified"] is False
        assert row["biotic_interaction_absence_identified"] is False
        assert row["source_target_author_match_verified"] is False


def test_globi_network_partial_fetch_keeps_full_taxon_denominator():
    c=frame()
    sel,_=select_species(c,fetch=fake_accepted_taxonomy_fetch(c)[0])
    fetch,_=fake_globi_fetch(sel)
    first=sel["species"][0]["canonical_name"]
    def broken(url,limit):
        if "targetTaxon="+first.replace(" ","%20") in url:
            raise ValueError("429 rate limited")
        return fetch(url,limit)
    out,raw=retrieve_globi(sel,fetch=broken)
    assert out["n_gbif_taxa_selected"]==48
    assert out["n_queries_completed"]==47
    assert out["n_GloBI_fetch_holds"]==1
    assert len(out["per_species"])==48
    assert any(r["retrieval_status"]=="GLOBI_SOURCE_HOLD"
               and r["exact_target_name_rows"] is None
               for r in out["per_species"])


def test_tampering_frame_cannot_replace_species_or_change_page_after_outcome():
    c=frame()
    c["species_selection_independent_of_GloBI_interaction_records"]=False
    with pytest.raises(ValueError,match="interactions cannot affect"):
        select_species(c,fetch=lambda *_:b"")
    c=frame()
    c["family_strata"][0]["fixed_offset"]+=20
    with pytest.raises(ValueError,match="sampling offset drift"):
        select_species(c,fetch=lambda *_:b"")
    c=frame()
    c["deterministic_seed"]="outcome-chosen"
    with pytest.raises(ValueError,match="seed differs"):
        select_species(c,fetch=lambda *_:b"")

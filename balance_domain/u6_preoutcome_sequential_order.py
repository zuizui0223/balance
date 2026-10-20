"""Original-source refinements to the *direction* of three U6 sequential visits.

Scientific object: which visitor acts first on the source pollen pool.
NOT the timing of developmentally regulated anther release, NOT the source's
architecture response, and NOT a measured SCH pure-function optimum or SLK
structural fitness contrast. All 21 frozen U6 groups remain unchanged.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
from pathlib import Path
from typing import Any

from .u6_preoutcome_common_support import (
    ROOT, SOURCE, PREDICTORS, CODERS, FREEZE, EXPECTED_SEQ,
    analyze as base_source_audit,
)

ORDER_LEDGER="data/BALANCE_U6_SEQUENTIAL_VISITOR_ORDER_SOURCE_V1.csv"
ORIGINAL_PACKET="data/BALANCE_PLANT_U6_PASS2_SOURCE_PACKET_V1.csv"
VALID_DIRECTIONS={
    "THEFT_BEFORE_EFFECTIVE_TRANSFER",
    "EFFECTIVE_TRANSFER_BEFORE_THEFT",
}
ORIGINAL_SOURCES={
    "Clusia_arrudae":"10.1111/j.1744-7429.2004.tb00329.x",
    "Crescentia_alata":"10.17129/botsci.1377",
    "Tolmiea_menziesii":"10.1007/s00606-003-0067-1",
}
CRITICAL_PRECISIONS={
    "Clusia_arrudae":("99%", "0.1%", "pollen"),
    "Crescentia_alata":("Four trees", "40%", "NECTAR not pollen"),
    "Tolmiea_menziesii":("No per-visit", "paternity"),
}


def _csv(base: Path, rel: str) -> tuple[list[dict[str,str]],str]:
    blob=(base/rel).read_bytes()
    with (base/rel).open(encoding="utf-8-sig",newline="") as f:
        rdr=csv.DictReader(f)
        fields=rdr.fieldnames
        rows=list(rdr)
    if not fields or len(fields)!=len(set(fields)) or any(
        None in r for r in rows
    ):
        raise ValueError("Malformed original source table: "+rel)
    return rows,hashlib.sha256(blob).hexdigest()


def analyze(base: Path=ROOT) -> dict[str,Any]:
    """Original-source order refinement with architecture and causal HOLDs."""
    baseline=base_source_audit(base)
    source, source_sha=_csv(base,SOURCE)
    timing,timing_sha=_csv(base,PREDICTORS)
    packet,packet_sha=_csv(base,ORIGINAL_PACKET)
    ledger,ledger_sha=_csv(base,ORDER_LEDGER)
    if (len(ledger)!=3 or
            {r.get("dependency_group") for r in ledger}!=EXPECTED_SEQ):
        raise ValueError("Refinement must cover every frozen sequential group, no extras")
    packet_map={r["dependency_group"]:r for r in packet}
    if len(packet_map)!=21:
        raise ValueError("Registered source packet group mapping changed")
    recorded_timing={
        r["cluster_id"]:r["reported_value"] for r in timing
        if r["predictor"]=="conflict_timing_geometry"
    }
    if len(recorded_timing)!=21:
        raise ValueError("Frozen source timing receipt count changed")
    if any(r["dependency_group"] not in packet_map for r in ledger):
        raise ValueError("Refinement group missing registered source packet")
    if baseline["double_coder_architecture_receipts"]["independently_adjudicated_architecture_groups"]!=0:
        raise ValueError("Do not promote original-source refinement as dual coder result")

    expected_dirs={
        "Clusia_arrudae":"THEFT_BEFORE_EFFECTIVE_TRANSFER",
        "Crescentia_alata":"THEFT_BEFORE_EFFECTIVE_TRANSFER",
        "Tolmiea_menziesii":"EFFECTIVE_TRANSFER_BEFORE_THEFT",
    }
    source_group={r["dependency_group"]:r for r in source}
    result_rows=[]
    for row in ledger:
        g=row["dependency_group"]
        if (row["source_timing_code"]!="SEQUENTIAL_WITHIN_UNIT"
                or recorded_timing[g]!="SEQUENTIAL_WITHIN_UNIT"
                or row["refined_ordering"] not in VALID_DIRECTIONS
                or row["refined_ordering"]!=expected_dirs[g]):
            raise ValueError("Original sequence polarity or screened status changed")
        if row["source_doi"]!=ORIGINAL_SOURCES[g] or (
            row["source_doi"] not in packet_map[g]["primary_source_basis"]
        ):
            raise ValueError("New source has no matching original packet DOI")
        if source_group[g]["packet_status"]!="FROZEN":
            raise ValueError("Source packet provenance not frozen")
        if (not row["first_agent"] or not row["second_agent"]
                or not row["original_observation"]
                or row["source_evidence_level"]!="ORIGINAL_ABSTRACT_ACCESSIBLE"
                or row["floral_architecture_inferred"]!="NOT_CODED"):
            raise ValueError("Source refinement cannot infer an anatomical outcome")
        for term in CRITICAL_PRECISIONS[g]:
            if term not in row["quantitative_evidence_with_units"]:
                raise ValueError("Original source quantitative qualifier or missingness changed")
        result_rows.append({
            "dependency_group":g,
            "chronology":row["refined_ordering"],
            "source_doi":row["source_doi"],
            "first_actor":row["first_agent"],
            "second_actor":row["second_agent"],
            "source_effect_receipt":row["quantitative_evidence_with_units"],
            "source_fitness_evidence_status":row["measured_fitness_effect"],
            "direct_architecture_outcome":None,
        })
    by_direction=dict(sorted(Counter(
        r["chronology"] for r in result_rows
    ).items()))
    return {
        "schema":"BALANCE_U6_ORIGINAL_SOURCE_SEQUENTIAL_DIRECTION_V1",
        "status":"COMPLETE_SEQUENTIAL_STRATUM_SOURCE_REFINEMENT_NOT_ARCHITECTURE",
        "source_roster":{"u6_admitted_groups":21,
                         "timing_simultaneous":18,"timing_sequential":3},
        "original_source_directions":by_direction,
        "source_sequential_groups":sorted(r["dependency_group"] for r in result_rows),
        "per_group_original_source_receipts":sorted(result_rows,key=lambda x:x["dependency_group"]),
        "source_hashes":{
            "preoutcome_u6_audit_manifest":baseline["source_sha256"][FREEZE],
            "source_recovery":source_sha,
            "source_screened_predictors":timing_sha,
            "original_double_coder_frame":baseline["source_sha256"][CODERS],
            "original_source_packet":packet_sha,
            "new_sequence_qualifier_ledger":ledger_sha,
        },
        "source_chronology_is_not_developmental_pollen_dosing":True,
        "upstream_visitor_order_is_not_the_value_of_a_temporal_anther_module":True,
        "source_fitness_effects_are_not_matched_across_taxa":True,
        "nonsequential_18_groups_not_assumed_zero_trait_conflict":True,
        "no_blinded_U6_architecture_coding_performed":True,
        "no_fitted_effect_or_p_value":True,
        "not_a_representative_global_taxon_rate":True,
        "preoutcome_V4_anatomical_responses_read":False,
        "new_heritable_module_origin_established":False,
        "falsifiable_prediction_only":(
            "holding total pollen and effective visitor encounter/handling "
            "constant, early theft can deplete later available pollen; "
            "post-export theft cannot remove pollen already exported, but "
            "can still affect subsequent encounters. No universal effect "
            "direction follows from the unadjusted chronology code alone."
        ),
    }

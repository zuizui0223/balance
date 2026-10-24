"""Source-only scientific evidence entry, not two independent architecture codings."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

from balance_domain.u6_original_source_ecology_pilot import (
    analyze,ROOT,FREEZE,PACKET,RECOVERY,PREDICTORS,DEPENDENCE,PILOT
)


def _copy(tmp_path):
    for rel in (FREEZE,PACKET,RECOVERY,PREDICTORS,DEPENDENCE,PILOT):
        src=ROOT/rel
        dest=tmp_path/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dest)


def _edit(path,edit):
    with path.open(encoding="utf-8",newline="") as f:
        rdr=csv.DictReader(f)
        fields=list(rdr.fieldnames or [])
        rows=list(rdr)
    edit(rows)
    with path.open("w",encoding="utf-8",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)


def test_real_selected_six_have_registered_source_only_observations():
    r=analyze()
    assert r["status"]=="SIX_ORIGINAL_ABSTRACT_SOURCE_OBSERVATIONS_NOT_ARCHITECTURE_ADJUDICATION"
    assert r["admitted_groups"]==21
    assert len(r["analysis_rows"])==21
    assert r["original_abstract_observations_extracted"]==6
    assert r["not_yet_extracted"]==15
    assert r["distinct_admission_source_reference_ids"]==21
    assert r["shared_original_source_reference_between_taxa"]=={
        "U6_REF_078":["Actinidia_deliciosa","Echium_plantagineum"]
    }
    assert r["taxa_with_shared_original_source_reference_are_not_independent_studies"]
    assert r["source_timing_groups"]=={"simultaneous":18,"sequential":3}
    assert r["selected_timing_counts"]=={
        "SIMULTANEOUS":3,"SEQUENTIAL_WITHIN_UNIT":3,
    }
    assert r["pilot_selected_groups"]==[
        "Actinidia_deliciosa","Amomum_subulatum",
        "Aphelandra_golfodulcensis","Clusia_arrudae",
        "Crescentia_alata","Tolmiea_menziesii",
    ]
    assert r["original_source_recovery_statuses"]=={
        "RESOLVED":15,"EVIDENCE_CEILING":6,
    }
    assert r["source_packet_for_blind_independent_A_B_unchanged"] is True
    assert r["independent_A_B_architecture_labels_written"]==0
    assert r["sealed_V4_architecture_outcome_opened"] is False
    assert r["source_abstract_sufficient_to_prove_new_heritable_module"] is False
    assert r["historical_evolutionary_causality_established"] is False
    assert all(len(x)==64 for x in r["source_sha256"].values())
    assert len(r["source_sha256"])==6


def test_ecological_observation_not_a_biological_structure_label():
    r=analyze()
    observed={x["dependency_group"]:x for x in r["analysis_rows"]
              if x["observation_literature_extracted_by_pilot"]}
    assert observed["Clusia_arrudae"]["original_timing_exposure_code"]=="SEQUENTIAL_WITHIN_UNIT"
    assert "99 percent" in observed["Clusia_arrudae"]["ecological_observation"]
    assert "dioecious" in observed["Clusia_arrudae"]["floral_observation"].lower()
    assert "protandry" in observed["Tolmiea_menziesii"]["floral_observation"]
    assert "narrow passage" in observed["Amomum_subulatum"]["floral_observation"]
    assert "four trees" in observed["Crescentia_alata"]["functional_time_observation"]
    assert observed["Aphelandra_golfodulcensis"]["source_recovery_status"]=="EVIDENCE_CEILING"
    assert "pollen" in observed["Actinidia_deliciosa"]["ecological_observation"]
    assert all(x["independent_A_B_coding_performed_by_this_audit"] is False
               for x in observed.values())
    assert all(x["original_primary_source_bibliography"] for x in r["analysis_rows"])
    assert len([x for x in r["analysis_rows"]
                if x["ecological_observation"] is None])==15


def test_locked_architecture_blind_pilot_selection_cannot_be_changed(tmp_path):
    _copy(tmp_path)
    def mutate(rows):
        rows[0]["dependency_group"]="Banksia_menziesii"
    _edit(tmp_path/PILOT,mutate)
    with pytest.raises(ValueError,match="six selected groups"):
        analyze(tmp_path)


def test_extractor_cannot_overwrite_frozen_coder_labels(tmp_path):
    _copy(tmp_path)
    def mutate(rows):
        rows[0]["formal_u6_architecture_assigned"]="STRUCTURAL_MODULE_DIVISION"
    _edit(tmp_path/PILOT,mutate)
    with pytest.raises(ValueError,match="cannot act as independent architecture coder"):
        analyze(tmp_path)


def test_source_cannot_falsify_coder_authorship(tmp_path):
    _copy(tmp_path)
    def mutate(rows):
        rows[0]["independent_coder_authorship"]="CODER_A"
    _edit(tmp_path/PILOT,mutate)
    with pytest.raises(ValueError,match="impersonate independent coder"):
        analyze(tmp_path)


def test_timing_source_switch_cannot_be_selected_post_outcome(tmp_path):
    _copy(tmp_path)
    def mutate(rows):
        for row in rows:
            if row["cluster_id"]=="Clusia_arrudae" and row["predictor"]=="conflict_timing_geometry":
                row["reported_value"]="SIMULTANEOUS"
    _edit(tmp_path/PREDICTORS,mutate)
    with pytest.raises(ValueError,match="timing source split changed"):
        analyze(tmp_path)


def test_taxonomic_dependence_must_keep_original_21_group_contract(tmp_path):
    _copy(tmp_path)
    def mutate(rows):
        rows.pop()
    _edit(tmp_path/DEPENDENCE,mutate)
    with pytest.raises(ValueError,match="frozen source reference/recovery/dependence"):
        analyze(tmp_path)


def test_studies_do_not_change_frozen_admission_or_sealed_architecture(tmp_path):
    _copy(tmp_path)
    f=tmp_path/FREEZE
    payload=json.loads(f.read_text())
    payload["pass1_contract"]["architecture_used_for_admission"]=True
    f.write_text(json.dumps(payload))
    with pytest.raises(ValueError,match="architecture-blind source contract"):
        analyze(tmp_path)


def test_partial_source_receipt_requires_missingness_qualification(tmp_path):
    _copy(tmp_path)
    def mutate(rows):
        rows[0]["missing_for_formal_architecture_coding"]=""
    _edit(tmp_path/PILOT,mutate)
    with pytest.raises(ValueError,match="lacks source or missingness status"):
        analyze(tmp_path)

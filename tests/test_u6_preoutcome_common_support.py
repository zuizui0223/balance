"""Source-only U6 frozen denominator, predictor feasibility and taxonomy gates."""
from __future__ import annotations

import csv
import json
import shutil

import pytest

from balance_domain.u6_preoutcome_common_support import (
    ROOT,FREEZE,SOURCE,PREDICTORS,DEPENDENCE,TAXON,CODERS,analyze
)


def _copy_sources(tmp_path):
    for rel in (FREEZE,SOURCE,PREDICTORS,DEPENDENCE,TAXON,CODERS):
        src=ROOT/rel; dst=tmp_path/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)


def _edit_csv(p, modifier):
    with p.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        fields=list(reader.fieldnames or ())
        rows=list(reader)
    modifier(rows)
    with p.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_all_real_source_receipts_without_sealed_v4():
    a=analyze()
    assert a["status"]=="FROZEN_SOURCE_SUPPORT_ONLY_ZERO_ARCHITECTURE_RECEIPTS"
    assert a["anchor_reference_universe"]==157
    assert a["candidate_reference_outcomes"]=={
        "include":21,"exclude":3,"retained_unresolved":9
    }
    assert a["admitted_conflict_first_dependency_groups"]==21
    assert a["source_recovery_statuses"]=={
        "EVIDENCE_CEILING":6,"RESOLVED":15
    }
    assert a["source_predictor_receipts"]==63
    assert a["source_predictor_statuses"]=={"SCREENED":63}
    assert a["source_predicted_geometry"]=={
        "module_substrate":{"SINGLE_OR_CONTINUOUS":21},
        "conflict_timing_geometry":{"SEQUENTIAL_WITHIN_UNIT":3,"SIMULTANEOUS":18},
        "conflict_spatial_geometry":{"SAME_UNIT":21},
    }
    assert a["source_sequential_exposure_groups"]==[
        "Clusia_arrudae","Crescentia_alata","Tolmiea_menziesii"
    ]
    assert a["predictor_source_opportunity"]["within_u6_module_substrate_contrast_identifiable"] is False
    assert a["predictor_source_opportunity"]["timing_architecture_effect_currently_identified"] is False
    assert a["frozen_taxon_dependency_actions"]=={
        "SHARED_SPECIES_BLOCK":1,"SHARED_TAXON_CONCEPT_BLOCK":1,"U6_ONLY":19
    }
    assert a["taxon_concept_overlay"]["cannot_claim_u6_u3_zero_overlap"] is True
    assert a["taxon_concept_overlay"]["same_biological_population_verified"] is False
    assert a["double_coder_architecture_receipts"]=={
        "frozen_coder_rows":42,
        "source_coding_status":{"UNSTARTED":42},
        "source_architecture_labels":{"UNRESOLVED":42},
        "independently_adjudicated_architecture_groups":0,
    }
    assert a["registered_primary_V4_outcomes_accessed"] is False
    assert a["qualified_u6_structure_effects"]==0
    assert all(len(x)==64 for x in a["source_sha256"].values())


def test_blinded_double_coder_outcome_change_is_not_promoted(tmp_path):
    _copy_sources(tmp_path)
    def update(rows):
        rows[0]["architecture_mode"]="STRUCTURAL_MODULE_DIVISION"
        rows[0]["coding_status"]="COMPLETED"
    _edit_csv(tmp_path/CODERS,update)
    with pytest.raises(ValueError,match="pre-outcome audit must not open"):
        analyze(tmp_path)


def test_screened_is_not_confirmatory_adjudication(tmp_path):
    _copy_sources(tmp_path)
    def update(rows):
        rows[0]["adjudication_status"]="ADJUDICATED"
    _edit_csv(tmp_path/PREDICTORS,update)
    with pytest.raises(ValueError,match="independently screened"):
        analyze(tmp_path)


def test_taxonomic_alias_populations_are_not_assumed_same(tmp_path):
    _copy_sources(tmp_path)
    def update(rows):
        next(r for r in rows if r["u6_dependency_group"]=="Melastoma_affine")[
            "biological_populations_identical"
        ]="TRUE"
    _edit_csv(tmp_path/TAXON,update)
    with pytest.raises(ValueError,match="cannot imply confirmed population identity"):
        analyze(tmp_path)


def test_old_no_u3_overlap_record_would_fail_before_counting(tmp_path):
    _copy_sources(tmp_path)
    def update(rows):
        row=next(r for r in rows if r["u6_dependency_group"]=="Melastoma_affine")
        row["overlap_universe"]="NONE"
        row["analysis_action"]="U6_ONLY"
    _edit_csv(tmp_path/DEPENDENCE,update)
    with pytest.raises(ValueError,match="Existing canonical U6 source taxon overlap"):
        analyze(tmp_path)


def test_outcome_blind_frozen_pass1_admission_is_not_reopened(tmp_path):
    _copy_sources(tmp_path)
    path=tmp_path/FREEZE
    data=json.loads(path.read_text(encoding="utf-8"))
    data["pass1_contract"]["architecture_used_for_admission"]=True
    path.write_text(json.dumps(data),encoding="utf-8")
    with pytest.raises(ValueError,match="architecture-blind Pass-1 freeze"):
        analyze(tmp_path)


def test_three_sequential_groups_cannot_be_hypothetically_imputed(tmp_path):
    _copy_sources(tmp_path)
    def update(rows):
        row=next(r for r in rows
                 if r["cluster_id"]=="Clusia_arrudae"
                 and r["predictor"]=="conflict_timing_geometry")
        row["reported_value"]="SIMULTANEOUS"
    _edit_csv(tmp_path/PREDICTORS,update)
    with pytest.raises(ValueError,match="Frozen U6 predictor class support"):
        analyze(tmp_path)

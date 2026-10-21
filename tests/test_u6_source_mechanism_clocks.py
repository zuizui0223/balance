"""Regress the exact first-six original-source biology without coding U6 outcomes."""
from __future__ import annotations

import json
import shutil

import pytest

from balance_domain.u6_source_mechanism_clocks import (
    ROOT,FREEZE,PACKET,RECOVERY,ORIGINAL_CODER,OBS,analyze
)


def _inputs(tmp_path):
    for f in (FREEZE,PACKET,RECOVERY,ORIGINAL_CODER,OBS):
        target=tmp_path/f
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/f,target)


def test_real_first_six_frozen_order_and_biological_clock_receipts():
    result=analyze()
    assert result["status"]=="SOURCE_REVIEW_ONLY_DOES_NOT_COMPLETE_ANY_U6_CODER_ROW"
    assert result["original_frozen_admitted_groups"]==21
    assert result["source_reviewed_initial_groups"]==6
    assert result["source_review_remaining_groups_unreviewed"]==15
    assert result["source_recovery_states"]=={"EVIDENCE_CEILING":1,"RESOLVED":5}
    assert result["source_programmes_evaluated"]==8
    assert result["source_contexts_not_matched_count"]==2
    assert result["frozen_human_coder_rows_left_untouched"]==42
    assert result["independent_adjudicated_architecture_groups"]==0
    assert result["qualifying_structural_origin_effects"]==0
    assert result["frozen_v4_outcome_file_read"] is False
    assert result["common_fitness_shared_plastic_module_comparator"] is False
    assert len(result["source_input_sha256"])==5
    assert all(len(x)==64 for x in result["source_input_sha256"].values())
    assert [x["frozen_dependency_group"] for x in result["source_observation_rows"]]==[
        "Actinidia_deliciosa","Amomum_subulatum",
        "Aphelandra_golfodulcensis","Banksia_menziesii",
        "Bromelia_antiacantha","Campanula_americana",
    ]


def test_different_temporal_axes_and_contexts_are_not_collapsed():
    r=analyze()
    taxa={x["frozen_dependency_group"]:x for x in r["source_observation_rows"]}
    assert "DAILY_VISITOR_TIMING" in taxa["Bromelia_antiacantha"]["distinct_clock_axes"]
    assert "FLORAL_DEVELOPMENTAL_SEX_PHASE" in taxa["Campanula_americana"]["distinct_clock_axes"]
    assert "POLLEN_REMOVAL_OR_DEPOSITION_FEEDBACK" in taxa["Campanula_americana"]["distinct_clock_axes"]
    assert "EXPERIMENTALLY_PLASTIC_MALE_AND_FEMALE_PHASE_DURATION" in (
        taxa["Campanula_americana"]["observed_anatomy_or_activity"]
    )
    assert "WITHIN_VISIT_CONTACT_GEOMETRY" in taxa["Amomum_subulatum"]["distinct_clock_axes"]
    assert "LAB_FEEDING_RATE" in taxa["Actinidia_deliciosa"]["distinct_clock_axes"]
    assert taxa["Actinidia_deliciosa"]["different_studies_not_a_matched_experiment"]
    assert taxa["Campanula_americana"]["different_studies_not_a_matched_experiment"]
    assert not taxa["Amomum_subulatum"]["different_studies_not_a_matched_experiment"]
    assert all(x["not_a_structural_module_outcome"] for x in taxa.values())


def test_a_source_evidence_ceiling_is_not_resolved_from_secondary_summary():
    r=analyze()
    a=next(x for x in r["source_observation_rows"]
           if x["frozen_dependency_group"]=="Aphelandra_golfodulcensis")
    assert a["original_source_recovery_status"]=="EVIDENCE_CEILING"
    assert "UNRESOLVED_FLORAL_ARCHITECTURE" in a["distinct_clock_axes"]


def test_no_outcome_based_replacement_of_first_six(tmp_path):
    _inputs(tmp_path)
    p=tmp_path/OBS
    d=json.loads(p.read_text(encoding="utf-8"))
    d["first_six"][0],d["first_six"][4]=d["first_six"][4],d["first_six"][0]
    p.write_text(json.dumps(d),encoding="utf-8")
    with pytest.raises(ValueError,match="cannot be reordered"):
        analyze(tmp_path)


def test_no_focal_architecture_labels_inserted_into_source_review(tmp_path):
    _inputs(tmp_path)
    p=tmp_path/OBS
    d=json.loads(p.read_text(encoding="utf-8"))
    d["first_six"][1]["architecture_mode"]="STRUCTURAL_MODULE_DIVISION"
    p.write_text(json.dumps(d),encoding="utf-8")
    with pytest.raises(ValueError,match="cannot insert frozen architecture"):
        analyze(tmp_path)


def test_source_context_cannot_be_misreported_as_one_experiment(tmp_path):
    _inputs(tmp_path)
    p=tmp_path/OBS
    d=json.loads(p.read_text(encoding="utf-8"))
    d["first_six"][-1]["source_contexts_not_matched"]=False
    p.write_text(json.dumps(d),encoding="utf-8")
    with pytest.raises(ValueError,match="Multiple study programmes"):
        analyze(tmp_path)


def test_frozen_u6_human_coding_returns_must_remain_untouched(tmp_path):
    _inputs(tmp_path)
    p=tmp_path/ORIGINAL_CODER
    s=p.read_text(encoding="utf-8")
    assert ",UNSTARTED," in s
    p.write_text(s.replace(",UNSTARTED,",",CODED,",1),encoding="utf-8")
    with pytest.raises(ValueError,match="never open U6 independent coder"):
        analyze(tmp_path)


def test_source_recovery_ceiling_not_autopromoted(tmp_path):
    _inputs(tmp_path)
    p=tmp_path/RECOVERY
    s=p.read_text(encoding="utf-8")
    assert ",EVIDENCE_CEILING," in s
    p.write_text(s.replace(",EVIDENCE_CEILING,",",RESOLVED,",1),encoding="utf-8")
    with pytest.raises(ValueError,match="Aphelandra source recovery ceiling"):
        analyze(tmp_path)


def test_candidate_evidence_must_have_verifiable_original_source(tmp_path):
    _inputs(tmp_path)
    p=tmp_path/OBS
    d=json.loads(p.read_text(encoding="utf-8"))
    d["first_six"][3]["source_records"][0]["url"]="https://example.invalid/source"
    p.write_text(json.dumps(d),encoding="utf-8")
    with pytest.raises(ValueError,match="Source paper URL"):
        analyze(tmp_path)

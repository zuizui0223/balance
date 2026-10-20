"""Regression of source-screen support / nonidentification, never V4 outcomes."""
from __future__ import annotations

import csv
from pathlib import Path
import shutil

import pytest

from balance_domain.plant_architecture_source_patterns import (
    REPO_ROOT, U2_PATH, PILOT_PATH,
)
from balance_domain.plant_function_timing_architecture_gate import (
    analyze, U3_MATCHED, U3_DEPENDENCE,
)


def test_real_original_sources_show_no_family_level_timing_structure_support():
    r=analyze()
    assert r["claim_level"]=="REAL_ORIGINAL_SOURCE_SCREEN_DESCRIPTIVE_ONLY"
    assert r["universe_pooled"] is False
    assert r["full_conditional_timing_to_structure_effect_identified"] is False
    assert r["no_source_receipt_for_matched_S_P_D_total_fitness"] is True

    u2=r["U2"]
    assert (u2["source_rows"],u2["positive_source_rows"])==(22,8)
    assert u2["positive_source_timing_codes"]=={
        "MIXED":5,"SEQUENTIAL_WITHIN_UNIT":2,"SIMULTANEOUS":1,
    }
    assert u2["simultaneous_source_architecture_codes"]=={"SHARED_INTEGRATED":1}
    assert u2["within_function_family_complete_timing_structural_2x2"]==[]

    pilot=r["PLANT_PILOT"]
    assert (pilot["source_rows"],pilot["positive_source_rows"])==(29,16)
    assert pilot["simultaneous_source_tag_count"]==8
    assert pilot["simultaneous_source_architecture_codes"]=={
        "SHARED_INTEGRATED":4,
        "SPATIAL_SEPARATION":1,
        "WITHIN_FLOWER_DIVISION_OF_LABOUR":3,
    }
    assert pilot["within_function_family_complete_timing_structural_2x2"]==[]
    assert pilot["positive_by_family"]["POLLINATOR_ANTAGONIST"]["positive_source_rows"]==7
    assert pilot["positive_by_family"]["POLLEN_REWARD_GAMETE"]["positive_source_rows"]==3
    assert pilot["positive_by_family"]["POLLEN_REWARD_GAMETE"]["structural_2x2_source_cells"]=={
        "simultaneous_structural":3,
        "simultaneous_nonstructural":0,
        "other_timing_structural":0,
        "other_timing_nonstructural":0,
    }
    assert pilot["positive_by_family"]["POLLINATOR_ANTAGONIST"]["structural_2x2_source_cells"]["simultaneous_nonstructural"]==4
    assert pilot["positive_by_family"]["POLLINATOR_ANTAGONIST"]["structural_2x2_source_cells"]["simultaneous_structural"]==0

    u3=r["U3"]
    assert u3["pass_case_control_pairs"]==4
    assert u3["independent_frozen_dependence_blocks"]==3
    assert u3["case_conflict_positive"]==4
    assert u3["control_conflict_positive"]==3
    assert u3["unresolved_controls"]==["Osbeckia chinensis"]
    assert u3["control_positive_routing_codes"]=={
        "AMONG_FLOWER_MODULE_DIVISION":1,
        "UNRESOLVED":1,
        "WITHIN_FLOWER_DIVISION_OF_LABOUR":1,
    }
    assert u3["reversible_plasticity_measured_by_this_ledger"] is False


def _source_copy(tmp_path):
    for path in (U2_PATH,PILOT_PATH,U3_MATCHED,U3_DEPENDENCE):
        dest=tmp_path/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(REPO_ROOT/path,dest)


def test_unrecognized_source_timing_code_is_rejected(tmp_path):
    _source_copy(tmp_path)
    path=tmp_path/PILOT_PATH
    raw=path.read_text(encoding="utf-8")
    assert ",SIMULTANEOUS," in raw
    path.write_text(raw.replace(",SIMULTANEOUS,",",MORPHOLOGY_IS_PLASTIC,",1),
                    encoding="utf-8")
    with pytest.raises(ValueError,match="source timing geometry"):
        analyze(tmp_path)


def test_frozen_u3_dependence_block_gate_fails_if_pass_is_revoked(tmp_path):
    _source_copy(tmp_path)
    path=tmp_path/U3_DEPENDENCE
    with path.open(encoding="utf-8",newline="") as fh:
        original=list(csv.DictReader(fh))
    fieldnames=list(original[0])
    assert original[0]["adjudication_state"]=="PASS"
    original[0]["adjudication_state"]="OPEN"
    with path.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(original)
    with pytest.raises(ValueError,match="PASS pair/dependence gate"):
        analyze(tmp_path)


def test_u3_unresolved_control_cannot_be_relabelled_zero_in_source(tmp_path):
    _source_copy(tmp_path)
    path=tmp_path/U3_MATCHED
    data=path.read_text(encoding="utf-8")
    assert "Osbeckia chinensis,UNRESOLVED," in data
    # Even if future source adjudication moves a source-coded unknown,
    # its provenance must be separately reviewed; no automatic zero fill.
    path.write_text(data.replace("Osbeckia chinensis,UNRESOLVED,",
                                 "Osbeckia chinensis,SHARED_INTEGRATED,",1),
                    encoding="utf-8")
    with pytest.raises(ValueError,match="frozen unresolved-control state"):
        analyze(tmp_path)


def test_same_timing_tag_never_promotes_to_direct_conflict_or_plastic_policy():
    r=analyze()
    for key in ("U2","PLANT_PILOT"):
        readout=r[key]
        assert not readout["source_timing_tag_is_direct_same_coordinate_C_measurement"]
        assert not readout["source_architecture_codes_measure_reversible_phenotypic_policy"]
        assert not readout["source_architecture_codes_identify_genetic_origin"]
    assert "SOURCE_TIMING_CODE_DOES_NOT_EQUAL_FUNCTIONAL_OVERLAP_STRENGTH"==r["rule"]

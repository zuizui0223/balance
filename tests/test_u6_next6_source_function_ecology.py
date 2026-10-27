"""Non-coder source-review evidence, source-position and unchanged V4 safeguards."""
from __future__ import annotations

import csv
import json
import shutil

import pytest

from balance_domain.u6_next6_source_function_ecology import (
    ROOT, FREEZE, PACKET, PREDICTORS, PILOT, NEXT6, DEPENDENCE, CODER, analyze,
)


def _copy_inputs(tmp_path):
    for path in (FREEZE,PACKET,PREDICTORS,PILOT,NEXT6,DEPENDENCE,CODER):
        dst=tmp_path/path
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/path,dst)


def _mutate_csv(path, edit):
    with path.open(encoding="utf-8",newline="") as h:
        reader=csv.DictReader(h)
        fields=list(reader.fieldnames or [])
        rows=list(reader)
    edit(rows)
    with path.open("w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_actual_six_source_observations_and_cross_draft_overlap():
    data=analyze()
    assert data["frozen_admitted_u6_taxa"]==21
    assert data["frozen_source_timing"]=={"sequential":3,"simultaneous":18}
    assert data["additional_six_source_extracted"]==6
    assert data["distinct_main_branch_source_observation_groups"]==12
    assert data["distinct_main_branch_unextracted"]==9
    assert data["provisional_cross_branch_selected_total"]==15
    assert data["cross_branch_remaining_unextracted"]==6
    assert data["cross_branch_results_not_formally_merged"]
    assert data["new_selected_source_groups"]==[
        "Campomanesia_pubescens","Echium_plantagineum",
        "Grevillea_barklyana","Hamelia_patens",
        "Impatiens_capensis","Melastoma_affine",
    ]
    assert data["admission_source_id_reused_across_taxa"]=={
        "U6_REF_078":["Actinidia_deliciosa","Echium_plantagineum"]
    }
    assert data["source_known_taxonomic_dependence"]=={
        "Impatiens_capensis":"SHARED_SPECIES_BLOCK",
        "Melastoma_affine":"SHARED_TAXON_CONCEPT_BLOCK",
    }
    assert data["primary_1995_hamelia_effect_not_read_or_recomputed"]
    assert data["independent_coder_architecture_labels_added"]==0
    assert not data["independent_coder_forms_modified"]
    assert not data["v4_outcome_file_opened"]
    assert not data["historical_evolutionary_origins_estimated"]
    assert len(data["source_sha256"])==7
    assert all(len(h)==64 for h in data["source_sha256"].values())


def test_source_position_matters_and_is_not_same_as_anther_depletion():
    data=analyze()
    records={r["dependency_group"]:r for r in data["source_rows"]}
    assert data["post_deposition_stigma_pollen_removal_taxa"]==[
        "Melastoma_affine"
    ]
    assert records["Melastoma_affine"]["functional_location"]==(
        "POST_DEPOSITION_STIGMA_POLLEN_REMOVAL"
    )
    assert records["Impatiens_capensis"]["ecological_mechanism"]==(
        "FORAGING_MODE_MEDIATES_POLLEN_TRANSFER_EFFICIENCY"
    )
    assert records["Hamelia_patens"]["source_adjudication"].startswith(
        "EVIDENCE_CEILING"
    )
    assert all(r["formal_u6_architecture_assigned"]=="NOT_ASSIGNED_BY_EXTRACTOR"
               and r["independent_coder_authorship"]=="NO_AI_EXTRACTOR_NOT_CODER_A_OR_B"
               for r in records.values())


def test_stigma_interception_never_silently_relabelled_anther_theft(tmp_path):
    _copy_inputs(tmp_path)
    def edit(rows):
        target=next(x for x in rows if x["dependency_group"]=="Melastoma_affine")
        target["functional_location"]="PRE_DEPOSITION_ANTHER_POLLEN_CONSUMED_BY_THRIPS"
    _mutate_csv(tmp_path/NEXT6,edit)
    with pytest.raises(ValueError,match="stigma deposition-phase locus"):
        analyze(tmp_path)


def test_independent_coders_not_impersonated_or_completed(tmp_path):
    _copy_inputs(tmp_path)
    def edit(rows):
        rows[0]["independent_coder_authorship"]="CODER_A"
        rows[0]["formal_u6_architecture_assigned"]="STRUCTURAL_MODULE_DIVISION"
    _mutate_csv(tmp_path/NEXT6,edit)
    with pytest.raises(ValueError,match="cannot be a four-class coder"):
        analyze(tmp_path)
    _copy_inputs(tmp_path)
    def mutate_frozen(rows):
        rows[0]["coding_status"]="COMPLETED"
        rows[0]["architecture_mode"]="SHARED"
    _mutate_csv(tmp_path/CODER,mutate_frozen)
    with pytest.raises(ValueError,match="No coded U6 architecture outcomes"):
        analyze(tmp_path)


def test_original_hamelia_primary_source_access_hold_cannot_disappear(tmp_path):
    _copy_inputs(tmp_path)
    def edit(rows):
        for x in rows:
            if x["dependency_group"]=="Hamelia_patens":
                x["source_adjudication"]="PRIMARY_EXPERIMENT_REPLICATED_ALL_RESULTS"
    _mutate_csv(tmp_path/NEXT6,edit)
    with pytest.raises(ValueError,match="Hamelia numerical source access ceiling"):
        analyze(tmp_path)


def test_original_admission_reference_not_replaced_by_supplementary_work(tmp_path):
    _copy_inputs(tmp_path)
    def edit(rows):
        for x in rows:
            if x["dependency_group"]=="Echium_plantagineum":
                x["admission_ref"]="U6_REF_FAKE"
    _mutate_csv(tmp_path/NEXT6,edit)
    with pytest.raises(ValueError,match="Admission original source reference"):
        analyze(tmp_path)


def test_selection_must_remain_blind_to_time_or_architecture_outcome(tmp_path):
    _copy_inputs(tmp_path)
    def edit(rows):
        for row in rows:
            if (row["cluster_id"]=="Campomanesia_pubescens"
                    and row["predictor"]=="conflict_timing_geometry"):
                row["reported_value"]="SEQUENTIAL_WITHIN_UNIT"
    _mutate_csv(tmp_path/PREDICTORS,edit)
    with pytest.raises(ValueError,match="Frozen U6 timing predictor frequencies"):
        analyze(tmp_path)


def test_taxon_dependence_with_u3_and_u1_cannot_be_hidden(tmp_path):
    _copy_inputs(tmp_path)
    def edit(rows):
        for row in rows:
            if row["u6_dependency_group"]=="Melastoma_affine":
                row["analysis_action"]="U6_ONLY"
    _mutate_csv(tmp_path/DEPENDENCE,edit)
    with pytest.raises(ValueError,match="Existing U1/U3 shared taxon dependence"):
        analyze(tmp_path)


def test_frozen_pass1_must_not_be_architecture_selected(tmp_path):
    _copy_inputs(tmp_path)
    p=tmp_path/FREEZE
    data=json.loads(p.read_text())
    data["pass1_contract"]["architecture_used_for_admission"]=True
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="Architecture-blind U6 Pass1 frozen cohort"):
        analyze(tmp_path)

"""Primary-source method scope and future exact-Dryad ingestion tests.

No test fixture is a biological observation from the original Dryad files.
All 2015 data-dependent outputs remain HOLD until both archived bytes match.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from balance_domain.dalechampia_method_scope import (
    ARMS, FILE_IDENTITIES,
    audit_dalechampia_method_scope,
    verify_exact_dryad_bytes,
)
from scripts.probe_dalechampia_2015_dryad import build_receipt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/"data"/"DALECHAMPIA_POSTANTHESIS_METHOD_AND_DRYAD_V2.json"


def contract():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def test_methods_treatment_scope_is_original_whole_blossom_foil():
    c = contract()
    result = audit_dalechampia_method_scope(c)
    assert result["status"] == "SOURCE_METHOD_CORRECTED_BRACT_CARBON_UNIDENTIFIED"
    assert result["original_historical_treatment_codes"] == list(ARMS)
    assert result["whole_blossom_foil_shade_includes_fruit_light"] is True
    assert result["bract_local_photosynthesis_only_intervention"] is False
    assert result["fruit_photosynthesis_in_whole_blossom_shade_isolated"] is False
    assert result["foil_specific_microclimate_control_available"] is False
    assert result["effect_on_four_week_seed_mass_as_total_treatment_package"] is True
    assert result["raw_file_bytes_verified"] is False
    assert result["raw_reanalysis_executed"] is False
    assert result["structural_BALANCE_identified"] is False
    assert result["new_independent_biological_clusters"] == 0


def test_archived_source_experiment_counts_are_recorded_without_abortion_imputation():
    o = audit_dalechampia_method_scope(contract())
    assert sum(o["historical_seed_count"].values()) == 1220
    assert sum(o["historical_aborted_seed_count"].values()) == 117
    assert o["historical_seed_count"] == {"bag":317,"cut":295,"cutcont":317,"cont":291}


def test_dryad_exact_metadata_freezes_two_original_file_digests():
    c = contract()
    files={x["source_file_id"]:x for x in c["dryad_source_files"]}
    assert len(files)==2
    for id_ in (46163,46164):
        filename,size,digest=FILE_IDENTITIES[id_]
        assert files[id_]["name"]==filename
        assert files[id_]["size_bytes"]==size
        assert files[id_]["md5"]==digest
        assert files[id_]["download_url"]==f"https://datadryad.org/api/v2/files/{id_}/download"


def test_forged_bract_only_shading_label_fails_closed():
    c=contract()
    bag=next(x for x in c["original_arms"] if x["code"]=="bag")
    bag["foil_entire_blossom"]=False
    with pytest.raises(ValueError,match="bag source intervention"):
        audit_dalechampia_method_scope(c)
    c=contract()
    bag=next(x for x in c["original_arms"] if x["code"]=="bag")
    bag["selective_bract_photosynthesis_disabled"]=True
    with pytest.raises(ValueError,match="bract-only light intervention"):
        audit_dalechampia_method_scope(c)


def test_foil_effect_cannot_promote_carbon_or_BALANCE():
    c=contract()
    c["identification"]["cause_of_seed_mass_effect_isolated_to_bract_carbon"]=True
    with pytest.raises(ValueError,match="cause_of_seed_mass_effect"):
        audit_dalechampia_method_scope(c)
    c=contract()
    c["identification"]["structural_architecture_BALANCE_occupancy_identified"]=True
    with pytest.raises(ValueError,match="structural_architecture_BALANCE"):
        audit_dalechampia_method_scope(c)
    c=contract()
    c["identification"]["new_independent_biological_clusters"]=1
    with pytest.raises(ValueError,match="cannot be counted anew"):
        audit_dalechampia_method_scope(c)


def test_historical_cut_control_cannot_be_reinterpreted_as_foil_control():
    c=contract()
    cutcont=next(x for x in c["original_arms"] if x["code"]=="cutcont")
    cutcont["foil_entire_blossom"]=True
    with pytest.raises(ValueError,match="cutcont source intervention"):
        audit_dalechampia_method_scope(c)


def test_dryad_wrong_hash_size_or_missing_file_never_enters_reanalysis():
    c=contract()
    fn1,size1,_=FILE_IDENTITIES[46163]
    fn2,size2,_=FILE_IDENTITIES[46164]
    with pytest.raises(ValueError,match="both exact named"):
        verify_exact_dryad_bytes(c,{fn1:b"x"*size1})
    with pytest.raises(ValueError,match="byte size"):
        verify_exact_dryad_bytes(c,{fn1:b"abc",fn2:b"x"*size2})
    # Matches a plausible file size but NOT original immutable Dryad MD5.
    with pytest.raises(ValueError,match="source MD5"):
        verify_exact_dryad_bytes(c,{fn1:b"x"*size1,fn2:b"x"*size2})


def test_metadata_runner_creates_hash_receipt_without_claiming_data(tmp_path):
    orig=SOURCE.read_bytes()
    result_file=tmp_path/"method_scope.json"
    receipt=build_receipt(SOURCE,result_file)
    assert receipt["source_contract_sha256"]==hashlib.sha256(orig).hexdigest()
    assert receipt["raw_file_bytes_verified"] is False
    assert receipt["raw_reanalysis_executed"] is False
    assert receipt["direct_mechanism_and_BALANCE_not_identified"] is True
    assert json.loads(result_file.read_text(encoding="utf-8"))==receipt
    assert SOURCE.read_bytes()==orig
    with pytest.raises(ValueError,match="already exists"):
        build_receipt(SOURCE,result_file)


def test_runner_requires_both_data_files_and_never_uses_placeholders(tmp_path):
    p=tmp_path/"one.txt";p.write_text("fake",encoding="utf-8")
    with pytest.raises(ValueError,match="both original Dryad seed and gas"):
        build_receipt(SOURCE,tmp_path/"out.json",seed_file=p)
    assert not (tmp_path/"out.json").exists()


def test_forged_public_raw_acquisition_status_requires_new_version():
    c=contract()
    c["source_access"]["raw_file_bytes_acquired_in_this_study"]=True
    with pytest.raises(ValueError,match="raw_file_bytes_acquired"):
        audit_dalechampia_method_scope(c)


def test_bad_archive_file_id_md5_or_version_fails_closed():
    c=contract()
    c["dryad_source_files"][0]["md5"]="0"*32
    with pytest.raises(ValueError,match="identity drift"):
        audit_dalechampia_method_scope(c)
    c=contract()
    c["dryad_version_id"]=11210
    with pytest.raises(ValueError,match="version ID"):
        audit_dalechampia_method_scope(c)

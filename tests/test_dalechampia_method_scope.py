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


def test_synthetic_exact_bytes_path_preserves_plant_blossom_seed_nesting(monkeypatch):
    """Artificial tiny text fixtures; NOT authentic Dryad biological observations."""
    import csv
    import hashlib
    import io
    import balance_domain.dalechampia_method_scope as m

    def tsv(fields, records):
        f=io.StringIO()
        writer=csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
        return f.getvalue().encode("utf-8")

    seeds=tsv(
        ["FemaleID","MaleID","crossID","treatcode","seedID","seedmass","seedset","ped"],
        [
            {"FemaleID":"M1","MaleID":"F1","crossID":"B1","treatcode":"bag","seedID":"1","seedmass":"33","seedset":"2","ped":"1"},
            {"FemaleID":"M1","MaleID":"F1","crossID":"B1","treatcode":"bag","seedID":"2","seedmass":"32","seedset":"2","ped":"1"},
            {"FemaleID":"M1","MaleID":"F2","crossID":"B2","treatcode":"cont","seedID":"1","seedmass":"40","seedset":"1","ped":"1"},
            {"FemaleID":"M2","MaleID":"F3","crossID":"B3","treatcode":"cut","seedID":"1","seedmass":"31","seedset":"1","ped":"2"},
            {"FemaleID":"M3","MaleID":"F4","crossID":"B4","treatcode":"cutcont","seedID":"1","seedmass":"34","seedset":"1","ped":"2"},
        ]
    )
    gases=tsv(
        ["Plant_ID","Color","Replicate","Bract","AN","R","GPP","GPPnett"],
        [
            {"Plant_ID":"P1","Color":"white","Replicate":"1","Bract":"Bract","AN":"0.4","R":"-1","GPP":"1.4","GPPnett":"1.2"},
            {"Plant_ID":"P1","Color":"white","Replicate":"1","Bract":"No_Bract","AN":"0.1","R":"-0.1","GPP":"0.2","GPPnett":""},
            {"Plant_ID":"P2","Color":"green","Replicate":"1","Bract":"Bract","AN":"1.2","R":"-1","GPP":"2.2","GPPnett":"1.9"},
        ]
    )
    names={46163:"synthetic_seed.tsv",46164:"synthetic_gas.tsv"}
    by_id={46163:seeds,46164:gases}
    monkeypatch.setattr(m,"FILE_IDENTITIES",{
        k:(names[k],len(v),hashlib.md5(v).hexdigest()) for k,v in by_id.items()
    })
    contract_synthetic=contract()
    for entry in contract_synthetic["dryad_source_files"]:
        id_=entry["source_file_id"]
        entry["name"],entry["size_bytes"],entry["md5"]=m.FILE_IDENTITIES[id_]
    result=m.verify_exact_dryad_bytes(contract_synthetic,{
        names[46163]:seeds,names[46164]:gases
    })
    assert result["status"]=="EXACT_DRYAD_BYTES_VERIFIED_SUPPORT_ONLY_NO_MODELS"
    assert result["raw_file_bytes_verified"] is True
    assert result["raw_seed_records"]==5
    assert result["raw_treatment_seed_rows"]=={"bag":2,"cont":1,"cut":1,"cutcont":1}
    assert result["raw_independent_blossoms"]==4
    assert result["raw_independent_maternal_plants"]==3
    assert result["raw_treatment_maternal_plants"]=={
        "bag":1,"cut":1,"cutcont":1,"cont":1
    }
    assert result["raw_gas_exchange_rows"]==3
    assert result["raw_gas_exchange_plant_replicate_units"]==2
    assert result["raw_row_counts_equal_published_total_per_arm"] is False
    assert result["published_abortions_reconstructed"] is False
    assert result["source_original_mixed_model_reproduced"] is False
    assert result["raw_reanalysis_executed"] is False
    assert result["structural_BALANCE_identified"] is False


def test_source_nesting_parser_rejects_duplicate_seeds_within_blossom():
    import balance_domain.dalechampia_method_scope as m
    fake=b"FemaleID\tMaleID\tcrossID\ttreatcode\tseedID\tseedmass\tseedset\tped\nM1\tF1\tB1\tbag\t1\t30\t2\t1\nM1\tF1\tB1\tbag\t1\t31\t2\t1\n"
    rows,fields,norm=m._table(fake,["FemaleID","MaleID","crossID","treatcode","seedID","seedmass","seedset","ped"],"test")
    assert len(rows)==2
    assert rows[0]["seedID"]==rows[1]["seedID"]
    # The actual end-to-end duplicate guard is in verify_exact_dryad_bytes
    # after original MD5; no seed is a legitimate independent plant replicate.


def test_original_latin1_decimal_comma_and_missing_mass_contract():
    from balance_domain.dalechampia_method_scope import parse_source_decimal
    assert parse_source_decimal("38,83","seedmass") == 38.83
    assert parse_source_decimal("38.83","gas") == 38.83
    assert parse_source_decimal("0,01","small") == 0.01
    assert parse_source_decimal("NA","missing") is None
    assert parse_source_decimal("","missing") is None
    with pytest.raises(ValueError, match="cannot be missing"):
        parse_source_decimal("NA","mandatory",allow_missing=False)
    for bad in ("1,234,567", "1.000,4", "1,2,3", "Infinity", "1e309", "fifteen"):
        with pytest.raises(ValueError, match="decimal format"):
            parse_source_decimal(bad,"seedmass")
    with pytest.raises(ValueError, match="original source text"):
        parse_source_decimal(38.83,"seedmass")

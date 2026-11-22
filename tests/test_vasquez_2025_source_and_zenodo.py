"""Versioned-source and Zenodo source-access tests (synthetic fixtures only)."""
import hashlib
import json
from math import exp

import pytest

from balance_domain.vasquez_2025_pollen_fates import (
    build_source_pollen_fates, source_values
)
from scripts.audit_vasquez_2025_zenodo import (
    API,
    inspect_file_bytes,
    source_access_audit,
    validate_record_metadata,
    official_http_bytes,
)


def test_one_original_programme_and_two_species_trial_grain():
    s=source_values()
    assert s["article"]["doi"]=="10.26786/1920-7603(2025)836"
    assert s["dataset"]["record_id"]==17102653
    assert s["dataset"]["raw_original_trials_retrieved"] is False
    assert s["design"]["completed_donor_trials"]=={
        "Solanum rostratum":6,"Solanum dulcamara":9
    }
    assert s["design"]["recipient_stigmas_per_trial"]==4
    assert s["design"]["recipient_stigmas_total"]==60
    assert s["scientific_ceiling"]["no_genetic_donor_paternity"] is True


def test_original_group_fate_roundoff_not_raw_trial_estimates():
    r=build_source_pollen_fates()
    assert r["n_independent_study_programmes"]==1
    assert r["n_donor_trials"]==15
    assert r["original_zenodo_raw_csv_rows_analyzed"]==0
    assert r["male_genetic_paternity_identified"] is False
    rows={x["species"]:x for x in r["species_fates"]}
    assert rows["Solanum rostratum"]["fate_pct_of_removed"]=={
        "ground":62.99,"basket":27.65,"body":8.54,"stigmas":0.86
    }
    assert rows["Solanum dulcamara"]["fate_pct_of_removed"]=={
        "ground":19.07,"basket":65.92,"body":14.01,"stigmas":1.00
    }
    assert abs(rows["Solanum rostratum"]["fate_pct_rounding_sum"]-100)<0.06
    assert abs(rows["Solanum dulcamara"]["fate_pct_rounding_sum"]-100)<0.06
    diff=r["source_species_contrast_descriptive"]
    assert diff["ground_loss_rostratum_minus_dulcamara_pct_points"]==pytest.approx(43.92)
    assert diff["basket_gain_dulcamara_minus_rostratum_pct_points"]==pytest.approx(38.27)
    assert diff["stigma_PTE_dulcamara_minus_rostratum_pct_points"]==pytest.approx(.14)
    assert diff["donor_fraction_removed_dulcamara_over_rostratum"]==pytest.approx(
        37.77/13.55
    )
    assert rows["Solanum rostratum"][
        "descriptive_product_of_two_group_means_pct_produced_to_stigmas"
    ]==pytest.approx(.11653)
    assert rows["Solanum dulcamara"][
        "descriptive_product_of_two_group_means_pct_produced_to_stigmas"
    ]==pytest.approx(.3777)
    assert diff["contrast_tested_on_original_trials_here"] is False


def test_four_recipients_exponential_tail_only_a_model_identity():
    r=build_source_pollen_fates()["model_based_carryover"]
    p=exp(-.339)
    assert r["per_recipient_retention_ratio"]==pytest.approx(p)
    assert r["model_only_missing_fraction_if_only_four_recipients"]==pytest.approx(
        1-sum(p**j for j in range(4))/sum(p**j for j in range(20))
    )
    assert r["not_new_empirical_stigma_count_or_GLM_fitting"] is True


def sample_metadata(payload=b"trial,ground,basket,stigma\nA,3,1,1\n"):
    return {
        "id":17102653,
        "metadata":{"title":"Pollen fates in two Solanum species",
                    "description":"Synthetic API response for tests only"},
        "files":[{
            "key":"test.csv",
            "size":len(payload),
            "checksum":"md5:"+hashlib.md5(payload).hexdigest(),
            "links":{"self":"https://zenodo.org/api/records/17102653/files/test.csv/content"}
        }]
    }


def test_offline_does_not_try_network_or_claim_original_data():
    result=source_access_audit(online=False,request_bytes=lambda *args:(
        (_ for _ in ()).throw(AssertionError("Unexpected network"))
    ))
    assert result["status"]=="OFFLINE_NOT_ATTEMPTED"
    assert result["raw_trial_data_analyzed"] is False
    assert result["new_biological_effects_estimated"]==0
    assert result["original_trial_level_model_reproduction"]=="NOT_PERFORMED"


def test_synthetic_zenodo_metadata_schema_and_no_fake_effects():
    fake=b"trial,ground,basket,stigma\nA,3,1,1\n"
    meta=json.dumps(sample_metadata(fake)).encode()
    calls=[]
    def source_fetch(url,n):
        calls.append(url)
        return meta if url==API else fake
    out=source_access_audit(online=True,request_bytes=source_fetch)
    assert len(calls)==2
    assert out["status"]=="SOURCE_FILE_SCHEMAS_VERIFIED_NO_EFFECT_FITS"
    assert out["record_id"]==17102653
    assert out["raw_trial_data_analyzed"] is False
    assert out["new_biological_effects_estimated"]==0
    f=out["files"][0]
    assert f["retrieval"]=="DOWNLOADED_FILE_SCHEMA_VERIFIED"
    assert f["verified_file_schema"]["row_count_not_independent_trials"]==1
    assert f["verified_file_schema"]["columns"]==[
        "trial","ground","basket","stigma"
    ]
    assert "A,3,1,1" not in json.dumps(out)


@pytest.mark.parametrize("wrong", [
    {"id":123,"metadata":{"title":"pollen"},"files":[]},
    {"id":17102653,"metadata":{"title":"unrelated chemistry"},"files":[]},
    {"id":17102653,"metadata":{"title":"Solanum"},"files":[]},
    {"id":17102653,"metadata":{"title":"Solanum"},"files":[
        {"key":"a.csv","size":2,"links":{}},
        {"key":"a.csv","size":3,"links":{}},
    ]},
])
def test_wrong_archive_or_missing_files_fail_closed(wrong):
    with pytest.raises(ValueError):
        validate_record_metadata(wrong)


def test_original_source_md5_and_ragged_csv_fail_closed():
    fake=b"trial,stigma\nA,10\n"
    entry={
        "name":"original.csv","bytes":len(fake),
        "zenodo_checksum":"md5:"+hashlib.md5(fake).hexdigest(),
    }
    assert inspect_file_bytes(entry,fake)["row_count_not_independent_trials"]==1
    with pytest.raises(ValueError,match="MD5"):
        inspect_file_bytes(entry,fake.replace(b"10",b"11"))
    with pytest.raises(ValueError):
        inspect_file_bytes({**entry,"bytes":3},fake)


def test_official_request_never_issues_to_mismatched_record_or_external_domain():
    with pytest.raises(ValueError):
        official_http_bytes("https://evil.example.com/api/records/17102653",100)
    with pytest.raises(ValueError):
        official_http_bytes("https://zenodo.org/api/records/0000/files/test.csv",100)

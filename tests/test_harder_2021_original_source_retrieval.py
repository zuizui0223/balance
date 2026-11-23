"""Only synthetic source fixtures for original orchid Zenodo authenticity gates."""
import csv
import hashlib
import io

import pytest

from scripts import audit_harder_2021_zenodo_mirror as audit


def make_synthetic_source():
    buf=io.StringIO()
    writer=csv.writer(buf)
    writer.writerow(["Trial_type","Trial","M_init","R","Visit","Deposition"])
    for treatment,n in (("Emasculated",16),("Intact",15)):
        for index in range(1,n+1):
            for visit in range(1,5):
                writer.writerow([treatment,index,200,2,visit,3 if treatment=="Intact" else 4])
    return buf.getvalue().encode("utf-8")


def synthetic_api(record_id=audit.RECORD_ID,checksum=audit.MD5):
    return {
        "id":record_id,
        "doi":audit.DRYAD_DOI,
        "metadata":{"title":"Mechanisms of male-male interference during dispersal of orchid pollen"},
        "files":[{
            "key":audit.FILE,"size":8050,
            "checksum":"md5:"+checksum,
            "links":{"self":f"https://zenodo.org/api/records/{audit.RECORD_ID}/files/{audit.FILE}/content"},
        }],
    }


def test_source_paper_and_mirror_identifiers_are_fixed():
    assert audit.RECORD_ID==4072200
    assert audit.PAPER_DOI=="10.1086/712378"
    assert audit.DRYAD_DOI=="10.5061/dryad.41ns1rnc0"
    assert audit.MD5=="650e40ae7ebb41bdfb333dcf63c63c71"
    assert audit.FILE=="Data_for_AmNat.csv"


def test_31_trial_synthetic_structure_is_not_called_ecological_refit(monkeypatch):
    original=make_synthetic_source()
    monkeypatch.setattr(audit,"MD5",hashlib.md5(original).hexdigest())
    source={
        "analysis":"synthetic_test_only","md5":audit.MD5,
        "raw_data_effects_estimated":0,
    }
    got=audit.source_schema_audit(original,source)
    assert got["independent_donor_visit_sequences"]==31
    assert got["source_recipient_rows"]==124
    assert got["original_treatment_trial_counts"]=={"Emasculated":16,"Intact":15}
    assert got["raw_data_effects_estimated"]==0
    assert got["recipient_rows_not_independent_trial_replicates"] is True
    assert got["source_pollen_export_not_genetic_siring"] is True


def test_incomplete_trial_or_wrong_source_bytes_fail_closed(monkeypatch):
    original=make_synthetic_source()
    with pytest.raises(ValueError,match="non-original"):
        audit.source_schema_audit(original,{})
    monkeypatch.setattr(audit,"MD5",hashlib.md5(original).hexdigest())
    wrong=original.replace(b"Intact",b"Unknown")
    with pytest.raises(ValueError,match="non-original"):
        audit.source_schema_audit(wrong,{})
    with pytest.raises(ValueError,match="16 emasculated"):
        audit.source_schema_audit(original.replace(b"Intact",b"Emasculat"),{})


def test_authentic_file_manifest_rejects_wrong_record_and_checksum():
    import json
    original=make_synthetic_source()
    meta=synthetic_api()
    payload=json.dumps(meta).encode()
    def get(url,max_bytes):
        return payload if url==audit.API else original
    with pytest.raises(ValueError,match="MD5"):
        audit.verified_original_source(fetcher=get)
    meta["id"]=123
    payload=json.dumps(meta).encode()
    with pytest.raises(ValueError,match="record"):
        audit.verified_original_source(fetcher=get)

"""No-network synthetic tests for archived Dryad acquisition and fail-closed controls.

Synthetic ZIPs and text records are *not* the published Dalechampia observations.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.error
import zipfile
from pathlib import Path

import pytest

import balance_domain.dalechampia_method_scope as scope
import scripts.retrieve_dalechampia_2015_dryad_bytes as retrieve


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/DALECHAMPIA_POSTANTHESIS_METHOD_AND_DRYAD_V2.json"


def _zip(members):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for n, value in members.items():
            z.writestr(n,value)
    return buffer.getvalue()


def _tsv(headers, records):
    b=io.StringIO()
    w=csv.DictWriter(b,fieldnames=headers,delimiter="\t",lineterminator="\n")
    w.writeheader()
    w.writerows(records)
    return b.getvalue().encode("utf-8")


def _fixture_pair(monkeypatch):
    seed=_tsv(["FemaleID","MaleID","crossID","treatcode","seedID","seedmass","seedset","ped"],[
        {"FemaleID":"P1","MaleID":"Q1","crossID":"B1","treatcode":"cont","seedID":"1","seedmass":"36","seedset":"1","ped":"1.0"},
        {"FemaleID":"P2","MaleID":"Q2","crossID":"B2","treatcode":"bag","seedID":"1","seedmass":"31","seedset":"1","ped":"1.1"},
        {"FemaleID":"P3","MaleID":"Q3","crossID":"B3","treatcode":"cut","seedID":"1","seedmass":"32","seedset":"1","ped":"1.2"},
        {"FemaleID":"P4","MaleID":"Q4","crossID":"B4","treatcode":"cutcont","seedID":"1","seedmass":"34","seedset":"1","ped":"1.3"},
    ])
    gas=_tsv(["Plant_ID","Color","Replicate","Bract","AN","R","GPP","GPPnett"],[
        {"Plant_ID":"G1","Color":"green","Replicate":"1","Bract":"Bract",
         "AN":"2","R":"-1","GPP":"3","GPPnett":"2"},
        {"Plant_ID":"G1","Color":"green","Replicate":"1","Bract":"No_Bract",
         "AN":"0","R":"-0.2","GPP":"0.2","GPPnett":""},
    ])
    names={46163:"Pelabon et al FE file 1.txt",46164:"Pelabon et al FE file 2.txt"}
    files={names[46163]:seed,names[46164]:gas}
    identities={
        k:(names[k],len(raw),hashlib.md5(raw).hexdigest())
        for k,raw in [(46163,seed),(46164,gas)]
    }
    monkeypatch.setattr(retrieve,"FILE_IDENTITIES",identities)
    monkeypatch.setattr(scope,"FILE_IDENTITIES",identities)
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    for f in c["dryad_source_files"]:
        f["name"],f["size_bytes"],f["md5"]=identities[f["source_file_id"]]
    return files,c


def test_original_unavailable_is_explicit_hold_not_new_fitness_data(tmp_path):
    def broken(url):
        raise urllib.error.HTTPError(url,401,"Access denied",{},None)
    out=tmp_path/"receipt.json"
    data=retrieve.retrieve(CONTRACT,tmp_path/"raw",out,download=broken)
    assert data["status"]=="ORIGINAL_SOURCE_DOWNLOAD_HOLD"
    assert data["raw_file_bytes_verified"] is False
    assert data["raw_reanalysis_executed"] is False
    assert data["bract_local_carbon_causally_identified"] is False
    assert data["structural_BALANCE_identified"] is False
    assert out.exists()
    assert not (tmp_path/"raw").exists()


def test_archived_version_zip_requires_exact_two_original_named_files(monkeypatch):
    files,_ = _fixture_pair(monkeypatch)
    good=_zip(files)
    result=retrieve._verify_version_zip(good)
    assert result==files
    assert retrieve._digest_ok(next(iter(files)),next(iter(files.values())))
    with pytest.raises(ValueError,match="two files"):
        retrieve._verify_version_zip(_zip({next(iter(files)):next(iter(files.values()))}))
    with pytest.raises(ValueError,match="unsafe"):
        retrieve._verify_version_zip(_zip({"../Pelabon et al FE file 1.txt":list(files.values())[0],
                                          "Pelabon et al FE file 2.txt":list(files.values())[1]}))


def test_verifier_rejects_valid_zip_format_with_changed_source_content(monkeypatch):
    files,_=_fixture_pair(monkeypatch)
    altered=dict(files)
    changed=list(files)[0]
    altered[changed]=altered[changed].replace(b"36",b"39")
    with pytest.raises(ValueError,match="member MD5 changed"):
        retrieve._verify_version_zip(_zip(altered))


def test_official_individual_url_fallback_requires_both_authenticated(monkeypatch):
    files,_=_fixture_pair(monkeypatch)
    def download(url):
        if url==retrieve.SOURCE_ZIP_URL:
            raise urllib.error.HTTPError(url,401,"blocked",{},None)
        if "/downloads/file_stream/" in url:
            return files[list(files)[0]] if url.endswith("46163") else files[list(files)[1]]
        raise AssertionError("fallback should stop after both official file streams")
    recovered,source=retrieve.recover_original_pair(download)
    assert source=="OFFICIAL_FILE_DOWNLOADS"
    assert recovered==files


def test_successful_fake_source_still_has_zero_statistical_replay(monkeypatch,tmp_path):
    files, contract = _fixture_pair(monkeypatch)
    p=tmp_path/"freeze.json"
    p.write_text(json.dumps(contract),encoding="utf-8")
    payload=_zip(files)
    receipt=tmp_path/"receipt.json"
    def download(url):
        assert url==retrieve.SOURCE_ZIP_URL
        return payload
    data=retrieve.retrieve(p,tmp_path/"raw",receipt,download=download)
    assert data["status"]=="ORIGINAL_DRYAD_BYTES_AND_ROW_SUPPORT_VERIFIED_NO_MODEL"
    assert data["raw_file_bytes_verified"] is True
    assert data["row_support"]["raw_independent_maternal_plants"] == 4
    assert data["row_support"]["raw_independent_blossoms"] == 4
    assert data["raw_reanalysis_executed"] is False
    assert data["is_original_mixed_model_replay"] is False
    assert data["bract_local_carbon_causally_identified"] is False
    assert data["source_route"]=="ARCHIVED_VERSION_ZIP"
    assert json.loads(receipt.read_text(encoding="utf-8"))==data
    assert all((tmp_path/"raw"/name).read_bytes()==raw for name,raw in files.items())
    with pytest.raises(ValueError,match="already exists"):
        retrieve.retrieve(p,tmp_path/"raw",receipt,download=download)


def test_authenticated_bytes_with_unresolved_parser_are_saved_as_hold(monkeypatch,tmp_path):
    files,c=_fixture_pair(monkeypatch)
    first=list(files)[0]
    files[first]=b"not,a,seed,mass\n"  # valid archive only after new identity frozen
    fixed={
        k:(name,len(files[name]),hashlib.md5(files[name]).hexdigest())
        for k,(name,_,_) in retrieve.FILE_IDENTITIES.items()
    }
    monkeypatch.setattr(retrieve,"FILE_IDENTITIES",fixed)
    monkeypatch.setattr(scope,"FILE_IDENTITIES",fixed)
    for f in c["dryad_source_files"]:
        f["name"],f["size_bytes"],f["md5"]=fixed[f["source_file_id"]]
    path=tmp_path/"contract.json";path.write_text(json.dumps(c),encoding="utf-8")
    data=retrieve.retrieve(path,tmp_path/"raw",tmp_path/"receipt.json",
        download=lambda url:_zip(files))
    assert data["status"]=="ORIGINAL_DRYAD_BYTES_VERIFIED_PARSER_HOLD"
    assert data["raw_file_bytes_verified"] is True
    assert data["parser_hold"]["type"]=="ValueError"
    assert data["raw_reanalysis_executed"] is False
    assert (tmp_path/"raw"/first).read_bytes()==files[first]


def test_zero_overwrite_and_contract_schema_guard(tmp_path):
    p=tmp_path/"already.json";p.write_text("existing",encoding="utf-8")
    with pytest.raises(ValueError,match="already exists"):
        retrieve.retrieve(CONTRACT,tmp_path/"raw",p,download=lambda _:b"")
    assert p.read_text()=="existing"
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    c["original_arms"][0]["selective_bract_photosynthesis_disabled"]=True
    bad=tmp_path/"bad.json";bad.write_text(json.dumps(c),encoding="utf-8")
    with pytest.raises(ValueError,match="bract-only light intervention"):
        retrieve.retrieve(bad,tmp_path/"raw",tmp_path/"new.json",download=lambda _:b"")

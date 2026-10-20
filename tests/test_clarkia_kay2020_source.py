"""Trust boundary for original public Dryad source; fixture is synthetic."""
from __future__ import annotations

import csv
from io import BytesIO, StringIO
import json
import zipfile
import pytest

from balance_domain.clarkia_kay2020_source import (
    SOURCE_FILES, DATA_DOI, inspect_archive, inspect_file, _member_basename,
)


def fake_metadata():
    return {"identifier":"doi:"+DATA_DOI,"versionNumber":1,
            "title":"Synthetic source fixture","license":"CC0"}


def input_archive(change=None):
    handle=BytesIO()
    with zipfile.ZipFile(handle,"w") as z:
        for name in SOURCE_FILES:
            if change is not None and name==change:
                continue
            if name.endswith(".csv"):
                output=StringIO()
                writer=csv.DictWriter(output,fieldnames=["species","mode","response"])
                writer.writeheader()
                writer.writerows([
                    {"species":"Clarkia a","mode":"source","response":1},
                    {"species":"Clarkia b","mode":"response","response":2},
                    {"species":"Clarkia c","mode":"source","response":3},
                ])
                content=output.getvalue()
            else:
                content="#NEXUS\nBegin trees; Tree tree1=(A,B); End;\n"
            z.writestr("Dryad_Dataset/"+name,content)
    return handle.getvalue()


def test_original_zip_gate_and_source_record_provenance():
    result=inspect_archive(input_archive(),fake_metadata())
    assert result["source_file_count"]==len(SOURCE_FILES)
    assert result["status"]=="ORIGINAL_ARCHIVE_SCHEMAS_VERIFIED_NO_NEW_BIOLOGICAL_EFFECT_YET"
    assert result["no_new_evolutionary_causal_origin"] is True
    p=result["source_files"]["pollen_data.csv"]
    assert p["source_data_rows"]==3
    assert p["columns"]==["species","mode","response"]
    assert p["low_cardinality_field_histograms"]["mode"]=={
        "source":2,"response":1
    }
    assert p["source_rows_distributed"] is False


def test_missing_outcome_data_fails_instead_of_implicit_negative():
    with pytest.raises(ValueError,match="required files absent"):
        inspect_archive(input_archive("pollen_data.csv"),fake_metadata())


def test_dataset_identity_fails_closed():
    meta=fake_metadata()
    meta["identifier"]="doi:10.5061/dryad.WRONG"
    with pytest.raises(ValueError,match="DOI mismatch"):
        inspect_archive(input_archive(),meta)


def test_zip_member_traversal_and_ambiguous_rename_fails():
    with pytest.raises(ValueError,match="unsafe"):
        _member_basename("../stolen.csv")
    with pytest.raises(ValueError,match="unsafe"):
        _member_basename("/tmp/stolen.csv")
    with pytest.raises(ValueError,match="unsafe"):
        _member_basename("folder\\attack.csv")


def test_pseudo_replicated_source_headers_fail():
    with pytest.raises(ValueError,match="duplicate source columns"):
        inspect_file("pollen_data.csv",b"id,id\n1,2\n")
    with pytest.raises(ValueError,match="malformed extra columns"):
        inspect_file("pollen_data.csv",b"x,y\n1,2,3\n")

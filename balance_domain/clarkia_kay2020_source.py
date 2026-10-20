"""Dryad original-data acquisition for Kay et al. 2020 Clarkia heteranthery.

This dataset is an OUTCOME-DISCOVERED independent mechanism/challenge system,
not an outcome-blind plant sampling frame. The work distinguishes:
  visible heteranthery, concurrent pollen-role specialization, and staggered
  temporal pollen release.
See DOI 10.1098/rspb.2020.2593 and source archive DOI
10.5061/dryad.8cz8w9gmp. Download bytes only into memory and write a
source-provenance summary; do not commit third-party raw source records.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
from io import BytesIO, StringIO
import json
from pathlib import Path, PurePosixPath
import zipfile
from urllib.parse import quote
from urllib.request import Request, urlopen

DATA_DOI = "10.5061/dryad.8cz8w9gmp"
PAPER_DOI = "10.1098/rspb.2020.2593"
API = "https://datadryad.org/api/v2"
ENCODED_DOI = quote("doi:" + DATA_DOI, safe="")
DATASET_URL = f"{API}/datasets/{ENCODED_DOI}"
DOWNLOAD_URL = DATASET_URL + "/download"
SOURCE_FILES = {
    "clarkia_phenotype_heteranthery.csv",
    "time_lapse_data.csv",
    "pollen_data.csv",
    "pollen_available.csv",
    "cungseeds.csv",
    "cungmanipulative.csv",
    "clarkiaits.nex",
}
MAX_ZIP_BYTES=70_000_000
MAX_SOURCE_ROWS=200_000


def _fetch_bytes(url: str, limit: int) -> bytes:
    if not url.startswith("https://datadryad.org/"):
        raise ValueError("source request must stay on Dryad's HTTPS host")
    headers={
        "Accept": "application/json" if "/download" not in url else "application/zip",
        "User-Agent": "BALANCE-source-audit/1.0 (scientific reproducibility)",
    }
    req=Request(url,headers=headers)
    with urlopen(req,timeout=70) as r:
        data=r.read(limit+1)
    if len(data)>limit:
        raise ValueError("Downloaded source exceeds registered size limit")
    return data


def _json(url: str) -> dict:
    blob=_fetch_bytes(url,1_000_000)
    val=json.loads(blob.decode("utf-8-sig"))
    if not isinstance(val,dict):
        raise ValueError("Dryad API response should be a JSON object")
    return val


def _member_basename(raw: str) -> str:
    if raw.startswith("/") or ".." in PurePosixPath(raw).parts or "\\" in raw:
        raise ValueError("unsafe Dryad ZIP member path")
    return PurePosixPath(raw).name.lower()


def _decode_source(blob: bytes) -> str:
    try:
        return blob.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Legacy R field files can be ISO-8859-1. Record decode choice in receipt.
        return blob.decode("latin-1")


def inspect_file(name: str, blob: bytes) -> dict:
    file_info={
        "filename":name,
        "sha256":hashlib.sha256(blob).hexdigest(),
        "byte_length":len(blob),
        "source_rows_distributed":False,
    }
    if not name.lower().endswith(".csv"):
        file_info["format"]="PHYLOGENY_NEXUS" if name.lower().endswith(".nex") else "AUXILIARY"
        file_info["line_count"]=len(_decode_source(blob).splitlines())
        return file_info
    text=_decode_source(blob)
    if not text.strip():
        raise ValueError("empty source CSV: "+name)
    csvreader=csv.DictReader(StringIO(text))
    fields=csvreader.fieldnames
    if not fields or len(fields)!=len(set(fields)):
        raise ValueError("missing/duplicate source columns "+name)
    counter=0
    value_counts={k:Counter() for k in fields}
    examples=[]
    for row in csvreader:
        counter+=1
        if counter>MAX_SOURCE_ROWS:
            raise ValueError("source CSV exceeds registered record count")
        if None in row:
            raise ValueError("malformed extra columns in source CSV "+name)
        if counter<=2:
            examples.append({k:str(row[k] or "")[:65] for k in fields[:12]})
        for key in fields:
            cell=str(row.get(key) or "").strip()
            value_counts[key][cell]+=1
    categories={}
    for key,hist in value_counts.items():
        if len(hist)<=20 and counter>=3:
            categories[key] = dict(sorted(hist.items(),key=lambda x:(-x[1],x[0]))) 
    file_info.update({
        "format":"CSV",
        "source_data_rows":counter,
        "columns":fields,
        "first_two_row_schema_examples_for_audit_only":examples,
        "low_cardinality_field_histograms":categories,
        "no_statistical_fit_yet":True,
    })
    return file_info


def inspect_archive(download: bytes, metadata: dict) -> dict:
    if str(metadata.get("identifier","")).lower()!="doi:"+DATA_DOI.lower():
        raise ValueError("Dryad metadata DOI mismatch")
    if not zipfile.is_zipfile(BytesIO(download)):
        raise ValueError("Expected direct zipped original Dryad dataset")
    files={}
    with zipfile.ZipFile(BytesIO(download)) as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            if item.file_size>25_000_000:
                raise ValueError("Unexpected large source member")
            basename=_member_basename(item.filename)
            if basename in files:
                raise ValueError("ambiguous duplicate source filename "+basename)
            blob=z.read(item)
            files[basename]=inspect_file(item.filename,blob)
    missing=sorted(SOURCE_FILES-set(files))
    # A source admission failure is distinct from any biological negative.
    if missing:
        raise ValueError("Dryad original study required files absent: "+str(missing))
    selection={
        "schema":"BALANCE_CLARKIA_KAY2020_DRYAD_SOURCE_ACQUISITION_V1",
        "status":"ORIGINAL_ARCHIVE_SCHEMAS_VERIFIED_NO_NEW_BIOLOGICAL_EFFECT_YET",
        "paper_doi":PAPER_DOI,
        "dataset_doi":DATA_DOI,
        "dataset_version_number":metadata.get("versionNumber"),
        "dataset_licence":metadata.get("license"),
        "dataset_title":metadata.get("title"),
        "download_zip_sha256":hashlib.sha256(download).hexdigest(),
        "download_zip_bytes":len(download),
        "source_file_count":len(files),
        "required_source_files":sorted(SOURCE_FILES),
        "source_files":dict(sorted(files.items())),
        "scope":"outcome-discovered original experiment and phylogenetic character data; NOT random taxa",
        "publication_conclusions_are_not_independent_results_of_this_schema_audit":True,
        "heteranthery_does_not_necessarily_mean_pollen_role_division":True,
        "no_new_evolutionary_causal_origin":True,
    }
    return selection


def fetch_and_inspect(output_path: Path) -> dict:
    metadata=_json(DATASET_URL)
    data=_fetch_bytes(DOWNLOAD_URL,MAX_ZIP_BYTES)
    result=inspect_archive(data,metadata)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    with output_path.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,ensure_ascii=False)
        f.write("\n")
    return result

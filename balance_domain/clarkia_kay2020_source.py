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



# Dataset version 97733 and its public 29-file manifest were verified on
# Dryad on 2026-10-20. API archive/file download requires OAuth; landing-
# page file_stream endpoints remain public but all bytes must match API SHA.
PINNED_VERSION=97733
VERSION_FILES_URL=f"{API}/versions/{PINNED_VERSION}/files?per_page=100"


def _public_registry(payload: dict) -> dict:
    rows=(payload.get("_embedded") or {}).get("stash:files")
    if payload.get("total") != 29 or not isinstance(rows,list) or len(rows)!=29:
        raise ValueError("Pinned Dryad 29-file manifest unavailable or changed")
    by_name={}
    for row in rows:
        key=_member_basename(row.get("path",""))
        if not key or key in by_name:
            raise ValueError("Duplicate or unnamed Dryad source file")
        by_name[key]=row
    if not SOURCE_FILES.issubset(by_name):
        raise ValueError("Required Clarkia source tables are absent")
    out={}
    for name in sorted(SOURCE_FILES):
        row=by_name[name]
        href=((row.get("_links") or {}).get("self") or {}).get("href","")
        if not href.startswith("/api/v2/files/") or not href.rsplit("/",1)[-1].isdigit():
            raise ValueError("Unrecognized source file ID")
        digest=str(row.get("digest","")).lower()
        if row.get("digestType","").lower() not in {"sha-256","sha256"} or len(digest)!=64:
            raise ValueError("No source-authored file SHA256")
        size=int(row.get("size") or 0)
        if size<=0 or size>25_000_000:
            raise ValueError("Source file size outside budget")
        out[name]={"id":href.rsplit("/",1)[-1],"sha256":digest,
                   "size":size,"name":row["path"]}
    return {"files":out,"source_original_file_count":len(by_name),
            "bombustrials2018_csv_missing":"bombustrials2018.csv" not in by_name}


def inspect_public_files(blobs: dict[str,bytes], metadata: dict, manifest: dict) -> dict:
    if str(metadata.get("identifier","")).lower()!="doi:"+DATA_DOI:
        raise ValueError("Dryad dataset DOI changed")
    files=manifest["files"]
    if set(files)!=set(blobs):
        raise ValueError("Unexpected original file set")
    verified={}
    for name,blob in blobs.items():
        info=files[name]
        if len(blob)!=info["size"] or hashlib.sha256(blob).hexdigest()!=info["sha256"]:
            raise ValueError("Dryad source digest/size verification failed: "+name)
        val=inspect_file(info["name"],blob)
        val["dryad_file_id"]=info["id"]
        val["original_declared_sha256_matched"]=True
        verified[name]=val
    return {
        "schema":"BALANCE_CLARKIA_KAY2020_DRYAD_SOURCE_ACQUISITION_V1",
        "status":"PUBLIC_DRYAD_FILE_STREAM_SOURCE_VERIFIED_NO_NEW_FIT_YET",
        "paper_doi":PAPER_DOI,"dataset_doi":DATA_DOI,
        "dataset_version_id":PINNED_VERSION,
        "dataset_version_number":metadata.get("versionNumber"),
        "dataset_title":metadata.get("title"),
        "dataset_licence":metadata.get("license"),
        "download_mode":"PUBLIC_LANDING_FILE_STREAM_SHA256_MATCHED",
        "source_file_count":manifest["source_original_file_count"],
        "source_files_verified":len(verified),
        "full_dataset_downloaded":False,
        "download_zip_sha256":None,
        "source_files":dict(sorted(verified.items())),
        "original_bombustrials2018_csv_missing":manifest["bombustrials2018_csv_missing"],
        "scope":"Outcome-discovered independent Clarkia original source, not random genus sample",
        "no_new_evolutionary_causal_origin":True,
        "published_conclusions_not_new_effect_estimates":True,
    }



def inspect_metadata_only(metadata: dict, registry: dict) -> dict:
    """Admit a public 29-file Dryad manifest without claiming data-byte access.

    Anonymous Dryad REST downloads return HTTP 401 and public file_stream
    links return HTTP 403 in this executor. Repeated retry would not identify
    biological effects. The SHA256 values are *declared*, not verified against
    downloaded bytes. A future user-authorized raw copy can be admitted
    separately through inspect_public_files with its own byte validation.
    """
    if str(metadata.get("identifier","")).lower()!="doi:"+DATA_DOI:
        raise ValueError("Original source identity mismatch")
    return {
        "schema":"BALANCE_CLARKIA_KAY2020_DRYAD_SOURCE_ACQUISITION_V1",
        "status":"HOLD_PUBLIC_METADATA_ONLY_SOURCE_BYTES_REQUIRE_AUTH",
        "paper_doi":PAPER_DOI,
        "dataset_doi":DATA_DOI,
        "dataset_version_id":PINNED_VERSION,
        "dataset_version_number":metadata.get("versionNumber"),
        "dataset_title":metadata.get("title"),
        "dataset_licence":metadata.get("license"),
        "source_file_count":registry["source_original_file_count"],
        "required_source_files":sorted(SOURCE_FILES),
        "original_file_digest_metadata_unverified_against_bytes":registry["files"],
        "source_files_verified":0,
        "source_rows_or_effect_sizes_computed":0,
        "full_dataset_downloaded":False,
        "raw_download_failure":"HTTP 401 API ZIP; HTTP 403 public file_stream as verified in independent GitHub Actions attempts",
        "original_bombustrials2018_csv_missing":
            registry["bombustrials2018_csv_missing"],
        "absence_of_downloaded_bytes_is_not_biological_null":True,
        "scope":"outcome-discovered study; no source original-data effect fit",
        "no_new_evolutionary_causal_origin":True,
    }


def fetch_and_inspect(output_path: Path) -> dict:
    meta=_json(DATASET_URL)
    latest=((meta.get("_links") or {}).get("stash:version") or {}).get("href")
    if latest!=f"/api/v2/versions/{PINNED_VERSION}":
        raise ValueError("Dryad public source version ID changed")
    listing=_public_registry(_json(VERSION_FILES_URL))
    # Full archive API and human-facing file-stream requests are access
    # restricted in unauthenticated Actions. Stop at proven metadata rather
    # than repeatedly try a 401/403 endpoint or claim a computed effect.
    result=inspect_metadata_only(meta,listing)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    with output_path.open("x",encoding="utf-8") as handle:
        json.dump(result,handle,indent=2,sort_keys=True,ensure_ascii=False)
        handle.write("\n")
    return result

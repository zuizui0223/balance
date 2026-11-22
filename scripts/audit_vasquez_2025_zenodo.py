"""Read-only Zenodo source inventory + authenticated candidate source-file schema audit.

The first run never fits ecological effects. It uses ONLY official Zenodo
record metadata, checks content byte lengths and Zenodo-provided MD5 when
present, and reports metadata-only CSV schemas without exposing source rows.
If downloads are blocked, it reports an explicit HOLD rather than making up
trial data, file hashes or successful biological analysis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from balance_domain.vasquez_2025_pollen_fates import source_values

ZENODO_ID = 17102653
API = f"https://zenodo.org/api/records/{ZENODO_ID}"
MAX_METADATA_BYTES = 4_000_000
MAX_DOWNLOAD_BYTES = 8_000_000
ALLOWED_SUFFIX = (".csv", ".tsv", ".txt", ".r", ".json", ".md")


def official_http_bytes(url: str, max_bytes: int) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc not in ("zenodo.org", "www.zenodo.org")
        or not parsed.path.startswith((
            f"/api/records/{ZENODO_ID}", f"/records/{ZENODO_ID}"
        ))
    ):
        raise ValueError("Refusing non-official Zenodo URL or wrong record")
    req = urllib.request.Request(
        url, headers={"User-Agent": "BALANCE-Vasquez2025-public-trial-data-audit/1.0",
                      "Accept": "application/json, text/csv, text/plain, */*"},
    )
    with urllib.request.urlopen(req, timeout=22) as resp:
        raw = resp.read(max_bytes+1)
    if not raw or len(raw)>max_bytes:
        raise ValueError("Empty/oversized public Zenodo response")
    return raw


def validate_record_metadata(record: dict) -> list[dict]:
    """Record identity and file info; never infer data existed from article."""
    if not isinstance(record, dict) or str(record.get("id")) != str(ZENODO_ID):
        raise ValueError("Zenodo API response belongs to a different record")
    meta = record.get("metadata")
    if not isinstance(meta, dict):
        raise ValueError("Zenodo record missing versioned metadata")
    title = str(meta.get("title", "")).lower()
    # This may be an R data/code package titled after Vasquez-Castro et al.
    expected_topics = ("pollen", "solanum", "vasquez", "transfer", "buzz")
    if not any(x in title for x in expected_topics):
        raise ValueError("Zenodo record title cannot be linked to focal pollen paper")
    payload = record.get("files")
    if isinstance(payload, dict):
        entries = [
            {**v, "key": v.get("key", key)}
            for key, v in payload.get("entries", {}).items()
        ] if isinstance(payload.get("entries"), dict) else []
    elif isinstance(payload, list):
        entries = payload
    else:
        raise ValueError("Zenodo file metadata list absent")
    if not entries:
        raise ValueError("Zenodo record has no exposed files")
    found = []
    keys = set()
    for f in entries:
        if not isinstance(f, dict):
            raise ValueError("Malformed file entry")
        key = f.get("key") or f.get("filename")
        size = f.get("size")
        if (
            not isinstance(key, str) or not key
            or key in keys or "/" in key or "\\" in key
            or isinstance(size,bool) or not isinstance(size,int) or size<=0
        ):
            raise ValueError("Invalid Zenodo file identity or size")
        keys.add(key)
        links=f.get("links") or {}
        if not isinstance(links,dict):
            raise ValueError("Zenodo file download links malformed")
        found.append({
            "name":key,
            "bytes":size,
            "zenodo_checksum":str(f.get("checksum") or ""),
            "public_content_url":links.get("content") or links.get("self") or "",
        })
    return found


def inspect_file_bytes(entry: dict, original: bytes) -> dict:
    """Schema and hashes only, not source-derived biological effects."""
    if not isinstance(original,bytes) or len(original)!=entry["bytes"]:
        raise ValueError("Downloaded file does not match Zenodo's declared byte size")
    if len(original)>MAX_DOWNLOAD_BYTES or original[:100].lstrip().lower().startswith(
        (b"<html", b"<!doctype")
    ):
        raise ValueError("Zenodo payload is oversized or an HTML error page")
    checksum=entry["zenodo_checksum"]
    if checksum.startswith("md5:"):
        if hashlib.md5(original).hexdigest()!=checksum[4:]:
            raise ValueError("Downloaded Zenodo file MD5 mismatch")
    if checksum.startswith("sha256:"):
        if hashlib.sha256(original).hexdigest()!=checksum[7:]:
            raise ValueError("Downloaded Zenodo file SHA-256 mismatch")
    try:
        source=original.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("Expected text file not decodable as UTF-8") from exc
    name=entry["name"]
    result={
        "name":name,
        "bytes":len(original),
        "sha256":hashlib.sha256(original).hexdigest(),
        "zenodo_checksum":checksum,
        "verification":"OFFICIAL_ZENODO_FILE_CONTENT_BYTES_AND_CHECKSUM_VERIFIED",
        "raw_source_biological_effect_estimated":False,
    }
    if name.lower().endswith((".csv",".tsv")):
        sep="\t" if name.lower().endswith(".tsv") else ","
        reader=csv.DictReader(io.StringIO(source),delimiter=sep)
        fields=reader.fieldnames
        if not fields or any(not x or not x.strip() for x in fields):
            raise ValueError("Empty/unlabeled Zenodo tabular dataset")
        if len(fields)!=len(set(fields)):
            raise ValueError("Duplicated Zenodo data columns")
        count=0
        for row in reader:
            if None in row or None in row.values():
                raise ValueError("Ragged source CSV/TSV rows")
            count+=1
        result.update({
            "row_count_not_independent_trials":count,
            "columns":fields,
            "possible_original_trial_unit":"UNVERIFIED_UNTIL_AUTHOR_CODE_AND_SPECIES_KEYS_REVIEWED",
        })
    else:
        result["text_lines"]=len(source.splitlines())
    return result


def source_access_audit(online=False, request_bytes=official_http_bytes) -> dict:
    receipt=source_values()
    output={
        "analysis":"BALANCE_VASQUEZ_2025_ZENODO_FILE_ACCESS_AUDIT",
        "original_article_doi":receipt["article"]["doi"],
        "record_id":ZENODO_ID,
        "raw_trial_data_analyzed":False,
        "new_biological_effects_estimated":0,
        "original_donor_trial_count_claim":15,
        "stigma_observations_nested_not_independent_trials":60,
        "original_trial_level_model_reproduction":"NOT_PERFORMED",
        "files":[],
        "status":"OFFLINE_NOT_ATTEMPTED",
        "source_claim_ceiling":"published-source metadata + authenticated source-file schemas only",
    }
    if not online:
        return output
    try:
        meta_raw=request_bytes(API,MAX_METADATA_BYTES)
        if meta_raw.lstrip().lower().startswith((b"<html",b"<!doctype")):
            raise ValueError("HTML error masquerades as Zenodo metadata")
        metadata=json.loads(meta_raw.decode("utf-8-sig"))
        files=validate_record_metadata(metadata)
    except (ValueError,TypeError,UnicodeError,TimeoutError,urllib.error.URLError,OSError) as e:
        output["status"]="ZENODO_PUBLIC_RECORD_ACCESS_HOLD"
        output["metadata_error_type"]=type(e).__name__
        if isinstance(e,urllib.error.HTTPError):
            output["metadata_http_status"]=e.code
        return output
    output["status"]="PUBLIC_RECORD_METADATA_VERIFIED"
    output["record_title"]=metadata["metadata"]["title"]
    output["record_doi"]=metadata.get("doi") or metadata["metadata"].get("doi")
    for entry in files:
        row={k:v for k,v in entry.items() if k!="public_content_url"}
        row["retrieval"]="NOT_ATTEMPTED"
        name=entry["name"]
        if not name.lower().endswith(ALLOWED_SUFFIX):
            row["retrieval"]="SKIP_NON_TEXT_FILE"
        elif entry["bytes"]>MAX_DOWNLOAD_BYTES:
            row["retrieval"]="SKIP_FILE_OVER_SIZE_CAP"
        elif not entry["public_content_url"]:
            row["retrieval"]="NO_OFFICIAL_FILE_DOWNLOAD_URL"
        else:
            try:
                original=request_bytes(entry["public_content_url"],MAX_DOWNLOAD_BYTES)
                result=inspect_file_bytes(entry,original)
                row["retrieval"]="DOWNLOADED_FILE_SCHEMA_VERIFIED"
                row["verified_file_schema"]=result
            except (ValueError,TypeError,UnicodeError,TimeoutError,
                    urllib.error.URLError,OSError) as e:
                row["retrieval"]="SOURCE_FILE_DOWNLOAD_HOLD"
                row["error_type"]=type(e).__name__
                if isinstance(e,urllib.error.HTTPError):
                    row["http_status"]=e.code
        output["files"].append(row)
    output["n_verified_file_schemas"]=sum(
        x["retrieval"]=="DOWNLOADED_FILE_SCHEMA_VERIFIED" for x in output["files"]
    )
    # A successful schema retrieval is NOT a successful original model refit.
    output["status"]=(
        "SOURCE_FILE_SCHEMAS_VERIFIED_NO_EFFECT_FITS"
        if output["n_verified_file_schemas"] else "PUBLIC_METADATA_ONLY_NO_SOURCE_FILES"
    )
    return output


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online",action="store_true",
                        help="Attempt the official public Zenodo API and small source text downloads")
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    report=source_access_audit(online=args.online)
    result=json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)
    print(result)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(result+"\n",encoding="utf-8")
    for f in report["files"]:
        detail=f.get("verified_file_schema",{})
        print(
            f"ZENODO_SOURCE_FILE|name={f['name']}|status={f['retrieval']}|"
            f"bytes={f['bytes']}|rows={detail.get('row_count_not_independent_trials','NA')}|"
            f"fields={','.join(detail.get('columns',[])[:60])}"
        )


if __name__=="__main__":
    main()

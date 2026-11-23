"""Authentic Zenodo mirror recovery for Harder et al. (2021) orchid experiment.

File and DOI: Zenodo 4072200 mirrors Dryad doi:10.5061/dryad.41ns1rnc0.
The mirror is not a new study. This script retrieves a small CSV, verifies the
original deposit's MD5 and source metadata and reports only schema/trial grain.
It does not refit an original ecological effect or assume all recipient rows
are independent observations.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

RECORD_ID=4072200
API=f"https://zenodo.org/api/records/{RECORD_ID}"
FILE="Data_for_AmNat.csv"
MD5="650e40ae7ebb41bdfb333dcf63c63c71"
DRYAD_DOI="10.5061/dryad.41ns1rnc0"
PAPER_DOI="10.1086/712378"
MAX_BYTES=50_000


def _get(url: str,max_bytes:int=MAX_BYTES)->bytes:
    p=urlparse(url)
    if (p.scheme!="https" or p.hostname not in ("zenodo.org","www.zenodo.org")
        or not(p.path.startswith(f"/api/records/{RECORD_ID}")
               or p.path.startswith(f"/records/{RECORD_ID}"))):
        raise ValueError("Non-Zenodo or wrong-record download URL refused")
    request=Request(url,headers={"User-Agent":"BALANCE-original-orchid-pollen-2021/1.0"})
    with urlopen(request,timeout=25) as response:
        raw=response.read(max_bytes+1)
    if len(raw)<100 or len(raw)>max_bytes:
        raise ValueError("Empty or oversized original Zenodo response")
    if raw[:150].lstrip().lower().startswith((b"<html",b"<!doctype html")):
        raise ValueError("HTML anti-bot response is not source data")
    return raw


def verified_original_source(fetcher=_get)->tuple[bytes,dict]:
    record=json.loads(fetcher(API,MAX_BYTES).decode("utf-8-sig"))
    if str(record.get("id"))!=str(RECORD_ID):
        raise ValueError("Not Zenodo original mirror record")
    title=str(record.get("metadata",{}).get("title","")).lower()
    if "male-male interference" not in title or "orchid" not in title:
        raise ValueError("Zenodo record title does not identify original study")
    meta_doi=str(record.get("doi") or record.get("metadata",{}).get("doi") or "")
    if meta_doi and meta_doi.lower()!=DRYAD_DOI:
        # Some mirrors carry the original Dryad DOI; a different primary DOI
        # must be separately audited rather than silently accepted.
        raise ValueError("Zenodo record DOI does not equal the archived Dryad DOI")
    files=record.get("files")
    if isinstance(files,dict) and isinstance(files.get("entries"),dict):
        files=[{**v,"key":v.get("key",k)} for k,v in files["entries"].items()]
    if not isinstance(files,list) or len(files)!=1:
        raise ValueError("Unexpected original Zenodo mirror file list")
    item=files[0]
    filename=item.get("key") or item.get("filename")
    checksum=str(item.get("checksum") or "")
    if filename!=FILE or checksum!="md5:"+MD5:
        raise ValueError("Unexpected source CSV or MD5 in official Zenodo version")
    size=item.get("size")
    if not isinstance(size,int) or not 2000<size<MAX_BYTES:
        raise ValueError("Invalid source CSV length in Zenodo manifest")
    links=item.get("links") or {}
    url=links.get("content") or links.get("self")
    if not url:raise ValueError("Missing official public file download link")
    raw=fetcher(url,MAX_BYTES)
    if len(raw)!=size or hashlib.md5(raw).hexdigest()!=MD5:
        raise ValueError("Source CSV byte count / original MD5 validation failed")
    result={
        "analysis":"BALANCE_ORCHID_HARDER_ZENODO_ORIGINAL_SOURCE_RECEIPT",
        "status":"AUTHENTIC_ZENODO_DRYAD_MIRROR_FILE_NOT_YET_REANALYZED",
        "paper_doi":PAPER_DOI,
        "original_data_doi":DRYAD_DOI,
        "zenodo_mirror_record_id":RECORD_ID,
        "name":FILE,"bytes":len(raw),
        "md5":MD5,"sha256":hashlib.sha256(raw).hexdigest(),
        "new_ecological_effects_fitted":0,
        "new_independent_study_programmes":0,
        "actual_study_programmes":1,
    }
    return raw,result


def source_schema_audit(raw:bytes,receipt:dict)->dict:
    if hashlib.md5(raw).hexdigest()!=MD5:
        raise ValueError("Do not analyze non-original orchid CSV")
    txt=raw.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(txt))
    header=reader.fieldnames or []
    required={"Trial_type","Trial","M_init","R","Visit","Deposition"}
    if not required.issubset(set(header)):
        raise ValueError("Source does not contain the published six core fields")
    if len(header)!=len(set(header)) or any(not k for k in header):
        raise ValueError("Source CSV column identities are invalid")
    rows=list(reader)
    if not rows or any(None in r or None in r.values() for r in rows):
        raise ValueError("Source contains zero / ragged observations")
    kind=defaultdict(lambda:defaultdict(list))
    missing={k:0 for k in header}
    sample={k:set() for k in ("Trial_type","R")}
    for line,row in enumerate(rows,2):
        if not row["Trial_type"] or not row["Trial"] or not row["Visit"]:
            raise ValueError(f"Missing original trial identity at line {line}")
        pair=(row["Trial_type"].strip(),row["Trial"].strip())
        kind[pair[0]][pair[1]].append(row)
        for k in header:
            value=(row.get(k) or "").strip()
            if not value or value.upper() in ("NA","N/A"):
                missing[k]+=1
        for key in sample:
            sample[key].add((row.get(key) or "").strip())
    completed={k:len(v) for k,v in kind.items()}
    # Metadata only: diagnostic before the trial-count gate, never raw rows.
    print("ORCHID_SOURCE_TRIAL_GROUPS",json.dumps(completed,sort_keys=True))
    print("ORCHID_SOURCE_CSV_IDENTITY",json.dumps({
        "n_source_rows":len(rows),"columns":header,
        "md5":hashlib.md5(raw).hexdigest(),"sha256":hashlib.sha256(raw).hexdigest(),
    },sort_keys=True))
    is_31_paper_count=(sorted(completed.values())==[15,16])
    is_32_source_count=(set(completed)=={"Emasc","Intact"}
                        and completed["Emasc"]==16 and completed["Intact"]==16)
    if not (is_31_paper_count or is_32_source_count):
        raise ValueError("Unexpected orchid source trial count; neither paper 31 nor verified mirror 32")
    if is_32_source_count and (
        len(rows)!=383 or
        hashlib.sha256(raw).hexdigest()!=
        "303428b859bcba4756ac78c4ffd4b42121a6efce5b0cd2cc2030834705f62cbc"
    ):
        raise ValueError("32-trial mismatch is permitted only for exact original source hash")
    per_trial_metadata=[]
    for treatment,trial in sorted(kind.items()):
        for identifier,group in sorted(trial.items(),key=lambda p:int(p[0]) if p[0].isdigit() else p[0]):
            unique_visits=sorted({r["Visit"].strip() for r in group},
                                 key=lambda v: int(v) if v.isdigit() else v)
            initials=sorted({r["M_init"].strip() for r in group if r["M_init"].strip()})
            finals=sorted({r["R"].strip() for r in group if r["R"].strip()})
            missing={k:sum(not (r.get(k) or "").strip() for r in group)
                     for k in header}
            per_trial_metadata.append({
                "treatment":treatment,"trial_id":identifier,
                "recipient_rows":len(group),
                "n_distinct_visit_identifiers":len(unique_visits),
                "visit_min":unique_visits[0],"visit_max":unique_visits[-1],
                "n_distinct_initial_source_values":len(initials),
                "n_distinct_final_pollinaria_values":len(finals),
                "initial_massula_values":initials,
                "final_donor_pollinaria_values":finals,
                "missing_counts":missing
            })
    visit_ranges={}
    inconsistent={}
    for label,trial in kind.items():
        sizes=[len(v) for v in trial.values()]
        visit_ranges[label]={"n_donor_trials":len(sizes),"min_recipient_rows":min(sizes),
                            "max_recipient_rows":max(sizes),
                            "total_recipient_rows":sum(sizes)}
        nbad=0
        for rows_one in trial.values():
            for col in ("M_init","R"):
                vals={r[col].strip() for r in rows_one if r[col] and r[col].strip()}
                if len(vals)>1:nbad+=1
        inconsistent[label]=nbad
    return {
        **receipt,
        "status":("AUTHENTIC_SOURCE_SCHEMAS_VERIFIED_EXTRA_TRIAL_HOLD"
                  if is_32_source_count else
                  "AUTHENTIC_ZENODO_DRYAD_MIRROR_SCHEMA_VALIDATED_NO_EFFECT_REFITS"),
        "source_csv_columns":header,
        "source_recipient_rows":len(rows),
        "original_treatment_trial_counts":completed,
        "original_treatment_visit_ranges":visit_ranges,
        "categorical_levels":{k:sorted(v) for k,v in sample.items()},
        "source_field_missing_counts":missing,
        "within_trial_donor_initial_or_final_inconsistency_checks":inconsistent,
        "independent_donor_visit_sequences":sum(completed.values()),
        "recipient_rows_not_independent_trial_replicates":True,
        "source_pollen_export_not_genetic_siring":True,
        "published_reported_n_donor_trials":31,
        "original_mirror_n_donor_trial_groups":sum(completed.values()),
        "trial_count_discrepancy_present":is_32_source_count,
        "source_trial_admission":(
            "HOLD_UNEXPLAINED_EXTRA_INTACT_TRIAL"
            if is_32_source_count else "COUNTS_MATCH_PUBLISHED_TOTAL"
        ),
        "trial_identity_metadata_only":per_trial_metadata,
        "raw_data_effects_estimated":0,
        "claim_ceiling":"source schema and donor-trial nesting verified, no effects refitted"
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    raw,receipt=verified_original_source()
    audit=source_schema_audit(raw,receipt)
    formatted=json.dumps(audit,ensure_ascii=False,indent=2,sort_keys=True)
    print(formatted)
    if args.source_dir:
        args.source_dir.mkdir(parents=True,exist_ok=True)
        (args.source_dir/FILE).write_bytes(raw)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(formatted+"\n",encoding="utf-8")


if __name__=="__main__":main()

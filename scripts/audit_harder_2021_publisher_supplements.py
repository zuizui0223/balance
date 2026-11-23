"""Optional official publisher supplement presence check for orchid 2021.

The original paper links a ZIP of R code/Excel models. Its trial inclusion
logic MAY help adjudicate 16+15 published donors versus 16+16 original CSV
coded groups. A publisher file is untrusted text and cannot override the
actual source DOI or justify selection based on effect directions. This
tool does not distribute the original ZIP or reproduce code excerpts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.error
from urllib.request import urlopen,Request
import zipfile

URL="https://www.journals.uchicago.edu/doi/suppl/10.1086/712378/suppl_file/59424Supplements.zip"
MAX_BYTES=24_000_000
MAX_MEMBER=5_000_000
KEYWORDS={
    "trial_id":"Trial",
    "source_file":"Data_for_AmNat",
    "experiment_emasculated":"Emasc",
    "experiment_intact":"Intact",
    "inclusion_words":"exclude|omitt|dropp|subset|filter",
}


def inspect_publisher_zip(raw:bytes)->dict:
    if len(raw)<200 or len(raw)>MAX_BYTES or not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("Original publisher supplementary response is not a bounded ZIP")
    out=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for entry in z.infolist():
            if entry.is_dir():continue
            name=entry.filename
            if len(out)>=100 or entry.file_size>MAX_MEMBER or "../" in name or name.startswith("/"):
                raise ValueError("Publisher archive members exceed safe metadata limit")
            base={
                "path":name,
                "bytes":entry.file_size,
                "is_author_model_source":name.lower().endswith((".r",".rmd",".txt",".csv")),
                "contains_usable_trial_admission_rule":"UNDETERMINED_BY_METADATA",
            }
            if base["is_author_model_source"]:
                data=z.read(entry)
                s=data.decode("utf-8-sig",errors="replace")
                base["lines"]=len(s.splitlines())
                base["keyword_line_counts"]={
                    key:len(re.findall(pattern,s,flags=re.IGNORECASE))
                    for key,pattern in KEYWORDS.items()
                }
                # Do not execute original author code or copy it into the repository.
            out.append(base)
    return {
        "status":"PUBLISHER_ZIP_DOWNLOADED_METADATA_INSPECTED_NOT_EXECUTED",
        "supplement_url":URL,
        "sha256":hashlib.sha256(raw).hexdigest(),
        "zip_file_count":len(out),
        "member_inventory":out,
        "verifies_original_31_trial_inclusion":False,
        "reuses_original_dryad_raw_evidence":False,
        "original_effect_models_refitted":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    out={
        "status":"PUBLISHER_SOURCE_ACCESS_HOLD",
        "supplement_url":URL,
        "author_31_trial_admission_rule_verified":False,
        "original_ecological_effects_refitted":False,
    }
    try:
        request=Request(URL,headers={"User-Agent":"BALANCE-orchid-source-audit/1.0"})
        with urlopen(request,timeout=18) as r:
            raw=r.read(MAX_BYTES+1)
        out=inspect_publisher_zip(raw)
    except (urllib.error.URLError,TimeoutError,OSError,ValueError,zipfile.BadZipFile) as e:
        out["failure_type"]=type(e).__name__
        if isinstance(e,urllib.error.HTTPError):
            out["http_status"]=e.code
    j=json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False)
    print(j)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(j+"\n",encoding="utf-8")


if __name__=="__main__":main()

"""Verify actual Zenodo original data and audit independent donor trial grain.

This stage deliberately DOES NOT fit species effects. It inspects source
categorical identity, four-recipient trial nesting, donor-stock repetition
and the original CSV's 10 columns. Files are downloaded only from the
official Zenodo record and checked against FIRST observed, fixed MD5/SHA256.
Raw trial bytes are never written to the repository or attached as artifacts.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from io import StringIO
import json
import re
from pathlib import Path

from scripts.audit_vasquez_2025_zenodo import (
    ZENODO_ID, API, MAX_METADATA_BYTES, validate_record_metadata,
    official_http_bytes, inspect_file_bytes,
)

RAW_CSV="data.csv"
RAW_SHA256="484ed52ac611dbc6dc1831320a6c54d314492e9830823edd8934690c35205b79"
RAW_MD5="d06dc42f897004e8eb6bd113a0e39bac"
RAW_BYTES=3965
README="README.txt"
README_SHA256="7ffc4a4d3fcfe7df2ac11eec8c5b99af9bb774a759301604f3985ced51a5ec40"
README_MD5="7ab422a249a685063e0ee1429bf837a2"
README_BYTES=1174
EXPECTED_COLUMNS=(
    "trial_number","bee_hive","bee_ID","flower_sp","recipient",
    "duration_visit","pollen_stigma","donor_released",
    "donor_remaining","donor_total",
)


def authenticated_source(fetcher=official_http_bytes) -> tuple[bytes,bytes]:
    manifest=json.loads(fetcher(API,MAX_METADATA_BYTES).decode("utf-8-sig"))
    index={x["name"]:x for x in validate_record_metadata(manifest)}
    if set(index)!={RAW_CSV,README}:
        raise ValueError("Original record file inventory changed unexpectedly")
    output=[]
    for filename,checksum,md5,bytes_expected in (
        (RAW_CSV,RAW_SHA256,RAW_MD5,RAW_BYTES),
        (README,README_SHA256,README_MD5,README_BYTES)
    ):
        row=index[filename]
        if (row["bytes"]!=bytes_expected or
            row["zenodo_checksum"]!="md5:"+md5 or
            not row["public_content_url"]):
            raise ValueError("Zenodo file manifest hash/size mismatch")
        raw=fetcher(row["public_content_url"],bytes_expected+1)
        verified=inspect_file_bytes(row,raw)
        if verified["sha256"]!=checksum:
            raise ValueError("Zenodo file original SHA256 mismatch")
        output.append(raw)
    return tuple(output)


def parse_trial_source(raw:bytes)->dict:
    from hashlib import sha256
    if sha256(raw).hexdigest()!=RAW_SHA256 or len(raw)!=RAW_BYTES:
        raise ValueError("Refusing a file that differs from authentic original data.csv")
    reader=csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    if tuple(reader.fieldnames or ())!=EXPECTED_COLUMNS:
        raise ValueError("Zenodo original column order/schema changed")
    rows=list(reader)
    if len(rows)!=60 or any(None in r or None in r.values() for r in rows):
        raise ValueError("Expected 60 intact recipient-level original rows")
    trial_groups=defaultdict(list)
    cat=defaultdict(Counter)
    numeric={x:[] for x in EXPECTED_COLUMNS
             if x not in ("trial_number","bee_hive","bee_ID","flower_sp","recipient")}
    for idx,r in enumerate(rows,2):
        for c in ("trial_number","bee_hive","bee_ID","flower_sp","recipient"):
            val=(r[c] or "").strip()
            if not val:raise ValueError(f"line {idx} missing {c}")
            cat[c][val]+=1
        # Use tuple of all actual identity labels instead of assuming trial number
        # or bee ID alone globally identifies a source donor.
        key=(r["flower_sp"],r["trial_number"],r["bee_hive"],r["bee_ID"])
        trial_groups[key].append(r)
        for c in numeric:
            if not (r[c] or "").strip():
                # Missing numeric data is reported, never imputed.
                continue
            try:v=float(r[c])
            except ValueError as exc:raise ValueError(f"line {idx} invalid {c}") from exc
            from math import isfinite
            if not isfinite(v) or v<0:
                raise ValueError(f"line {idx} invalid nonnegative source value in {c}")
            numeric[c].append(v)
    if len(trial_groups)!=15:
        raise ValueError("Recipient rows cannot be assigned to 15 donor-bee trial keys")
    nested_sizes=Counter(len(group) for group in trial_groups.values())
    if nested_sizes!={4:15}:
        raise ValueError("Source lacks complete exactly-four-recipient trial nests")
    trials_by_species=Counter(k[0] for k in trial_groups)
    if sorted(trials_by_species.values())!=[6,9]:
        raise ValueError("Original trial species contrast 6 vs 9 not recovered")
    repeated={}
    for label,group in trial_groups.items():
        for col in ("donor_released","donor_remaining","donor_total"):
            vals=[r[col] for r in group]
            if len(set(vals))>1:
                repeated[col]=repeated.get(col,0)+1
    # Record only the original 15-trial grain, no ecological effects.
    return {
        "analysis":"BALANCE_VASQUEZ_2025_AUTHENTIC_60_RECIPIENT_TRIAL_GRAIN",
        "status":"ORIGINAL_CSV_HASH_VERIFIED_TRIAL_SCHEMA_AUDITED_NO_BIOLOGICAL_MODEL_FITTED",
        "record_id":ZENODO_ID,
        "raw_csv_sha256":RAW_SHA256,
        "raw_csv_size":RAW_BYTES,
        "source_recipient_rows":len(rows),
        "independent_completed_donor_bee_trial_keys":len(trial_groups),
        "trial_nesting_distribution":dict(nested_sizes),
        "species_trial_counts":dict(trials_by_species),
        "categorical_levels":{k:dict(v) for k,v in cat.items()},
        "numeric_missing_counts":{k:len(rows)-len(v) for k,v in numeric.items()},
        "numeric_observed_min_max":{
            k:{"min":min(v) if v else None,"max":max(v) if v else None}
            for k,v in numeric.items()
        },
        "within_trial_donor_stock_inconsistency_counts":repeated,
        "one_stigma_row_is_not_an_independent_trial":True,
        "independent_donor_paternity_fitness_unavailable":True,
        "real_original_effect_estimates_newly_fitted":0,
        "note":"C,D,F,G ground/basket/body compartments not in published Zenodo data.csv"
    }


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--source-dir",type=Path)
    args=p.parse_args()
    data,readme=authenticated_source()
    audit=parse_trial_source(data)
    from hashlib import sha256
    audit["source_readme_sha256"]=sha256(readme).hexdigest()
    report=json.dumps(audit,ensure_ascii=False,indent=2,sort_keys=True)
    print(report)
    # Readme text is 31 lines and included only as compact source column labels
    # in the workflow's transient original-supplement inspection.
    print("ORIGINAL_README_TEXT_START")
    print(readme.decode("utf-8-sig"))
    print("ORIGINAL_README_TEXT_END")
    if args.source_dir:
        args.source_dir.mkdir(parents=True,exist_ok=True)
        (args.source_dir/RAW_CSV).write_bytes(data)
        (args.source_dir/README).write_bytes(readme)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(report+"\n",encoding="utf-8")


if __name__=="__main__":
    main()

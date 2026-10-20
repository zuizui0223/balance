#!/usr/bin/env python3
"""Read published Kay 2020 Dryad 29-file metadata without raw-byte access."""
from __future__ import annotations
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from balance_domain.clarkia_kay2020_source import fetch_and_inspect


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=fetch_and_inspect(args.out)
    print(json.dumps({
        "source":result["dataset_doi"],
        "version":result["dataset_version_number"],
        "version_id":result["dataset_version_id"],
        "status":result["status"],
        "source_file_count":result["source_file_count"],
        "declared_original_digests_unverified_against_bytes":
            result["original_file_digest_metadata_unverified_against_bytes"],
        "source_bytes_recovered":result["source_files_verified"],
        "raw_fitness_effect_estimates_computed":
            result["source_rows_or_effect_sizes_computed"],
    },indent=2,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Download original Kay et al. Clarkia Dryad data and write bounded provenance."""
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
        "source":result["dataset_doi"],"version":result["dataset_version_number"],
        "archive_sha256":result["download_zip_sha256"],
        "status":result["status"],
        "files":result["source_files"],
    },indent=2,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()

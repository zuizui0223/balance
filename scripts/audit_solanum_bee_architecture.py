"""Describe authenticated Wilkins et al. (2022) bee trials."""
import argparse
import json
from pathlib import Path

from balance_domain.solanum_bee_architecture import CSV_NAME, R_NAME, audit_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--download", action="store_true", help="Fetch missing pinned supplements")
    parser.add_argument("--out", type=Path, help="Save the verified descriptive report as JSON")
    args = parser.parse_args()
    if args.out and args.out.resolve() in {
        (args.source_dir / name).resolve() for name in (CSV_NAME, R_NAME)
    }:
        parser.error("--out must be distinct from the source supplements")
    report = audit_source(args.source_dir, download=args.download)
    output = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()

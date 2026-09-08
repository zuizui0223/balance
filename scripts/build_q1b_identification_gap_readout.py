from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

REQUIRED = {
    "study_key",
    "system_taxon",
    "q1b_class",
    "first_failed_gate",
    "claim_ceiling",
}

PASS_CLASS = "STRICT_Q1B_EFFECT_READY"


def build(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or ())
        missing = sorted(REQUIRED - fields)
        if missing:
            raise ValueError("missing required columns: " + ", ".join(missing))
        rows = list(reader)

    classes = Counter(row["q1b_class"] for row in rows if row["q1b_class"])
    failed = Counter(row["first_failed_gate"] for row in rows if row["first_failed_gate"])
    strict = [row for row in rows if row["q1b_class"] == PASS_CLASS]
    controls = [row for row in rows if "NEGATIVE_CONTROL" in row["q1b_class"]]

    return {
        "analysis": "balance_q1b_identification_gap_readout",
        "n_audited_programmes": len(rows),
        "n_strict_q1b_effect_ready": len(strict),
        "strict_q1b_effect_ready_studies": sorted(row["study_key"] for row in strict),
        "n_design_matched_negative_controls": len(controls),
        "q1b_class_counts": dict(sorted(classes.items())),
        "first_failed_gate_counts": dict(sorted(failed.items())),
        "n_nonpass_programmes": len(rows) - len(strict),
        "pooling_implication": "one_effect_ready_positive_is_below_three_cluster_pooling_gate",
        "claim_ceiling": (
            "targeted_design_coverage_audit_not_natural_prevalence_"
            "or_exhaustive_global_systematic_review"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(args.ledger)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()

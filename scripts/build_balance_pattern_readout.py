from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

REQUIRED = {
    "cluster_id",
    "pattern_class",
    "context_axis",
    "evidence_level",
    "confidence",
    "quantitative_pool_eligible",
}

MIDDLE_CLASSES = {
    "CONFLICT_WITHOUT_SPLITTING",
    "SANDWICHED_TRANSITION_MOSAIC",
    "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE",
}


def build(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or ())
        missing = sorted(REQUIRED - fields)
        if missing:
            raise ValueError("missing required columns: " + ", ".join(missing))
        rows = list(reader)

    clusters = {r["cluster_id"] for r in rows if r["cluster_id"]}
    patterns = Counter(r["pattern_class"] for r in rows if r["pattern_class"])
    contexts = Counter(r["context_axis"] for r in rows if r["context_axis"])
    confidence = Counter(r["confidence"] for r in rows if r["confidence"])
    domains = Counter(r.get("domain", "") for r in rows if r.get("domain", ""))
    quantitative = {
        r["cluster_id"]
        for r in rows
        if r["quantitative_pool_eligible"].lower() == "true"
    }

    def class_clusters(pattern_class: str) -> set[str]:
        return {
            r["cluster_id"]
            for r in rows
            if r["pattern_class"] == pattern_class and r["cluster_id"]
        }

    middle = {
        r["cluster_id"]
        for r in rows
        if r["pattern_class"] in MIDDLE_CLASSES and r["cluster_id"]
    }

    return {
        "analysis": "balance_reality_pattern_readout",
        "n_records": len(rows),
        "n_independent_clusters": len(clusters),
        "pattern_class_counts": dict(sorted(patterns.items())),
        "context_axis_counts": dict(sorted(contexts.items())),
        "confidence_counts": dict(sorted(confidence.items())),
        "domain_counts": dict(sorted(domains.items())),
        "n_middle_regime_signature_clusters": len(middle),
        "n_conflict_without_splitting_clusters": len(
            class_clusters("CONFLICT_WITHOUT_SPLITTING")
        ),
        "n_sandwiched_transition_mosaic_clusters": len(
            class_clusters("SANDWICHED_TRANSITION_MOSAIC")
        ),
        "n_persistent_integration_with_alternative_clusters": len(
            class_clusters("PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE")
        ),
        "n_boundary_crossing_clusters": len(class_clusters("BOUNDARY_CROSSING")),
        "n_hysteresis_clusters": len(
            class_clusters("HYSTERESIS_OR_PATH_DEPENDENCE")
        ),
        "n_direct_differentiation_boundary_clusters": len(
            class_clusters("DIRECT_DIFFERENTIATION")
        ),
        "n_unresolved_clusters": len(class_clusters("UNRESOLVED")),
        "n_quantitative_pool_eligible_clusters": len(quantitative),
        "claim_ceiling": (
            "screened_source_adjudicated_recurrence_not_natural_prevalence_"
            "or_direct_Phi_identification"
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

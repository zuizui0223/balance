from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

REQUIRED = {
    "cluster_id",
    "source_id",
    "system_taxon",
    "domain",
    "conflict_present",
    "shared_architecture_present",
    "alternative_architecture_present",
    "pattern_class",
    "context_axis",
    "evidence_level",
    "confidence",
    "quantitative_pool_eligible",
    "source_basis",
    "claim_ceiling",
    "notes",
}

PATTERN_CLASSES = {
    "CONFLICT_WITHOUT_SPLITTING",
    "SANDWICHED_TRANSITION_MOSAIC",
    "BOUNDARY_CROSSING",
    "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE",
    "HYSTERESIS_OR_PATH_DEPENDENCE",
    "DIRECT_DIFFERENTIATION",
    "UNRESOLVED",
}

MIDDLE_CLASSES = {
    "CONFLICT_WITHOUT_SPLITTING",
    "SANDWICHED_TRANSITION_MOSAIC",
    "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE",
}

_MISSING_TEXT = {"none", "null", "nan", "required_before_use"}
_REQUIRED_TEXT_FIELDS = (
    "cluster_id",
    "source_id",
    "system_taxon",
    "domain",
    "pattern_class",
    "context_axis",
    "evidence_level",
    "confidence",
    "source_basis",
    "claim_ceiling",
)


def _required_text(value: object, field: str, row_number: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"row {row_number} {field} must be a frozen string")
    text = value.strip()
    if not text or text.casefold() in _MISSING_TEXT:
        raise ValueError(f"row {row_number} {field} must be frozen before readout")
    return text


def _validated_rows(reader: csv.DictReader) -> list[dict[str, str]]:
    rows = list(reader)
    if not rows:
        raise ValueError("pattern ledger must contain at least one adjudicated cluster")

    seen: set[str] = set()
    validated: list[dict[str, str]] = []
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {row_number} has fields outside the canonical ledger schema")
        clean = dict(row)
        for field in _REQUIRED_TEXT_FIELDS:
            clean[field] = _required_text(row.get(field), field, row_number)

        cluster_id = clean["cluster_id"]
        if cluster_id in seen:
            raise ValueError(
                f"duplicate cluster_id {cluster_id!r}: each independent cluster must occupy exactly one ledger row"
            )
        seen.add(cluster_id)

        pattern_class = clean["pattern_class"]
        if pattern_class not in PATTERN_CLASSES:
            raise ValueError(
                f"row {row_number} pattern_class {pattern_class!r} is not a registered reality-pattern class"
            )

        for field in (
            "conflict_present",
            "shared_architecture_present",
            "alternative_architecture_present",
        ):
            clean[field] = _required_text(row.get(field), field, row_number)

        quantitative = _required_text(
            row.get("quantitative_pool_eligible"),
            "quantitative_pool_eligible",
            row_number,
        ).casefold()
        if quantitative not in {"true", "false"}:
            raise ValueError(
                f"row {row_number} quantitative_pool_eligible must be literal true or false"
            )
        clean["quantitative_pool_eligible"] = quantitative
        # Notes may be empty, but if present preserve normalized text.
        clean["notes"] = (row.get("notes") or "").strip()
        validated.append(clean)
    return validated


def build(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or ())
        missing = sorted(REQUIRED - fields)
        if missing:
            raise ValueError("missing required columns: " + ", ".join(missing))
        extra = sorted(fields - REQUIRED)
        if extra:
            raise ValueError("unexpected columns outside canonical ledger schema: " + ", ".join(extra))
        rows = _validated_rows(reader)

    # One validated row is one independent biological cluster. This invariant is
    # enforced above rather than inferred after aggregation, so a cluster cannot
    # inflate recurrence by appearing in multiple pattern classes or domains.
    clusters = {r["cluster_id"] for r in rows}
    patterns = Counter(r["pattern_class"] for r in rows)
    contexts = Counter(r["context_axis"] for r in rows)
    confidence = Counter(r["confidence"] for r in rows)
    domains = Counter(r["domain"] for r in rows)
    quantitative = {
        r["cluster_id"]
        for r in rows
        if r["quantitative_pool_eligible"] == "true"
    }

    def class_clusters(pattern_class: str) -> set[str]:
        return {
            r["cluster_id"]
            for r in rows
            if r["pattern_class"] == pattern_class
        }

    middle = {
        r["cluster_id"]
        for r in rows
        if r["pattern_class"] in MIDDLE_CLASSES
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

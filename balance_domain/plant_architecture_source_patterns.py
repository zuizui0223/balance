"""Source-stratified real floral conflict/architecture patterns.

Reads the *already screened, outcome-enriched* U2 and pilot frames separately.
No pooling, p-values, V4 outcome opening, morphological imputation, historical
transition inference, or new source adjudication is performed here.
"""
from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
U2_PATH = "data/BALANCE_PLANT_U2_SCREENING_V1.csv"
PILOT_PATH = "data/BALANCE_PLANT_MACRO_PILOT_V1.csv"

FOUR_CLASSES = {
    "SHARED_INTEGRATED": "SHARED",
    "TEMPORAL_SEPARATION": "NONSTRUCTURAL_SEPARATION",
    "SPATIAL_SEPARATION": "NONSTRUCTURAL_SEPARATION",
    "TEMPORAL_AND_SPATIAL_SEPARATION": "NONSTRUCTURAL_SEPARATION",
    "POLYMORPHIC_OR_MOSAIC": "MOSAIC",
    "AMONG_FLOWER_MODULE_DIVISION": "STRUCTURAL_MODULE_DIVISION",
    "WITHIN_FLOWER_DIVISION_OF_LABOUR": "STRUCTURAL_MODULE_DIVISION",
    "UNRESOLVED": "UNRESOLVED",
}
STATUS = {
    "POSITIVE",
    "NO_DEMONSTRATED_CONFLICT",
    "ALIGNED_NO_CONFLICT",
    "UNRESOLVED",
}
STRUCTURAL = {"AMONG_FLOWER_MODULE_DIVISION", "WITHIN_FLOWER_DIVISION_OF_LABOUR"}
SPECIAL_HISTORICAL = "Solanum_rostratum_historical"
CURRENT_SOLANUM = "Solanum_rostratum"


def load_screen(base: Path, relpath: str, expected_frame: str) -> tuple[list[dict[str, str]], str]:
    """Load the exact tracked source text and reject confirmatory contamination."""
    blob = (base / relpath).read_bytes()
    rows = list(csv.DictReader(blob.decode("utf-8-sig").splitlines()))
    if not rows:
        raise ValueError(f"empty source: {relpath}")
    required = {
        "dependency_group", "source_id", "conflict_status",
        "architecture_mode", "structural_module_division",
        "adjudication_status", "primary_model_eligible", "sampling_frame_id",
        "function_a", "function_b", "conflict_family",
    }
    if not required.issubset(rows[0]):
        raise ValueError(f"source schema changed: {relpath}")
    for row in rows:
        if (
            not row["dependency_group"] or not row["source_id"]
            or row["sampling_frame_id"] != expected_frame
        ):
            raise ValueError(f"source/frame identity failure: {relpath}")
        if row["conflict_status"] not in STATUS:
            raise ValueError("unrecognized conflict status")
        if row["architecture_mode"] not in FOUR_CLASSES:
            raise ValueError("unrecognized architecture mode")
        if row["structural_module_division"] not in {"true", "false", "unresolved"}:
            raise ValueError("structural status requires three-valued coding")
        if row["structural_module_division"] == "true" and row["architecture_mode"] not in STRUCTURAL:
            raise ValueError("structural claim contradicts architecture mode")
        if row["architecture_mode"] in STRUCTURAL and row["structural_module_division"] != "true":
            raise ValueError("structural mode without source structural receipt")
        if row["adjudication_status"] != "SCREENED" or row["primary_model_eligible"] != "false":
            raise ValueError("may analyze only frozen SCREENED, non-confirmatory source rows")
    return rows, hashlib.sha256(blob).hexdigest()


def _count(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(row[key] for row in rows).items()))


def _four_class_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(sorted(Counter(FOUR_CLASSES[r["architecture_mode"]] for r in rows).items()))


def _screen_summary(rows: list[dict[str, str]], *, relpath: str, sha: str) -> dict:
    positives = [r for r in rows if r["conflict_status"] == "POSITIVE"]
    not_demonstrated = [r for r in rows if r["conflict_status"] == "NO_DEMONSTRATED_CONFLICT"]
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in positives:
        by_family[row["conflict_family"]].append(row)
    return {
        "source": relpath,
        "raw_text_sha256": sha,
        "source_rows": len(rows),
        "distinct_dependency_groups": len({r["dependency_group"] for r in rows}),
        "status_counts": _count(rows, "conflict_status"),
        "four_class_counts_all": _four_class_counts(rows),
        "conflict_positive_four_class": _four_class_counts(positives),
        "no_demonstrated_conflict_four_class": _four_class_counts(not_demonstrated),
        "conflict_positive_structural_true": sum(
            r["structural_module_division"] == "true" for r in positives
        ),
        "conflict_positive_structural_unresolved": sum(
            r["structural_module_division"] == "unresolved" for r in positives
        ),
        "conflict_positive_by_function_family": {
            family: {
                "source_rows": len(group),
                "dependency_groups": len({r["dependency_group"] for r in group}),
                "four_class": _four_class_counts(group),
                "structural_confirmed": sum(
                    r["structural_module_division"] == "true" for r in group
                ),
            }
            for family, group in sorted(by_family.items())
        },
    }


def analyze(base: Path = REPO_ROOT) -> dict:
    """Report observed states only, preserving independent sampling universes."""
    u2, hash_u2 = load_screen(base, U2_PATH, "U2_BARRETT_2002")
    pilot, hash_pilot = load_screen(base, PILOT_PATH, "PLANT_PILOT_V1")
    if len({r["dependency_group"] for r in u2}) != len(u2):
        raise ValueError("U2 review contains duplicate dependency groups")

    pilot_by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in pilot:
        pilot_by_group[row["dependency_group"]].append(row)
    u2_by_group = {r["dependency_group"]: r for r in u2}
    overlaps = []
    for group in sorted(set(u2_by_group).intersection(pilot_by_group)):
        for pilot_row in pilot_by_group[group]:
            source = u2_by_group[group]
            overlaps.append({
                "exact_dependency_group": group,
                "u2_source_id": source["source_id"],
                "pilot_source_id": pilot_row["source_id"],
                "u2_function_pair": [source["function_a"], source["function_b"]],
                "pilot_function_pair": [pilot_row["function_a"], pilot_row["function_b"]],
                "u2_function_family": source["conflict_family"],
                "pilot_function_family": pilot_row["conflict_family"],
                "u2_conflict_status": source["conflict_status"],
                "pilot_conflict_status": pilot_row["conflict_status"],
                "u2_architecture_mode": source["architecture_mode"],
                "pilot_architecture_mode": pilot_row["architecture_mode"],
                "conflict_status_differs": source["conflict_status"] != pilot_row["conflict_status"],
                "architecture_mode_differs": source["architecture_mode"] != pilot_row["architecture_mode"],
                "independent_species_replicate": False,
                "valid_pooled_fitness_effect": False,
            })

    # The historical U2 label is NOT a taxon-ID-verified exact match.
    # This is especially important because GloBI's bare 'S. rostratum'
    # query can retrieve a different Solanum authorship.
    homonym_hold = (
        SPECIAL_HISTORICAL in u2_by_group
        and CURRENT_SOLANUM in pilot_by_group
    )
    return {
        "schema": "BALANCE_SOURCE_STRATIFIED_TRAIT_ARCHITECTURE_V1",
        "admission": "EXPLORATORY_SOURCE_SCREEN_ONLY",
        "u2": _screen_summary(u2, relpath=U2_PATH, sha=hash_u2),
        "plant_pilot": _screen_summary(pilot, relpath=PILOT_PATH, sha=hash_pilot),
        "exact_dependency_group_overlaps": overlaps,
        "historical_Solanum_name_join_held": homonym_hold,
        "not_pooled": True,
        "prohibited_promotions": [
            "cross_universe_prevalence",
            "conflict_absence_from_NO_DEMONSTRATED_CONFLICT",
            "source_or_context_rows_as_independent_species",
            "four_class_V4_confirmatory_effect",
            "causal_structural_fitness_worldline",
            "historical_module_origin",
            "architecture_cost_from_BITA_residual",
        ],
    }

"""Post-open, outcome-blind audit of U6 pollen-loss measurement coordinates.

Consumes the unchanged frozen U6 Pass-1 admission and source-side receipts.
The three flags are *post-open reviewer questions*, not revised admissions,
not coder A/B architecture outcomes and not independently adjudicated predictors.

This module must never be used to silently filter the V4 primary denominator.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

from .plant_confirmatory import load_plant_predictor_receipts
from .plant_model_v4 import _design_matrices, _matrix_rank
from .plant_preoutcome_generality import _complete_screened
from .plant_u2_screen import load_u2_conflict_screen


ADJ_FIELDS = (
    "adjudication_id", "reference_id", "plant_taxon", "dependency_group",
    "primary_source_status", "qualifying_receipt", "decision", "reason_code",
    "source_basis", "notes",
)
FLAG_FIELDS = (
    "dependency_group", "flag_code", "source_stage", "primary_doi",
    "evidence_limit", "review_status",
)
RECEIPT_TYPES = (
    "DIRECT_CONSUMPTION_AVAILABLE_POLLEN_LOSS",
    "DIRECT_REMOVAL_FITNESS_COST",
    "DIRECT_POLLEN_ROBBING_NO_POLLINATION",
    "DIRECT_REMOVAL_LOW_DEPOSITION",
)
EXPECTED_POSTOPEN_FLAGS = {
    "Melastoma_affine": (
        "POST_DEPOSITION_RECIPIENT_STIGMA",
        "RECIPIENT_STIGMA",
        "10.1016/S0006-3207(98)00010-X",
    ),
    "Zea_mays": (
        "POST_DISPERSAL_POLLEN_FOOD",
        "DEPOSITED_WIND_POLLEN",
        "10.1603/0046-225X-33.4.958",
    ),
    "Nothofagus_pumilio": (
        "DESTRUCTIVE_FLOWER_CONSUMPTION_BUNDLE",
        "WHOLE_FLOWER_AND_POLLEN",
        "10.1111/j.1442-9993.2006.01637.x",
    ),
}
HARD_STAGE_MISMATCH = {
    "POST_DEPOSITION_RECIPIENT_STIGMA", "POST_DISPERSAL_POLLEN_FOOD"
}
MIN_LEVEL_GROUPS = 2


def _load_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"Unexpected source-column schema: {path.name}")
        rows = list(reader)
    if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Empty or malformed source rows: {path.name}")
    return rows


def _audit_admissions(
    frozen: dict, batches: list[Path]
) -> tuple[dict[str, str], dict[str, list[str]], dict]:
    frozen_groups = frozen["included_dependency_groups"]
    if len(frozen_groups) != 21 or len(set(frozen_groups)) != 21:
        raise ValueError("Frozen U6 requires 21 unique dependency groups")
    reference_ids = set(frozen["candidate_reference_outcomes"]["included_reference_ids"])
    if len(reference_ids) != 21:
        raise ValueError("Frozen U6 requires 21 included primary reference IDs")
    rows = [row for path in batches for row in _load_csv(path, ADJ_FIELDS)]
    included = [row for row in rows if row["decision"] == "INCLUDE"]
    if len(included) != 22:
        raise ValueError("Frozen admission contains exactly 22 included taxon-reference rows")
    if len({row["adjudication_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate U6 source adjudication ID")
    if {row["dependency_group"] for row in included} != set(frozen_groups):
        raise ValueError("Included dependency groups differ from frozen U6")
    if {row["reference_id"] for row in included} != reference_ids:
        raise ValueError("Included references differ from frozen U6")

    refs_by_group: dict[str, set[str]] = defaultdict(set)
    groups_by_ref: dict[str, set[str]] = defaultdict(set)
    kinds_by_group: dict[str, set[str]] = defaultdict(set)
    for row in included:
        if row["qualifying_receipt"] not in RECEIPT_TYPES:
            raise ValueError("Unknown source-admission evidence type")
        refs_by_group[row["dependency_group"]].add(row["reference_id"])
        groups_by_ref[row["reference_id"]].add(row["dependency_group"])
        kinds_by_group[row["dependency_group"]].add(row["qualifying_receipt"])
    frozen_map = frozen["source_reference_ids_by_dependency_group"]
    if {k: sorted(v) for k, v in refs_by_group.items()} != {
        k: sorted(v) for k, v in frozen_map.items()
    }:
        raise ValueError("Reference-to-group mapping differs from Pass-1 freeze")
    if any(len(v) != 1 for v in kinds_by_group.values()):
        raise ValueError("Conflicting primary-source evidence tags within one group")
    evidence_by_group = {k: next(iter(v)) for k, v in kinds_by_group.items()}
    groups_by_source = {
        ref: sorted(v) for ref, v in sorted(groups_by_ref.items()) if len(v) > 1
    }
    return (
        evidence_by_group,
        {group: sorted(v) for group, v in sorted(refs_by_group.items())},
        {
            "included_adjudication_rows": len(included),
            "included_unique_primary_reference_ids": len(reference_ids),
            "source_refs_spanning_multiple_groups": groups_by_source,
            "groups_supported_by_multiple_source_refs": {
                k: sorted(v) for k, v in refs_by_group.items() if len(v) > 1
            },
        },
    )


def _load_postopen_flags(path: Path, frozen_groups: set[str]) -> dict[str, dict[str, str]]:
    rows = _load_csv(path, FLAG_FIELDS)
    if len(rows) != 3:
        raise ValueError("Exactly three predeclared post-open reviewer flags are required")
    result = {}
    for row in rows:
        group = row["dependency_group"]
        if group in result or group not in frozen_groups:
            raise ValueError("Duplicate or unregistered reviewer-flag dependency group")
        if row["review_status"] != "POSTOPEN_EXPLORATORY_NOT_ADJUDICATED":
            raise ValueError("Reviewer flags are not formal adjudication decisions")
        expected = EXPECTED_POSTOPEN_FLAGS.get(group)
        if expected is None or (
            row["flag_code"], row["source_stage"], row["primary_doi"]
        ) != expected:
            raise ValueError("Unexpected post-open stage flag or source identity")
        if not row["evidence_limit"].strip():
            raise ValueError("Reviewer flag requires explicit evidence limit")
        result[group] = row
    if set(result) != set(EXPECTED_POSTOPEN_FLAGS):
        raise ValueError("Post-open flag roster cannot be silently changed")
    return result


def _screened_design_rows(
    u2_screen: Path, u2_receipts: Path, u6_receipts: Path,
    frozen_groups: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    u2_screen_rows = load_u2_conflict_screen(u2_screen)
    u2_positive = {
        r["dependency_group"] for r in u2_screen_rows
        if r["conflict_status"] == "POSITIVE"
    }
    u2_receipt_rows = load_plant_predictor_receipts(u2_receipts)
    u6_receipt_rows = load_plant_predictor_receipts(u6_receipts)
    if any(r["adjudication_status"] != "SCREENED"
           for r in u2_receipt_rows + u6_receipt_rows):
        raise ValueError("This source-side audit accepts SCREENED receipts only")
    u2 = _complete_screened(u2_receipt_rows, u2_positive)
    u6 = _complete_screened(u6_receipt_rows)
    if len(u2) != 8 or {r["dependency_group"] for r in u2} != u2_positive:
        raise ValueError("Original eight U2 source-screen positives required")
    if {r["dependency_group"] for r in u6} != frozen_groups:
        raise ValueError("Original 21 U6 SCREENED source-predictor groups required")
    if {r["dependency_group"] for r in u2} & frozen_groups:
        raise ValueError("U2/U6 dependence group overlap must be explicitly audited")
    return u2, u6


def _scenario(
    u2: list[dict[str, str]], u6: list[dict[str, str]],
    retained_u6: set[str],
) -> dict:
    subset = [row for row in u6 if row["dependency_group"] in retained_u6]
    if len(subset) != len(retained_u6):
        raise ValueError("Scenario specifies a nonexistent U6 source group")
    matrix_rows = [
        {
            "universe_id": "U2_BARRETT_2002",
            "module_opportunity2": r["module"],
            "temporal_exposure3": r["timing"],
        } for r in u2
    ] + [
        {
            "universe_id": "U6_POLLEN_THEFT_HARGREAVES_2009",
            "module_opportunity2": r["module"],
            "temporal_exposure3": r["timing"],
        } for r in subset
    ]
    slope_names, slopes, full_names, full = _design_matrices(matrix_rows)
    module = Counter(r["module_opportunity2"] for r in matrix_rows)
    timing = Counter(r["temporal_exposure3"] for r in matrix_rows)
    if len(full_names) != 5 or len(slope_names) != 3:
        raise ValueError("Frozen V4 predictor design dimension changed")
    single_timing = {
        universe: {
            timed: sum(
                r["module_opportunity2"] == "SINGLE"
                and r["temporal_exposure3"] == timed
                and r["universe_id"] == uid
                for r in matrix_rows
            )
            for timed in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        }
        for universe, uid in (
            ("U2", "U2_BARRETT_2002"),
            ("U6", "U6_POLLEN_THEFT_HARGREAVES_2009"),
        )
    }
    return {
        "u6_included_groups_after_hypothetical_filter": len(subset),
        "pooled_source_screened_groups": len(matrix_rows),
        "u6_screened_timing": {
            timed: sum(r["timing"] == timed for r in subset)
            for timed in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        },
        "full_design_rank": _matrix_rank(full),
        "full_design_columns": len(full_names),
        "slope_design_rank": _matrix_rank(slopes),
        "frozen_min_primary_level_support": {
            "module": all(module[k] >= MIN_LEVEL_GROUPS for k in ("SINGLE", "MODULAR")),
            "timing": all(timing[k] >= MIN_LEVEL_GROUPS for k in (
                "SIMULTANEOUS", "ORDERED_OR_ALTERNATING", "VARIABLE_CONTEXT"
            )),
        },
        "u6_has_two_ordered_groups": sum(
            r["timing"] == "ORDERED_OR_ALTERNATING" for r in subset
        ) >= 2,
        "shared_single_module_timing_counts": single_timing,
        "g1_predictor_common_support_only": all(
            single_timing[u][t] >= 2
            for u in ("U2", "U6")
            for t in ("SIMULTANEOUS", "ORDERED_OR_ALTERNATING")
        ),
        "note": "hypothetical filtered-screen diagnostic, not a revised primary denominator",
    }


def build_u6_source_coordinate_audit(
    pass1_path: Path,
    admission_batch_paths: list[Path],
    postopen_flags_path: Path,
    u2_screen_path: Path,
    u2_receipt_path: Path,
    u6_receipt_path: Path,
) -> dict:
    """Read-only group-level evidence ladder and post-open stage sensitivity."""
    with pass1_path.open(encoding="utf-8") as fh:
        freeze = json.load(fh)
    if freeze.get("pass2", {}).get("primary_model_admission") is not False:
        raise ValueError("U6 source frozen universe must not be primary model eligible")
    evidence, reference_map, source_dependence = _audit_admissions(
        freeze, admission_batch_paths
    )
    all_groups = set(freeze["included_dependency_groups"])
    flags = _load_postopen_flags(postopen_flags_path, all_groups)
    u2, u6 = _screened_design_rows(
        u2_screen_path, u2_receipt_path, u6_receipt_path, all_groups
    )
    counts = Counter(evidence.values())
    hard_flags = {
        group for group, flag in flags.items()
        if flag["flag_code"] in HARD_STAGE_MISMATCH
    }
    if hard_flags != {"Melastoma_affine", "Zea_mays"}:
        raise ValueError("Unexpected hard stage mismatch set")
    all_flags = set(flags)
    fitness_tag_groups = {
        g for g, category in evidence.items()
        if category == "DIRECT_REMOVAL_FITNESS_COST"
    }
    expected_fitness_tag_groups = {
        "Clusia_arrudae", "Melastoma_affine",
        "Campanula_americana", "Grevillea_barklyana"
    }
    if fitness_tag_groups != expected_fitness_tag_groups:
        raise ValueError("Frozen direct-fitness-admission tags changed")

    scenarios = {
        "FROZEN_ALL": all_groups,
        "POSTOPEN_REMOVE_TWO_STAGE_MISMATCHES": all_groups - hard_flags,
        "POSTOPEN_REMOVE_STAGE_AND_BUNDLED_FLOWER": all_groups - all_flags,
        "SOURCE_ADMISSION_FITNESS_TAG_ONLY": fitness_tag_groups,
        "FITNESS_TAG_WITHOUT_HARD_STAGE_MISMATCH": (
            fitness_tag_groups - hard_flags
        ),
    }
    audited = {key: _scenario(u2, u6, value) for key, value in scenarios.items()}

    paths = [
        pass1_path, *admission_batch_paths, postopen_flags_path,
        u2_screen_path, u2_receipt_path, u6_receipt_path,
    ]
    return {
        "analysis": "BALANCE_U6_POSTOPEN_POLLEN_STAGE_EVIDENCE_AUDIT_V1",
        "status": "SOURCE_ONLY_POSTOPEN_EXPLORATORY_NOT_CONFIRMATORY",
        "frozen_u6_group_count": len(all_groups),
        "included_source_receipt_type_counts_by_unique_group": {
            k: counts[k] for k in RECEIPT_TYPES
        },
        "fitness_tag_groups": sorted(fitness_tag_groups),
        "fitness_tag_count_not_causal_effects": len(fitness_tag_groups),
        "postopen_review_flags": {
            group: {
                "flag_code": item["flag_code"],
                "source_stage": item["source_stage"],
                "primary_doi": item["primary_doi"],
                "evidence_limit": item["evidence_limit"],
                "status": item["review_status"],
            }
            for group, item in sorted(flags.items())
        },
        "source_reference_dependence": source_dependence,
        "all_frozen_u6_primary_references_retained": True,
        "original_source_reference_map_unchanged": True,
        "scenario_summary": audited,
        "source_content_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths
        },
        "architecture_outcomes_accessed": False,
        "predictor_adjudications_performed": False,
        "v4_fit_performed": False,
        "biological_inference_limit": (
            "The direct-fitness receipt is an admission evidence tag, not a "
            "reconstructed common-fitness experiment. The flagged mechanism "
            "routes are source-review questions, not retrospective exclusions. "
            "No outcome-class or matched shared-versus-differentiated fitness "
            "worldline has been observed."
        ),
    }

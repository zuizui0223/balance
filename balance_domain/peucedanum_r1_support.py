"""Noninferential observation-grain and complete-case audit for Peucedanum R1.

This does not estimate selection gradients or recreate the source regression.
It records both fruit-complete rows and candidate source-model rows under the
global InitialFruitN + Height complete-case restriction in the archived
R_script_Kudo&Shibata.R, before subsequent FinalFruitN filtering.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping
import csv

from .peucedanum_ingest import NORMALIZED_FIELDS


MISSINGNESS_FIELDS = (
    "initial_fruit_count",
    "intact_fruit_count",
    "flower_stem_height",
    "predator_egg_count",
    "seed_predation_rate",
)
PROVENANCE_KEY = (
    "dataset_id", "source_file", "source_sheet", "source_row_number",
)
BIOLOGICAL_KEY = ("year", "population_id", "plant_id")


def _text(row: Mapping[str, object], key: str) -> str:
    value = row.get(key)
    if value is None:
        return ""
    return str(value).strip()


def _is_present(row: Mapping[str, object], key: str) -> bool:
    return bool(_text(row, key))


def build_r1_row_support_audit(rows: Iterable[Mapping[str, object]]) -> dict:
    """Return source-row counts, missingness, and ID-key collisions.

    Do not deduplicate observations on plant ID. Source-row identity must
    always be unique; biological-ID collisions are reported, not 'repaired'.
    """
    rows = list(rows)
    if not rows:
        raise ValueError("Peucedanum R1 support audit requires source rows")

    by_year_plot: dict[tuple[str, str], Counter] = defaultdict(Counter)
    by_plot: dict[str, Counter] = defaultdict(Counter)
    missing_counts: Counter = Counter()
    biological_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    seen_source_rows: set[tuple[str, ...]] = set()
    year_counts: Counter = Counter()
    plot_counts: Counter = Counter()

    for i, row in enumerate(rows, start=1):
        absent = [field for field in NORMALIZED_FIELDS if field not in row]
        if absent:
            raise ValueError(
                f"normalized row {i} lacks canonical fields: " + ", ".join(absent)
            )
        provenance = tuple(_text(row, key) for key in PROVENANCE_KEY)
        if not all(provenance):
            raise ValueError(f"row {i} has incomplete source provenance")
        if provenance in seen_source_rows:
            raise ValueError(f"duplicate source-row provenance at row {i}")
        seen_source_rows.add(provenance)

        biological_key = tuple(_text(row, key) for key in BIOLOGICAL_KEY)
        if not all(biological_key):
            raise ValueError(f"row {i} has incomplete year/plot/plant identity")
        biological_groups[biological_key].append(provenance[-1])
        year, plot, _plant_id = biological_key
        year_counts[year] += 1
        plot_counts[plot] += 1

        cell = by_year_plot[(year, plot)]
        plot_cell = by_plot[plot]
        for counter in (cell, plot_cell):
            counter["source_rows"] += 1

        for field in MISSINGNESS_FIELDS:
            if not _is_present(row, field):
                missing_counts[field] += 1
                cell[f"missing_{field}"] += 1

        # The *original* archived R script excludes missing InitialFruitN and
        # Height before EVERY final-fruit model, including the single-trait
        # differential and nls female-gain fit. FinalFruitN is filtered next.
        # Keep the broader fruit-complete count only as a pre-height diagnostic.
        fruit_complete = (
            _is_present(row, "initial_fruit_count")
            and _is_present(row, "intact_fruit_count")
        )
        source_fit_candidate = fruit_complete and _is_present(
            row, "flower_stem_height"
        )
        if fruit_complete:
            cell["pre_height_fruit_complete_rows"] += 1
            plot_cell["pre_height_fruit_complete_rows"] += 1
        if source_fit_candidate:
            cell["differential_candidate_rows"] += 1
            plot_cell["differential_candidate_rows"] += 1
            cell["gradient_candidate_rows"] += 1
            plot_cell["gradient_candidate_rows"] += 1

    reused_ids = [
        {
            "year": key[0],
            "population_id": key[1],
            "plant_id": key[2],
            "source_row_numbers": sorted(ids, key=int),
        }
        for key, ids in sorted(biological_groups.items())
        if len(ids) > 1
    ]
    by_cell = [
        {
            "year": year,
            "population_id": plot,
            "source_rows": counts["source_rows"],
            "missing_intact_fruit_count": counts["missing_intact_fruit_count"],
            "missing_flower_stem_height": counts["missing_flower_stem_height"],
            "pre_height_fruit_complete_rows": counts["pre_height_fruit_complete_rows"],
            "differential_candidate_rows": counts["differential_candidate_rows"],
            "gradient_candidate_rows": counts["gradient_candidate_rows"],
        }
        for (year, plot), counts in sorted(by_year_plot.items())
    ]
    return {
        "schema_version": "BALANCE_PEUCEDANUM_R1_ROW_SUPPORT_AUDIT_V1",
        "analysis": "noninferential_raw_observation_support",
        "source_rows": len(rows),
        "observed_plot_year_cells": len(by_cell),
        "source_fit_plot_year_cells": sum(
            cell["differential_candidate_rows"] > 0 for cell in by_cell
        ),
        "observed_cells_without_source_fit_candidates": [
            {
                "year": cell["year"],
                "population_id": cell["population_id"],
                "source_rows": cell["source_rows"],
            }
            for cell in by_cell
            if cell["differential_candidate_rows"] == 0
        ],
        "year_counts": dict(sorted(year_counts.items())),
        "plot_counts": dict(sorted(plot_counts.items())),
        "missing_counts": {
            key: missing_counts[key] for key in MISSINGNESS_FIELDS
        },
        "pre_height_fruit_complete_rows": sum(
            x["pre_height_fruit_complete_rows"] for x in by_cell
        ),
        "differential_candidate_rows": sum(
            x["differential_candidate_rows"] for x in by_cell
        ),
        "gradient_candidate_rows": sum(
            x["gradient_candidate_rows"] for x in by_cell
        ),
        "candidate_rows_by_plot": {
            plot: {
                "source_rows": counts["source_rows"],
                "pre_height_fruit_complete_rows": counts["pre_height_fruit_complete_rows"],
                "differential_candidate_rows": counts["differential_candidate_rows"],
                "gradient_candidate_rows": counts["gradient_candidate_rows"],
            }
            for plot, counts in sorted(by_plot.items())
        },
        "by_year_plot": by_cell,
        "reused_year_plot_plant_id_keys": reused_ids,
        "reused_biological_id_keys_are_not_automatically_deduplicated": True,
        "candidate_rule": (
            "Source script globally filters InitialFruitN and Height before "
            "differentials, gradients and female-gain fits; final-fruit models "
            "then require FinalFruitN. Fruit-complete before Height restriction "
            "is separately reported. Model-specific inclusion remains subject "
            "to actual source fitting."
        ),
        "claim_ceiling": (
            "source_row_support_only_not_reproduction_of_published_model_"
            "not_independent_individuals_or_balanced_panel"
        ),
    }


def audit_normalized_csv(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != NORMALIZED_FIELDS:
            raise ValueError("normalized Peucedanum CSV header differs from canonical schema")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("normalized CSV contains fields outside canonical schema")
    return build_r1_row_support_audit(rows)

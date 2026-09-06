"""Fail-closed readiness helpers for the Peucedanum raw-data reanalysis.

This module deliberately starts *after* source-specific spreadsheet mapping.
It validates semantically normalized rows and checks whether a reanalysis
recovers the published qualitative regime before any new criticality estimate
is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping


PLOT_ORDER = ("HA", "HL", "HC", "KD", "HD")

PUBLISHED_2025 = {
    "S": {"HA": -0.027, "HL": -0.051, "HC": 0.036, "KD": 0.021, "HD": 0.024},
    "beta": {"HA": -0.035, "HL": -0.029, "HC": 0.034, "KD": 0.008, "HD": 0.026},
    "female_gain_b": {"HA": 0.63, "HL": 0.45, "HC": 1.15, "KD": 1.26, "HD": 1.55},
}

REQUIRED_NORMALIZED_FIELDS = (
    "dataset_id",
    "source_doi",
    "year",
    "population_id",
    "plant_id",
    "flowering_day",
    "perfect_flower_count",
    "male_flower_count",
)


@dataclass(frozen=True)
class RawInventory:
    n_records: int
    years: tuple[int, ...]
    populations: tuple[str, ...]
    datasets: tuple[str, ...]
    seed_predation_rows: int
    female_fitness_rows: int


@dataclass(frozen=True)
class ReproductionGate:
    qualitative_status: str
    failed_checks: tuple[str, ...]
    max_abs_difference_from_published: float
    numeric_tolerance_registered: bool


def _finite_nonnegative(value: object, name: str) -> float:
    x = float(value)
    if not math.isfinite(x) or x < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return x


def validate_normalized_rows(rows: Iterable[Mapping[str, object]]) -> RawInventory:
    """Validate rows after source-specific columns have been mapped.

    This does not guess column meanings.  It only validates the normalized
    semantic contract and preserves missing optional values.
    """
    records = list(rows)
    if not records:
        raise ValueError("at least one normalized record is required")

    years: set[int] = set()
    populations: set[str] = set()
    datasets: set[str] = set()
    seed_rows = 0
    female_rows = 0

    for i, row in enumerate(records):
        missing = [field for field in REQUIRED_NORMALIZED_FIELDS if field not in row]
        if missing:
            raise ValueError(f"row {i} missing normalized fields: {missing}")

        year = int(row["year"])
        population = str(row["population_id"]).strip()
        dataset = str(row["dataset_id"]).strip()
        plant = str(row["plant_id"]).strip()
        if not population or not dataset or not plant:
            raise ValueError(f"row {i} has an empty identifier")

        flowering_day = float(row["flowering_day"])
        if not math.isfinite(flowering_day):
            raise ValueError(f"row {i} flowering_day must be finite")
        perfect = _finite_nonnegative(row["perfect_flower_count"], f"row {i} perfect_flower_count")
        male = _finite_nonnegative(row["male_flower_count"], f"row {i} male_flower_count")
        total = perfect + male
        if total <= 0:
            raise ValueError(f"row {i} has zero total flowers")

        if row.get("seed_predation_rate") not in (None, ""):
            pred = float(row["seed_predation_rate"])
            if not math.isfinite(pred) or not 0 <= pred <= 1:
                raise ValueError(f"row {i} seed_predation_rate must lie in [0,1]")
            seed_rows += 1

        if row.get("intact_fruit_count") not in (None, ""):
            _finite_nonnegative(row["intact_fruit_count"], f"row {i} intact_fruit_count")
            female_rows += 1

        if row.get("male_fraction") not in (None, ""):
            observed = float(row["male_fraction"])
            expected = male / total
            if not math.isclose(observed, expected, rel_tol=1e-9, abs_tol=1e-9):
                raise ValueError(f"row {i} male_fraction is inconsistent with flower counts")

        years.add(year)
        populations.add(population)
        datasets.add(dataset)

    return RawInventory(
        n_records=len(records),
        years=tuple(sorted(years)),
        populations=tuple(sorted(populations)),
        datasets=tuple(sorted(datasets)),
        seed_predation_rows=seed_rows,
        female_fitness_rows=female_rows,
    )


def published_regime_reproduction_gate(
    estimates: Mapping[str, Mapping[str, float]],
) -> ReproductionGate:
    """Check the source-paper regime before allowing new criticality analyses.

    ``estimates`` must contain ``S``, ``beta`` and ``female_gain_b`` for all
    five registered plots.  Numeric closeness is reported but is *not* used as
    a pass/fail gate until the archived source model/code is reproduced and a
    prospective numeric tolerance is registered.
    """
    failed: list[str] = []
    diffs: list[float] = []

    for metric, published in PUBLISHED_2025.items():
        if metric not in estimates:
            raise ValueError(f"missing metric {metric!r}")
        for plot in PLOT_ORDER:
            if plot not in estimates[metric]:
                raise ValueError(f"metric {metric!r} missing plot {plot!r}")
            value = float(estimates[metric][plot])
            if not math.isfinite(value):
                raise ValueError(f"estimate {metric}/{plot} must be finite")
            diffs.append(abs(value - published[plot]))

    # Published critical-region regime: HA/HL on the early/high-predation side,
    # HC/KD/HD on the later/lower-predation side.
    for metric in ("S", "beta"):
        for plot in ("HA", "HL"):
            if not estimates[metric][plot] < 0:
                failed.append(f"{metric}:{plot}:expected_negative")
        for plot in ("HC", "KD", "HD"):
            if not estimates[metric][plot] > 0:
                failed.append(f"{metric}:{plot}:expected_positive")

    for plot in ("HA", "HL"):
        if not estimates["female_gain_b"][plot] < 1:
            failed.append(f"female_gain_b:{plot}:expected_below_1")
    for plot in ("HC", "KD", "HD"):
        if not estimates["female_gain_b"][plot] > 1:
            failed.append(f"female_gain_b:{plot}:expected_above_1")

    status = (
        "PUBLISHED_REGIME_REPRODUCED"
        if not failed
        else "PUBLISHED_REGIME_NOT_REPRODUCED"
    )
    return ReproductionGate(
        qualitative_status=status,
        failed_checks=tuple(failed),
        max_abs_difference_from_published=max(diffs),
        numeric_tolerance_registered=False,
    )

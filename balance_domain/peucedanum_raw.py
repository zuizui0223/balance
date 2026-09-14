"""Fail-closed readiness helpers for the Peucedanum raw-data reanalysis.

This module deliberately starts *after* source-specific spreadsheet mapping.
It validates semantically normalized rows and checks whether a reanalysis
recovers the published qualitative regime before any new criticality estimate
is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
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

_MISSING_IDENTIFIERS = {"none", "null", "nan", "required_before_use"}
_MALE_FRACTION_TOLERANCE = F.from_float(1e-9)


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


def _finite_numeric(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite numeric evidence, not boolean")
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite numeric evidence") from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite numeric evidence")
    return out


def _finite_nonnegative(value: object, name: str) -> float:
    x = _finite_numeric(value, name)
    if x < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return x


def _required_identifier(value: object, name: str) -> str:
    if value is None or isinstance(value, bool):
        raise ValueError(f"{name} must be a non-empty identifier")
    if isinstance(value, (int, float)):
        numeric = _finite_numeric(value, name)
        text = str(value).strip()
        if not math.isfinite(numeric):  # defensive; _finite_numeric already checks
            raise ValueError(f"{name} must be a non-empty identifier")
    else:
        text = str(value).strip()
    if not text or text.casefold() in _MISSING_IDENTIFIERS:
        raise ValueError(f"{name} must be a frozen non-missing identifier")
    return text


def _integer_year(value: object, name: str) -> int:
    numeric = _finite_numeric(value, name)
    if not numeric.is_integer():
        raise ValueError(f"{name} must be an integer-valued finite year")
    return int(numeric)


def _male_fraction_matches(perfect: float, male: float, observed: float) -> bool:
    """Apply the previous math.isclose contract without overflowing counts.

    The expected fraction is evaluated exactly at the supplied-float level.
    This preserves rel_tol=abs_tol=1e-9 while avoiding ``perfect + male``
    overflow for finite large counts.
    """
    perfect_q = F.from_float(perfect)
    male_q = F.from_float(male)
    total_q = perfect_q + male_q
    if total_q <= 0:
        return False
    expected_q = male_q / total_q
    observed_q = F.from_float(observed)
    difference = abs(observed_q - expected_q)
    tolerance = max(
        _MALE_FRACTION_TOLERANCE,
        _MALE_FRACTION_TOLERANCE * max(abs(observed_q), abs(expected_q)),
    )
    return difference <= tolerance


def validate_normalized_rows(rows: Iterable[Mapping[str, object]]) -> RawInventory:
    """Validate rows after source-specific columns have been mapped.

    This does not guess column meanings. It only validates the normalized
    semantic contract and preserves missing optional values. Core provenance
    identifiers must be present and non-empty, and ``year`` must be genuinely
    integer-valued rather than silently truncated by ``int()``.
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

        year = _integer_year(row["year"], f"row {i} year")
        population = _required_identifier(row["population_id"], f"row {i} population_id")
        dataset = _required_identifier(row["dataset_id"], f"row {i} dataset_id")
        _required_identifier(row["source_doi"], f"row {i} source_doi")
        _required_identifier(row["plant_id"], f"row {i} plant_id")

        _finite_numeric(row["flowering_day"], f"row {i} flowering_day")
        perfect = _finite_nonnegative(
            row["perfect_flower_count"], f"row {i} perfect_flower_count"
        )
        male = _finite_nonnegative(row["male_flower_count"], f"row {i} male_flower_count")
        if perfect == 0.0 and male == 0.0:
            raise ValueError(f"row {i} has zero total flowers")

        if row.get("seed_predation_rate") not in (None, ""):
            pred = _finite_numeric(
                row["seed_predation_rate"], f"row {i} seed_predation_rate"
            )
            if not 0 <= pred <= 1:
                raise ValueError(f"row {i} seed_predation_rate must lie in [0,1]")
            seed_rows += 1

        if row.get("intact_fruit_count") not in (None, ""):
            _finite_nonnegative(
                row["intact_fruit_count"], f"row {i} intact_fruit_count"
            )
            female_rows += 1

        if row.get("male_fraction") not in (None, ""):
            observed = _finite_numeric(row["male_fraction"], f"row {i} male_fraction")
            if not _male_fraction_matches(perfect, male, observed):
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
    five registered plots. Numeric closeness is reported but is *not* used as
    a pass/fail gate until the archived source model/code is reproduced and a
    prospective numeric tolerance is registered.
    """
    failed: list[str] = []
    diffs: list[float] = []
    normalized: dict[str, dict[str, float]] = {}

    for metric, published in PUBLISHED_2025.items():
        if metric not in estimates:
            raise ValueError(f"missing metric {metric!r}")
        normalized_metric: dict[str, float] = {}
        for plot in PLOT_ORDER:
            if plot not in estimates[metric]:
                raise ValueError(f"metric {metric!r} missing plot {plot!r}")
            value = _finite_numeric(estimates[metric][plot], f"estimate {metric}/{plot}")
            normalized_metric[plot] = value
            diffs.append(abs(value - published[plot]))
        normalized[metric] = normalized_metric

    # Published critical-region regime: HA/HL on the early/high-predation side,
    # HC/KD/HD on the later/lower-predation side.
    for metric in ("S", "beta"):
        for plot in ("HA", "HL"):
            if not normalized[metric][plot] < 0:
                failed.append(f"{metric}:{plot}:expected_negative")
        for plot in ("HC", "KD", "HD"):
            if not normalized[metric][plot] > 0:
                failed.append(f"{metric}:{plot}:expected_positive")

    for plot in ("HA", "HL"):
        if not normalized["female_gain_b"][plot] < 1:
            failed.append(f"female_gain_b:{plot}:expected_below_1")
    for plot in ("HC", "KD", "HD"):
        if not normalized["female_gain_b"][plot] > 1:
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

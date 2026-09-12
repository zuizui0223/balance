from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean, variance


REQUIRED_FIELDS = {
    "plant_id",
    "flower_id",
    "assigned_z_level",
    "D_state",
    "G_state",
    "P_state",
    "undamaged_mature_viable_seed_count",
    "flower_retained_to_maturity",
    "missing_or_loss_reason",
}

TRUTHY = {"1", "true", "yes", "y", "retained", "matured"}
FALSY = {"0", "false", "no", "n", "lost", "failed"}


def _parse_float(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        out = float(value)
    except ValueError as exc:
        raise ValueError(f"not a numeric value: {value!r}") from exc
    if not math.isfinite(out):
        raise ValueError(f"non-finite numeric value: {value!r}")
    return out


def _parse_retention(value: str) -> bool | None:
    v = (value or "").strip().lower()
    if not v:
        return None
    if v in TRUTHY:
        return True
    if v in FALSY:
        return False
    raise ValueError(f"unrecognized flower_retained_to_maturity value: {value!r}")


def _icc_one_way(values_by_plant: dict[str, list[float]]) -> dict[str, float | int | None]:
    groups = [vals for vals in values_by_plant.values() if vals]
    n_groups = len(groups)
    n_total = sum(len(vals) for vals in groups)
    repeated_groups = sum(len(vals) >= 2 for vals in groups)
    if n_groups < 2 or n_total <= n_groups or repeated_groups < 2:
        return {
            "status": "NOT_ESTIMABLE_NEED_AT_LEAST_TWO_REPEATED_PLANTS",
            "n_plants": n_groups,
            "n_observations": n_total,
            "n_repeated_plants": repeated_groups,
            "icc_one_way": None,
            "between_plant_variance": None,
            "within_plant_variance": None,
            "effective_mean_cluster_size_n0": None,
        }

    grand = sum(sum(vals) for vals in groups) / n_total
    ss_between = sum(len(vals) * (fmean(vals) - grand) ** 2 for vals in groups)
    ss_within = sum(sum((x - fmean(vals)) ** 2 for x in vals) for vals in groups)
    df_between = n_groups - 1
    df_within = n_total - n_groups
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within

    sum_n2 = sum(len(vals) ** 2 for vals in groups)
    n0 = (n_total - sum_n2 / n_total) / df_between
    if n0 <= 0:
        return {
            "status": "NOT_ESTIMABLE_NONPOSITIVE_EFFECTIVE_CLUSTER_SIZE",
            "n_plants": n_groups,
            "n_observations": n_total,
            "n_repeated_plants": repeated_groups,
            "icc_one_way": None,
            "between_plant_variance": None,
            "within_plant_variance": ms_within,
            "effective_mean_cluster_size_n0": n0,
        }

    between_var = max((ms_between - ms_within) / n0, 0.0)
    denom = ms_between + (n0 - 1.0) * ms_within
    icc = None if denom <= 0 else (ms_between - ms_within) / denom
    if icc is not None:
        icc = max(-1.0, min(1.0, icc))

    return {
        "status": "ESTIMABLE",
        "n_plants": n_groups,
        "n_observations": n_total,
        "n_repeated_plants": repeated_groups,
        "icc_one_way": icc,
        "between_plant_variance": between_var,
        "within_plant_variance": ms_within,
        "effective_mean_cluster_size_n0": n0,
    }


def build_receipt(path: Path, *, min_complete: int = 20, min_plants: int = 5) -> dict:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or ())
        missing = sorted(REQUIRED_FIELDS - fields)
        if missing:
            raise ValueError("missing required columns: " + ", ".join(missing))
        rows = list(reader)

    if not rows:
        raise ValueError("pilot file contains no data rows")

    seeds: list[float] = []
    values_by_plant: dict[str, list[float]] = defaultdict(list)
    retention_values: list[bool] = []
    missing_reasons: Counter[str] = Counter()
    cell_counts: Counter[str] = Counter()
    plants = set()
    flowers = set()

    for row in rows:
        plant = (row.get("plant_id") or "").strip()
        flower = (row.get("flower_id") or "").strip()
        if plant:
            plants.add(plant)
        if flower:
            flowers.add(flower)

        retention = _parse_retention(row.get("flower_retained_to_maturity", ""))
        if retention is not None:
            retention_values.append(retention)

        reason = (row.get("missing_or_loss_reason") or "").strip()
        if reason:
            missing_reasons[reason] += 1

        seed = _parse_float(row.get("undamaged_mature_viable_seed_count", ""))
        if seed is not None:
            if seed < 0:
                raise ValueError("undamaged_mature_viable_seed_count cannot be negative")
            seeds.append(seed)
            if plant:
                values_by_plant[plant].append(seed)

        z = (row.get("assigned_z_level") or "NA").strip() or "NA"
        d = (row.get("D_state") or "NA").strip() or "NA"
        g = (row.get("G_state") or "NA").strip() or "NA"
        p = (row.get("P_state") or "NA").strip() or "NA"
        cell_counts[f"z={z}|D={d}|G={g}|P={p}"] += 1

    n_rows = len(rows)
    n_complete = len(seeds)
    outcome_mean = fmean(seeds) if seeds else None
    outcome_variance = variance(seeds) if len(seeds) >= 2 else None
    zero_fraction = (sum(x == 0 for x in seeds) / n_complete) if seeds else None
    dispersion_ratio = (
        outcome_variance / outcome_mean
        if outcome_variance is not None and outcome_mean is not None and outcome_mean > 0
        else None
    )
    retention_fraction = (
        sum(retention_values) / len(retention_values) if retention_values else None
    )
    complete_fraction = n_complete / n_rows

    icc = _icc_one_way(values_by_plant)
    gate_reasons = []
    if n_complete < min_complete:
        gate_reasons.append(f"complete_outcomes_below_minimum:{n_complete}<{min_complete}")
    if len(plants) < min_plants:
        gate_reasons.append(f"plants_below_minimum:{len(plants)}<{min_plants}")
    if outcome_variance is None:
        gate_reasons.append("outcome_variance_not_estimable")
    if icc["status"] != "ESTIMABLE":
        gate_reasons.append("plant_icc_not_estimable")

    status = "NUISANCE_RECEIPT_READY_FOR_POWER_INPUT" if not gate_reasons else "NUISANCE_RECEIPT_INCOMPLETE"

    return {
        "analysis": "pedicularis_stage0_nuisance_receipt_v1",
        "source_file": path.name,
        "status": status,
        "claim_ceiling": (
            "stage0_nuisance_parameters_only_not_evidence_for_SCH_conflict_"
            "BALANCE_occupancy_or_BITA_mechanism"
        ),
        "anti_circularity_rule": (
            "pilot outcome effects must not be used to choose z/A/D levels or the minimum "
            "biologically meaningful effect for power"
        ),
        "thresholds_for_receipt_readiness": {
            "min_complete_outcomes": min_complete,
            "min_unique_plants": min_plants,
        },
        "gate_reasons": gate_reasons,
        "counts": {
            "rows": n_rows,
            "unique_plants": len(plants),
            "unique_flowers": len(flowers),
            "complete_seed_outcomes": n_complete,
            "complete_seed_outcome_fraction": complete_fraction,
            "retention_records": len(retention_values),
            "retention_fraction": retention_fraction,
        },
        "seed_count_nuisance": {
            "mean": outcome_mean,
            "variance": outcome_variance,
            "variance_to_mean_ratio": dispersion_ratio,
            "zero_fraction": zero_fraction,
        },
        "plant_dependence": icc,
        "provisional_cell_counts": dict(sorted(cell_counts.items())),
        "missing_or_loss_reason_counts": dict(sorted(missing_reasons.items())),
        "next_required_inputs": [
            "prospectively_frozen_minimum_biologically_meaningful_effects",
            "prospectively_frozen_equivalence_margins",
            "candidate_plants_and_flowers_per_plant_allocation",
            "attrition_inflation_rule",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pilot_csv", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-complete", type=int, default=20)
    parser.add_argument("--min-plants", type=int, default=5)
    args = parser.parse_args()
    if args.min_complete < 2 or args.min_plants < 2:
        raise SystemExit("minimum thresholds must be >= 2")
    result = build_receipt(
        args.pilot_csv,
        min_complete=args.min_complete,
        min_plants=args.min_plants,
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()

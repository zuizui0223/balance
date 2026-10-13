"""Pre-outcome water-baseline profile screen for the Pedicularis SCH/BALANCE bridge.

This is *not* a structural-architecture or ecological causal test. It checks
whether measured water-depth profiles are compatible with the prospectively
frozen interpretation SCH fixed-water == Experiment-B dry y0.

Inputs contain only water-method measurements; never read seed, pollen, attack,
fitness, or other treatment outcomes. This receipt cannot substitute for direct
source-lineage, B0 selectivity, or physical manipulation verification.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

SCHEMA = "PEDICULARIS_SCH_XY_BASELINE_METHOD_V1"
ARMS = ("SCH_FIXED", "XY_Y0_DRY", "XY_Y1_WET")
FIELDS = (
    "context_id", "population_id", "season_id", "protocol_version",
    "plant_id", "water_compartment_id", "arm",
    "water_depth_early_mm", "water_depth_late_mm",
)
LIMITS = (
    "min_independent_plants_per_arm",
    "max_dry_water_depth_mm",
    "min_wet_water_depth_mm",
    "max_within_arm_water_depth_range_mm",
    "max_sch_y0_profile_endpoint_gap_mm",
)


@dataclass(frozen=True)
class PedicularisBaselineMethodScreen:
    status: str
    reasons: tuple[str, ...]
    context_id: str
    fitness_scale_id: str
    plant_counts: dict[str, int]
    water_depth_extrema_mm: dict[str, tuple[float, float] | None]
    sch_y0_profile_endpoint_gap_mm: float | None
    claim_level: str = "METHOD_PROFILE_ONLY_NOT_CAUSAL_OR_ARCHITECTURE"
    source_field_lineage_verified: bool = False
    reproduction_outcomes_read: bool = False
    structural_architecture_cost_identified: bool = False


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} requires nonblank text")
    s = value.strip()
    if s.casefold() in {"none", "null", "nan", "required_before_use"}:
        raise ValueError(f"{name} requires frozen real identity")
    return s


def _number(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} cannot be boolean")
    try:
        x = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite nonnegative numeric") from exc
    if not isfinite(x) or x < 0:
        raise ValueError(f"{name} must be finite nonnegative numeric")
    return x


def evaluate_pedicularis_baseline_method(rows, config) -> PedicularisBaselineMethodScreen:
    """Screen wet/dry method identity without accessing reproductive outcomes.

    No label-only pass is permitted: SCH and XY y0 must both have dry depth
    support, the profiles must agree within a pre-outcome frozen margin, and
    XY y1 must independently meet the wet depth requirement. Plant counts,
    not repeated flowers, define sample support. Even a passed screen is
    not verified source identity, a B0 causal effect, or BALANCE occupancy.
    """
    if not isinstance(config, dict) or config.get("schema_version") != SCHEMA:
        raise ValueError("baseline method schema mismatch")
    if config.get("status") != "FROZEN_PRE_OUTCOME":
        raise ValueError("baseline method thresholds must be frozen pre-outcome")
    if config.get("blinded_to_biological_outcomes") is not True:
        raise ValueError("baseline method screen must be blinded to outcomes")
    if config.get("expected_sch_water_state") != "XY_Y0_DRY":
        raise ValueError("SCH baseline must prospectively be fixed at dry y0")
    ids = {
        key: _text(config.get(key), key)
        for key in ("context_id", "population_id", "season_id", "protocol_version")
    }
    scale = _text(config.get("fitness_scale_id"), "fitness_scale_id")
    _text(config.get("threshold_justification"), "threshold_justification")
    if not isinstance(config.get("thresholds"), dict) or set(config["thresholds"]) != set(LIMITS):
        raise ValueError("baseline method threshold set mismatch")
    limits = {k: _number(config["thresholds"][k], k) for k in LIMITS}
    minimum = limits["min_independent_plants_per_arm"]
    if not minimum.is_integer() or minimum < 2:
        raise ValueError("min_independent_plants_per_arm must be integer >=2")
    if limits["min_wet_water_depth_mm"] <= limits["max_dry_water_depth_mm"]:
        raise ValueError("wet/dry thresholds must not overlap")
    # Freeze an explicit tolerance, not one tuned after fitness outcomes.
    groups: dict[str, list[float]] = {a: [] for a in ARMS}
    plants: dict[str, set[str]] = {a: set() for a in ARMS}
    seen_compartments: set[str] = set()
    seen_plants: set[str] = set()
    rows = list(rows)
    if not rows:
        raise ValueError("baseline method records are empty")

    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"row {number}: only method-only canonical columns allowed")
        for key, expected in ids.items():
            if _text(row.get(key), f"row {number}.{key}") != expected:
                raise ValueError(f"row {number}: {key} mismatches frozen context")
        arm = _text(row.get("arm"), f"row {number}.arm")
        if arm not in ARMS:
            raise ValueError(f"row {number}: invalid method arm")
        plant = _text(row.get("plant_id"), f"row {number}.plant_id")
        compartment = _text(row.get("water_compartment_id"), f"row {number}.water_compartment_id")
        if plant in seen_plants:
            raise ValueError("duplicate plant_id: only one independent plant/arm assignment")
        if compartment in seen_compartments:
            raise ValueError("duplicate water_compartment_id")
        seen_plants.add(plant)
        seen_compartments.add(compartment)
        early = _number(row.get("water_depth_early_mm"), "water_depth_early_mm")
        late = _number(row.get("water_depth_late_mm"), "water_depth_late_mm")
        groups[arm].extend((early, late))
        plants[arm].add(plant)

    reasons: set[str] = set()
    extrema: dict[str, tuple[float, float] | None] = {}
    for arm in ARMS:
        depths = groups[arm]
        if len(plants[arm]) < int(minimum):
            reasons.add(f"insufficient_independent_plants:{arm}")
        if not depths:
            extrema[arm] = None
            continue
        low, high = min(depths), max(depths)
        extrema[arm] = (low, high)
        if high - low > limits["max_within_arm_water_depth_range_mm"]:
            reasons.add(f"water_depth_not_held_fixed:{arm}")
        if arm == "XY_Y1_WET":
            if low < limits["min_wet_water_depth_mm"]:
                reasons.add("xy_y1_not_reliably_wet")
        elif high > limits["max_dry_water_depth_mm"]:
            reasons.add(f"baseline_not_reliably_dry:{arm}")

    endpoint_gap = None
    sch, y0 = extrema["SCH_FIXED"], extrema["XY_Y0_DRY"]
    if sch is not None and y0 is not None:
        endpoint_gap = max(abs(sch[0] - y0[0]), abs(sch[1] - y0[1]))
        if endpoint_gap > limits["max_sch_y0_profile_endpoint_gap_mm"]:
            reasons.add("sch_y0_water_profile_not_matched")
    return PedicularisBaselineMethodScreen(
        status=(
            "BASELINE_METHOD_PROFILE_SCREEN_PASSED_NOT_CAUSAL"
            if not reasons else "BASELINE_METHOD_HOLD"
        ),
        reasons=tuple(sorted(reasons)),
        context_id=ids["context_id"],
        fitness_scale_id=scale,
        plant_counts={arm: len(plants[arm]) for arm in ARMS},
        water_depth_extrema_mm=extrema,
        sch_y0_profile_endpoint_gap_mm=endpoint_gap,
    )

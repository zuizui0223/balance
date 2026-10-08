"""Source-informed, outcome-blinded allocation gate: density x water defence.

Scientific scope: only checks whether a prospective within-patch randomized
three-arm water comparison could identify treatment-effect heterogeneity
conditional on *observed* local patch density. No density-causal or
water-fitness result is inferred. Density strata require pre-outcome freeze.

Unit: one water-holding bract/whorl compartment per randomized plant,
nested in a patch (density replication is PATCHES, never individual plants).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import isfinite

SCHEMA = "PEDICULARIS_DENSITY_WATER_ALLOCATION_PROTOCOL_V1"
ARMS = ("INTACT_WET", "INTACT_DRY", "INTACT_REFILLED_WET")
FIELDS = (
    "context_id", "population_id", "season_id", "protocol_version",
    "site_id", "patch_id", "randomization_block_id",
    "plant_id", "water_compartment_id", "assigned_water_arm",
    "preassignment_density_flowering_plants_m2",
    "preassignment_patch_size_flowering_plants",
    "assignment_locked_before_outcomes",
    "water_compartment_confirmed",
)
LIMIT_KEYS = (
    "sparse_max_density_flowering_plants_m2",
    "dense_min_density_flowering_plants_m2",
    "min_patches_per_stratum",
    "min_plants_per_arm_per_patch",
    "min_blocks_with_all_three_arms_per_patch",
)
INTEGER_KEYS = {
    "min_patches_per_stratum", "min_plants_per_arm_per_patch",
    "min_blocks_with_all_three_arms_per_patch",
}


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: required nonblank text")
    value = value.strip()
    if value.casefold() in {"required_before_use", "none", "null", "nan"}:
        raise ValueError(f"{field}: not prospectively frozen")
    return value


def _float(value, field, *, positive=False):
    if isinstance(value, bool):
        raise ValueError(f"{field}: boolean is not a numeric measurement")
    try:
        out = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{field}: not finite numeric") from exc
    if not isfinite(out) or out < 0 or (positive and out <= 0):
        raise ValueError(f"{field}: invalid nonnegative / positive numeric")
    return out


def _binary(value, field):
    if str(value).strip() not in {"0", "1"}:
        raise ValueError(f"{field}: expected 0/1")
    return str(value).strip() == "1"


def _frozen_config(config):
    if not isinstance(config, dict) or config.get("schema_version") != SCHEMA:
        raise ValueError("patch-density water protocol schema mismatch")
    if config.get("status") != "FROZEN_PRE_OUTCOME":
        raise ValueError("patch-density water protocol is not prospectively frozen")
    if config.get("water_method_B0_status") != "B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL":
        raise ValueError("prospectively validated water-only B0 method required")
    # This identifies a claimed upstream method receipt; a SHA alone does not
    # verify its content. Independent matching is a downstream audit.
    sha = _text(config.get("water_B0_receipt_sha256"), "water_B0_receipt_sha256")
    if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("water B0 receipt requires lowercase sha256")
    ids = {k: _text(config.get(k), k) for k in
           ("context_id", "population_id", "season_id", "protocol_version")}
    _text(config.get("density_cutoffs_justification"), "density_cutoffs_justification")
    _text(config.get("water_B0_context_id"), "water_B0_context_id")
    _text(config.get("water_B0_protocol_version"), "water_B0_protocol_version")
    if config.get("allocation_locked_before_biological_outcomes") is not True:
        raise ValueError("allocation not frozen before biological outcomes")
    limits = config.get("thresholds")
    if not isinstance(limits, dict) or set(limits) != set(LIMIT_KEYS):
        raise ValueError("density allocation threshold keys mismatch")
    result = {}
    for key in LIMIT_KEYS:
        val = _float(limits[key], key, positive=True)
        if key in INTEGER_KEYS:
            if not val.is_integer() or val < 1:
                raise ValueError(f"{key}: requires integer >=1")
            result[key] = int(val)
        else:
            result[key] = val
    if result["sparse_max_density_flowering_plants_m2"] >= (
        result["dense_min_density_flowering_plants_m2"]
    ):
        raise ValueError("density strata overlap")
    return ids, result, sha


def assess_density_water_allocation(
    rows, config, *, b0_method_receipt, b0_method_sha256
):
    """No egg, seed, pollen, visit, geometry-outcome, or treatment-effect input.

    The B0 receipt must come from an independently run method-feasibility
    audit. The caller must provide its SHA256, which the CLI computes from
    actual input bytes. This is a provenance check, not proof of experimental
    water fidelity in the *new* density trial.
    """
    ids, lim, receipt_sha = _frozen_config(config)
    if b0_method_sha256 != receipt_sha:
        raise ValueError("B0 receipt bytes do not match prospectively frozen SHA256")
    if not isinstance(b0_method_receipt, dict):
        raise ValueError("validated B0 method receipt required")
    if (b0_method_receipt.get("schema_version")
            != "PEDICULARIS_WATER_B0_METHOD_FEASIBILITY_RECEIPT_V1"
            or b0_method_receipt.get("status")
            != "B0_METHOD_FEASIBILITY_SCREEN_PASSED_NOT_CAUSAL"):
        raise ValueError("independently checked B0 method PASS receipt required")
    source_ctx = b0_method_receipt.get("context")
    if not isinstance(source_ctx, dict):
        raise ValueError("B0 method context mapping missing")
    for field in ("population_id", "season_id"):
        if source_ctx.get(field) != ids[field]:
            raise ValueError("B0 method and density design contexts do not match")
    if (source_ctx.get("context_id") != config["water_B0_context_id"]
            or source_ctx.get("protocol_version")
            != config["water_B0_protocol_version"]):
        raise ValueError("B0 source method context/version not registered")
    # A method pilot and a final randomized trial can use distinct versions.
    if b0_method_receipt.get("randomization_unit") != (
        "PLANT_WITH_ONE_WATER_COMPARTMENT_PER_PLANT"
    ):
        raise ValueError("B0 and B1 randomization units do not match")
    if b0_method_receipt.get("gate_reasons") != []:
        raise ValueError("B0 method receipt contains unresolved failures")
    if (b0_method_receipt.get("causal_water_effect_identified") is not False
            or b0_method_receipt.get("structural_architecture_BALANCE_identified")
            is not False):
        raise ValueError("B0 receipt misrepresents method-only claim ceiling")
    rows = list(rows)
    if not rows:
        raise ValueError("no density allocation rows")
    seen_plants = set()
    seen_compartments = set()
    patches = defaultdict(list)
    reasons = set()
    for idx, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"row {idx}: noncanonical design-only field set")
        for field, expected in ids.items():
            if _text(row.get(field), field) != expected:
                raise ValueError(f"row {idx}: frozen identity mismatch: {field}")
        arm = _text(row["assigned_water_arm"], "assigned_water_arm")
        if arm not in ARMS:
            raise ValueError("unregistered water intervention")
        plant = _text(row["plant_id"], "plant_id")
        compartment = _text(row["water_compartment_id"], "water_compartment_id")
        if plant in seen_plants:
            raise ValueError("duplicate plant ID: allocation must be one compartment per plant")
        if compartment in seen_compartments:
            raise ValueError("duplicate water-compartment ID")
        seen_plants.add(plant)
        seen_compartments.add(compartment)
        if not _binary(row["assignment_locked_before_outcomes"],
                       "assignment_locked_before_outcomes"):
            reasons.add("assignment_not_preoutcome_locked")
        if not _binary(row["water_compartment_confirmed"],
                       "water_compartment_confirmed"):
            reasons.add("unverified_shared_water_compartment")
        density = _float(row["preassignment_density_flowering_plants_m2"],
                         "preassignment_density", positive=True)
        patch_size = _float(row["preassignment_patch_size_flowering_plants"],
                            "preassignment_patch_size", positive=True)
        if not patch_size.is_integer():
            raise ValueError("patch_size must be an integer count")
        site = _text(row["site_id"], "site_id")
        patch = _text(row["patch_id"], "patch_id")
        block = _text(row["randomization_block_id"], "randomization_block_id")
        patches[(site, patch)].append({
            "plant": plant, "block": block, "arm": arm,
            "density": density, "patch_size": int(patch_size),
        })

    patch_summaries = []
    by_stratum = Counter()
    for (site, patch), samples in sorted(patches.items()):
        density_vals = {x["density"] for x in samples}
        patch_sizes = {x["patch_size"] for x in samples}
        if len(density_vals) != 1 or len(patch_sizes) != 1:
            raise ValueError("patch baseline density/size changed between plant records")
        density = next(iter(density_vals))
        patch_size = next(iter(patch_sizes))
        if len(samples) > patch_size:
            raise ValueError("sampled independent plants exceed patch's registered size")
        stratum = (
            "SPARSE" if density < lim["sparse_max_density_flowering_plants_m2"]
            else "DENSE" if density > lim["dense_min_density_flowering_plants_m2"]
            else "INTERMEDIATE_NOT_REGISTERED"
        )
        if stratum == "INTERMEDIATE_NOT_REGISTERED":
            reasons.add("intermediate_density_patch_requires_preregistered_route")
        arms = Counter(x["arm"] for x in samples)
        for arm in ARMS:
            if arms[arm] < lim["min_plants_per_arm_per_patch"]:
                reasons.add(f"insufficient_arm_support:{site}/{patch}/{arm}")
        by_block = defaultdict(set)
        for x in samples:
            by_block[x["block"]].add(x["arm"])
        shared_blocks = sum(set(ARMS).issubset(v) for v in by_block.values())
        if shared_blocks < lim["min_blocks_with_all_three_arms_per_patch"]:
            reasons.add(f"within_patch_arms_confounded_with_blocks:{site}/{patch}")
        if stratum != "INTERMEDIATE_NOT_REGISTERED":
            by_stratum[stratum] += 1
        patch_summaries.append({
            "site_id": site, "patch_id": patch,
            "density_stratum": stratum,
            "density_flowering_plants_m2": density,
            "patch_size_flowering_plants": patch_size,
            "n_independent_plants": len(samples),
            "n_plants_by_arm": dict(sorted(arms.items())),
            "n_blocks_with_all_arms": shared_blocks,
        })
    for stratum in ("SPARSE", "DENSE"):
        if by_stratum[stratum] < lim["min_patches_per_stratum"]:
            reasons.add(f"insufficient_independent_patches:{stratum}")
    return {
        "schema_version": "PEDICULARIS_DENSITY_WATER_ALLOCATION_SUPPORT_V1",
        "status": ("DENSITY_STRATIFIED_WATER_ALLOCATION_SUPPORTED_NOT_EFFECT"
                   if not reasons else "DENSITY_WATER_ALLOCATION_HOLD"),
        "context": ids, "n_independent_plants": len(seen_plants),
        "n_independent_patches": len(patches),
        "patches_by_stratum": dict(sorted(by_stratum.items())),
        "patches": patch_summaries,
        "gate_reasons": sorted(reasons),
        "B0_method_receipt_status": b0_method_receipt["status"],
        "B0_receipt_sha256_content_linked": receipt_sha,
        "B0_method_qualifies_new_density_context_without_retest": False,
        "plant_water_randomization_verified_independently": False,
        "water_effect_identified": False,
        "causal_patch_density_effect_identified": False,
        "water_by_density_effect_heterogeneity_identified": False,
        "BALANCE_worldline_occupancy_identified": False,
        "claim_ceiling": (
            "design_support_only_no_reproductive_outcomes_"
            "no_causal_density_or_architecture_inference"
        ),
    }

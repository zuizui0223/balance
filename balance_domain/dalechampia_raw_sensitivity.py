"""Independent descriptive sensitivity analysis of EXACT Dalechampia 2015 files.

This is not a reproduction of the source mixed-effects model, nor a new
confirmatory test. Experimental arms affect entire blossoms or bract integrity.
Maternal plants, not individual seeds, are resampling units; each blossom
contributes one mean to its maternal plant's treatment mean. All comparisons
condition on observed seed mass, with a separate >=20 mg proxy analysis that
does NOT independently recover the authors' morphological abortion criterion.
"""
from __future__ import annotations

from collections import defaultdict
from math import ceil, floor, fsum, isfinite
import random

from .dalechampia_method_scope import (
    ARMS, FILE_IDENTITIES, SOURCE_ABORTED_COUNTS, SOURCE_SEED_COUNTS,
    _nonblank, _table, parse_source_decimal, verify_exact_dryad_bytes,
)

SCHEMA = "DALECHAMPIA_2015_SOURCE_MATERNAL_SENSITIVITY_V1"
REPS = 10000
SEED = 20261015
REFERENCE_ARM = "cont"
COMPARISON_ARMS = ("bag", "cut", "cutcont")


def _percentile(values: list[float], probability: float) -> float:
    if not values or not 0 <= probability <= 1:
        raise ValueError("invalid bootstrap quantile")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * probability
    a, b = floor(pos), ceil(pos)
    return ordered[a] + (ordered[b] - ordered[a]) * (pos - a)


def _mother_paired_contrast(
    blossoms: dict[tuple[str, str], dict], *,
    arm: str, keep_min_mass: float, random_seed: int,
) -> dict:
    # Every blossom receives equal weight within its mother's arm.
    groups: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    for (mother, _), b in blossoms.items():
        masses = [v for v in b["masses"] if v >= keep_min_mass]
        if masses:
            groups[(mother, b["arm"])].append(fsum(masses) / len(masses))
    maternal_arm: dict[tuple[str, str], float] = {
        key: fsum(means) / len(means) for key, means in groups.items()
    }
    mothers = sorted({x[0] for x in maternal_arm})
    paired = [
        maternal_arm[(m, arm)] - maternal_arm[(m, REFERENCE_ARM)]
        for m in mothers
        if (m, arm) in maternal_arm and (m, REFERENCE_ARM) in maternal_arm
    ]
    n = len(paired)
    if n < 2:
        raise ValueError("not enough source maternal pairs for a contrast")
    point = fsum(paired) / n
    rng = random.Random(random_seed)
    boot = [
        fsum(paired[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(REPS)
    ]
    low = _percentile(boot, .025)
    high = _percentile(boot, .975)
    if not all(isfinite(x) for x in (point, low, high)):
        raise ValueError("maternal contrast is not finite")
    return {
        "comparison": f"{arm}_minus_cont",
        "n_maternal_pairs": n,
        "mean_of_within_mother_blossom_mean_differences_mg": round(point, 6),
        "bootstrap_percentile_95_interval_mg": [round(low, 6), round(high, 6)],
        "bootstrap_replicates": REPS,
        "bootstrap_seed": random_seed,
        "effect_causally_specific_to_bract_carbon": False,
        "original_mixed_model_fitted": False,
    }


def _gas_maternal_paired_summary(
    rows: list[dict], fields: dict[str, str], normalize,
) -> dict:
    """Paired Green-vs-White bract gas exchange, 6 independent plants.

    The source GPPnett column is the intact-minus-bract-removed GPP within
    each blossom. Dividing by the original intact bract area reproduces the
    published area-based photosynthesis. Plant—not replicate or blossom—is
    the bootstrap unit. This experiment is DISTINCT from the maternal
    seed-mass experiment and cannot be joined to causal seed carbon flux.
    """
    source: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        stage = _nonblank(row, fields, normalize("Color"), "gas stage").casefold()
        structure = _nonblank(row, fields, normalize("Bract"), "gas state").casefold()
        if stage not in {"green", "white"} or structure != "bract":
            continue
        plant = _nonblank(row, fields, normalize("Plant_ID"), "gas plant")
        gppnet = parse_source_decimal(row.get(fields[normalize("GPPnett")]),
                                      "GPPnett", allow_missing=False)
        area = parse_source_decimal(row.get(fields[normalize("Area_Leaf.1")]),
                                    "Area_Leaf.1", allow_missing=False)
        if area <= 0:
            raise ValueError("source bract area must be positive")
        source[(plant, stage)].append(gppnet / area)
    plants = sorted({m for m, _ in source})
    if len(plants) != 6 or any(
        len(source[(p, c)]) != 2 for p in plants for c in ("green", "white")
    ):
        raise ValueError("gas assay must retain two independent bract observations per stage on six plants")
    stage_means = {
        color: fsum(value for p in plants for value in source[(p, color)]) / 12
        for color in ("green", "white")
    }
    # Pair within the *gas physiology* plants only; not seed-mass mothers.
    differences = [
        fsum(source[(p, "green")]) / 2 - fsum(source[(p, "white")]) / 2
        for p in plants
    ]
    point = fsum(differences) / len(plants)
    rng = random.Random(SEED + 999)
    boot = [
        fsum(differences[rng.randrange(len(plants))]
             for _ in range(len(plants))) / len(plants)
        for _ in range(REPS)
    ]
    lo, hi = _percentile(boot, .025), _percentile(boot, .975)
    if (round(stage_means["green"], 2), round(stage_means["white"], 2)) != (1.47, 0.42):
        raise ValueError("raw area-based gas source does not reproduce printed green/white means")
    return {
        "source_physiology_plants": 6,
        "source_green_bract_measurements": 12,
        "source_white_bract_measurements": 12,
        "units": "umol_C_per_m2_s",
        "area_based_green_mean": round(stage_means["green"], 6),
        "area_based_white_mean": round(stage_means["white"], 6),
        "ratio_of_means_descriptive_only": round(
            stage_means["green"] / stage_means["white"], 6
        ),
        "within_plant_green_minus_white_mean": round(point, 6),
        "bootstrap_plant_cluster_95_interval": [round(lo, 6), round(hi, 6)],
        "bootstrap_replicates": REPS,
        "plant_seed_mass_experiment_jointly_observed": False,
        "seed_carbon_transfer_identified": False,
        "original_gas_mixed_model_reproduced": False,
    }


def analyze_authenticated_dalechampia(
    contract: dict, raw_files: dict[str, bytes],
) -> dict:
    """Operate only after both files match archived byte size and MD5."""
    authenticated = verify_exact_dryad_bytes(contract, raw_files)
    if authenticated["status"] != "EXACT_DRYAD_BYTES_VERIFIED_SUPPORT_ONLY_NO_MODELS":
        raise ValueError("source row-support receipt not qualified")
    if authenticated["raw_seed_missing_mass"] != 1:
        raise ValueError("exact source missing-mass support drift")
    if authenticated["raw_seed_records"] != 1221:
        raise ValueError("exact source seed record count drift")
    if not authenticated["recorded_mass_counts_match_published_seeds"]:
        raise ValueError("recorded mass counts do not match published treatment totals")
    if not authenticated["numeric_below_20_counts_match_published_abortions"]:
        raise ValueError("numeric <20 mg proxy differs from published abortion counts")

    name = FILE_IDENTITIES[46163][0]
    expected = next(f["expected_fields"] for f in contract["dryad_source_files"]
                    if f["source_file_id"] == 46163)
    rows, fields, normalize = _table(raw_files[name], expected, "original seed source")
    blossoms = {}
    n_masses = 0
    for row in rows:
        mother = _nonblank(row, fields, normalize("FemaleID"), "mother")
        blossom = _nonblank(row, fields, normalize("crossID"), "crossID")
        arm = _nonblank(row, fields, normalize("treatcode"), "treatcode").lower()
        key = (mother, blossom)
        b = blossoms.setdefault(key, {"arm": arm, "masses": []})
        if b["arm"] != arm:
            raise ValueError("blossom treatment must not change across seeds")
        mass = parse_source_decimal(row.get(fields[normalize("seedmass")]),
                                    "seedmass")
        if mass is not None:
            b["masses"].append(mass)
            n_masses += 1

    if (len(blossoms), n_masses) != (142, 1220):
        raise ValueError("exact source blossom/mass coverage drift")
    # Number under 20 reproduces the numerical cutoff only. Original source
    # classified aborted seeds using physical seed-coat/embryo morphology too.
    treatments = {}
    for a in ARMS:
        n = sum(1 for b in blossoms.values() if b["arm"] == a)
        treatments[a] = {"n_blossoms": n}

    analyses = {}
    for lane, minimum in [("all_measured_masses", 0.0),
                          ("numeric_ge20_proxy_only", 20.0)]:
        analyses[lane] = {
            "inclusion_rule": (
                "all_nonmissing_seed_mass"
                if minimum == 0 else "seed_mass_gte20mg_numeric_proxy_not_morphology"
            ),
            "arm_contrasts": [
                _mother_paired_contrast(
                    blossoms, arm=a, keep_min_mass=minimum,
                    random_seed=SEED + 100 * (minimum > 0) + i,
                ) for i, a in enumerate(COMPARISON_ARMS)
            ],
            "original_published_mixed_model_reproduced": False,
            "new_confirmatory_p_values_computed": False,
        }
    gas_name = FILE_IDENTITIES[46164][0]
    gas_expected = next(
        f["expected_fields"] for f in contract["dryad_source_files"]
        if f["source_file_id"] == 46164
    )
    gas_rows, gas_fields, gas_normalize = _table(
        raw_files[gas_name], gas_expected, "original gas source"
    )
    physiology = _gas_maternal_paired_summary(
        gas_rows, gas_fields, gas_normalize
    )
    return {
        "gas_exchange_within_plant": physiology,
        "schema_version": SCHEMA,
        "status": "EXACT_SOURCE_DESCRIPTIVE_MATERNAL_PAIR_SENSITIVITY_NOT_PUBLISHED_MODEL",
        "source_dataset_doi": "10.5061/dryad.nb675",
        "original_files_sha256": authenticated["original_file_sha256"],
        "published_seed_count_support_by_arm": dict(SOURCE_SEED_COUNTS),
        "numeric_20mg_proxy_support_by_arm": dict(SOURCE_ABORTED_COUNTS),
        "numeric_abortions_independently_confirmed_by_morphology": False,
        "n_seed_records": authenticated["raw_seed_records"],
        "n_seed_masses_recorded": n_masses,
        "n_blossoms": len(blossoms),
        "n_maternal_plants_with_any_seed_record": authenticated["raw_independent_maternal_plants"],
        "original_2015_published_model_reproduced": False,
        "original_source_2015_treatment_biological_unit": "blossom",
        "within_blossom_observations_independent": False,
        "bootstrap_sampling_unit": "maternal_plant_paired_treatment_difference",
        "treatments": treatments,
        "analyses": analyses,
        "whole_blossom_foil_treatment_effect_not_bract_local_carbon": True,
        "cross_2013_2012_study_join_forbidden": True,
        "structural_BALANCE_identified": False,
        "new_independent_biological_clusters": 0,
        "claim_ceiling": (
            "retrospective unadjusted paired maternal descriptive sensitivity "
            "conditional on measured seed masses; not original mixed-model or "
            "causal bract carbon mechanism; no structural architecture worldlines"
        ),
    }

"""Forensic fruit-denominator compatibility for exact Xia et al. 2013 XLSX.

This checks *conditional arithmetic consistency*, not biological data errors.
The source workbook does not supply independent fruit-production counts nor
within-patch plant identifiers. No fruit count is imputed or substituted into
the published fruit ANCOVA from this diagnostic.
"""
from __future__ import annotations

from collections import Counter
from math import isfinite

SCHEMA = "PEDICULARIS_2013_FRUIT_INTEGER_DENOMINATOR_AUDIT_V1"
# Original 2013 workbook includes mixed decimal precision, sometimes only
# two decimal places; ±0.0051 percentage points conservatively permits
# normal two-decimal rate rounding plus binary floating-point noise.
RATE_TOLERANCE_PERCENT_POINTS = 0.0051

def _numeric(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a recorded finite number")
    x = float(value)
    if not isfinite(x):
        raise ValueError(f"{name} is not finite")
    return x


def _integer_count(value, name):
    x = _numeric(value, name)
    if x <= 0 or x != int(x):
        raise ValueError(f"{name} must be positive integer count")
    return int(x)


def _possible_numerators(rate_percent, denominator, tolerance):
    if denominator <= 0:
        raise ValueError("integer denominator must be positive")
    return [
        k for k in range(denominator + 1)
        if abs(100.0*k/denominator - rate_percent) <= tolerance
    ]


def audit_fruit_denominators(rows, *,
                             tolerance_pct_points=RATE_TOLERANCE_PERCENT_POINTS):
    """rows: original 74 biological fruit-worksheet records (no legends)."""
    tolerance = _numeric(tolerance_pct_points, "tolerance_pct_points")
    if not 0 < tolerance <= RATE_TOLERANCE_PERCENT_POINTS:
        raise ValueError("denominator audit cannot relax frozen rounding tolerance")
    rows = list(rows)
    if len(rows) != 74:
        raise ValueError("expected 74 source biological fruit worksheet rows")
    group_sizes = Counter()
    data = []
    status_counts = Counter()
    by_year = {"2005": Counter(), "2011": Counter()}
    invalid_fruit = []
    invalid_pred = []
    for source_row, row in enumerate(rows, start=2):
        if not isinstance(row, (list, tuple)) or len(row) != 6:
            raise ValueError("source fruit row must preserve six original columns")
        year_code, density_code, size_code, n_flowers, fruit_pct, pred_pct = row
        if (year_code not in (1, 2) or density_code not in (1, 2)
                or size_code not in (1, 2)):
            raise ValueError("original source category code changed")
        n_flowers = _integer_count(n_flowers, "flowers")
        fruit_pct = _numeric(fruit_pct, "fruit set")
        pred_pct = _numeric(pred_pct, "fruit predation")
        if not (0 <= fruit_pct <= 100 and 0 <= pred_pct <= 100):
            raise ValueError("source fruit percentage outside [0,100]")
        yr = "2005" if year_code == 1 else "2011"
        density = "sparse" if density_code == 1 else "dense"
        size = "small" if size_code == 1 else "large"
        key = f"{yr}_{density}_{size}"
        group_sizes[key] += 1
        fruit_candidates = _possible_numerators(
            fruit_pct, n_flowers, tolerance
        )
        pred_candidates = (
            _possible_numerators(pred_pct, fruit_candidates[0], tolerance)
            if len(fruit_candidates) == 1 and fruit_candidates[0] > 0
            else []
        )
        if not fruit_candidates:
            status = "FRUIT_SET_DENOMINATOR_NOT_INTEGER_COMPATIBLE"
            invalid_fruit.append(source_row)
        elif len(fruit_candidates) > 1:
            status = "FRUIT_SET_DENOMINATOR_NOT_UNIQUE"
            invalid_fruit.append(source_row)
        elif fruit_candidates[0] == 0:
            status = "PREDATION_DENOMINATOR_ZERO"
            invalid_pred.append(source_row)
        elif not pred_candidates:
            status = "PREDATION_NOT_COMPATIBLE_WITH_FRUIT_SET_COUNT"
            invalid_pred.append(source_row)
        elif len(pred_candidates) > 1:
            status = "PREDATION_DAMAGE_NUMERATOR_NOT_UNIQUE"
            invalid_pred.append(source_row)
        else:
            status = "JOINT_INTEGER_CHAIN_COMPATIBLE_NOT_INDEPENDENTLY_VERIFIED"
        status_counts[status] += 1
        by_year[yr][status] += 1
        data.append({
            "source_xlsx_row": source_row,
            "year": yr, "density": density, "size": size,
            "flowers_recorded": n_flowers,
            "fruit_set_rate_percent_recorded": fruit_pct,
            "fruit_predation_rate_percent_recorded": pred_pct,
            "candidate_fruit_production_counts": fruit_candidates,
            "candidate_damaged_fruit_counts_if_fruit_set_compatible":
                pred_candidates,
            "status": status,
        })
    expected = {
        "2005_sparse_large": 6, "2005_dense_large": 10,
        "2011_sparse_small": 9, "2011_sparse_large": 17,
        "2011_dense_small": 7, "2011_dense_large": 25,
    }
    if dict(group_sizes) != expected:
        raise ValueError("fruit category support differs from registered source")
    # This is an *inferential* hold, not a source-integrity or
    # registered-ANOVA failure. Source percentages remain untouched.
    result = {
        "schema_version": SCHEMA,
        "status": "CONDITIONAL_INTEGER_DENOMINATOR_CHAIN_INCOMPLETE_HOLD",
        "source_article_doi": "10.1098/rsbl.2013.0387",
        "source_dataset_doi": "10.5061/dryad.6cv06",
        "source_xlsx_sha256":
            "d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380",
        "rate_tolerance_percent_points": tolerance,
        "original_fruit_sheet_biological_rows": len(rows),
        "counts": dict(sorted(status_counts.items())),
        "counts_by_year": {
            k:dict(sorted(v.items())) for k,v in by_year.items()
        },
        "fruit_set_rate_not_supported_by_integer_count_rows":invalid_fruit,
        "predation_not_supported_conditional_on_fruit_count_rows": invalid_pred,
        "source_row_records":data,
        "joint_chain_support_rows":status_counts[
            "JOINT_INTEGER_CHAIN_COMPATIBLE_NOT_INDEPENDENTLY_VERIFIED"],
        "fruit_production_count_identified_as_source_variable":False,
        "fruit_predation_denominator_independently_verified":False,
        "published_fruit_ANCOVA_covariate_reconstructed":False,
        "observed_rates_changed_or_imputed":False,
        "patch_clustered_inference_identified":False,
        "source_anomaly_interpreted_as_error":False,
        "claim_ceiling":"conditional_integer_arithmetic_audit_only_no_raw_fruit_production_or_patch_ids",
    }
    return result

"""Relaxed equal-patch average bounds when original patch memberships are lost.

Exactly sharp for an *unconstrained* nonempty row-to-patch partition subject to
a minimum number of sampled rows per patch. Ignoring fixed patch-size
categories or plant clustering makes these an OUTER envelope for the actual
unknown field estimand, not a confidence interval or a patch reconstruction.
"""
from __future__ import annotations
import math


def equal_patch_mean_envelope(values, patch_count: int, minimum_rows: int = 1) -> dict:
    if isinstance(patch_count, bool) or not isinstance(patch_count, int) or patch_count < 2:
        raise ValueError("at least two independently named patches required")
    if isinstance(minimum_rows, bool) or not isinstance(minimum_rows, int) or minimum_rows < 1:
        raise ValueError("minimum rows per patch must be an integer >=1")
    values = list(values)
    if len(values) < patch_count * minimum_rows:
        raise ValueError("not enough observations for assumed patch count and min sample")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or
           not math.isfinite(v) or not 0 <= v <= 100 for v in values):
        raise ValueError("observed outcomes must be finite percentages in [0,100]")
    s = sorted(float(v) for v in values)
    n = len(s)
    small_total = (patch_count-1)*minimum_rows
    large_count = n-small_total
    lower = (math.fsum(s[:small_total])/minimum_rows +
             math.fsum(s[small_total:])/large_count)/patch_count
    upper = (math.fsum(s[large_count:])/minimum_rows +
             math.fsum(s[:large_count])/large_count)/patch_count
    if lower > upper + 1e-10:
        raise ValueError("internal envelope order failure")
    return {
        "sample_rows": n,
        "published_patch_count": patch_count,
        "assumed_min_rows_per_patch": minimum_rows,
        "row_weighted_mean_percent": math.fsum(s)/n,
        "hypothetical_equal_patch_mean_lower_percent": lower,
        "hypothetical_equal_patch_mean_upper_percent": upper,
        "extreme_allocation_group_sizes_only": [minimum_rows]*(patch_count-1)+[large_count],
        "actual_patch_ids_observed": False,
        "patch_level_confidence_interval": False,
    }


def density_contrast_envelope(sparse_values, dense_values, sparse_patches, dense_patches,
                              minimum_rows=1):
    sparse = equal_patch_mean_envelope(sparse_values, sparse_patches, minimum_rows)
    dense = equal_patch_mean_envelope(dense_values, dense_patches, minimum_rows)
    lo = (dense["hypothetical_equal_patch_mean_lower_percent"] -
          sparse["hypothetical_equal_patch_mean_upper_percent"])
    hi = (dense["hypothetical_equal_patch_mean_upper_percent"] -
          sparse["hypothetical_equal_patch_mean_lower_percent"])
    return {
        "sparse": sparse, "dense": dense,
        "row_weighted_dense_minus_sparse_pp": (
            dense["row_weighted_mean_percent"]-sparse["row_weighted_mean_percent"]),
        "relaxed_equal_patch_dense_minus_sparse_lower_pp": lo,
        "relaxed_equal_patch_dense_minus_sparse_upper_pp": hi,
        "relaxed_envelope_contains_both_signs": lo < 0 < hi,
        "patch_size_categories_and_plant_membership_not_enforced": True,
        "actual_patch_membership_reconstructed": False,
        "patch_level_p_value_or_se_estimated": False,
        "causal_density_effect_identified": False,
    }

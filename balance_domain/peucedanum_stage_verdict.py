"""Audit-only synthesis of Peucedanum observed stage support and slope receipts.

Exploratory q-values are screening diagnostics, not causal-selection proofs.
The source published-coefficient reproduction remains a separate open gate.
"""
from __future__ import annotations

import math


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def adjudicate_stage_exploration(
    support: dict, unadjusted: dict, adjusted: dict
) -> dict:
    _require(support.get("schema_version") == "BALANCE_PEUCEDANUM_STAGE_SUPPORT_AUDIT_V1",
             "stage support schema mismatch")
    _require(support.get("source_rows") == 685, "source-row support changed")
    _require(support.get("observed_plot_year_cells") == 19, "plot-year source support changed")
    _require(support.get("status") == "COUNT_INCONSISTENCY_HOLD",
             "source count-inconsistency gate unexpectedly changed")
    _require(len(support.get("count_inconsistencies", [])) == 3,
             "nonnested fruit-count audit unexpectedly changed")
    _require(unadjusted.get("schema_version") == "PEUCEDANUM_STAGE_SLOPES_EXPLORATORY_V1",
             "unadjusted paired-slope schema mismatch")
    _require(adjusted.get("schema_version") == "PEUCEDANUM_STAGE_ADJUSTED_EXPLORATORY_V1",
             "adjusted paired-slope schema mismatch")
    _require(adjusted.get("status") == "EXPLORATORY_ASSOCIATION_ONLY",
             "adjusted stage status is not exploratory")
    _require(adjusted.get("source_normalized_csv_sha256") ==
             "ed6bf4c5301309283ca2e3d2033fdab1e253d46ed94bbba5fde1f3ee43281dbc",
             "adjusted result lacks exact source-byte binding")
    _require(adjusted.get("primary_predictor") == "log1p_male_flower_count",
             "primary predictor changed")

    raw = unadjusted.get("cells", [])
    _require(len(raw) == 18, "unadjusted plot-year support changed")
    raw_keys = set()
    flip = []
    for cell in raw:
        key = (cell["year"], cell["plot"])
        _require(key not in raw_keys, "duplicate unadjusted plot-year")
        raw_keys.add(key)
        _require(cell.get("status") == "DESCRIPTIVE_ONLY", "unsupported raw slope cell")
        a, b = cell["beta_initial"], cell["beta_final"]
        _require(math.isfinite(a) and math.isfinite(b), "nonfinite raw slope")
        if (a > 0 > b) or (a < 0 < b):
            flip.append({"year": cell["year"], "plot": cell["plot"],
                         "beta_initial": a, "beta_final": b})
    _require(set(adjusted.get("variants", {})) == {
        "log_male_count_all_pairs",
        "log_male_count_excluding_nonnested",
        "perfect_fraction_all_pairs",
        "perfect_fraction_excluding_nonnested",
    }, "adjusted variants changed")

    findings = {}
    for name, group in sorted(adjusted["variants"].items()):
        cells = group["cells"]
        _require(len(cells) == 19, "adjusted plot-year support changed")
        _require(len({(x["year"], x["plot"]) for x in cells}) == 19,
                 "duplicate adjusted plot-year")
        _require(raw_keys.issubset({(x["year"], x["plot"]) for x in cells}),
                 "unadjusted cells absent in adjusted result")
        _require(group.get("n_nonnull_tests") == 17,
                 "adjusted estimability unexpectedly changed")
        n = sum(x["n"] for x in cells)
        _require(n == (605 if name.endswith("_excluding_nonnested") else 608),
                 "adjusted source-row support unexpectedly changed")
        eligible = [x for x in cells if x.get("p_normal_hc3") is not None]
        _require(len(eligible) == 17, "nondegenerate test count changed")
        for x in eligible:
            _require(x.get("status") == "EXPLORATORY_FIT", "non-fit with numeric p")
            for field in ("coefficient_per_sd", "se_hc3", "p_normal_hc3",
                          "q_bh_within_variant"):
                _require(math.isfinite(x[field]), "nonfinite exploratory statistic")
            _require(x["se_hc3"] > 0, "nonpositive standard error")
            _require(0 <= x["p_normal_hc3"] <= 1, "invalid p value")
            _require(x["p_normal_hc3"] <= x["q_bh_within_variant"] <= 1 + 1e-12,
                     "invalid BH multiplicity result")
        # Recompute BH independently rather than trusting reported q-values.
        ranked = sorted(enumerate(eligible), key=lambda pair: pair[1]["p_normal_hc3"])
        expected_q = [None] * len(ranked)
        ceiling = 1.0
        for rank in range(len(ranked) - 1, -1, -1):
            original_index, item = ranked[rank]
            ceiling = min(ceiling, item["p_normal_hc3"] * len(ranked) / (rank + 1))
            expected_q[original_index] = ceiling
        for item, q_expected in zip(eligible, expected_q):
            _require(abs(item["q_bh_within_variant"] - q_expected) < 1e-9,
                     "BH-adjusted q differs from independently reproduced value")
        best = min(eligible, key=lambda x: x["p_normal_hc3"])
        min_q = min(x["q_bh_within_variant"] for x in eligible)
        findings[name] = {
            "fitted_source_rows": n,
            "nondegenerate_tests": len(eligible),
            "minimum_nominal_p": best["p_normal_hc3"],
            "minimum_BH_q_within_variant": min_q,
            "strongest_nominal_cell": {"year": best["year"], "plot": best["plot"]},
            "q_below_0_05": sum(x["q_bh_within_variant"] < 0.05 for x in eligible),
            "screening_label": (
                "EXPLORATORY_Q_BELOW_0_05_NOT_CONFIRMATORY"
                if min_q < 0.05 else "NO_BH_SCREENING_SIGNAL"
            ),
        }

    # This is explicitly a post-observation synthesis: no interpretation of
    # significant nominal p-values or flip counts as independent confirmation.
    return {
        "schema_version": "BALANCE_PEUCEDANUM_STAGE_EXPLORATORY_ADJUDICATION_V1",
        "status": "EXPLORATORY_REPORT_COMPLETED_NOT_CONFIRMATORY",
        "source_rows": 685,
        "source_count_inconsistency_hold": True,
        "descriptive_sign_flip_count": len(flip),
        "descriptive_sign_flips": flip,
        "adjusted_variants": findings,
        "original_publication_R1_reproduction": "NOT_FULLY_REPRODUCED",
        "independent_ecological_discovery": False,
        "causal_predation_mediation_identified": False,
        "BALANCE_worldline_occupancy_identified": False,
        "claim_ceiling": (
            "retrospective_source_specific_robustness_only_"
            "no_independent_reversal_or_architecture_evidence"
        ),
    }

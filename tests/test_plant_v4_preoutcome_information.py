"""Tests of a source-side information *benchmark*, not biological outcomes."""
from pathlib import Path

import pytest

from balance_domain.plant_v4_preoutcome_information import (
    _exact_inverse_of_gram,
    build_v4_preoutcome_information_benchmark,
)

ROOT = Path(__file__).resolve().parents[1]
U2_CONFLICT = ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
U2_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U6_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"


def run(u6=U6_RECEIPTS):
    return build_v4_preoutcome_information_benchmark(
        U2_CONFLICT, U2_RECEIPTS, u6
    )


def test_exact_optimistic_information_ceiling_matches_frozen_v4_design():
    b = run()
    z = b["optimistic_binary_logit_benchmarks"]["pooled_universe_adjusted"]
    assert z["module_MODULAR"]["gram_inverse_diagonal_exact"] == "33/56"
    assert z["temporal_ORDERED_OR_ALTERNATING"]["gram_inverse_diagonal_exact"] == "7/24"
    assert z["temporal_VARIABLE_CONTEXT"]["gram_inverse_diagonal_exact"] == "33/56"
    assert z["module_MODULAR"]["optimistic_binary_logit_se_floor"] == pytest.approx(
        1.535298947157477
    )
    assert z["temporal_ORDERED_OR_ALTERNATING"][
        "optimistic_binary_logit_se_floor"
    ] == pytest.approx(1.0801234497346432)


def test_u2_only_is_more_information_limited_than_pooled():
    b = run()["optimistic_binary_logit_benchmarks"]
    assert b["u2_only"]["module_MODULAR"]["gram_inverse_diagonal_exact"] == "3/4"
    assert b["u2_only"]["temporal_ORDERED_OR_ALTERNATING"][
        "gram_inverse_diagonal_exact"
    ] == "7/6"
    assert b["u6_only"]["temporal_ORDERED_OR_ALTERNATING"][
        "gram_inverse_diagonal_exact"
    ] == "7/18"
    assert b["u2_only"]["temporal_ORDERED_OR_ALTERNATING"][
        "optimistic_binary_logit_se_floor"
    ] > b["pooled_universe_adjusted"]["temporal_ORDERED_OR_ALTERNATING"][
        "optimistic_binary_logit_se_floor"
    ]


def test_same_kirk_1987_original_research_programme_is_not_counted_twice():
    b = run()
    assert b["n_source_screened_biological_groups"] == 29
    assert b["source_key_block_count"] == 28
    assert b["multi_group_source_blocks"] == {
        "Kirk 1987 Ecological Entomology; DOI 10.1111/j.1365-2311.1987.tb00982.x": [
            "Actinidia_deliciosa", "Echium_plantagineum"
        ]
    }
    loo = b["leave_one_primary_source_key_out"]
    assert loo["n_blocks_checked"] == 28
    assert loo["rank_deficient_deletions"] == 0
    assert loo["minimum_primary_level_support_failures"] == 0


def test_never_reads_focal_architecture_or_interprets_binary_bound_as_v4_power():
    b = run()
    assert b["architecture_outcomes_used"] is False
    assert b["fitted_effects"] is False
    assert b["statistical_power_estimated"] is False
    assert "not the posterior uncertainty" in b["information_assumptions"]


def test_singular_gram_fails_closed():
    with pytest.raises(ValueError, match="Singular design"):
        _exact_inverse_of_gram([[1, 1], [1, 1], [1, 1]])


def test_incomplete_u6_source_screen_fails_closed(tmp_path):
    raw = U6_RECEIPTS.read_text(encoding="utf-8")
    assert ",SCREENED," in raw
    changed = raw.replace(",SCREENED,", ",ADJUDICATED,", 1)
    path = tmp_path / "u6_invalid.csv"
    path.write_text(changed, encoding="utf-8")
    with pytest.raises(ValueError, match="SCREENED receipts only"):
        run(u6=path)

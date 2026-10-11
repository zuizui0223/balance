"""Synthetic integer-chain tests; no source values are altered or imputed."""
import pytest

from balance_domain.pedicularis_2013_fruit_denominators import (
    RATE_TOLERANCE_PERCENT_POINTS,
    audit_fruit_denominators,
)


def fixture_rows():
    # Exactly the registered source support: 6/10 in 2005, 9/17/7/25
    # by sparse-small/sparse-large/dense-small/dense-large in 2011.
    groups = [(1,1,2,6),(1,2,2,10),
              (2,1,1,9),(2,1,2,17),(2,2,1,7),(2,2,2,25)]
    rows = []
    for yr,den,size,n in groups:
        for _ in range(n):
            rows.append([yr,den,size,40,50.0,50.0])
    assert len(rows) == 74
    return rows


def test_compatible_integer_chain_is_only_arithmetic_support():
    r = audit_fruit_denominators(fixture_rows())
    assert r["joint_chain_support_rows"] == 74
    assert r["status"] == "CONDITIONAL_INTEGER_DENOMINATOR_CHAIN_INCOMPLETE_HOLD"
    assert r["source_anomaly_interpreted_as_error"] is False
    assert r["published_fruit_ANCOVA_covariate_reconstructed"] is False
    assert r["patch_clustered_inference_identified"] is False


def test_rate_rounding_tolerance_does_not_automatically_correct_source():
    rows = fixture_rows()
    rows[0][4] = 77.73  # impossible among 0..44 integers for 44 flowers
    rows[0][3] = 44
    r = audit_fruit_denominators(rows)
    assert r["fruit_set_rate_not_supported_by_integer_count_rows"] == [2]
    assert r["joint_chain_support_rows"] == 73
    assert r["source_row_records"][0]["candidate_fruit_production_counts"] == []


def test_predation_denominator_incompatibility_is_separate_from_fruit_set():
    rows = fixture_rows()
    rows[0] = [1,1,2,40,90.0,5.128205128]  # 36 fruit, 2/39 predation
    report = audit_fruit_denominators(rows)
    assert report["predation_not_supported_conditional_on_fruit_count_rows"] == [2]
    assert report["joint_chain_support_rows"] == 73
    rec = report["source_row_records"][0]
    assert rec["candidate_fruit_production_counts"] == [36]
    assert rec["candidate_damaged_fruit_counts_if_fruit_set_compatible"] == []


def test_rounded_two_decimal_fraction_permitted():
    rows = fixture_rows()
    rows[0] = [1,1,2,44,63.64,50]  # 28/44, 14/28
    report = audit_fruit_denominators(rows)
    assert report["joint_chain_support_rows"] == 74


def test_count_or_rate_domain_failure_rejected():
    rows = fixture_rows()
    rows[0][3] = 0
    with pytest.raises(ValueError, match="positive integer"):
        audit_fruit_denominators(rows)
    rows = fixture_rows()
    rows[0][4] = 110
    with pytest.raises(ValueError, match="outside"):
        audit_fruit_denominators(rows)
    rows = fixture_rows()
    rows[0][5] = float("nan")
    with pytest.raises(ValueError, match="not finite"):
        audit_fruit_denominators(rows)


def test_frozen_tolerance_and_exact_category_counts():
    rows = fixture_rows()
    with pytest.raises(ValueError, match="cannot relax"):
        audit_fruit_denominators(rows, tolerance_pct_points=0.5)
    rows[0][1] = 2
    with pytest.raises(ValueError, match="category support"):
        audit_fruit_denominators(rows)
    with pytest.raises(ValueError, match="74"):
        audit_fruit_denominators(rows[:-1])

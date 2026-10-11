"""Analytic ANCOVA oracle and honest partial-reproduction reporting."""
from copy import deepcopy

import pytest

from scripts import adjudicate_pedicularis_2013_raw_workbook as source


def _orthogonal_rows():
    # 16 rows, 5 orthogonal columns, residuals +/-1: RSS=16, df=11.
    # F_j = 11 * beta_j**2, independently of any matrix implementation.
    rows = []
    for year in (1, 2):
        for density in (1, 2):
            a, b = 2 * year - 3, 2 * density - 3
            for flower_offset in (-1, 1):
                for error in (-1, 1):
                    rows.append([year, density, 2, 50 + flower_offset,
                                 30 + 3*a + 2*b + a*b + 4*flower_offset + error,
                                 10.0])
    return rows


def test_five_parameter_ancova_matches_independent_orthogonal_oracle():
    assert hasattr(source, "ancova_fruit_set"), "fixed fruit-set ANCOVA missing"
    rows = _orthogonal_rows()
    before = deepcopy(rows)
    result = source.ancova_fruit_set(rows)
    assert result["n"] == 16
    assert result["df_residual"] == 11
    assert result["F"] == pytest.approx({
        "year": 99.0, "density": 44.0, "interaction": 11.0, "flowers": 176.0,
    })
    assert result["patch_cluster_robust"] is False
    assert rows == before


def test_flower_covariate_translation_does_not_change_the_four_F_tests():
    assert hasattr(source, "ancova_fruit_set"), "fixed fruit-set ANCOVA missing"
    rows = _orthogonal_rows()
    expected = source.ancova_fruit_set(rows)
    for row in rows:
        row[3] += 100000
    assert source.ancova_fruit_set(rows)["F"] == pytest.approx(expected["F"])


@pytest.mark.parametrize("column,value", [
    (0, True), (0, 3), (1, None), (2, False),
    (3, 0), (3, 1.5), (3, float("inf")), (3, True),
    (4, None), (4, float("nan")), (4, 101), (4, -1),
])
def test_invalid_input_cannot_become_an_ancova_result(column, value):
    assert hasattr(source, "ancova_fruit_set"), "fixed fruit-set ANCOVA missing"
    rows = _orthogonal_rows()
    rows[0][column] = value
    with pytest.raises(ValueError):
        source.ancova_fruit_set(rows)


def test_rank_deficient_flower_covariate_is_rejected():
    assert hasattr(source, "ancova_fruit_set"), "fixed fruit-set ANCOVA missing"
    rows = _orthogonal_rows()
    for row in rows:
        row[3] = 50
    with pytest.raises(ValueError, match="rank|singular"):
        source.ancova_fruit_set(rows)


def test_one_unmatched_F_remains_visible_in_partial_reproduction():
    assert hasattr(source, "compare_fruit_set_ancova"), "ANCOVA comparison missing"
    # Numerical fixture exercises failure reporting; it is not source evidence.
    stats = {"year": 67.671, "density": 2.945, "interaction": 0.08,
             "flowers": 3.855}
    result = source.compare_fruit_set_ancova(stats)
    assert result["matched_F_count"] == 3
    assert result["attempted_F_count"] == 4
    assert result["all_F_reproduced"] is False
    assert result["status"] == "PARTIAL_REPRODUCTION_HOLD"
    assert result["comparisons"]["interaction"]["published_F"] == 0.355
    assert result["comparisons"]["interaction"]["recomputed_F"] == 0.08
    assert result["comparisons"]["interaction"]["difference"] == pytest.approx(-0.275)


@pytest.mark.parametrize("stats", [
    {"year": 67.671, "density": 2.945, "flowers": 3.855},
    {"year": 67.671, "density": 2.945, "interaction": float("nan"), "flowers": 3.855},
])
def test_omitted_or_nonfinite_comparison_cannot_inflate_match_count(stats):
    assert hasattr(source, "compare_fruit_set_ancova"), "ANCOVA comparison missing"
    with pytest.raises(ValueError):
        source.compare_fruit_set_ancova(stats)


def test_source_runner_rejects_altered_workbook_before_excel_import(tmp_path):
    from importlib import import_module
    from importlib.util import find_spec
    name = "scripts.audit_pedicularis_2013_fruit_set_ancova"
    assert find_spec(name) is not None, "exact-source ANCOVA runner missing"
    runner = import_module(name)
    altered = tmp_path / "altered.xlsx"
    altered.write_bytes(b"not the registered original workbook")
    with pytest.raises(ValueError, match="source.*digest|source.*bytes"):
        runner.audit_source(altered)

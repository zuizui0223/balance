"""Regression tests are synthetic: they do not create field evidence."""
from copy import deepcopy
import pytest
from scripts.audit_pedicularis_2013_ancova_sensitivity import fit, diagnose


def toy():
    rows=[]
    for year in (1,2):
        for density in (1,2):
            a,b=2*year-3,2*density-3
            for offset in (-1,1):
                for err in (-1,1):
                    rows.append([year,density,2,50+offset,
                                 30+3*a+2*b+a*b+4*offset+err,10.])
    return rows


def test_orthogonal_F_oracle_and_original_rows_unchanged():
    rows=toy()
    old=deepcopy(rows)
    actual=fit(rows)
    assert actual["F"]==pytest.approx(
        {"year":99.,"density":44.,"interaction":11.,"flowers":176.})
    assert actual["conditional_dense_minus_sparse_fruit_set_pp"]==pytest.approx(
        {"2005":2.,"2011":6.})
    assert rows==old


def test_interaction_is_invariant_to_factor_coding_and_response_units():
    rows=toy()
    first=fit(rows)
    dummy=fit(rows,coding="dummy")
    fraction=fit(rows,response_divisor=100.)
    assert dummy["F"]["interaction"]==pytest.approx(first["F"]["interaction"])
    assert fraction["F"]==pytest.approx(first["F"])
    assert dummy["conditional_dense_minus_sparse_fruit_set_pp"]==pytest.approx(
        first["conditional_dense_minus_sparse_fruit_set_pp"])


@pytest.mark.parametrize("col,value",[
    (0,3),(1,None),(2,False),(3,0),(3,8.2),
    (3,float("nan")),(4,101.),(4,float("inf")),(4,True)])
def test_invalid_inputs_rejected(col,value):
    rows=toy()
    rows[0][col]=value
    with pytest.raises(ValueError):
        fit(rows)


def test_global_covariate_translation_does_not_change_f():
    rows=toy()
    expected=fit(rows)["F"]
    for row in rows: row[3]+=100000
    assert fit(rows)["F"]==pytest.approx(expected)


def test_rank_deficiency_is_not_a_valid_source_fit():
    rows=toy()
    for row in rows: row[3]=50
    with pytest.raises(ValueError,match="rank|singular"):
        fit(rows)


def test_no_fabricated_source_rows_and_no_omitted_comparison():
    with pytest.raises(ValueError):
        diagnose(toy(),[16,57,68,72],list(range(19,35)),{})

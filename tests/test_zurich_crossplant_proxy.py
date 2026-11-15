"""Same-garden visitor-composition proxy: source-gated exploratory tests."""
import importlib.util
import os
from pathlib import Path
import pytest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/audit_zurich_crossplant_proxy.py"

def module():
    spec=importlib.util.spec_from_file_location("zurich_crossplant",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_source_24_gardens_and_asymmetric_cross_plant_proxy():
    pytest.importorskip("numpy")
    source=os.getenv("BALANCE_ZURICH_ORIGINAL_ARCHIVE")
    if not source:pytest.skip("Original external EnviDat ZIP is not in default CI")
    result=module().audit(Path(source))
    assert result["garden_count"]==24
    assert result["plant_specific_causation_identified"] is False
    assert result["crossplant_exposure_is_a_negative_control"] is False
    z=result["results"]
    assert z["Carrot"]["none"]["own"]["rmse_change_pct_relative_to_total"]==pytest.approx(19.3953,abs=.02)
    assert z["Carrot"]["none"]["crossplant"]["rmse_change_pct_relative_to_total"]==pytest.approx(-18.4092,abs=.02)
    assert z["Radish"]["none"]["own"]["rmse_change_pct_relative_to_total"]<0
    assert z["Radish"]["none"]["crossplant"]["rmse_change_pct_relative_to_total"]==pytest.approx(18.0509,abs=.02)
    assert z["Radish"]["latitude_longitude"]["crossplant"]["rmse_change_pct_relative_to_total"]>15
    assert z["Carrot"]["mean_flowers"]["own"]["rmse_change_pct_relative_to_total"]>19
    assert result["V4_inputs_modified"] is False

def test_independent_leave_one_out_refits():
    np=pytest.importorskip("numpy")
    y=np.array([.2,.4,.3,.7,.5,.15,.9,.8,.2,.5])
    v=np.linspace(-1,1,10)
    X=np.column_stack([np.ones(10),v])
    calculated=module().independent_loo(y,X)
    expected=[]
    for j in range(len(y)):
        train=np.arange(len(y))!=j
        beta=np.linalg.lstsq(X[train],y[train],rcond=None)[0]
        expected.append(y[j]-X[j]@beta)
    assert calculated["rmse"]==pytest.approx(float(np.sqrt(np.mean(np.square(expected)))))

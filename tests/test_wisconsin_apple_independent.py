"""Independent original MD5-verified orchard numerical replay guards."""
import importlib.util
import os
from pathlib import Path
import pytest
SCRIPT=Path(__file__).resolve().parents[1]/"scripts/audit_wisconsin_apple_independent.py"

def module():
    spec=importlib.util.spec_from_file_location("orchard", SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_original_source_and_context_conditional_result():
    pytest.importorskip("numpy")
    src=os.environ.get("BALANCE_WISCONSIN_APPLE_ORIGINAL")
    if not src:pytest.skip("External original XLSX not present in standard repo CI")
    m=module()
    data=m.analyze(Path(src))
    assert data["original_orchard_years"]==47
    assert data["observed_orchard_years"]==36
    assert data["independent_orchards"]==21
    assert data["independent_studies"]==1
    assert data["frozen_V4_opened"] is False
    res=data["results"]
    assert res["pooled_year_frost"]["models"]["total"]["rmse_orchard_equal"]==pytest.approx(0.12174759865694666)
    assert res["pooled_year_frost"]["delta_vs_total_pct"]["total_both"]==pytest.approx(6.763157814435516)
    assert res["frost_2012"]["delta_vs_total_pct"]["total_both"]==pytest.approx(19.188341752305593)
    assert res["year_2013"]["delta_vs_total_pct"]["total_both"]==pytest.approx(-7.335896008141485)
    assert res["no_frost_2012"]["delta_vs_total_pct"]["total_share"] <0
    assert res["pooled_year_only"]["delta_vs_total_pct"]["total_share"] <0
    assert res["pooled_raw_abundance_sensitivity"]["delta_vs_total_pct"]["total_both"]==pytest.approx(5.162893963898818)

def test_source_checksum_mutation(tmp_path):
    src=os.environ.get("BALANCE_WISCONSIN_APPLE_ORIGINAL")
    if not src:pytest.skip("External original XLSX not present in standard repo CI")
    m=module()
    b=Path(src).read_bytes()
    (tmp_path/"tampered.xlsx").write_bytes(b[:-1]+bytes([b[-1]^1]))
    with pytest.raises(ValueError,match="MD5 mismatch"):
        m.read_original(tmp_path/"tampered.xlsx")

def test_apple_group_holdout_numeric_direct_check():
    np=pytest.importorskip("numpy")
    m=module()
    rows=[]
    for g in range(1,12):
        for y in (2012,2013):
            rows.append({"orchard":g,"year":y,"fruit":0.1+0.01*g+0.002*(y-2012),
                         "frost":g/20 if y==2012 else 0,
                         "total":float(2*g+3),"share":g/12,
                         "rich":float(1+g),"organic":float(g%2)})
    result=m.grouped_cv(rows,("year","frost","total"))
    assert result["n_orchards"]==11
    assert result["n_rows"]==22
    y=np.array([np.arcsin(np.sqrt(r["fruit"])) for r in rows])
    X=np.array([[1,float(r["year"]==2013),r["frost"],np.log1p(r["total"])] for r in rows])
    g=np.array([r["orchard"] for r in rows])
    mse=[]
    for v in set(g):
        train=g!=v
        beta=np.linalg.lstsq(X[train],y[train],rcond=None)[0]
        mse.append(np.mean((y[~train]-X[~train]@beta)**2))
    assert result["rmse_orchard_equal"]==pytest.approx(float(np.sqrt(np.mean(mse))))

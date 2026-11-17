"""Fail-closed test for conditional Alpinia seed-per-flower index and sampling bias."""
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/audit_alpinia_seed_proxy.py"

def module():
    spec=importlib.util.spec_from_file_location("alpinia_seed_proxy",SCRIPT)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def test_real_s2_counts_and_yearwise_index():
    m=module()
    z=m.analyze(m.load_csv())
    assert z["source_n_cells"]==16
    assert z["overall"]["robbed"]["fruit_n"]==5174
    assert z["overall"]["unrobbed"]["fruit_n"]==7001
    assert z["overall"]["robbed"]["sampled_fruit_n"]==881
    assert z["overall"]["unrobbed"]["sampled_fruit_n"]==814
    assert z["overall"]["robbed"]["seed_per_original_flower_proxy"]==pytest.approx(8.69189107007004)
    assert z["overall"]["unrobbed"]["seed_per_original_flower_proxy"]==pytest.approx(12.335126602357233)
    assert z["pooled"]["seed_per_flower_proxy_ratio"]==pytest.approx(0.7046454690144021)
    assert z["years"]["2005"]["seed_per_flower_proxy_ratio"]==pytest.approx(0.6106105217030373)
    assert z["years"]["2007"]["seed_per_flower_proxy_ratio"]==pytest.approx(0.7781150549722835)
    assert z["year_direction"]["lower_proxy_in_robbed"]==8

def test_compensation_and_fruit_sampling_bias():
    z=module().analyze(module().load_csv())
    a=z["pooled"]
    assert a["robbed_to_unrobbed_sampled_seed_per_fruit_ratio"]==pytest.approx(0.9753124859196397)
    assert a["required_seed_per_fruit_ratio_for_break_even"]==pytest.approx(1.3841180122591632)
    assert a["relative_multiplier_needed_to_erase_proxy_deficit"]==pytest.approx(1.4191533813432657)
    assert a["equal_opposite_relative_mean_errors_required"]==pytest.approx(0.17326449185728166)
    assert a["ratio_band_if_sample_mean_bias_at_most_15pct"][1]<1
    assert a["ratio_band_if_sample_mean_bias_at_most_20pct"][1]>1
    assert z["overall"]["robbed"]["sampled_fruit_fraction"]==pytest.approx(0.17027444916892154)
    assert z["overall"]["unrobbed"]["sampled_fruit_fraction"]==pytest.approx(0.11626910441365519)

def test_year_direction_reweighting_and_claim_ceiling():
    z=module().analyze(module().load_csv())
    s=z["year_direction"]
    assert len(s["rows"])==8
    assert s["equal_stratum_proxy_ratio"]==pytest.approx(0.7114675304349262)
    assert s["min_stratum_proxy_ratio"]==pytest.approx(0.4807977804585064)
    assert s["max_stratum_proxy_ratio"]==pytest.approx(0.9172359957058804)
    assert all(v is False for v in z["claim_guards"].values())
    assert z["claim_level"]=="CONDITIONAL_COMPOSITE_INDEX_NOT_REALIZED_FEMALE_FITNESS"

def test_changed_csv_and_unphysical_sample_fail(tmp_path):
    m=module()
    altered=tmp_path/"altered.csv"
    altered.write_bytes(m.CSV_PATH.read_bytes().replace(
        b"2005,Robbed,W-E,60,2080,695",
        b"2005,Robbed,W-E,60,2080,696"))
    with pytest.raises(ValueError,match="SHA256"):
        m.load_csv(altered)
    invalid=m.load_csv()
    invalid[0]["sampled_fruits"]=invalid[0]["fruits"]+1
    with pytest.raises(ValueError,match="denominator"):
        m.analyze(invalid)

def test_missing_and_duplicate_source_strata_fail():
    m=module()
    original=m.load_csv()
    with pytest.raises(ValueError,match="16"):
        m.analyze(original[:-1])
    bad=[dict(r) for r in original]
    bad[0]=dict(original[1])
    with pytest.raises(ValueError,match="duplicate"):
        m.analyze(bad)

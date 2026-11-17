"""PLOS Alpinia 2015 original S2 stage identification checks; no new studies counted."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"scripts/audit_alpinia_original_stage.py"

def module():
    spec=importlib.util.spec_from_file_location("alpinia_original_stage",PATH)
    x=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(x)
    return x

def test_authoritative_cells_and_aggregation():
    m=module()
    rows=m.load_csv()
    assert len(rows)==16
    z=m.analyze(rows)
    assert z["by_treatment"]["Robbed"]["flowers"]==17231
    assert z["by_treatment"]["Unrobbed"]["flowers"]==16845
    assert z["by_treatment"]["Robbed"]["fruits"]==5174
    assert z["by_treatment"]["Unrobbed"]["fruits"]==7001
    assert z["by_treatment"]["Robbed"]["seeds_in_sample"]==25502
    assert z["by_treatment"]["Robbed"]["sampled_fruits"]==881
    assert z["by_treatment"]["Unrobbed"]["seeds_in_sample"]==24159
    assert z["by_treatment"]["Unrobbed"]["sampled_fruits"]==814
    assert z["contrasts"]["fruit_rate_difference_percentage_points"]==pytest.approx(-11.53401773216)
    assert z["contrasts"]["fruit_rate_ratio"]==pytest.approx(.7224817473)

def test_stage_signs_across_all_original_year_directions():
    z=module().analyze(module().load_csv())
    assert z["contrasts"]["fruit_rate_negative_cells"]==8
    assert z["contrasts"]["sampled_seed_negative_cells"]==4
    assert z["contrasts"]["sampled_seed_positive_cells"]==3
    assert z["contrasts"]["sampled_seed_zero_cells"]==1
    assert len(z["paired_source_strata"])==8
    assert z["by_year"]["2005"]["Robbed"]["fruit_set_rate"] < z["by_year"]["2005"]["Unrobbed"]["fruit_set_rate"]
    assert z["by_year"]["2007"]["Robbed"]["fruit_set_rate"] < z["by_year"]["2007"]["Unrobbed"]["fruit_set_rate"]

def test_source_tampering_and_incorrect_denominator_rejected(tmp_path):
    m=module()
    path=tmp_path/"changed.csv"
    raw=m.CSV_PATH.read_bytes()
    path.write_bytes(raw.replace(b"2005,Robbed,W-E,60,2080,695",b"2005,Robbed,W-E,60,2080,696"))
    with pytest.raises(ValueError,match="checksum"):
        m.load_csv(path)
    rows=m.load_csv()
    with pytest.raises(ValueError,match="Duplicate"):
        m.validate(rows[:-1]+[rows[0]])
    bad=[dict(x) for x in rows]
    bad[0]["fruits"]=bad[0]["flowers"]+1
    with pytest.raises(ValueError,match="fruits"):
        m.validate(bad)

def test_causal_architecture_and_percent_guardrails():
    s=module().analyze(module().load_csv())
    g=s["claim_guards"]
    assert all(g.values())
    assert g["cannot_infer_seed_set_percentage_without_ovule_denominator"]
    assert g["no_shared_vs_separate_architecture_fitness_test"]
    assert g["no_individual_flower_or_inflorescence_rows"]

def test_authentic_download_against_original_16_cells_if_available():
    md=os.getenv("BALANCE_ALPINIA_2015_S2_DOC")
    tx=os.getenv("BALANCE_ALPINIA_2015_ANTIWORD_TEXT")
    if not md or not tx:
        pytest.skip("Separate original-source workflow provides PLOS DOC and antiword text")
    m=module()
    import hashlib
    assert hashlib.sha256(Path(md).read_bytes()).hexdigest()==m.ORIGINAL_DOC_SHA256
    assert m.extract_source_doc_text(Path(tx).read_text(encoding="utf-8")) == m.load_csv()

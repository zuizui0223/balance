"""Primary 2018 paper treatment summaries versus source-hashed 2025 larceny effects."""
import importlib.util, math, os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/audit_heiling_2018_paper_treatment_map.py'

def getmod():
    spec=importlib.util.spec_from_file_location('heiling_paper_treatment',SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

@pytest.fixture(scope='module')
def original():
    s=os.getenv('BALANCE_LARCENY_2025_ORIGINAL')
    if not s:pytest.skip('Official Figshare 776-effect XLSX required in original-source workflow')
    return getmod().audit(Path(s))

def test_exact_seed_treatment_id_assignment(original):
    assert original['seed_treatment_uniqueness']['unique_seed_ID_attribution_confirmed'] is True
    m=original['candidate_treatment_groups']
    assert m['PR']['candidate_meta_stage_group']['seed set']['effect_id']==256
    assert m['CR']['candidate_meta_stage_group']['seed set']['effect_id']==259
    assert m['PR']['seed_lnRR_reported_paper_means']==pytest.approx(math.log(6.73/7.56))
    assert m['CR']['seed_lnRR_reported_paper_means']==pytest.approx(math.log(8.65/7.56))
    for x in ('PR','CR'):
        assert abs(m[x]['seed_lnRR_meta_minus_original']) < 2e-13

def test_published_fruit_means_do_not_reconstruct_meta_lnrr(original):
    m=original['candidate_treatment_groups']
    assert m['PR']['fruit_lnRR_reproducible_from_rounded_2018_means'] is False
    assert m['CR']['fruit_lnRR_reproducible_from_rounded_2018_means'] is False
    assert m['PR']['fruit_lnRR_meta_minus_original_means']==pytest.approx(-.0858844471046061)
    assert m['CR']['fruit_lnRR_meta_minus_original_means']==pytest.approx(-.039881,abs=0.002)
    assert m['PR']['candidate_meta_seed_minus_fruit_lnRR']==pytest.approx(-.01680594737442)
    assert m['CR']['candidate_meta_seed_minus_fruit_lnRR']==pytest.approx(.059590741400992)

def test_primary_2015_units_and_assignment(original):
    d=original['published_experimental_design']
    assert d['year']==2015 and d['total_plants']==15 and d['plants_per_group']==5
    assert d['lateral_racemes_per_plant']==5
    assert d['flowers_treated_percent_per_plant']==[10,20]
    assert d['plant_allocation']=='haphazard, NOT independently confirmed randomized'
    assert d['pollen_receipt_fruit_and_seed_reported_in_one_experimental_programme'] is True

def test_dryad_provenance_and_scientific_firewall(original):
    assert original['Dryad_file_id']==41496
    assert original['Dryad_file_md5_from_original_metadata']=='31e7e67fa98c5ffb7b4b133686191b90'
    assert original['original_Dryad_workbook_recovered'] is False
    assert original['original_Dryad_delivery_status']=={'web_file_stream_HTTP':403,'REST_file_download_HTTP':401}
    assert all(original['interpretive_firewall'].values())
    assert original['candidate_treatment_groups']['CR']['fruit_and_pollen_treatment_identity_verified_with_raw_Dryad'] is False

def test_checksum_changes_fail_closed(tmp_path):
    path=tmp_path/'bad.xlsx'
    path.write_bytes(b'placeholder is not author original')
    with pytest.raises(ValueError,match='SHA256 mismatch'):
        getmod().audit(path)

def test_frozen_paper_means_and_unverified_vs_verified_identity():
    m=getmod()
    assert m.PUBLISHED['control']['seed_per_raceme']==7.56
    assert m.PUBLISHED['PR']['fruit_proportion']==.73
    assert m.PUBLISHED['CR']['sqrt_pollen']==28.54
    assert m.META_TRIPLETS['PR']=={'pollen deposition':254,'fruit set':255,'seed set':256}
    assert m.META_TRIPLETS['CR']=={'pollen deposition':257,'fruit set':258,'seed set':259}

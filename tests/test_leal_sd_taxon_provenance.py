"""Frozen source checks for Leal 2025 archive SD, logROM and primary taxa."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import os
import pytest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/'scripts/audit_leal_sd_taxon_provenance.py'

def getmod():
    spec=importlib.util.spec_from_file_location('leal_sd_taxon_audit',MODULE)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

@pytest.fixture(scope='module')
def audited():
    source=os.environ.get('BALANCE_LEAL_SD_TAXON_ORIGINAL')
    if not source:pytest.skip('Original Leal Zenodo archive needed in GitHub source replay')
    return getmod().audit(Path(source))

def test_replay_267_original_rows_and_all_seven_sd_transpositions(audited):
    assert audited['source_effect_count']==267
    sd=audited['ROM_variance']
    assert sd['source_vi_matches_archived_SD_order']==260
    assert sd['source_vi_matches_only_exchanged_SD_order']==7
    assert sd['source_vi_discordant_sample_ids']==['56','79','81','83','84','88','178']
    assert sd['max_absolute_error_of_swapped_SD_formula']<1e-9
    for case in sd['discrepancies']:
        assert abs(case['vi_archived']-case['vi_recomputed_with_SD_columns_exchanged'])<1e-9
        assert abs(case['vi_archived']-case['vi_recomputed_archived_SD_columns'])>1e-6

def test_three_signed_roman_ratio_reversals_are_not_reclassified(audited):
    z=audited['ROM_effect_sign']
    assert z['archived_sign_opposite_to_group_means_n']==3
    assert [v['sample_id'] for v in z['cases']]==['79','88','178']
    assert z['source_direction_recode_unknown'] is True
    for x in z['cases']:
        assert x['yi_archived']==pytest.approx(-x['ln_group_mean_ratio'],abs=1e-9)

def test_gelvez_2016_original_paper_se_confirms_sd_columns_swapped(audited):
    z=audited['primary_source_2016_sample88']
    assert z['paper_species']=='Collaea_cipoensis'
    assert z['original_paper_is_not_Collaea_speciosa']
    assert z['robbed_reported_N']==44 and z['intact_reported_N']==237
    assert z['SD_derived_from_paper_SE_and_N_if_SE_is_mean_SE'][0]==pytest.approx(1.05*math.sqrt(44))
    assert z['SD_derived_from_paper_SE_and_N_if_SE_is_mean_SE'][1]==pytest.approx(2.7*math.sqrt(237))
    assert z['archived_SD_columns'][0]==pytest.approx(2.7*math.sqrt(237),abs=1e-5)
    assert z['archived_SD_columns'][1]==pytest.approx(1.05*math.sqrt(44),abs=.0002)
    assert z['reported_N_for_visitation_must_not_be_assumed_to_be_independent_plants']

def test_taxonomic_source_mismatches_affect_ten_effect_rows_and_phylogeny(audited):
    assert audited['effect_rows_with_paper_taxon_label_disagreement']==10
    cases=audited['primary_article_taxon_discrepancies']
    assert len(cases)==2
    assert [(z['archived_species'],z['published_species'],z['effect_row_count']) for z in cases]==[
        ('Collaea_speciosa','Collaea_cipoensis',2),
        ('Pitcairnia_augustifolia','Pitcairnia_angustifolia',8)]
    for item in cases:
        assert item['archived_name_appears_in_original_phylogeny']
        assert not item['primary_study_name_appears_in_original_phylogeny']
    assert audited['phylogeny_rebuilding_required_before_any_verified_taxonomy_correction']

def test_source_is_not_treated_as_revised_metaanalysis(audited):
    assert all(audited['claim_guards'].values())
    assert audited['ROM_variance']['no_claim_that_all_seven_source_SD_values_independently_recovered']
    assert audited['ROM_variance']['original_source_vi_unmodified']
    assert audited['original_zip_sha256']=='3f6e9b5b55ad8090f41f62faeb2f306c6700a9beb274ac6467106ebab9573c2d'

def test_changed_Zenodo_bytes_rejected(tmp_path):
    m=getmod()
    source=tmp_path/'spoof.zip'
    source.write_bytes(b'not official Zenodo')
    with pytest.raises(ValueError,match='SHA256 mismatch'):
        m.audit(source)
    with pytest.raises(ValueError,match='Invalid original'):
        m._variance({'mean_larcenist':'0','mean_control':'1','sd_larcenist':'3','sd_control':'2',
                     'n_larcenist':'1','n_control':'1'})


def test_two_primary_studies_hidden_by_taxonomy_and_publication_year():
    leal=os.environ.get('BALANCE_LEAL_SD_TAXON_ORIGINAL')
    zhong=os.environ.get('BALANCE_LEAL_ZHONG_ORIGINAL')
    if not leal or not zhong:
        pytest.skip('Both original Zenodo and Figshare sources required')
    z=getmod().audit(Path(leal),Path(zhong))['cross_meta_original_paper_recovery']
    assert z['prior_provisional_first_author_year_species_candidate_pairs']==45
    assert z['recoverable_additional_primary_paper_species_candidate_pairs']==2
    assert z['updated_paper_species_candidate_upper_bound']==47
    p=z['additional_primary_identified_sources']
    assert [(x['zhong_ref_ID'],x['zhong_effect_IDs'][0],x['leal_effect_samples'][0]) for x in p]==[(23,562,77),(24,572,87)]
    assert p[0]['primary_publication_doi']=='10.1111/j.1442-1984.2012.00388.x'
    assert p[1]['primary_publication_doi']=='10.1016/j.rmb.2016.09.004'
    assert all(not x['identical_experimental_contrast_IDs_verified'] for x in p)
    assert z['all_47_are_DOI_verified_independent_effects'] is False

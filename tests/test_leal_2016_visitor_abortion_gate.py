"""Primary PDF plus official original meta ZIP/XLSX regression checks for 2016 source endpoints."""
from __future__ import annotations
import importlib.util, math, os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/audit_leal_2016_visitor_abortion_gate.py'

def module():
    spec=importlib.util.spec_from_file_location('source_guild_abortion',SCRIPT)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

@pytest.fixture(scope='module')
def original():
    names=('BALANCE_2016_AUDIT_LEAL_ZIP','BALANCE_2016_AUDIT_ZHONG_XLSX',
           'BALANCE_2016_AUDIT_CUEVAS_PDF','BALANCE_2016_AUDIT_GELVEZ_PDF')
    values=[os.getenv(k) for k in names]
    if not all(values):pytest.skip('Dedicated source workflow supplies four official original source files')
    return module().audit(*(Path(v) for v in values))

def test_original_2016_pdf_provenance_and_2025_Zenodo_Figshare(original):
    p=original['verified_primary_source_receipts']
    assert p['Cuevas_RosasGuerrero_2016_original_DOI']=='10.1111/plb.12311'
    assert p['Gelvez_Zuniga_2016_original_DOI']=='10.1016/j.rmb.2016.09.004'
    assert p['Cuevas_RosasGuerrero_2016_author_pdf_SHA256']=='216750e6c649d8472420e54f272c5448caab875e59aab51603fd5b5e9afb5cdf'
    assert p['Gelvez_Zuniga_2016_journal_pdf_SHA256']=='1e8ef9017756cacd5f893cef6e42abe2669cd0baf7ea506999324c9f386b0a0a'
    assert p['Leal_2025_original_Zenodo_sha256']=='3f6e9b5b55ad8090f41f62faeb2f306c6700a9beb274ac6467106ebab9573c2d'

def test_source_salvia_cuevas_is_visitor_guild_candidate_not_legitimate_service(original):
    a=original['salvia_source_sample_56']
    assert a['sample_id']==56
    assert a['original_primary_species']=='Salvia_gesneriflora'
    assert a['archived_species']=='Salvia_gesnerifolia'
    assert a['original_primary_video_plants']==7
    assert a['original_total_film_hours']==44
    assert a['original_flower_count_film']==204
    assert a['primary_robber_visitor']=='Diglossa baritula'
    assert a['legitimate_hummingbird_visitor']=='Eugenes fulgens'
    assert a['source_figure_primary_robber_approximate_robbed_vs_unrobbed']==[.21,.07]
    assert a['archived_effect_ynatural_log_ROM']==pytest.approx(math.log(3),abs=1e-9)
    assert a['not_verified_legitimate_pollinator_service_effect'] is True
    assert 'unverified' in a['guild_fingerprint']
    assert a['paired_video_plants_are_NOT_two_independent_groups_of_7'] is True

def test_meta_same_salvia_paper_but_visitor_endpoint_incomparable(original):
    a=original['salvia_source_sample_56']
    assert a['Zhong_same_primary_effect_IDs']==list(range(501,507))
    assert a['Zhong_same_primary_visitor_effect_ID']==506
    assert a['Zhong_visit_lnRR']==pytest.approx(.677562449543247)
    assert a['Zhong_visitor_guild_cannot_be_confirmed_from_meta_label_alone']
    assert a['after_salvia_primary_source_reconciliation_candidate_count_at_least']==49
    assert a['not_49_verified_identical_experimental_effects']

def test_collaea_abortions_wrong_way_round_if_called_female_fitness(original):
    a=original['collaea_source_sample_87']
    assert a['original_primary_plant_count']==44
    assert a['original_damaged_flower_count']==570
    assert a['original_intact_flower_count']==716
    assert a['archived_metric']=='female'
    assert a['primary_measured_metric']=='flower_abortion_fraction'
    assert a['original_plant_random_effect_in_abortion_GLMM'] is True
    assert a['original_reported_abortion_difference_not_significant']
    assert a['original_p_value_of_abortion_test']==.11
    assert a['archived_abortion_lnRR']==pytest.approx(math.log(.38/.22),abs=1e-9)
    assert a['illustrative_nonabortion_ratio_not_fruit_set']==pytest.approx(math.log(.62/.78))
    assert a['do_not_negate_yi_to_translate_abortion_to_fitness'] is True
    assert a['original_source_SE_based_on_per_plant_analysis_not_570_independent_plants']

def test_collaea_observational_visitation_sign_is_opposite_original(original):
    a=original['collaea_source_sample_88']
    assert a['original_robbed_lnRR']==pytest.approx(math.log(3.44/17.11))
    assert a['archived_visitation_lnRR']==pytest.approx(-math.log(3.44/17.11),abs=1e-9)
    assert a['archived_visitation_sign_is_opposite_original_robbed_over_intact']
    assert a['still_observational_natural_damage_contrast']

def test_sensitivity_descriptive_not_a_refitted_meta_model(original):
    s=original['subset_sensitivity_descriptive_not_refit']
    assert s['female_robbers_as_archived']['effect_rows']==130
    assert s['female_robbers_excluding_abortion_87']['effect_rows']==129
    assert s['female_robbers_as_archived']['equal_study_averaged_archived_lnRR']==pytest.approx(-.19576068258711)
    assert s['female_robbers_excluding_abortion_87']['equal_study_averaged_archived_lnRR']==pytest.approx(-.21431829230179)
    assert s['visitation_robbers_as_archived']['effect_rows']==44
    assert s['visitation_robbers_excluding_observational_56_and_misoriented_88']['effect_rows']==42
    assert s['visitation_robbers_as_archived']['equal_study_averaged_archived_lnRR']==pytest.approx(-.11980169886162)
    assert s['visitation_robbers_excluding_observational_56_and_misoriented_88']['equal_study_averaged_archived_lnRR']==pytest.approx(-.3159621857765)
    assert s['visitation_robbers_hypothetical_reorient_88']['equal_study_averaged_archived_lnRR']==pytest.approx(-.3085301243627)
    assert s['no_correction_to_published_random_effects_or_phylogenetic_model']

def test_fumero_and_same_guild_source_not_overpromoted(original):
    q=original['remaining_review_queue']
    assert q['original_Fumero_2013_full_table_data_not_acquired']==[79,81,83,84]
    assert q['Fumero_79_effect_direction_still_unresolved']
    assert q['Salvia_56_figure_guild_and_SD_source_stage_audited_but_exact_SE_SD_pending']
    assert all(original['claim_guards'].values())

def test_untrusted_primary_pdf_and_meta_source_rejected(tmp_path):
    m=module()
    bogus=tmp_path/'Cuevas2016.pdf'
    bogus.write_bytes(b'%PDF-fake not the original')
    with pytest.raises(ValueError,match='SHA256 mismatch'):
        m._pdf_source(bogus,m.CUEVAS_SHA,('Salvia gesneriflora',))
    with pytest.raises(ValueError,match='SHA256 mismatch'):
        m._pdf_source(bogus,m.GELVEZ_SHA,('Collaea cipoensis',))

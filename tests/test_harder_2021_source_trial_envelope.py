"""Synthetic-only regression guards for orchid original-source trial ambiguity.

Tests verify expected estimator behavior without pretending that artificial
trial rows are the Harder et al. original empirical observations.
"""
import json

import pytest

from scripts import audit_harder_2021_export_sensitivity as source
from scripts.audit_harder_2021_zenodo_mirror import MD5


def fake_coded_groups():
    # This is an artificial unit test source, NOT real 2021 source data.
    em_ids=[2,3,7,8,10,12,14,16,18,22,24,26,28,30,32,33]
    intact_ids=[1,4,5,6,9,11,13,15,17,19,21,23,25,27,29,31]
    result=[]
    for arm,ids in (("Emasc",em_ids),("Intact",intact_ids)):
        for trial in ids:
            if arm=="Emasc" and trial==2:
                M=201;n=10;h=12;v_min=1;v_max=10
            elif arm=="Emasc" and trial==3:
                M=201;n=7;h=10;v_min=11;v_max=17
            else:
                M=200;n=13;h=35 if arm=="Emasc" else 20
                v_min=1;v_max=n
            result.append({
                "treatment":arm,"source_trial_code":str(trial),
                "source_recipient_rows":n,"visit_min":v_min,"visit_max":v_max,
                "visits_contiguous":True,"n_R_values_in_group":1,
                "M_init":M,"donor_massula_deposited":h,
                "source_deposition_fraction":h/M,
                "early_six_visit_deposition_fraction":h/M*6/n if v_min==1 and n>=6 else None
            })
    return result


def test_original_sha256_is_pinned_without_arbitrary_trial_exclusion():
    assert source.ORIGINAL_SHA256=="303428b859bcba4756ac78c4ffd4b42121a6efce5b0cd2cc2030834705f62cbc"
    assert source.ORIGINAL_BYTES==8041
    assert MD5=="650e40ae7ebb41bdfb333dcf63c63c71"


def test_all_16_intact_exclusions_are_reported_without_cherry_picking(monkeypatch):
    fake=fake_coded_groups()
    assert len(fake)==32
    monkeypatch.setattr(source,"_read_source_groups",lambda raw:fake)
    x=source.diagnostic_source_effect(b"synthetic only",bootstrap_reps=150)
    assert x["status"]=="AUTHENTIC_ORIGINAL_SOURCE_32_CODE_GROUP_EXPLORATORY_DISCREPANCY_ANALYSIS"
    assert x["source_group_counts"]=={"Emasc":16,"Intact":16}
    assert x["published_trial_counts"]=={"Emasc":16,"Intact":15}
    assert x["n_original_coded_trial_groups"]==32
    assert x["all_sixteen_possible_one_intact_group_omission_envelope"]["n_scenarios"]==16
    assert x["all_sixteen_possible_one_intact_group_omission_envelope"]["no_selected_favorable_trial_exclusion"] is True
    assert x["possible_contiguous_split_Emasc_2_3_merge"]["results_if_merged"][
        "n_emasculated_coded_groups"]==15
    assert x["source_coded_groups_mean_export_fraction"]["n_emasculated_coded_groups"]==16
    assert x["source_coded_groups_mean_export_fraction"]["n_intact_coded_groups"]==16
    assert x["claim_limits"]["32_code_groups_not_verified_32_independent_bees"] is True
    assert x["claim_limits"]["no_unique_original_31_trial_mapping"] is True
    assert x["raw_source_rows_exported"] is False


def test_wrong_real_source_never_accepted_as_a_real_field_effect():
    with pytest.raises(ValueError,match="exact archived public source CSV"):
        source._read_source_groups(b"Trial_type,Trial,Deposition\nIntact,1,3\n")


def test_wrong_contiguous_trial_metadata_blocks_possible_merge():
    fake=fake_coded_groups()
    altered=[dict(x) for x in fake]
    target=next(x for x in altered if x["source_trial_code"]=="3" and x["treatment"]=="Emasc")
    target["visit_min"]=1
    with pytest.raises(ValueError,match="continuity flag"):
        source._merge_possible_split(altered)


def test_all_synthetic_32_group_import_and_one_intact_removal_preserve_trial_count():
    group=fake_coded_groups()
    full=source._contrast(group)
    assert full["n_emasculated_coded_groups"]==16
    assert full["n_intact_coded_groups"]==16
    no_intact=next(r for r in group if r["treatment"]=="Intact")
    minus=source._contrast([r for r in group if r is not no_intact])
    assert minus["n_emasculated_coded_groups"]==16
    assert minus["n_intact_coded_groups"]==15
    assert minus["intact_minus_emasculated_difference"]<0

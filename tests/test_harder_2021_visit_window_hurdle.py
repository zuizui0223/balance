"""Synthetic-only tests of orchid first-six matched opportunity audit.

Nothing in synthetic fixtures below is an original Harder (2021) field
measurement; original biological results are run on authenticated Zenodo CSV
on a branch-specific Action and separately source-digested.
"""
from pathlib import Path

import pytest

from scripts.check_harder_2021_visit_window_hurdle import (
    EARLY_VISITS,ORIGINAL_SHA256,_quantile,_six_window_summary,
    _verified_recipient_groups
)

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"check_harder_2021_visit_window_hurdle.py"
WORKFLOW=ROOT/".github"/"workflows"/"harder-2021-orchid-original-data.yml"


def synthetic_groups():
    """Synthetic 32 source codes; E3=11..17, E7=1..2, I4=1..4."""
    em=(2,3,7,8,10,12,14,16,18,22,24,26,28,30,32,33)
    intact=(1,4,5,6,9,11,13,15,17,19,21,23,25,27,29,31)
    groups={}
    for arm,codes in (("Emasc",em),("Intact",intact)):
        for code in codes:
            if arm=="Emasc" and code==3:
                visits=range(11,18)
            elif arm=="Emasc" and code==7:
                visits=range(1,3)
            elif arm=="Intact" and code==4:
                visits=range(1,5)
            else:
                visits=range(1,12)
            deposits=[4 if arm=="Emasc" else 2 for _ in visits]
            groups[(arm,str(code))]=[
                {"visit":visit,"deposition":deposits[i],"M_init":200}
                for i,visit in enumerate(visits)
            ]
    return groups


def test_original_source_sha_and_paper_observation_count_not_imputed():
    s=SCRIPT.read_text(encoding="utf-8")
    assert ORIGINAL_SHA256=="303428b859bcba4756ac78c4ffd4b42121a6efce5b0cd2cc2030834705f62cbc"
    assert '("Intact","4")' in s
    assert 'assert 383-len(removed)==379' in s
    assert '"does_not_match_published_second_stage_reversed_arm_counts":True' in s
    assert '"does_not_prove_original_paper_exclusion_rule":True' in s
    assert 'original_R_varies_within_four_source_codes' in s


def test_original_source_wrong_bytes_fail_closed():
    with pytest.raises(ValueError,match="authenticated original"):
        _verified_recipient_groups(b"Trial_type,Trial,M_init,R,Visit,Deposition\n")


def test_synthetic_first_six_pollen_eligibility_and_per_group_averages():
    got=_six_window_summary(synthetic_groups(),bootstraps=120)
    assert got["eligible_coded_group_counts"]=={"Emasc":14,"Intact":15}
    assert got["n_total_recipient_position_observations"]==174
    assert set((r["treatment"],r["code"]) for r in got[
        "excluded_coded_group_metadata"])=={
        ("Emasc","3"),("Emasc","7"),("Intact","4")
    }
    e=got["arm_descriptions"]["Emasc"]
    i=got["arm_descriptions"]["Intact"]
    assert e["means_by_equal_coded_group"]["six_recipient_deposition_pct"]==pytest.approx(12)
    assert i["means_by_equal_coded_group"]["six_recipient_deposition_pct"]==pytest.approx(6)
    assert e["means_by_equal_coded_group"]["fraction_six_stigmas_with_stained_donor_massulae"]==1
    assert i["means_by_equal_coded_group"]["fraction_six_stigmas_with_stained_donor_massulae"]==1
    assert got["observed_intact_minus_emasculated"][
        "six_recipient_deposition_pct"]==pytest.approx(-6)
    assert got["observed_intact_minus_emasculated"][
        "positive_stigma_mean_deposition_per_initial_massulae"]==pytest.approx(-.01)
    assert got["source_recipient_opportunity_held_constant_at_six"] is True
    assert got["stigma_contact_vs_zero_transfer_not_identified"] is True


def test_synthetic_zero_stigma_responses_are_not_interpreted_as_no_contact():
    fake=synthetic_groups()
    arr=fake[("Intact","1")]
    for j in range(3):
        arr[j]["deposition"]=0
    got=_six_window_summary(fake,bootstraps=110)
    no=got["arm_descriptions"]["Intact"]["per_recipient_position"]
    assert no["1"]["n_positive_stigmas"]==14
    assert no["1"]["fraction_no_stained_donor_massulae"]==pytest.approx(1/15)
    assert got["arm_descriptions"]["Intact"][
        "means_by_equal_coded_group"][
        "fraction_six_stigmas_with_stained_donor_massulae"
    ] < 1
    assert got["stigma_contact_vs_zero_transfer_not_identified"] is True


def test_source_script_workflow_runs_after_authentication_not_as_v4_coding():
    s=SCRIPT.read_text(encoding="utf-8")
    w=WORKFLOW.read_text(encoding="utf-8")
    assert "scripts.check_harder_2021_visit_window_hurdle" in w
    assert w.index("scripts.audit_harder_2021_zenodo_mirror") < w.index(
        "scripts.check_harder_2021_visit_window_hurdle"
    )
    assert '"original_trial_rows_committed":0' in s
    assert '"no_frozen_BALANCE_V4_architecture_outcomes_changed":True' in s
    assert '"first_six_extensive_zero_is_not_contact_probability":True' in s
    assert _quantile([2,5,9],0)==pytest.approx(2)
    assert _quantile([2,5,9],.5)==pytest.approx(5)
    assert _quantile([2,5,9],1)==pytest.approx(9)

"""Lock authenticated orchid paper-aligned candidate and early-six outcomes.

These are real original 383 source recipient lines with ambiguous trial
code-level dependence, NOT a reconstructed original 31-trial likelihood,
not an independent study, genetic paternity or confirmed stigma contact.
"""
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results"/"harder_2021"/"PAPER_ALIGNED_379_AND_COMMON_SIX_HURDLE_20261124.json"


def read():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def test_genuine_original_source_and_nonselected_379_candidate():
    x=read()
    assert x["status"]=="ACTUAL_AUTHENTIC_SOURCE_ORIGINAL_31_PAPER_CANDIDATE_AND_29_COMMON_SIX_CODES_POSTOPEN"
    assert x["source_sha256"]=="303428b859bcba4756ac78c4ffd4b42121a6efce5b0cd2cc2030834705f62cbc"
    assert x["original_383_recipient_rows"]==383
    assert x["n_original_source_trial_codes"]==32
    assert x["published_methods_group_counts"]=={"Emasc":16,"Intact":15}
    assert x["published_model_fitting_group_counts"]=={"Emasc":15,"Intact":16}
    a=x["paper_aligned_candidate"]
    assert a["excluded_original_source_code"]=="4"
    assert a["excluded_treatment"]=="Intact"
    assert a["excluded_n_recipient_rows"]==4
    assert a["retained_n_recipient_rows"]==379
    assert a["retained_coded_group_counts"]=={"Emasc":16,"Intact":15}
    assert a["does_not_prove_original_paper_exclusion_rule"] is True
    assert a["does_not_match_published_second_stage_reversed_arm_counts"] is True
    assert a["source_code_group_contrast"]["intact_over_emasculated_mean_ratio"]==pytest.approx(.8033850475941143)
    assert x["provenance"]["workflow_run_id"]==45245113786
    assert x["provenance"]["artifact_id"]==14854211333
    assert x["provenance"]["artifact_zip_sha256"]=="6ea7736f7fac86286b94f105569d37604dab17e095d251ab380f53145829b646"


def test_common_six_opportunities_true_original_study_group_grain():
    x=read()["original_source_six_recipient_hurdle"]
    assert x["eligible_coded_group_counts"]=={"Emasc":14,"Intact":15}
    assert x["n_total_recipient_position_observations"]==174
    assert {(r["treatment"],r["code"]) for r in x["excluded_coded_group_metadata"]}=={
        ("Emasc","3"),("Emasc","7"),("Intact","4")
    }
    e=x["arm_descriptions"]["Emasc"]
    i=x["arm_descriptions"]["Intact"]
    assert e["n_original_source_coded_groups"]==14
    assert i["n_original_source_coded_groups"]==15
    assert e["n_with_no_stained_donor_deposition"]==0
    assert i["n_with_no_stained_donor_deposition"]==0
    means={
        "Emasc":(.4990222517191172,.8571428571428572,.10048334474644462),
        "Intact":(.3602838670603070,.7111111111111111,.0893222635701015)
    }
    for arm,(flux,nonzero,positive) in means.items():
        row=x["arm_descriptions"][arm]["means_by_equal_coded_group"]
        assert row["six_recipient_deposition_pct"]==pytest.approx(flux*100)
        assert row["fraction_six_stigmas_with_stained_donor_massulae"]==pytest.approx(nonzero)
        assert row["positive_stigma_mean_deposition_per_initial_massulae"]==pytest.approx(positive)
    assert x["source_recipient_opportunity_held_constant_at_six"] is True
    assert x["stigma_contact_vs_zero_transfer_not_identified"] is True


def test_observed_zero_and_conditional_intensity_not_overinterpreted():
    x=read()["original_source_six_recipient_hurdle"]
    expected={
        "six_recipient_deposition_pct":(-13.873838465881015,-25.48340565470231,-2.068275695398626),
        "fraction_six_stigmas_with_stained_donor_massulae":(-.14603174603174607,-.29126984126984135,-.00952380952380949),
        "positive_stigma_mean_deposition_per_initial_massulae":(-.01116108117634311,-.03774218514161498,.016575264442793964)
    }
    for name,(beta,l,h) in expected.items():
        assert x["observed_intact_minus_emasculated"][name]==pytest.approx(beta)
        row=x["postopen_trial_code_bootstrap"][name]
        assert row["intact_minus_emasculated_95pct_interval"]==pytest.approx([l,h])
        assert row["n_bootstrap_coded_groups"]==20000
        assert row["resamples_with_defined_statistic"]==20000
        assert row["not_a_valid_confirmatory_donor_population_or_genetic_paternity_test"] is True
    interval=x["postopen_trial_code_bootstrap"]["positive_stigma_mean_deposition_per_initial_massulae"][
        "intact_minus_emasculated_95pct_interval"
    ]
    assert interval[0]<0<interval[1]


def test_no_blind_v4_upgrade_or_confirmatory_genetic_male_fitness():
    r=read()["inference_limits"]
    assert all(r.values())
    assert r["source_code_groups_may_not_be_independent_unique_donors"] is True
    assert r["candidate_inclusion_not_confirmed_by_author_code"] is True
    assert r["original_paper_internal_group_allocation_contradictory"] is True
    assert r["first_six_extensive_zero_is_not_contact_probability"] is True
    assert r["first_six_positive_massula_load_is_not_fatherhood"] is True
    assert r["no_frozen_BALANCE_V4_architecture_outcomes_changed"] is True

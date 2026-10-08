"""Synthetic regression tests for evidence-ceiling and report provenance.

No synthetic fixture is presented as observed ecological evidence.
"""
import copy
import pytest

from balance_domain.peucedanum_stage_verdict import adjudicate_stage_exploration

CELLS = [
    ("2020", "HA", 29), ("2020", "HC", 30), ("2020", "HD", 30),
    ("2020", "KD", 29), ("2021", "HC", 29), ("2021", "HD", 29),
    ("2021", "HL", 30), ("2021", "KD", 28), ("2022", "HA", 47),
    ("2022", "HC", 33), ("2022", "HD", 28), ("2022", "HL", 33),
    ("2022", "KD", 38), ("2023", "HA", 50), ("2023", "HC", 40),
    ("2023", "HD", 40), ("2023", "HL", 25), ("2023", "KD", 40)
]


def receipts():
    support = {
        "schema_version": "BALANCE_PEUCEDANUM_STAGE_SUPPORT_AUDIT_V1",
        "status": "COUNT_INCONSISTENCY_HOLD", "source_rows": 685,
        "observed_plot_year_cells": 19,
        "count_inconsistencies": [{"source_row_number": str(x)} for x in (356,481,498)],
    }
    flips = {("2020", "HA"), ("2020", "HC"), ("2022", "HA"),
             ("2021", "HD")}
    raw_cells = []
    for year,plot,n in CELLS:
        flipped = (year,plot) in flips
        raw_cells.append({
            "year": year, "plot": plot, "n": n,
            "status": "DESCRIPTIVE_ONLY",
            "beta_initial": 0.1 if flipped else 0.2,
            "beta_final": -0.1 if flipped else 0.1,
        })
    raw = {"schema_version":"PEUCEDANUM_STAGE_SLOPES_EXPLORATORY_V1",
           "cells":raw_cells}
    adjusted = {
        "schema_version": "PEUCEDANUM_STAGE_ADJUSTED_EXPLORATORY_V1",
        "status": "EXPLORATORY_ASSOCIATION_ONLY",
        "source_normalized_csv_sha256":
            "ed6bf4c5301309283ca2e3d2033fdab1e253d46ed94bbba5fde1f3ee43281dbc",
        "primary_predictor": "log1p_male_flower_count",
        "variants": {},
    }
    for predictor in ("log_male_count", "perfect_fraction"):
        for exclude in (False, True):
            name = predictor + ("_excluding_nonnested" if exclude else "_all_pairs")
            cells = [{"year":"2021","plot":"HA","n":0,
                      "status":"INSUFFICIENT_SAMPLE"}]
            for year,plot,n in CELLS:
                if exclude and (year,plot)==("2022","HC"):
                    n -= 1
                if exclude and (year,plot)==("2022","KD"):
                    n -= 2
                if (year,plot)==("2023","HD"):
                    cells.append({"year":year,"plot":plot,"n":n,
                                  "status":"DEGENERATE_OUTCOME",
                                  "p_normal_hc3":None})
                else:
                    cells.append({
                        "year":year,"plot":plot,"n":n,
                        "status":"EXPLORATORY_FIT",
                        "coefficient_per_sd":0.025,
                        "se_hc3":0.02,
                        "p_normal_hc3":0.25,
                        "q_bh_within_variant":0.25
                    })
            adjusted["variants"][name] = {"n_nonnull_tests":17,"cells":cells}
    return support,raw,adjusted


def test_negative_exploratory_receipt_does_not_claim_causality():
    support,raw,adjusted=receipts()
    result=adjudicate_stage_exploration(support,raw,adjusted)
    assert result["status"]=="EXPLORATORY_REPORT_COMPLETED_NOT_CONFIRMATORY"
    assert result["descriptive_sign_flip_count"]==4
    assert not result["independent_ecological_discovery"]
    assert not result["causal_predation_mediation_identified"]
    assert not result["BALANCE_worldline_occupancy_identified"]
    for name,item in result["adjusted_variants"].items():
        assert item["nondegenerate_tests"]==17
        assert item["minimum_BH_q_within_variant"]==pytest.approx(0.25)
        assert item["screening_label"]=="NO_BH_SCREENING_SIGNAL"
        assert item["fitted_source_rows"]==(
            605 if name.endswith("_excluding_nonnested") else 608
        )


def test_source_violation_count_must_not_be_silently_repaired():
    s,r,a=receipts()
    s["count_inconsistencies"]=[]
    with pytest.raises(ValueError,match="nonnested fruit-count"):
        adjudicate_stage_exploration(s,r,a)


def test_reject_false_q_and_missing_adjusted_cell():
    s,r,a=receipts()
    a["variants"]["log_male_count_all_pairs"]["cells"][1]["q_bh_within_variant"]=0.8
    with pytest.raises(ValueError,match="BH-adjusted q differs"):
        adjudicate_stage_exploration(s,r,a)
    s,r,a=receipts()
    a["variants"]["log_male_count_all_pairs"]["cells"].pop()
    with pytest.raises(ValueError,match="plot-year support"):
        adjudicate_stage_exploration(s,r,a)


def test_even_positive_screen_is_never_causal_promotion():
    s,r,a=receipts()
    group=a["variants"]["log_male_count_all_pairs"]
    eligible=[x for x in group["cells"] if x.get("p_normal_hc3") is not None]
    eligible[0]["p_normal_hc3"]=0.00001
    for x in eligible:
        x["q_bh_within_variant"]=0.25
    eligible[0]["q_bh_within_variant"]=0.00017
    result=adjudicate_stage_exploration(s,r,a)
    positive=result["adjusted_variants"]["log_male_count_all_pairs"]
    assert positive["screening_label"]=="EXPLORATORY_Q_BELOW_0_05_NOT_CONFIRMATORY"
    assert positive["q_below_0_05"]==1
    assert result["independent_ecological_discovery"] is False
    assert result["BALANCE_worldline_occupancy_identified"] is False

def test_one_ulp_bh_roundoff_allowed_but_material_q_change_rejected():
    s,r,a=receipts()
    group=a["variants"]["log_male_count_all_pairs"]
    eligible=[x for x in group["cells"] if x.get("p_normal_hc3") is not None]
    # BH should equal p for a constant p vector, but JSON float
    # roundoff can make stored q 1e-15 smaller than p.
    eligible[0]["q_bh_within_variant"]=eligible[0]["p_normal_hc3"]-1e-15
    out=adjudicate_stage_exploration(s,r,a)
    assert out["status"]=="EXPLORATORY_REPORT_COMPLETED_NOT_CONFIRMATORY"
    # Use a q above p to isolate the independent BH recalculation guard.
    eligible[0]["q_bh_within_variant"]=0.251
    with pytest.raises(ValueError, match="BH-adjusted q differs"):
        adjudicate_stage_exploration(s,r,a)

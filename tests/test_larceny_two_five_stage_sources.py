"""Original Figshare-776 source guards for 2018 Corydalis vs 2020 Gentiana pathways.

A paper that mentions five outcomes is not a common-grain experimental mediation.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
CODE=ROOT/"scripts/audit_larceny_two_five_stage_sources.py"

def module():
    spec=importlib.util.spec_from_file_location("larceny_two_studies",CODE)
    x=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(x)
    return x

@pytest.fixture(scope="module")
def result():
    source=os.getenv("BALANCE_LARCENY_2025_ORIGINAL")
    if not source:
        pytest.skip("Original source ZIP/XLSX supplied only through dedicated Figshare workflow")
    return module().audit(Path(source))

def test_authoritative_rows_and_paper_species_keys(result):
    assert result["source_effects"]==776
    assert result["meta_source_papers"]==153
    assert result["paper_species_candidates"]==2
    assert [(x["ref_ID"],x["species"]) for x in result["sources"]]==[
        (29,"Corydalis_caseana"),(101,"Gentiana_straminea")]
    assert [x["total_effects"] for x in result["sources"]]==[11,36]

def test_five_stage_experiment_grain_intersection_is_empty(result):
    for source in result["sources"]:
        assert len(source["stages"])==5
        assert source["all_stages_have_common_experiment_level"] is False
        assert source["shared_experimental_contrast_id_present_in_meta"] is False
        assert source["all_five_stages_same_cohort_verified"] is False
        assert all(v["n_effects"]>0 for v in source["stages"].values())

def test_potential_combinations_are_not_real_observation_units(result):
    c,g=result["sources"]
    assert c["five_stage_cartesian_products_not_real_paths"]==12
    assert g["five_stage_cartesian_products_not_real_paths"]==512
    assert c["possible_fruit_seed_cross_products_not_matched_pairs"]==4
    assert g["possible_fruit_seed_cross_products_not_matched_pairs"]==16
    assert c["fruit_minus_seed_order_is_pairing_invariant"] is False
    assert g["fruit_minus_seed_order_is_pairing_invariant"] is True

def test_heiling_two_by_two_fruit_seed_sign_ambiguity(result):
    c=result["sources"][0]
    z=c["seed_minus_fruit_all_hypothetical_cross_products"]
    assert z["positive"]==2 and z["negative"]==2
    assert z["minimum"]==pytest.approx(-.1913934358861587)
    assert z["maximum"]==pytest.approx(+.2341782299127307)
    assert c["stages"]["fruit set"]["effects"]==[255,258]
    assert c["stages"]["seed set"]["effects"]==[256,259]
    assert c["source_paper_doi"]=="10.1111/oik.05440"

def test_gentiana_all_sign_reversals_exist_but_are_not_mediation(result):
    g=result["sources"][1]
    for stage,sign in [("nectar volume","negative"),("visitation rate","positive"),
                       ("pollen deposition","negative"),("fruit set","positive"),
                       ("seed set","negative")]:
        s=g["stages"][stage]
        assert s["sign_category"]==sign
    z=g["seed_minus_fruit_all_hypothetical_cross_products"]
    assert z["negative"]==16 and z["positive"]==0
    assert z["minimum"]==pytest.approx(-.4283105798290215)
    assert z["maximum"]==pytest.approx(-.2390982541965456)
    assert g["original_publication_doi_independently_confirmed"] is False
    assert g["stages"]["pollen deposition"]["experiment_levels"]==["individual-flower success"]
    assert g["stages"]["fruit set"]["experiment_levels"]==["whole-plant fitness"]

def test_study_identity_and_strict_fitness_gates(result):
    assert all(result["scope_guards"].values())
    for s in result["sources"]:
        assert s["endpoint_covariance_identified"] is False
        assert s["same_treatment_and_control_contrast_verified"] is False
        assert s["structural_architecture_cost_or_fitness_measured"] is False
        assert s["original_plant_study_count_increment"]==0
    assert "source_title" in result["sources"][1]

def test_original_checksum_is_required(tmp_path):
    m=module()
    f=tmp_path/"wrong.xlsx"
    f.write_bytes(b"not official meta original")
    with pytest.raises(ValueError,match="SHA256 mismatch"):
        m.audit(f)

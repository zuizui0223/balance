"""Synthetic mathematical checks; real source analysis occurs only after MD5 gates."""
from __future__ import annotations

import pytest
from balance_domain.dalechampia_raw_sensitivity import (
    _mother_paired_contrast, _percentile, REPS, SCHEMA,
)


def example():
    # Each seed is nested inside one blossom, each blossom inside a mother.
    # A has two bract-shade seeds but counts as exactly ONE biological pair.
    return {
        ("A","1"): {"arm":"cont","masses":[32.,34.]},
        ("A","2"): {"arm":"bag","masses":[30.,32.]},
        ("B","3"): {"arm":"cont","masses":[40.]},
        ("B","4"): {"arm":"bag","masses":[38.]},
        ("C","5"): {"arm":"cont","masses":[36.,38.]},
        ("C","6"): {"arm":"bag","masses":[34.,36.]},
        ("D","7"): {"arm":"cut","masses":[34.]},
        # D is not paired with an unmeasured control.
    }


def test_paired_mother_effect_is_not_seed_pseudoreplication():
    x=_mother_paired_contrast(example(),arm="bag",keep_min_mass=20.,random_seed=11)
    assert x["n_maternal_pairs"] == 3
    assert x["mean_of_within_mother_blossom_mean_differences_mg"] == -2.
    assert x["bootstrap_percentile_95_interval_mg"] == [-2.,-2.]
    assert x["original_mixed_model_fitted"] is False
    assert x["effect_causally_specific_to_bract_carbon"] is False
    assert x["bootstrap_replicates"] == REPS


def test_low_mass_numerical_screen_changes_estimand_not_morphology():
    x=example()
    x[("A","2")]["masses"].extend([5.,8.])
    all_mass=_mother_paired_contrast(x,arm="bag",keep_min_mass=0.,random_seed=44)
    proxy=_mother_paired_contrast(x,arm="bag",keep_min_mass=20.,random_seed=44)
    assert all_mass["mean_of_within_mother_blossom_mean_differences_mg"] < (
        proxy["mean_of_within_mother_blossom_mean_differences_mg"])
    assert proxy["n_maternal_pairs"] == all_mass["n_maternal_pairs"] == 3
    assert proxy["effect_causally_specific_to_bract_carbon"] is False


def test_unpaired_mothers_are_excluded_without_imputation():
    x=example()
    with pytest.raises(ValueError, match="not enough"):
        _mother_paired_contrast(x,arm="cut",keep_min_mass=20.,random_seed=1)


def test_bootstrap_is_deterministic_and_percentile_bounded():
    a=_mother_paired_contrast(example(),arm="bag",keep_min_mass=0,random_seed=101)
    b=_mother_paired_contrast(example(),arm="bag",keep_min_mass=0,random_seed=101)
    assert a==b
    assert _percentile([1,2,3,4],.25)==1.75
    with pytest.raises(ValueError,match="invalid"):
        _percentile([],.5)
    with pytest.raises(ValueError,match="invalid"):
        _percentile([1,2],2)


def test_source_schema_is_explicitly_not_a_published_mixed_model():
    assert SCHEMA.endswith("SOURCE_MATERNAL_SENSITIVITY_V1")


def test_source_gas_green_white_paired_plants_without_seed_jointness():
    import csv, io
    from balance_domain.dalechampia_method_scope import _table
    from balance_domain.dalechampia_raw_sensitivity import _gas_maternal_paired_summary
    f=io.StringIO()
    headers=["Plant_ID","Color","Replicate","Bract","GPPnett","Area_Leaf.1"]
    writer=csv.DictWriter(f, fieldnames=headers,delimiter="\t",lineterminator="\n")
    writer.writeheader()
    for i in range(6):
        for c, raw in (("Green","14.7"),("White","4.2")):
            for rep in ("A","B"):
                writer.writerow({"Plant_ID":f"P{i}","Color":c,"Replicate":rep,
                                 "Bract":"Bract","GPPnett":raw,"Area_Leaf.1":"10"})
    rows,fields,normalize=_table(f.getvalue().encode("utf-8"),headers,"synthetic gas")
    out=_gas_maternal_paired_summary(rows,fields,normalize)
    assert out["source_physiology_plants"] == 6
    assert out["area_based_green_mean"] == 1.47
    assert out["area_based_white_mean"] == 0.42
    assert out["within_plant_green_minus_white_mean"] == 1.05
    assert out["bootstrap_plant_cluster_95_interval"] == [1.05,1.05]
    assert out["seed_carbon_transfer_identified"] is False
    assert out["plant_seed_mass_experiment_jointly_observed"] is False


def test_gas_missing_source_plant_pairs_are_not_inferred():
    import csv, io
    from balance_domain.dalechampia_method_scope import _table
    from balance_domain.dalechampia_raw_sensitivity import _gas_maternal_paired_summary
    fields=["Plant_ID","Color","Replicate","Bract","GPPnett","Area_Leaf.1"]
    t="\t".join(fields)+"\nP1\tGreen\tA\tBract\t14.7\t10\nP1\tWhite\tB\tBract\t4.2\t10\n"
    rows,found,norm=_table(t.encode("utf-8"),fields,"test")
    with pytest.raises(ValueError,match="six plants"):
        _gas_maternal_paired_summary(rows,found,norm)

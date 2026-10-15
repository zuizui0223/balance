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

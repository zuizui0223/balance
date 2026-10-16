"""Synthetic hierarchical controls. Never claim they are original Dryad rows."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pandas = pytest.importorskip("pandas")
pytest.importorskip("statsmodels")

from balance_domain.dalechampia_blossom_clustered import (
    SCHEMA,
    fit_blossom_clustered,
    analyze_authenticated_blossom_clusters,
)

ROOT = Path(__file__).resolve().parents[1]


def _synthetic_data():
    rows=[]
    for mother in range(9):
        for a,arm in enumerate(("cont","bag","cut","cutcont")):
            # Each blossom has three correlated seed measures. The mother
            # and blossom are the real assignment/uncertainty units.
            effect={"cont":0,"bag":-2,"cut":-1,"cutcont":0.3}[arm]
            ped=0.85 + .03*mother + .008*a + .001*mother*a
            blossom_mean=29 + 0.4*mother + effect + (mother%3)*0.2*a
            for seed in range(3):
                rows.append({
                    "FemaleID":f"mother-{mother}",
                    "crossID":str(a+1),
                    "treatcode":arm,
                    "seedmass":blossom_mean+(-.5+seed*.5),
                    "ped":ped,
                    "seedset":8+(mother%2),
                })
    return pandas.DataFrame(rows)


def test_blossom_unit_and_maternal_cluster_not_seed_pseudoreplication():
    df=_synthetic_data()
    assert len(df)==108
    x=fit_blossom_clustered(df)
    assert x["n_seed_rows"]==108
    assert x["n_blossoms"]==36
    assert x["n_maternal_plants"]==9
    assert x["interval_method"].startswith("clustered_maternal_robust")
    assert x["original_2015_mixed_model_reproduced"] is False
    assert x["with_seedset_covariate"] is False
    assert set(x["effects"])=={"bag_minus_cont","cut_minus_cont","cutcont_minus_cont"}
    assert x["effects"]["bag_minus_cont"]["mean_difference_mg"] < 0
    assert x["effects"]["cut_minus_cont"]["mean_difference_mg"] < 0


def test_seedset_sensitivity_is_distinct_from_unadjusted_model():
    df=_synthetic_data()
    x=fit_blossom_clustered(df,with_seedset=True)
    assert x["with_seedset_covariate"] is True
    assert "seedset" in x["formula_semantics"]
    assert x["n_blossoms"]==36


def test_blind_rows_within_blossom_cannot_switch_treatment_or_peduncle():
    df=_synthetic_data()
    altered=df.copy()
    altered.loc[0,"treatcode"]="bag"
    with pytest.raises(ValueError,match="within-blossom"):
        fit_blossom_clustered(altered)
    altered=df.copy()
    altered.loc[0,"ped"]+=.1
    with pytest.raises(ValueError,match="within-blossom"):
        fit_blossom_clustered(altered)


def test_missing_seed_mass_or_unknown_treatment_rejected():
    df=_synthetic_data()
    altered=df.copy()
    altered.loc[0,"seedmass"]=None
    with pytest.raises(ValueError,match="complete selected"):
        fit_blossom_clustered(altered)
    altered=df.copy()
    altered.loc[0,"treatcode"]="fruit_only"
    with pytest.raises(ValueError,match="four original arms"):
        fit_blossom_clustered(altered)


def test_authentic_original_pair_required_not_synthetic_bytes():
    d=json.loads((ROOT/"data/DALECHAMPIA_POSTANTHESIS_METHOD_AND_DRYAD_V2.json").read_text())
    with pytest.raises(ValueError,match="both exact named original Dryad"):
        analyze_authenticated_blossom_clusters(d,{"some_seed_file":b"x"})


def test_frozen_source_result_states_no_new_mechanism_or_structural_balance():
    f=json.loads((ROOT/"data/DALECHAMPIA_2015_BLOSSOM_CLUSTERED_FROZEN_V1.json").read_text())
    assert f["schema_version"]=="DALECHAMPIA_2015_BLOSSOM_CLUSTERED_FROZEN_V1"
    assert f["inference_limits"]["source_published_mixed_model_reproduced"] is False
    assert f["inference_limits"]["structural_balance_occupancy_identified"] is False
    assert f["comparison_definition"]["original_morphological_abortion_reconstructed"] is False
    m=f["models"]["numeric_ge20_proxy__ped_only"]
    assert (m["n_seed_rows"],m["n_blossoms"],m["n_maternal_plants"])==(1103,132,36)
    assert all(x["witnesses_zero_in_interval"] is True for x in m["effects"].values())
    # A separate exploratory all-mass + seedset specification happens to
    # exclude zero; do not select it post hoc as sole decisive result.
    assert (f["models"]["all_nonmissing__plus_seedset"]["effects"]
            ["bag_minus_cont"]["witnesses_zero_in_interval"] is False)

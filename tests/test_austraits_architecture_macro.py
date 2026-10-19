"""Pure fixtures keep the external macro lane honest without live web dependency."""
from __future__ import annotations

import csv
import json
import pytest

from balance_domain.austraits_architecture_macro import (
    SELECTED_TRAITS, _pair_analysis, _safe_species_value, analyze_selected_csv,
    select_frozen_release,
)

FIELDS = [
    "taxon_name","trait_name","trait_value","trait_unit","dataset_key","source_record_id",
]

def _record(name,trait,value,id):
    return {
        "taxon_name": name,
        "trait_name": trait,
        "trait_value": value,
        "trait_unit":"",
        "dataset_key":"Example_Study_1",
        "source_record_id":str(id),
    }

def _create(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

def _manifest():
    return {
        "release_version":"v7.0.0",
        "archive_checksum_verified":True,
        "archive_sha256":"source-hash-fixture",
        "doi":"10.9999/synthetic.fixture",
        "requested_trait_names":sorted(SELECTED_TRAITS),
    }

def test_frozen_release_selects_registered_version_only():
    versions={"hits":{"hits":[
        {"metadata":{"version":"v6.0.0"},"id":6},
        {"metadata":{"version":"7.0.0"},"id":7},
    ]}}
    assert select_frozen_release(versions)["id"] == 7
    with pytest.raises(ValueError,match="exactly one"):
        select_frozen_release({"hits":{"hits":[versions["hits"]["hits"][1]]*2}})
    with pytest.raises(ValueError,match="exactly one"):
        select_frozen_release({"hits":{"hits":[{"metadata":{"version":"8.0.0"}}]}})

def test_species_first_strict_states_exclude_ambiguities(tmp_path):
    rows=[
        _record("Rosa alba","sex_type","hermaphrodite",1),
        _record("Rosa alba","pollination_syndrome","insect",2),
        _record("Rosa rubra","sex_type","dioecious",3),
        _record("Rosa rubra","pollination_syndrome","wind",4),
        _record("Rosa ambiguous","sex_type","monoecious",5),
        _record("Rosa ambiguous","sex_type","dioecious",6),
        _record("Rosa ambiguous","pollination_syndrome","wind",7),
        _record("Rosa unknown","sex_type","uncertain",8),
        _record("Rosa unknown","pollination_syndrome","wind",9),
        _record("Rosa subset var. v","sex_type","dioecious",10),
        _record("Rosa subset var. v","pollination_syndrome","wind",11),
        _record("Rosa alba","pollination_system","bee",12),
        _record("Rosa alba","flower_structural_sex_type","bisexual",13),
    ]
    p=tmp_path/"source.csv"
    _create(p,rows)
    result=analyze_selected_csv(p,_manifest())
    pair=result["sex_system_pollination_syndrome_pilot"]
    assert result["standardized_selected_rows"] == len(rows)
    assert pair["qualified_exact_species_overlap"] == 2
    assert pair["by_pollen_mode"]["INSECT"]["species"] == 1
    assert pair["by_pollen_mode"]["WIND"]["species"] == 1
    assert pair["source_species_denominator"]["multiple_raw_labels_excluded"] == 1
    assert pair["source_species_denominator"]["unmapped_single_raw_label_species"] == 1
    assert pair["source_species_denominator"]["non_binomial_source_rows_excluded"] == 1
    assert pair["genera_with_both_pollen_modes"] == 1
    assert pair["postopen_genus_overlap_signs"] == {
        "positive": 1, "negative": 0, "zero": 0,
    }
    source_sensitivity = pair["postopen_source_cohort_sensitivity"]
    assert source_sensitivity["admitted_single_source_pair_species"] == 2
    assert source_sensitivity["multiple_datasets_in_either_trait"] == 0
    assert source_sensitivity["by_pollen_source"]["Example_Study_1"]["status"] == "HOLD_INSUFFICIENT_COMMON_SUPPORT"
    assert pair["status"] == "HOLD_INSUFFICIENT_COMMON_SUPPORT"
    assert pair["raw_difference_wind_minus_insect"] is None
    assert pair["sex_system_by_mode"] == {
        "INSECT | SHARED_SEX_SYSTEM":1,
        "WIND | SEX_SEPARATED_AMONG_INDIVIDUALS":1,
    }
    # Distinct plant-reproductive sex and flower-level structure are not collapsed.
    assert result["trait_coverage"]["flower_structural_sex_type"]["source_rows"] == 1

def test_no_unverified_or_modified_source_promotion(tmp_path):
    p=tmp_path/"source.csv"
    _create(p,[_record("Rosa alba","sex_type","hermaphrodite",1)])
    m=_manifest()
    m["archive_checksum_verified"]=False
    with pytest.raises(ValueError,match="unverified"):
        analyze_selected_csv(p,m)
    m=_manifest()
    m["requested_trait_names"]=["sex_type"]
    with pytest.raises(ValueError,match="Selected trait"):
        analyze_selected_csv(p,m)
    m=_manifest()
    m["release_version"]="8.0.0"
    with pytest.raises(ValueError,match="source release mismatch"):
        analyze_selected_csv(p,m)

def test_source_duplicate_identity_and_source_specificity_fail_closed(tmp_path):
    p=tmp_path/"source.csv"
    _create(p,[
        _record("Rosa alba","sex_type","hermaphrodite",1),
        _record("Rosa rubra","sex_type","dioecious",1),
    ])
    with pytest.raises(ValueError,match="not unique"):
        analyze_selected_csv(p,_manifest())
    _create(p,[_record("Rosa alba","functional_conflict","positive",3)])
    with pytest.raises(ValueError,match="Incomplete raw trait"):
        analyze_selected_csv(p,_manifest())

def test_minimum_arm_and_genus_gate_not_significance():
    rows=[]
    for j in range(20):
        for value,mode,offset in [
            ("hermaphrodite","insect",0),
            ("dioecious","wind",1),
        ]:
            species=f"Genus{j} name{offset}"
            rows.extend([
                _record(species,"sex_type",value,2*j*2+offset),
                _record(species,"pollination_syndrome",mode,100+2*j+offset),
            ])
    # These fixture names deliberately fail the strict botanical binomial
    # filter because they include digits. The data adequacy gate must HOLD.
    result=_pair_analysis(rows)
    assert result["status"] == "HOLD_INSUFFICIENT_COMMON_SUPPORT"
    assert result["qualified_exact_species_overlap"] == 0


def test_primary_species_contrast_invariant_to_duplicate_source_provenance():
    rows=[
        _record("Rosa alba","sex_type","hermaphrodite",1),
        _record("Rosa alba","pollination_syndrome","insect",2),
        _record("Rosa rubra","sex_type","dioecious",3),
        _record("Rosa rubra","pollination_syndrome","wind",4),
    ]
    first=_pair_analysis(rows)
    duplicate=_record("Rosa alba","sex_type","hermaphrodite",5)
    duplicate["dataset_key"]="Independent_Study_2"
    enriched=_pair_analysis(rows+[duplicate])
    assert enriched["qualified_exact_species_overlap"] == first["qualified_exact_species_overlap"]
    assert enriched["sex_system_by_mode"] == first["sex_system_by_mode"]
    assert enriched["postopen_source_cohort_sensitivity"]["admitted_single_source_pair_species"] == 1
    assert enriched["postopen_source_cohort_sensitivity"]["multiple_datasets_in_either_trait"] == 1

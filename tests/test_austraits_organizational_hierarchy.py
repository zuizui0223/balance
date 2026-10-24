"""Real-source adapter's post-open structural-level estimands on synthetic fixtures."""
from __future__ import annotations

from balance_domain.austraits_organizational_hierarchy import (
    analyze_organizational_hierarchy,
)


def rec(name, trait, value, index):
    return {
        "taxon_name": name, "trait_name": trait, "trait_value": value,
        "trait_unit": "", "dataset_key": "Synthetic_Original_Source",
        "source_record_id": f"test:{index}",
    }


def add(rows, name, sex, flower, pollen):
    for trait, value in (
        ("sex_type", sex),
        ("flower_structural_sex_type", flower),
        ("pollination_syndrome", pollen),
    ):
        rows.append(rec(name, trait, value, len(rows) + 1))


def make_rows():
    rows = []
    add(rows, "Aster alba", "hermaphrodite", "bisexual", "insect")
    add(rows, "Aster rubra", "monoecious", "unisexual", "wind")
    add(rows, "Begonia lutea", "dioecious", "unisexual", "insect")
    add(rows, "Begonia alba", "hermaphrodite", "unisexual", "wind")
    add(rows, "Camellia rosea", "hermaphrodite", "incompletely_unisexual", "insect")
    add(rows, "Daisy alba", "dioecious", "bisexual", "wind")
    return rows


def test_distinct_organism_and_flower_organization_levels():
    audit = analyze_organizational_hierarchy(make_rows())
    assert audit["not_direct_functional_conflict"]
    assert audit["not_historical_origins"]
    v = audit["sex_system_x_flower_structure"]
    assert v["same_exact_binomial_species"] == 6
    assert v["classification"] == {
        "AMONG_FLOWERS_SEPARATED": 1,
        "AMONG_INDIVIDUALS_SEPARATED": 1,
        "CROSS_LEVEL_LABEL_DISCORDANCE": 2,
        "FLOWER_PARTIAL_STATE": 1,
        "WITHIN_FLOWER_SHARED": 1,
    }
    assert v["cross_level_unresolved_or_discordant"] == 3


def test_flower_level_is_not_equivalent_to_whole_species_sex_system():
    a = analyze_organizational_hierarchy(make_rows())
    t = a["flower_structure_x_pollen_mode"]
    assert t["same_exact_binomial_species"] == 6
    assert t["source_by_mode"]["INSECT"]["all_flower_states_species"] == 3
    assert t["source_by_mode"]["INSECT"]["qualified_bisexual_unisexual_species"] == 2
    assert t["source_by_mode"]["WIND"]["qualified_bisexual_unisexual_species"] == 3
    assert t["cross_table"] == {
        "INSECT | BISEXUAL_FLOWER": 1,
        "INSECT | PARTIAL_UNISEXUAL_FLOWER": 1,
        "INSECT | UNISEXUAL_FLOWER": 1,
        "WIND | BISEXUAL_FLOWER": 1,
        "WIND | UNISEXUAL_FLOWER": 2,
    }
    assert t["status"] == "HOLD_INSUFFICIENT_COMMON_SUPPORT"
    assert t["wind_minus_insect_unisexual_fraction"] is None
    assert a["sex_system_x_flower_structure_x_pollen"]["status"] == (
        "HOLD_INSUFFICIENT_COMMON_SUPPORT"
    )


def test_genus_balanced_and_within_genus_can_disagree():
    x = analyze_organizational_hierarchy(make_rows())
    g = x["genus_balanced_sex_system_pollen"]
    assert g["genera_by_mode"] == {"INSECT": 3, "WIND": 3}
    assert g["genera_with_both_modes"] == 2
    assert abs(g["wind_minus_insect_equal_genus"] - (1 / 3)) < 1e-12
    assert abs(g["within_genus_mean"]) < 1e-12
    assert g["within_genus_signs"] == {
        "positive": 1, "negative": 1, "zero": 0,
    }


def test_conflicting_flower_source_states_never_create_causal_transition():
    rows = make_rows()
    rows.append(rec("Aster alba", "flower_structural_sex_type", "unisexual", 999))
    x = analyze_organizational_hierarchy(rows)
    assert x["flower_source_quality"]["multiple_raw_labels_excluded"] == 1
    assert x["sex_system_x_flower_structure"]["same_exact_binomial_species"] == 5
    assert x["flower_structure_x_pollen_mode"]["same_exact_binomial_species"] == 5
    assert x["not_historical_origins"]


def test_flower_level_source_strata_and_genus_weight_do_not_force_comparisons():
    data = analyze_organizational_hierarchy(make_rows())
    obj = data["flower_structure_x_pollen_mode"][
        "postopen_provenance_genus_diagnostics"
    ]
    genus = obj["genus_equal_weight"]
    assert genus["genera_by_mode"] == {"INSECT": 2, "WIND": 3}
    assert genus["genera_with_both_modes"] == 2
    assert abs(genus["wind_minus_insect"] - (1 / 6)) < 1e-12
    assert genus["within_genus_signs"] == {
        "positive": 1, "negative": 0, "zero": 1
    }
    source = obj["source_provider_strata"]
    assert source["single_source_key_species"] == 5
    assert source["multiple_dataset_keys_excluded"] == 0
    assert source["by_source_pair"][
        "Synthetic_Original_Source -> Synthetic_Original_Source"
    ]["status"] == "HOLD_INSUFFICIENT_COMMON_SUPPORT"
    assert data["sex_system_x_flower_structure_x_pollen"][
        "wind_minus_insect_fraction"
    ] is None


def test_flower_source_ambiguity_never_fills_competing_source_strata():
    rows = make_rows()
    duplicate = rec("Aster alba", "flower_structural_sex_type", "bisexual", 1001)
    duplicate["dataset_key"] = "Another_Source"
    rows.append(duplicate)
    diagnostic = analyze_organizational_hierarchy(rows)[
        "flower_structure_x_pollen_mode"
    ]["postopen_provenance_genus_diagnostics"]["source_provider_strata"]
    assert diagnostic["single_source_key_species"] == 4
    assert diagnostic["multiple_dataset_keys_excluded"] == 1

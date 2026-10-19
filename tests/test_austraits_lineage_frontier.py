"""Synthetic guards for an outcome-blind congeneric candidate frontier."""
from __future__ import annotations

from balance_domain.austraits_lineage_frontier import analyze_candidate_lineages


def row(name, trait, value, index):
    return {
        "taxon_name": name,
        "trait_name": trait,
        "trait_value": value,
        "dataset_key": "Registered_Botanical_Source",
        "source_record_id": f"synthetic:{index}",
        "trait_unit": "",
    }


def data():
    out = []
    for name, sex, flower, pollen in (
        ("Aster alba", "hermaphrodite", "bisexual", "insect"),
        ("Aster rubra", "hermaphrodite", "bisexual", "insect"),
        ("Aster lutea", "monoecious", "unisexual", "wind"),
        ("Aster rosea", "dioecious", "unisexual", "wind"),
        ("Begonia alba", "hermaphrodite", "bisexual", "insect"),
        ("Begonia rubra", "dioecious", "unisexual", "wind"),
        ("Begonia viridis", "hermaphrodite", "bisexual", "insect"),
        ("Camellia alba", "hermaphrodite", "bisexual", "insect"),
        ("Camellia rubra", "hermaphrodite", "bisexual", "insect"),
        ("Camellia viridis", "dioecious", "unisexual", "wind"),
        ("Camellia rosea", "dioecious", "unisexual", "wind"),
    ):
        for trait, value in (
            ("sex_type", sex),
            ("flower_structural_sex_type", flower),
            ("pollination_syndrome", pollen),
        ):
            out.append(row(name, trait, value, len(out) + 1))
    return out


def test_minimum_two_species_each_state_and_unique_genus():
    v = analyze_candidate_lineages(data())
    assert v["source_trait_records_redistributed"] is False
    p = v["species_sex_system_candidate_lineages"]
    flower = v["flower_structural_sex_candidate_lineages"]
    assert p["candidate_genera_meeting_two_per_state"] == 2
    assert flower["candidate_genera_meeting_two_per_state"] == 2
    assert [r["genus"] for r in p["top_candidate_genera"]] == [
        "Aster", "Camellia"
    ]
    assert all(
        x["not_a_reconstructed_transition"] for x in p["top_candidate_genera"]
    )
    assert p["candidates_with_both_pollen_modes"] == 2
    assert flower["candidates_with_both_pollen_modes"] == 2


def test_conflicting_source_label_fails_to_complete_genus():
    rows = data()
    rows.append(row("Aster alba", "flower_structural_sex_type", "unisexual", 999))
    v = analyze_candidate_lineages(rows)
    flower = v["flower_structural_sex_candidate_lineages"]
    assert flower["candidate_genera_meeting_two_per_state"] == 1
    assert [r["genus"] for r in flower["top_candidate_genera"]] == ["Camellia"]
    assert v["source_quality"]["flower"]["multiple_raw_labels_excluded"] == 1
    assert v["species_sex_system_candidate_lineages"][
        "candidate_genera_meeting_two_per_state"
    ] == 2


def test_external_pollen_mismatch_does_not_create_an_origin_claim():
    rows = data()
    for r in rows:
        if r["trait_name"] == "pollination_syndrome":
            r["trait_value"] = "insect wind"
    v = analyze_candidate_lineages(rows)
    assert v["species_sex_system_candidate_lineages"][
        "candidate_genera_meeting_two_per_state"
    ] == 2
    assert v["species_sex_system_candidate_lineages"][
        "candidates_with_both_pollen_modes"
    ] == 0
    assert v["flower_structural_sex_candidate_lineages"][
        "candidates_with_both_pollen_modes"
    ] == 0
    assert v["source_quality"]["pollen"]["unmapped_single_raw_label_species"] == 11

from pathlib import Path

from balance_domain.plant_u2 import (
    build_u2_readout,
    build_u2_double_code_handoff,
    build_u2_reference_handoff,
    load_u2_double_code_sample,
    load_u2_universe,
)


ROOT = Path(__file__).resolve().parents[1]
U2 = ROOT / "data" / "BALANCE_PLANT_U2_BARRETT_REVIEW_UNIVERSE_V1.csv"
COVERAGE = ROOT / "data" / "BALANCE_PLANT_U2_REFERENCE_COVERAGE_V1.csv"
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"
PACKET = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv"


def test_u2_review_universe_validates():
    rows = load_u2_universe(U2)
    assert len(rows) == 22
    assert len({r["dependency_group"] for r in rows}) == 22


def test_u2_is_discovery_only_even_when_source_resolution_is_closed():
    readout = build_u2_readout(U2)
    assert readout["n_registered_dependency_groups"] == 22
    assert readout["n_species_level_source_resolved"] == 22
    assert readout["n_taxon_resolution_pending"] == 0
    assert "not_conflict_positive" in readout["claim_ceiling"]


def test_u2_reference_coverage_and_source_handoff_are_closed():
    handoff = build_u2_reference_handoff(U2, COVERAGE)
    assert handoff["n_registered_dependency_groups"] == 22
    assert handoff["n_barrett_references"] == 37
    assert handoff["n_pending_reference_classifications"] == 0
    assert handoff["n_unresolved_primary_sources"] == 0
    assert handoff["review_reference_coverage_closed"] is True
    assert handoff["species_source_resolution_closed"] is True
    assert handoff["discovery_universe_source_closed"] is True
    assert "not_conflict_status" in handoff["claim_ceiling"]


def test_eichhornia_multiple_studies_are_one_dependency_group():
    rows = load_u2_universe(U2)
    eich = [r for r in rows if r["dependency_group"] == "Eichhornia_paniculata"]
    assert len(eich) == 1
    assert "Kohn_Barrett_1992" in eich[0]["review_reference"]
    assert "Harder_Barrett_1995" in eich[0]["review_reference"]
    assert "Harder_Barrett_Cole_2000" in eich[0]["review_reference"]


def test_review_universe_retains_null_or_specificity_case():
    rows = load_u2_universe(U2)
    pont = next(r for r in rows if r["dependency_group"] == "Pontederia_cordata")
    assert pont["evidence_family"] == "PHYSICAL_SEX_ORGAN_INTERFERENCE_NULL_TEST"
    assert pont["screening_status"] == "UNSCREENED"


def test_alpinia_flexistyly_program_is_resolved_to_species():
    rows = load_u2_universe(U2)
    alpinia = next(r for r in rows if r["dependency_group"] == "Alpinia_kwangsiensis")
    assert alpinia["taxon_raw"] == "Alpinia kwangsiensis"
    assert alpinia["source_resolution_status"] == "RESOLVED_PRIMARY"
    assert alpinia["primary_source_doi"] == "10.1038/35068635"


def test_u2_source_closed_first20_is_ready_for_independent_double_coding():
    handoff = build_u2_double_code_handoff(U2, SAMPLE, PACKET)
    assert handoff["n_universe_groups"] == 22
    assert handoff["n_sampled_groups"] == 20
    assert handoff["n_source_packet_groups"] == 20
    assert handoff["all_sampled_sources_resolved"] is True
    assert handoff["selection_rule_closed"] is True
    assert handoff["source_packet_blinded_to_review_evidence_family"] is True
    assert handoff["independent_double_coding_ready"] is True


def test_u2_double_code_sample_retains_first20_lexicographic_groups():
    rows = load_u2_double_code_sample(SAMPLE)
    taxa = [r["taxon_raw"] for r in rows]
    assert taxa[:5] == [
        "Alpinia kwangsiensis",
        "Asclepias exaltata",
        "Campsis radicans",
        "Chamaecrista fasciculata (Todd: Cassia chamaecrista)",
        "Eichhornia paniculata",
    ]
    assert taxa[-3:] == [
        "Wachendorfia brachyandra",
        "Wachendorfia paniculata",
        "Wachendorfia parviflora",
    ]

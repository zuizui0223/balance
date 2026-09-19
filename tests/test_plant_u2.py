from pathlib import Path

from balance_domain.plant_u2 import build_u2_readout, load_u2_universe


ROOT = Path(__file__).resolve().parents[1]
U2 = ROOT / "data" / "BALANCE_PLANT_U2_BARRETT_REVIEW_UNIVERSE_V1.csv"


def test_u2_provisional_review_universe_validates():
    rows = load_u2_universe(U2)
    assert len(rows) == 16
    assert len({r["dependency_group"] for r in rows}) == 16


def test_u2_is_discovery_only_not_claimed_closed():
    readout = build_u2_readout(U2)
    assert readout["n_registered_dependency_groups"] == 16
    assert readout["n_species_level_source_resolved"] == 16
    assert readout["n_taxon_resolution_pending"] == 0
    assert readout["review_universe_closed"] is False
    assert "not_conflict_positive" in readout["claim_ceiling"]


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

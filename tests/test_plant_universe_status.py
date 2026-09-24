from pathlib import Path

from balance_domain.plant_universe_status import build_plant_universe_status, load_plant_universe_status


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data" / "BALANCE_PLANT_UNIVERSE_STATUS_V1.csv"


def test_three_universe_status_contract_validates():
    rows = load_plant_universe_status(STATUS)
    assert {r["universe_id"] for r in rows} == {
        "U1_HAAS_LORTIE_2020",
        "U2_BARRETT_2002",
        "U3_VALLEJOMARIN_2010",
    }


def test_only_u2_is_currently_double_code_ready():
    readout = build_plant_universe_status(STATUS)
    assert readout["double_code_ready_universes"] == ["U2_BARRETT_2002"]
    assert readout["source_closed_universes"] == [
        "U2_BARRETT_2002",
        "U3_VALLEJOMARIN_2010",
    ]
    assert readout["outcome_blind_universes"] == [
        "U1_HAAS_LORTIE_2020",
        "U2_BARRETT_2002",
    ]


def test_u1_is_explicitly_incomplete_full_review_frame():
    rows = {r["universe_id"]: r for r in load_plant_universe_status(STATUS)}
    u1 = rows["U1_HAAS_LORTIE_2020"]
    assert u1["registered_units"] == 44
    assert u1["target_units"] == 47
    assert u1["source_closed"] is False
    assert "INGEST_LOCATED_SUPPLEMENT_TABLES" in u1["current_blocker"]


def test_u3_blocker_uses_frozen_plastome_ranking_not_obsolete_marker_tie():
    rows = {r["universe_id"]: r for r in load_plant_universe_status(STATUS)}
    u3 = rows["U3_VALLEJOMARIN_2010"]
    blocker = u3["current_blocker"]
    assert "68_CDS_PLASTOME_RANKING" in blocker
    assert "DIRECT_SPECIES_LEVEL_EFFECTIVE_POLLINATION" in blocker
    assert "HIGHER_RESOLUTION_PHYLOGENY" not in blocker

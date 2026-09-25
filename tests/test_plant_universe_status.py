from pathlib import Path
from balance_domain.plant_universe_status import build_plant_universe_status, load_plant_universe_status

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data" / "BALANCE_PLANT_UNIVERSE_STATUS_V1.csv"

def test_three_universe_status_contract_validates():
    rows = load_plant_universe_status(STATUS)
    assert {r["universe_id"] for r in rows} == {"U1_HAAS_LORTIE_2020","U2_BARRETT_2002","U3_VALLEJOMARIN_2010"}

def test_u1_and_u2_are_double_code_ready():
    readout = build_plant_universe_status(STATUS)
    assert readout["double_code_ready_universes"] == ["U1_HAAS_LORTIE_2020","U2_BARRETT_2002"]
    assert readout["source_closed_universes"] == ["U1_HAAS_LORTIE_2020","U2_BARRETT_2002","U3_VALLEJOMARIN_2010"]

def test_u1_is_closed_at_full47():
    u1 = {r["universe_id"]: r for r in load_plant_universe_status(STATUS)}["U1_HAAS_LORTIE_2020"]
    assert u1["registered_units"] == 47 and u1["target_units"] == 47
    assert u1["source_closed"] is True and u1["double_code_ready"] is True
    assert u1["current_blocker"] == "INDEPENDENT_SECOND_CODER_REQUIRED"

def test_u3_blocker_distinguishes_frozen_retrieval_ceiling_from_new_evidence_need():
    u3 = {r["universe_id"]: r for r in load_plant_universe_status(STATUS)}["U3_VALLEJOMARIN_2010"]
    blocker = u3["current_blocker"]
    assert "PROSPECTIVE_BRASSICACEAE_CONTROL_SEARCH_IN_PROGRESS" in blocker
    assert "BIXACEAE_RETAINED_AS_EVIDENCE_CEILING_BLOCKED_MATCHING_STAGE_MISSINGNESS" in blocker
    assert "EVIDENCE_CEILING_OPEN" not in blocker

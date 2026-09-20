from pathlib import Path

from balance_domain.plant_u3_controls import build_u3_matched_control_readout, load_u3_matched_controls


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"


def test_real_u3_matched_control_registry_is_screened_not_adjudicated():
    rows = load_u3_matched_controls(PAIRS, CASES, U3)
    assert len(rows) == 1
    pair = rows[0]
    assert pair["case_taxon"] == "Solanum rostratum"
    assert pair["control_taxon"] == "Solanum lycocarpum"
    assert pair["pair_role"] == "PRIMARY"
    assert pair["selection_status"] == "SCREENED"
    assert pair["predictor_blinding_status"] == "BLINDED"
    assert pair["animal_pollination_eligible"] is True
    assert pair["heteranthery_absence_confirmed"] is True


def test_real_u3_matched_control_layer_stays_open():
    readout = build_u3_matched_control_readout(PAIRS, CASES, U3)
    assert readout["n_pairs"] == 1
    assert readout["n_adjudicated_primary_pairs"] == 0
    assert readout["n_registered_case_taxa"] == 6
    assert readout["n_cases_with_adjudicated_primary_control"] == 0
    assert readout["case_control_layer_closed"] is False

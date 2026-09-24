from pathlib import Path

from balance_domain.plant_u3_matched_extraction import (
    build_u3_matched_extraction_readout,
    load_u3_matched_extraction,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
EXTRACT = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_EXTRACTION_V1.csv"


def test_matched_extraction_covers_four_pass_pairs():
    rows = load_u3_matched_extraction(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert len(rows) == 8
    assert {r["pair_id"] for r in rows} == {
        "U3_PAIR_SOLRO_001",
        "U3_PAIR_MELMA_001",
        "U3_PAIR_SENAL_001",
        "U3_PAIR_SENBI_001",
    }


def test_current_matched_lane_has_one_resolved_control_conflict_but_is_not_ready():
    out = build_u3_matched_extraction_readout(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert out["n_pairs"] == 4
    assert out["case_conflict_status_counts"] == {"POSITIVE": 2, "UNRESOLVED": 2}
    assert out["control_conflict_status_counts"] == {
        "POSITIVE": 1,
        "UNRESOLVED": 3,
    }
    assert out["n_controls_with_resolved_conflict"] == 1
    assert out["matched_conflict_estimand_ready"] is False


def test_module_substrate_is_extracted_not_forced_to_match():
    out = build_u3_matched_extraction_readout(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert out["control_module_substrate_counts"] == {
        "REPEATED_FLOWERS": 1,
        "SERIAL_WITHIN_FLOWER": 3,
    }
    assert out["n_module_substrate_matched_pairs"] == 3


def test_nonheterantherous_controls_are_not_assumed_globally_integrated():
    out = build_u3_matched_extraction_readout(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert out["control_architecture_mode_counts"] == {
        "AMONG_FLOWER_MODULE_DIVISION": 1,
        "UNRESOLVED": 3,
    }
    assert out["n_controls_shared_integrated"] == 0
    assert out["n_controls_with_alternative_resolved_architecture"] == 1
    assert out["matched_integrated_control_contrast_ready"] is False


def test_alata_spectabilis_pair_keeps_conflict_and_broader_architecture_unresolved():
    rows = load_u3_matched_extraction(EXTRACT, ADJ, PAIRS, CASES, U3)
    pair = [r for r in rows if r["pair_id"] == "U3_PAIR_SENAL_001"]
    assert {r["taxon_role"] for r in pair} == {"CASE", "CONTROL"}
    case = next(r for r in pair if r["taxon_role"] == "CASE")
    control = next(r for r in pair if r["taxon_role"] == "CONTROL")
    assert case["pollen_fate_conflict_status"] == "UNRESOLVED"
    assert control["pollen_fate_conflict_status"] == "UNRESOLVED"
    assert control["architecture_mode"] == "UNRESOLVED"
    assert control["module_substrate"] == "SERIAL_WITHIN_FLOWER"


def test_bicapsularis_covesii_pair_keeps_conflict_and_broader_architecture_unresolved():
    rows = load_u3_matched_extraction(EXTRACT, ADJ, PAIRS, CASES, U3)
    pair = [r for r in rows if r["pair_id"] == "U3_PAIR_SENBI_001"]
    assert {r["taxon_role"] for r in pair} == {"CASE", "CONTROL"}
    case = next(r for r in pair if r["taxon_role"] == "CASE")
    control = next(r for r in pair if r["taxon_role"] == "CONTROL")
    assert case["pollen_fate_conflict_status"] == "UNRESOLVED"
    assert control["pollen_fate_conflict_status"] == "UNRESOLVED"
    assert control["architecture_mode"] == "UNRESOLVED"
    assert control["module_substrate"] == "SERIAL_WITHIN_FLOWER"

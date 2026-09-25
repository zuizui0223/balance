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


def test_current_matched_lane_has_two_fully_resolved_conflict_pairs_but_is_not_ready():
    out = build_u3_matched_extraction_readout(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert out["n_pairs"] == 4
    assert out["case_conflict_status_counts"] == {"POSITIVE": 3, "UNRESOLVED": 1}
    assert out["control_conflict_status_counts"] == {
        "POSITIVE": 2,
        "UNRESOLVED": 2,
    }
    assert out["n_cases_with_resolved_conflict"] == 3
    assert out["n_controls_with_resolved_conflict"] == 2
    assert out["n_pairs_with_both_conflict_resolved"] == 2
    assert out["matched_conflict_estimand_ready"] is False


def test_matched_conflict_ready_requires_both_case_and_control_resolution(tmp_path):
    rows = EXTRACT.read_text(encoding="utf-8")
    rows = rows.replace(
        "U3_PAIR_MELMA_001,CONTROL,Osbeckia chinensis,UNRESOLVED,SERIAL_WITHIN_FLOWER,UNRESOLVED,NO_MATCHED_POLLEN_FATE_CONFLICT_EXPERIMENT",
        "U3_PAIR_MELMA_001,CONTROL,Osbeckia chinensis,UNRESOLVED,SERIAL_WITHIN_FLOWER,POSITIVE,DIRECT_TEST_FIXTURE",
    ).replace(
        "U3_PAIR_SENBI_001,CONTROL,Senna covesii,UNRESOLVED,SERIAL_WITHIN_FLOWER,UNRESOLVED,NO_MATCHED_POLLEN_FATE_CONFLICT_EXPERIMENT",
        "U3_PAIR_SENBI_001,CONTROL,Senna covesii,UNRESOLVED,SERIAL_WITHIN_FLOWER,POSITIVE,DIRECT_TEST_FIXTURE",
    )
    path = tmp_path / "extract.csv"
    path.write_text(rows, encoding="utf-8")
    out = build_u3_matched_extraction_readout(path, ADJ, PAIRS, CASES, U3)
    assert out["n_controls_with_resolved_conflict"] == 4
    assert out["case_conflict_status_counts"]["UNRESOLVED"] == 1
    assert out["matched_conflict_estimand_ready"] is False


def test_module_substrate_is_extracted_not_forced_to_match():
    out = build_u3_matched_extraction_readout(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert out["control_module_substrate_counts"] == {
        "REPEATED_FLOWERS": 1,
        "SERIAL_WITHIN_FLOWER": 3,
    }
    assert out["n_module_substrate_matched_pairs"] == 3


def test_nonheterantherous_controls_can_use_other_functional_architectures():
    out = build_u3_matched_extraction_readout(EXTRACT, ADJ, PAIRS, CASES, U3)
    assert out["control_architecture_mode_counts"] == {
        "AMONG_FLOWER_MODULE_DIVISION": 1,
        "UNRESOLVED": 2,
        "WITHIN_FLOWER_DIVISION_OF_LABOUR": 1,
    }
    assert out["n_controls_shared_integrated"] == 0
    assert out["n_controls_with_alternative_resolved_architecture"] == 2
    assert out["matched_integrated_control_contrast_ready"] is False


def test_alata_spectabilis_pair_has_direct_conflict_on_both_sides():
    rows = load_u3_matched_extraction(EXTRACT, ADJ, PAIRS, CASES, U3)
    pair = [r for r in rows if r["pair_id"] == "U3_PAIR_SENAL_001"]
    case = next(r for r in pair if r["taxon_role"] == "CASE")
    control = next(r for r in pair if r["taxon_role"] == "CONTROL")
    assert case["pollen_fate_conflict_status"] == "POSITIVE"
    assert "Amorim_et_al_2017" in case["source_id"]
    assert control["pollen_fate_conflict_status"] == "POSITIVE"
    assert control["architecture_mode"] == "WITHIN_FLOWER_DIVISION_OF_LABOUR"
    assert "Amorim_et_al_2017" in control["source_id"]
    assert "nonheterantherous" in control["notes"]


def test_bicapsularis_covesii_pair_remains_functionally_unresolved():
    rows = load_u3_matched_extraction(EXTRACT, ADJ, PAIRS, CASES, U3)
    pair = [r for r in rows if r["pair_id"] == "U3_PAIR_SENBI_001"]
    case = next(r for r in pair if r["taxon_role"] == "CASE")
    control = next(r for r in pair if r["taxon_role"] == "CONTROL")
    assert case["pollen_fate_conflict_status"] == "UNRESOLVED"
    assert control["pollen_fate_conflict_status"] == "UNRESOLVED"

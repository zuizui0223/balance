from pathlib import Path

from balance_domain.plant_readiness import build_plant_v4_readiness


ROOT = Path(__file__).resolve().parents[1]


def test_current_plant_v4_readiness_separates_primary_and_external_human_gates():
    out = build_plant_v4_readiness(
        u1_first20_conflict_path=ROOT / "data" / "BALANCE_PLANT_U1_BLIND_CONFLICT_SCREEN_V1.csv",
        u1_production27_conflict_path=ROOT / "data" / "BALANCE_PLANT_U1_PRODUCTION_BLIND_CONFLICT_SCREEN_V1.csv",
        u1_sample_path=ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv",
        u1_worksheet_path=ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
        u1_adjudication_path=ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
        u2_conflict_path=ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv",
        u2_sample_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv",
        u2_worksheet_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
        u2_adjudication_path=ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
        u2_predictor_receipts_path=ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        u6_freeze_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json",
        u6_worksheet_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
        u6_adjudication_path=ROOT / "data" / "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
        u6_predictor_receipts_path=ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        u6_dependence_path=ROOT / "data" / "BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv",
    )

    assert out["model_specification"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4"
    assert out["all_machine_preparation_complete"] is True
    assert out["machine_complete"] == {
        "u1_full47_source_screen": True,
        "u2_full22_source_screen": True,
        "u2_positive_predictor_source_screen": True,
        "u6_pass1_conflict_first_freeze": True,
        "u6_predictor_source_screen": True,
        "u6_cross_universe_dependence": True,
    }
    assert out["primary_human_open_gates"] == {
        "u2_independent_double_coding": True,
        "u2_post_coding_adjudication": True,
        "u6_independent_double_coding": True,
        "u6_post_coding_adjudication": True,
        "u2_predictor_independent_adjudication": True,
        "u6_predictor_independent_adjudication": True,
    }
    assert out["external_validation_open_gates"] == {
        "u1_independent_double_coding": True,
        "u1_post_coding_adjudication": True,
    }
    assert out["source_screen_summary"] == {
        "U1": {"n_groups": 47, "n_positive": 0, "n_unresolved": 0},
        "U2": {"n_groups": 22, "n_positive": 8, "n_unresolved": 0},
        "U6": {"n_groups": 21, "architecture_coding_complete": False},
    }
    assert out["primary_model_assembly_ready"] is False
    assert out["v4_estimability_ready_to_evaluate"] is False

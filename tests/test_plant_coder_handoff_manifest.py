import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "BALANCE_PLANT_CODER_HANDOFF_MANIFEST_V1.json"


def test_coder_handoff_manifest_points_only_to_existing_frozen_surfaces():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["status"] == "READY_FOR_HUMAN_INDEPENDENT_CODING"
    assert data["shared"]["frozen_coder_ids"] == ["CODER_A", "CODER_B"]
    assert data["shared"]["reliability_trigger_raw_agreement"] == 0.80
    assert data["shared"]["no_source_adjudication_before_reliability_pass"] is True

    assert data["lanes"]["U1"]["primary_model_denominator"] is False
    assert data["lanes"]["U2"]["primary_model_denominator"] is True
    assert data["lanes"]["U6"]["primary_model_denominator"] is True

    path_keys = {
        "U1": ["sample", "source_packet", "worksheet", "post_coding_adjudication", "predictor_receipts"],
        "U2": ["sample", "source_packet", "worksheet", "post_coding_adjudication", "predictor_receipts"],
        "U6": ["pass1_freeze", "source_packet", "worksheet", "post_coding_adjudication", "predictor_receipts"],
    }
    for lane, keys in path_keys.items():
        for key in keys:
            path = ROOT / data["lanes"][lane][key]
            assert path.exists(), f"missing {lane} {key}: {path}"


def test_coder_handoff_sequence_keeps_reliability_before_adjudication():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    seq = data["return_sequence"]
    reliability_index = next(i for i, step in enumerate(seq) if step.startswith("agreement report"))
    repair_index = next(i for i, step in enumerate(seq) if "raw agreement <0.80" in step)
    adjudication_index = next(i for i, step in enumerate(seq) if step.startswith("only after reliability pass"))
    predictor_index = next(i for i, step in enumerate(seq) if step.startswith("separately adjudicate predictor"))
    fit_index = next(i for i, step in enumerate(seq) if step.startswith("fit V4"))

    assert reliability_index < repair_index < adjudication_index < predictor_index < fit_index
    assert data["current_primary_model"] == "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4"
    assert data["current_publication_status"] == "DORMANT_PAPER_BRANCH"

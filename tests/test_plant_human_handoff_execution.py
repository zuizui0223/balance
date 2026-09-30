import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data" / "BALANCE_PLANT_HUMAN_HANDOFF_EXECUTION_V1.json"


def _load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_handoff_execution_receipt_rebuilds_deterministic_packets(tmp_path):
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["status"] == "PACKETS_GENERATED_AWAITING_INDEPENDENT_HUMAN_RETURNS"

    coder = _load_script(
        "build_plant_coder_packets",
        ROOT / "scripts" / "build_plant_coder_packets.py",
    )
    predictor = _load_script(
        "build_plant_predictor_adjudication_packet",
        ROOT / "scripts" / "build_plant_predictor_adjudication_packet.py",
    )

    coder_out = coder.build_all(tmp_path / "coders")
    for coder_id in ("CODER_A", "CODER_B"):
        zip_path, receipt_path = coder_out[coder_id]
        frozen = data["architecture_coding"]["packets"][coder_id]
        assert _sha256(zip_path) == frozen["packet_sha256"]
        assert _sha256(receipt_path) == frozen["receipt_sha256"]

    predictor_zip, predictor_receipt = predictor.build_packet(tmp_path / "predictor")
    frozen_predictor = data["predictor_receipt_adjudication"]
    assert _sha256(predictor_zip) == frozen_predictor["packet_sha256"]
    assert _sha256(predictor_receipt) == frozen_predictor["receipt_sha256"]


def test_handoff_execution_receipt_freezes_cross_role_evidence_identity():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    hashes = data["architecture_coding"]["audit"]["cross_role_shared_hashes"]

    assert _sha256(ROOT / "data" / "BALANCE_PLANT_MACRO_CODEBOOK_V1.csv") == (
        hashes["codebook_sha256"]
    )
    assert _sha256(
        ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv"
    ) == hashes["U2_source_packet_sha256"]
    assert _sha256(
        ROOT / "data" / "BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv"
    ) == hashes["U6_source_packet_sha256"]

    predictor = data["predictor_receipt_adjudication"]
    assert predictor["architecture_outputs_included"] is False
    assert (
        predictor["audit"]["cross_role_shared_hashes_match_architecture_coder_packets"]
        is True
    )
    assert (
        predictor["audit"]["focal_architecture_label_hits_in_receipt_value_source_or_notes"]
        == 0
    )

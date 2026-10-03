import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_plant_u2_predictor_expansion_packet.py"


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "build_plant_u2_predictor_expansion_packet",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_predictor_expansion_packet_is_deterministic_and_blinded(tmp_path):
    module = _load_script()
    zip_a, receipt_a = module.build_packet(tmp_path / "a")
    zip_b, receipt_b = module.build_packet(tmp_path / "b")

    assert _sha(zip_a) == _sha(zip_b)
    assert _sha(receipt_a) == _sha(receipt_b)

    receipt = json.loads(receipt_a.read_text(encoding="utf-8"))
    assert receipt["role"] == "INDEPENDENT_U2_PREDICTOR_EXPANSION_CODING"
    assert receipt["n_groups"] == 12
    assert receipt["n_predictor_slots"] == 36
    assert receipt["selective_gap_filling_forbidden"] is True
    assert receipt["architecture_outputs_included"] is False
    assert receipt["conflict_screen_outputs_included"] is False

    with zipfile.ZipFile(zip_a) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
        assert "PACKET_RECEIPT.json" in names
        assert "data/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv" in names
        assert "data/BALANCE_PLANT_U2_PREDICTOR_EXPANSION_SOURCE_PACKET_V2.csv" in names
        upper = "\n".join(names).upper()
        assert "DOUBLE_CODE_WORKSHEET" not in upper
        assert "CONFLICT_SCREEN" not in upper
        assert "ADJUDICATION_TEMPLATE" not in upper
        embedded = json.loads(archive.read("PACKET_RECEIPT.json"))
        assert embedded == receipt

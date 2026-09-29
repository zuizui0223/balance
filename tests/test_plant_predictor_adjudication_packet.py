import csv
import importlib
import io
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
builder = importlib.import_module("build_plant_predictor_adjudication_packet")


def test_predictor_adjudication_packet_contains_only_allowed_surfaces(tmp_path):
    zip_path, receipt_path = builder.build_packet(tmp_path)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["role"] == "INDEPENDENT_PREDICTOR_RECEIPT_REVIEW"
    assert receipt["architecture_outputs_included"] is False
    assert receipt["primary_universes"] == [
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    ]

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        assert "PACKET_RECEIPT.json" in names
        assert "data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv" in names
        assert "data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv" in names
        assert "data/BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv" in names
        assert "data/BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv" in names

        forbidden = (
            "WORKSHEET",
            "ARCHITECTURE_HANDOFF",
            "DOUBLE_CODE_ADJUDICATION",
            "AGREEMENT",
            "REACTIVATION",
        )
        for name in names:
            if name == "PACKET_RECEIPT.json":
                continue
            upper = name.upper()
            assert all(fragment not in upper for fragment in forbidden), name


def test_predictor_packet_receipts_have_no_architecture_columns(tmp_path):
    zip_path, _receipt_path = builder.build_packet(tmp_path)
    with zipfile.ZipFile(zip_path) as archive:
        for name in (
            "data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
            "data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        ):
            rows = list(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8"))))
            assert rows
            assert "architecture_mode" not in rows[0]
            assert "structural_module_division" not in rows[0]
            assert set(row["predictor"] for row in rows) == {
                "module_substrate",
                "conflict_timing_geometry",
                "conflict_spatial_geometry",
            }


def test_predictor_adjudication_packet_is_byte_deterministic(tmp_path):
    first = builder.build_packet(tmp_path / "first")[0].read_bytes()
    second = builder.build_packet(tmp_path / "second")[0].read_bytes()
    assert first == second

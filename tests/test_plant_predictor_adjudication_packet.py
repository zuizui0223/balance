import csv
import hashlib
import importlib
import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

from balance_domain.plant_predictor_expansion import (
    FIELDS as EXPANSION_FIELDS,
    load_expansion_coding,
)


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
builder = importlib.import_module("build_plant_predictor_adjudication_packet")




def _write_rows(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _freeze_script():
    path = ROOT / "scripts" / "freeze_plant_u2_predictor_receipts_v2.py"
    spec = importlib.util.spec_from_file_location(
        "freeze_plant_u2_predictor_receipts_v2_packet_test",
        path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _v2_freeze_workspace(tmp_path):
    template = ROOT / "data" / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"
    rows = load_expansion_coding(template)
    target_group = rows[0]["cluster_id"]
    values = {
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
    }
    for row in rows:
        if row["cluster_id"] == target_group:
            row.update({
                "coding_status": "CODED",
                "reported_value": values[row["predictor"]],
                "evidence_type": "INTEGRATED_STATE_DESCRIPTION",
                "outcome_independence": "TRUE",
                "notes": "synthetic source-side evidence",
            })
        else:
            row.update({
                "coding_status": "EVIDENCE_CEILING",
                "notes": "synthetic evidence ceiling",
            })

    returned = tmp_path / "expansion_return.csv"
    _write_rows(returned, EXPANSION_FIELDS, rows)
    freeze_dir = tmp_path / "v2_freeze"
    _freeze_script().freeze_v2(coding_return=returned, out_dir=freeze_dir)
    return freeze_dir

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





def test_predictor_v1_packet_preserves_executed_handoff_sha256(tmp_path):
    zip_path, receipt_path = builder.build_packet(tmp_path / "legacy_v1")
    execution = json.loads(
        (ROOT / "data" / "BALANCE_PLANT_HUMAN_HANDOFF_EXECUTION_V1.json").read_text(
            encoding="utf-8"
        )
    )
    frozen = execution["predictor_receipt_adjudication"]
    assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == frozen["packet_sha256"]
    assert hashlib.sha256(receipt_path.read_bytes()).hexdigest() == frozen["receipt_sha256"]

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert "u2_predictor_receipt_version" not in receipt
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        assert "docs/BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V1.md" in names
        assert "docs/BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V2.md" not in names


def test_predictor_adjudication_packet_can_use_hash_bound_u2_v2(tmp_path):
    freeze_dir = _v2_freeze_workspace(tmp_path)
    zip_path, receipt_path = builder.build_packet(
        tmp_path / "packet_v2",
        u2_v2_freeze_dir=freeze_dir,
    )
    assert zip_path.name == (
        "BALANCE_PLANT_PREDICTOR_ADJUDICATION_PACKET_U2V2_V1.zip"
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["u2_predictor_receipt_version"] == "V2"
    assert receipt["u2_v2_freeze_receipt_included"] is True
    assert (
        receipt["u2_v2_n_groups_with_three_resolved_independent_predictors"]
        == 9
    )

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        assert (
            "data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv"
            in names
        )
        assert (
            "provenance/BALANCE_PLANT_U2_PREDICTOR_RECEIPT_FREEZE_V2.json"
            in names
        )
        assert (
            "data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
            not in names
        )
        assert (
            "data/BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
            in names
        )
        assert (
            "docs/BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V2.md"
            in names
        )
        assert (
            "docs/BALANCE_PLANT_PREDICTOR_RECEIPT_ADJUDICATION_PROTOCOL_V1.md"
            not in names
        )

        u2_rows = list(csv.DictReader(io.StringIO(
            archive.read(
                "data/BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V2.csv"
            ).decode("utf-8")
        )))
        assert len(u2_rows) == 60
        assert "architecture_mode" not in u2_rows[0]
        assert {row["adjudication_status"] for row in u2_rows} == {"SCREENED"}


def test_predictor_adjudication_v2_packet_is_byte_deterministic(tmp_path):
    freeze_dir = _v2_freeze_workspace(tmp_path)
    first = builder.build_packet(
        tmp_path / "first_v2",
        u2_v2_freeze_dir=freeze_dir,
    )[0].read_bytes()
    second = builder.build_packet(
        tmp_path / "second_v2",
        u2_v2_freeze_dir=freeze_dir,
    )[0].read_bytes()
    assert first == second


def test_predictor_adjudication_v2_packet_rejects_tampered_frozen_frame(tmp_path):
    freeze_dir = _v2_freeze_workspace(tmp_path)
    frame = freeze_dir / builder.U2_V2_BASENAME
    frame.write_bytes(frame.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="frozen frame SHA256 mismatch"):
        builder.build_packet(
            tmp_path / "bad_v2",
            u2_v2_freeze_dir=freeze_dir,
        )


def test_predictor_adjudication_v2_packet_receipt_hashes_freeze_receipt(tmp_path):
    freeze_dir = _v2_freeze_workspace(tmp_path)
    _zip, receipt_path = builder.build_packet(
        tmp_path / "packet_v2_hash",
        u2_v2_freeze_dir=freeze_dir,
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    freeze_receipt = freeze_dir / builder.U2_V2_FREEZE_RECEIPT
    assert receipt["u2_v2_freeze_receipt_sha256"] == hashlib.sha256(
        freeze_receipt.read_bytes()
    ).hexdigest()

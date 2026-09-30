import csv
import json
import zipfile
from pathlib import Path

import pytest

from balance_domain.plant_architecture_adjudication import (
    ADJUDICATION_BASENAMES,
    build_architecture_adjudication_packet,
    write_architecture_adjudication_workspace,
)
from balance_domain.plant_human_return_intake import (
    CODER_RETURN_BASENAMES,
    write_human_return_intake,
)
from balance_domain.plant_macro_agreement import FIELDS
from balance_domain.plant_u6 import PASS2_FIELDS


ROOT = Path(__file__).resolve().parents[1]


def _read_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or ()), list(reader)


def _write_rows(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _build_architecture_returns(return_dir, *, lanes, u2_timing_disagreements=0):
    generic = {
        "U1": ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
        "U2": ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
    }
    for lane in ("U1", "U2"):
        if lane not in lanes:
            continue
        fields, rows = _read_rows(generic[lane])
        assert tuple(fields) == FIELDS
        for coder in ("CODER_A", "CODER_B"):
            selected = []
            coder_rows = [row for row in rows if row["coder_id"] == coder]
            for index, row in enumerate(coder_rows):
                clean = dict(row)
                clean.update({
                    "conflict_status": "NO_DEMONSTRATED_CONFLICT",
                    "architecture_mode": "SHARED_INTEGRATED",
                    "module_substrate": "SINGLE_OR_CONTINUOUS",
                    "conflict_timing_geometry": "SIMULTANEOUS",
                    "conflict_spatial_geometry": "SAME_UNIT",
                    "notes": "synthetic completed return",
                })
                if (
                    lane == "U2"
                    and coder == "CODER_B"
                    and index < u2_timing_disagreements
                ):
                    clean["conflict_timing_geometry"] = "SEQUENTIAL_WITHIN_UNIT"
                selected.append(clean)
            _write_rows(
                return_dir / CODER_RETURN_BASENAMES[(lane, coder)],
                fields,
                selected,
            )

    if "U6" in lanes:
        source = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"
        fields, rows = _read_rows(source)
        assert tuple(fields) == PASS2_FIELDS
        for coder in ("CODER_A", "CODER_B"):
            selected = []
            for row in rows:
                if row["coder_id"] != coder:
                    continue
                clean = dict(row)
                clean.update({
                    "architecture_mode": "SHARED_INTEGRATED",
                    "module_substrate": "SINGLE_OR_CONTINUOUS",
                    "conflict_timing_geometry": "SIMULTANEOUS",
                    "conflict_spatial_geometry": "SAME_UNIT",
                    "coding_status": "CODED",
                    "notes": "synthetic completed return",
                })
                selected.append(clean)
            _write_rows(
                return_dir / CODER_RETURN_BASENAMES[("U6", coder)],
                fields,
                selected,
            )


def _intake(tmp_path, *, scope, u2_timing_disagreements=0):
    returns = tmp_path / f"{scope.lower()}_returns"
    if scope == "PRIMARY":
        lanes = ("U2", "U6")
    else:
        lanes = ("U1",)
    _build_architecture_returns(
        returns,
        lanes=lanes,
        u2_timing_disagreements=u2_timing_disagreements,
    )
    intake = tmp_path / f"{scope.lower()}_intake"
    write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=intake,
    )
    return intake


def _complete_adjudication_return(return_dir, lane, *, override=None):
    template = ROOT / "data" / ADJUDICATION_BASENAMES[lane]
    fields, rows = _read_rows(template)
    for row in rows:
        if lane in {"U1", "U2"}:
            row.update({
                "conflict_status": "NO_DEMONSTRATED_CONFLICT",
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "adjudication_status": "ADJUDICATED",
                "adjudication_basis": "CODER_CONSENSUS",
                "notes": "coder consensus retained",
            })
        else:
            row.update({
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "adjudication_status": "ADJUDICATED",
                "adjudication_basis": "CODER_CONSENSUS",
                "notes": "coder consensus retained",
            })
    if override is not None:
        field, value = override
        rows[0][field] = value
    _write_rows(return_dir / ADJUDICATION_BASENAMES[lane], fields, rows)


def test_primary_adjudication_packet_is_post_reliability_and_predictor_blind(tmp_path):
    intake = _intake(tmp_path, scope="PRIMARY")
    out = tmp_path / "packet"
    result = build_architecture_adjudication_packet(
        root=ROOT,
        intake_dir=intake,
        scope="PRIMARY",
        out_dir=out,
    )

    with zipfile.ZipFile(result["packet"]) as archive:
        names = set(archive.namelist())
        assert archive.testzip() is None
        assert any("U2_DOUBLE_CODE_SOURCE_PACKET" in name for name in names)
        assert any("U6_PASS2_FROZEN_SOURCE_PACKET" in name for name in names)
        assert any("U2_AGREEMENT_REPORT" in name for name in names)
        assert any("U6_DISAGREEMENTS" in name for name in names)
        assert not any("PREDICTOR" in name.upper() for name in names)
        assert not any("REACTIVATION" in name.upper() for name in names)

    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))
    assert receipt["scope"] == "PRIMARY"
    assert receipt["lanes"] == ["U2", "U6"]
    assert receipt["predictor_review_outputs_included"] is False


def test_primary_packet_is_forbidden_when_reliability_fails(tmp_path):
    intake = _intake(
        tmp_path,
        scope="PRIMARY",
        u2_timing_disagreements=5,
    )
    with pytest.raises(ValueError, match="reliability PASS"):
        build_architecture_adjudication_packet(
            root=ROOT,
            intake_dir=intake,
            scope="PRIMARY",
            out_dir=tmp_path / "packet",
        )


def test_primary_adjudication_return_builds_immutable_validated_workspace(tmp_path):
    intake = _intake(tmp_path, scope="PRIMARY")
    returns = tmp_path / "adjudication_returns"
    returns.mkdir()
    _complete_adjudication_return(returns, "U2")
    _complete_adjudication_return(returns, "U6")

    workspace = tmp_path / "adjudicated"
    result = write_architecture_adjudication_workspace(
        root=ROOT,
        intake_dir=intake,
        return_dir=returns,
        scope="PRIMARY",
        out_dir=workspace,
    )
    assert result["complete"] is True
    assert result["lanes"] == ["U2", "U6"]
    assert (workspace / ADJUDICATION_BASENAMES["U2"]).exists()
    assert (workspace / ADJUDICATION_BASENAMES["U6"]).exists()
    assert (workspace / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv").exists()
    assert (workspace / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv").exists()

    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))
    assert receipt["primary_model_gate_closed"] is True
    assert receipt["external_validation_gate_closed"] is False

    with pytest.raises(ValueError, match="output directory already exists"):
        write_architecture_adjudication_workspace(
            root=ROOT,
            intake_dir=intake,
            return_dir=returns,
            scope="PRIMARY",
            out_dir=workspace,
        )


def test_adjudication_return_cannot_override_coder_consensus(tmp_path):
    intake = _intake(tmp_path, scope="PRIMARY")
    returns = tmp_path / "adjudication_returns"
    returns.mkdir()
    _complete_adjudication_return(
        returns,
        "U2",
        override=("architecture_mode", "TEMPORAL_SEPARATION"),
    )
    _complete_adjudication_return(returns, "U6")

    with pytest.raises(ValueError, match="cannot override coder consensus"):
        write_architecture_adjudication_workspace(
            root=ROOT,
            intake_dir=intake,
            return_dir=returns,
            scope="PRIMARY",
            out_dir=tmp_path / "adjudicated",
        )


def test_external_u1_adjudication_is_independent_of_primary(tmp_path):
    intake = _intake(tmp_path, scope="EXTERNAL")
    packet = build_architecture_adjudication_packet(
        root=ROOT,
        intake_dir=intake,
        scope="EXTERNAL",
        out_dir=tmp_path / "packet",
    )
    assert packet["lanes"] == ["U1"]

    returns = tmp_path / "adjudication_returns"
    returns.mkdir()
    _complete_adjudication_return(returns, "U1")
    result = write_architecture_adjudication_workspace(
        root=ROOT,
        intake_dir=intake,
        return_dir=returns,
        scope="EXTERNAL",
        out_dir=tmp_path / "adjudicated",
    )
    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))
    assert receipt["external_validation_gate_closed"] is True
    assert receipt["primary_model_gate_closed"] is False

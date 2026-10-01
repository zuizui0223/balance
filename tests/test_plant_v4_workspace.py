import csv
import hashlib
import json
from pathlib import Path

import pytest

from balance_domain.plant_architecture_adjudication import (
    ADJUDICATION_BASENAMES,
    write_architecture_adjudication_workspace,
)
from balance_domain.plant_human_return_intake import (
    CODER_RETURN_BASENAMES,
    PREDICTOR_RETURN_BASENAMES,
    write_human_return_intake,
)
from balance_domain.plant_macro_agreement import FIELDS
from balance_domain.plant_u6 import PASS2_FIELDS
from balance_domain.plant_v4_workspace import compose_v4_human_input_workspace


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


def _primary_coder_returns(path):
    source = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv"
    fields, rows = _read_rows(source)
    assert tuple(fields) == FIELDS
    for coder in ("CODER_A", "CODER_B"):
        selected = []
        for row in rows:
            if row["coder_id"] != coder:
                continue
            clean = dict(row)
            clean.update({
                "conflict_status": "NO_DEMONSTRATED_CONFLICT",
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "notes": "synthetic primary return",
            })
            selected.append(clean)
        _write_rows(
            path / CODER_RETURN_BASENAMES[("U2", coder)],
            fields,
            selected,
        )

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
                "notes": "synthetic primary return",
            })
            selected.append(clean)
        _write_rows(
            path / CODER_RETURN_BASENAMES[("U6", coder)],
            fields,
            selected,
        )


def _complete_primary_adjudication(path):
    for lane in ("U2", "U6"):
        template = ROOT / "data" / ADJUDICATION_BASENAMES[lane]
        fields, rows = _read_rows(template)
        for row in rows:
            if lane == "U2":
                row.update({
                    "conflict_status": "NO_DEMONSTRATED_CONFLICT",
                    "architecture_mode": "SHARED_INTEGRATED",
                    "module_substrate": "SINGLE_OR_CONTINUOUS",
                    "conflict_timing_geometry": "SIMULTANEOUS",
                    "conflict_spatial_geometry": "SAME_UNIT",
                    "adjudication_status": "ADJUDICATED",
                    "adjudication_basis": "CODER_CONSENSUS",
                    "notes": "consensus retained",
                })
            else:
                row.update({
                    "architecture_mode": "SHARED_INTEGRATED",
                    "module_substrate": "SINGLE_OR_CONTINUOUS",
                    "conflict_timing_geometry": "SIMULTANEOUS",
                    "conflict_spatial_geometry": "SAME_UNIT",
                    "adjudication_status": "ADJUDICATED",
                    "adjudication_basis": "CODER_CONSENSUS",
                    "notes": "consensus retained",
                })
        _write_rows(path / ADJUDICATION_BASENAMES[lane], fields, rows)


def _predictor_returns(path, *, reject_one_u2=False):
    for lane in ("U2", "U6"):
        source = ROOT / "data" / PREDICTOR_RETURN_BASENAMES[lane]
        fields, rows = _read_rows(source)
        rejected = False
        for row in rows:
            if (
                row["reported_value"] != "UNRESOLVED"
                and row["outcome_independence"] == "TRUE"
            ):
                if lane == "U2" and reject_one_u2 and not rejected:
                    row["adjudication_status"] = "REJECTED"
                    rejected = True
                else:
                    row["adjudication_status"] = "ADJUDICATED"
            else:
                row["adjudication_status"] = "REJECTED"
        _write_rows(path / PREDICTOR_RETURN_BASENAMES[lane], fields, rows)


def _build_primary_adjudication_workspace(tmp_path):
    returns = tmp_path / "primary_returns"
    _primary_coder_returns(returns)
    intake = tmp_path / "primary_intake"
    write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=intake,
    )

    adjudication_returns = tmp_path / "primary_adjudication_returns"
    adjudication_returns.mkdir()
    _complete_primary_adjudication(adjudication_returns)
    adjudicated = tmp_path / "primary_adjudicated"
    write_architecture_adjudication_workspace(
        root=ROOT,
        intake_dir=intake,
        return_dir=adjudication_returns,
        scope="PRIMARY",
        out_dir=adjudicated,
    )
    return adjudicated


def _build_predictor_workspace(tmp_path, *, reject_one_u2=False):
    returns = tmp_path / "predictor_returns"
    _predictor_returns(returns, reject_one_u2=reject_one_u2)
    intake = tmp_path / "predictor_intake"
    write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=intake,
    )
    return intake


def test_compositor_closes_primary_human_gates_across_separate_workspaces(tmp_path):
    primary = _build_primary_adjudication_workspace(tmp_path)
    predictor = _build_predictor_workspace(tmp_path)
    composed = tmp_path / "composed"

    result = compose_v4_human_input_workspace(
        root=ROOT,
        primary_adjudication_dir=primary,
        predictor_intake_dir=predictor,
        out_dir=composed,
    )
    assert result["primary_model_assembly_ready"] is True
    assert result["external_validation_included"] is False
    assert result["next_step"] == "BUILD_V4_ANALYSIS_INPUTS"

    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))
    assert receipt["primary_model_assembly_ready"] is True
    assert receipt["primary_human_open_gates"] == {
        "u2_independent_double_coding": False,
        "u2_post_coding_adjudication": False,
        "u6_independent_double_coding": False,
        "u6_post_coding_adjudication": False,
        "u2_predictor_independent_adjudication": False,
        "u6_predictor_independent_adjudication": False,
    }
    assert receipt["external_validation_included"] is False
    assert receipt["build_command"].endswith("--build")

    expected = {
        "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
        "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv",
        "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
        "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv",
        "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv",
        "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv",
    }
    assert expected <= set(receipt["files"])
    for basename, provenance in receipt["files"].items():
        path = composed / basename
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == provenance["composed_sha256"]
        assert provenance["source_sha256"] == provenance["composed_sha256"]


def test_compositor_rejects_incomplete_predictor_stage(tmp_path):
    primary = _build_primary_adjudication_workspace(tmp_path)
    predictor = _build_predictor_workspace(tmp_path, reject_one_u2=True)

    with pytest.raises(ValueError, match="predictor review is not COMPLETE"):
        compose_v4_human_input_workspace(
            root=ROOT,
            primary_adjudication_dir=primary,
            predictor_intake_dir=predictor,
            out_dir=tmp_path / "composed",
        )


def test_compositor_never_overwrites_existing_workspace(tmp_path):
    primary = _build_primary_adjudication_workspace(tmp_path)
    predictor = _build_predictor_workspace(tmp_path)
    composed = tmp_path / "composed"
    composed.mkdir()
    sentinel = composed / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(ValueError, match="output directory already exists"):
        compose_v4_human_input_workspace(
            root=ROOT,
            primary_adjudication_dir=primary,
            predictor_intake_dir=predictor,
            out_dir=composed,
        )
    assert sentinel.read_text(encoding="utf-8") == "preserve"



def test_compositor_rejects_primary_workspace_file_hash_drift(tmp_path):
    primary = _build_primary_adjudication_workspace(tmp_path)
    predictor = _build_predictor_workspace(tmp_path)

    receipt = json.loads(
        (primary / "BALANCE_PLANT_PRIMARY_ARCHITECTURE_ADJUDICATION_RECEIPT_V1.json")
        .read_text(encoding="utf-8")
    )
    u2_name = receipt["outputs"]["coding_ledgers"]["U2"]
    path = primary / u2_name
    path.write_bytes(path.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="output SHA256 mismatch"):
        compose_v4_human_input_workspace(
            root=ROOT,
            primary_adjudication_dir=primary,
            predictor_intake_dir=predictor,
            out_dir=tmp_path / "composed",
        )


def test_compositor_rejects_predictor_frame_hash_drift(tmp_path):
    primary = _build_primary_adjudication_workspace(tmp_path)
    predictor = _build_predictor_workspace(tmp_path)

    receipt = json.loads(
        (predictor / "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json")
        .read_text(encoding="utf-8")
    )
    u2_name = receipt["outputs"]["predictor_reviewed_frames"]["U2"]
    path = predictor / u2_name
    path.write_bytes(path.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="output SHA256 mismatch"):
        compose_v4_human_input_workspace(
            root=ROOT,
            primary_adjudication_dir=primary,
            predictor_intake_dir=predictor,
            out_dir=tmp_path / "composed",
        )


def test_compositor_revalidates_predictor_semantics_even_if_receipt_hash_is_forged(tmp_path):
    primary = _build_primary_adjudication_workspace(tmp_path)
    predictor = _build_predictor_workspace(tmp_path)

    receipt_path = predictor / "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    u2_name = receipt["outputs"]["predictor_reviewed_frames"]["U2"]
    path = predictor / u2_name
    fields, rows = _read_rows(path)
    rows[0]["source_id"] = "tampered-source"
    _write_rows(path, fields, rows)

    receipt["output_sha256"]["predictor_reviewed_frames"]["U2"] = (
        hashlib.sha256(path.read_bytes()).hexdigest()
    )
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="cannot modify frozen source_id"):
        compose_v4_human_input_workspace(
            root=ROOT,
            primary_adjudication_dir=primary,
            predictor_intake_dir=predictor,
            out_dir=tmp_path / "composed",
        )

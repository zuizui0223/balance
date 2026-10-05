import csv
import hashlib
import importlib.util
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
    U2_PREDICTOR_V2_BASENAME,
    U2_PREDICTOR_V2_FREEZE_RECEIPT,
    U2_PREDICTOR_V2_FROZEN_BASENAME,
    write_human_return_intake,
)
from balance_domain.plant_macro_agreement import FIELDS
from balance_domain.plant_predictor_expansion import (
    FIELDS as EXPANSION_FIELDS,
    load_expansion_coding,
)
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


def _load_freeze_v2_script():
    path = ROOT / "scripts" / "freeze_plant_u2_predictor_receipts_v2.py"
    spec = importlib.util.spec_from_file_location(
        "freeze_plant_u2_predictor_receipts_v2_workspace_test",
        path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_u2_v2_freeze_workspace(tmp_path):
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
                "notes": "synthetic source-side expansion evidence",
            })
        else:
            row.update({
                "coding_status": "EVIDENCE_CEILING",
                "notes": "synthetic source-side evidence ceiling",
            })

    returned = tmp_path / "u2_expansion_return.csv"
    _write_rows(returned, EXPANSION_FIELDS, rows)
    freeze_dir = tmp_path / "u2_v2_freeze"
    module = _load_freeze_v2_script()
    module.freeze_v2(coding_return=returned, out_dir=freeze_dir)
    return freeze_dir


def _build_predictor_workspace_v2(tmp_path):
    freeze_dir = _build_u2_v2_freeze_workspace(tmp_path)
    returns = tmp_path / "predictor_returns_v2"

    u2_source = freeze_dir / U2_PREDICTOR_V2_BASENAME
    fields, rows = _read_rows(u2_source)
    for row in rows:
        row["adjudication_status"] = (
            "ADJUDICATED"
            if row["reported_value"] != "UNRESOLVED"
            and row["outcome_independence"] == "TRUE"
            else "REJECTED"
        )
    _write_rows(returns / U2_PREDICTOR_V2_BASENAME, fields, rows)

    u6_source = ROOT / "data" / PREDICTOR_RETURN_BASENAMES["U6"]
    fields, rows = _read_rows(u6_source)
    for row in rows:
        row["adjudication_status"] = (
            "ADJUDICATED"
            if row["reported_value"] != "UNRESOLVED"
            and row["outcome_independence"] == "TRUE"
            else "REJECTED"
        )
    _write_rows(returns / PREDICTOR_RETURN_BASENAMES["U6"], fields, rows)

    intake = tmp_path / "predictor_intake_v2"
    write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=intake,
        u2_v2_freeze_dir=freeze_dir,
    )
    return intake


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



def test_compositor_preserves_v2_predictor_version_and_frozen_baseline(tmp_path):
    primary = _build_primary_adjudication_workspace(tmp_path)
    predictor = _build_predictor_workspace_v2(tmp_path)
    composed = tmp_path / "composed_v2"

    result = compose_v4_human_input_workspace(
        root=ROOT,
        primary_adjudication_dir=primary,
        predictor_intake_dir=predictor,
        out_dir=composed,
    )
    assert result["primary_model_assembly_ready"] is True

    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))
    assert receipt["u2_predictor_receipt_version"] == "V2"
    assert receipt["u2_predictor_reviewed_basename"] == U2_PREDICTOR_V2_BASENAME
    assert (
        receipt["u2_predictor_frozen_baseline_basename"]
        == U2_PREDICTOR_V2_FROZEN_BASENAME
    )
    assert (
        receipt["u2_predictor_freeze_receipt_basename"]
        == U2_PREDICTOR_V2_FREEZE_RECEIPT
    )

    expected = {
        U2_PREDICTOR_V2_BASENAME,
        U2_PREDICTOR_V2_FROZEN_BASENAME,
        U2_PREDICTOR_V2_FREEZE_RECEIPT,
        PREDICTOR_RETURN_BASENAMES["U6"],
    }
    assert expected <= set(receipt["files"])
    for basename in expected:
        path = composed / basename
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == (
            receipt["files"][basename]["composed_sha256"]
        )


def test_compositor_rejects_tampered_v2_frozen_baseline_even_with_intake_hash_forged(
    tmp_path,
):
    primary = _build_primary_adjudication_workspace(tmp_path)
    predictor = _build_predictor_workspace_v2(tmp_path)

    intake_receipt_path = predictor / "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json"
    intake_receipt = json.loads(intake_receipt_path.read_text(encoding="utf-8"))
    frozen_name = intake_receipt["outputs"]["predictor_frozen_frames"]["U2"]
    frozen = predictor / frozen_name
    frozen.write_bytes(frozen.read_bytes() + b"\n")
    intake_receipt["output_sha256"]["predictor_frozen_frames"]["U2"] = (
        hashlib.sha256(frozen.read_bytes()).hexdigest()
    )
    intake_receipt_path.write_text(
        json.dumps(intake_receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="frozen baseline SHA256 disagrees"):
        compose_v4_human_input_workspace(
            root=ROOT,
            primary_adjudication_dir=primary,
            predictor_intake_dir=predictor,
            out_dir=tmp_path / "composed_bad_v2",
        )

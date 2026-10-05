import csv
import importlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

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
from balance_domain.plant_predictor_expansion import (
    FIELDS as EXPANSION_FIELDS,
    load_expansion_coding,
)
from balance_domain.plant_v4_workspace import compose_v4_human_input_workspace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
analysis_cli = importlib.import_module("build_plant_v4_analysis_inputs")


ARCHITECTURE_CYCLE = (
    "SHARED_INTEGRATED",
    "TEMPORAL_SEPARATION",
    "WITHIN_FLOWER_DIVISION_OF_LABOUR",
    "POLYMORPHIC_OR_MOSAIC",
)


def _read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or ()), list(reader)


def _write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _predictor_values(lane):
    path = ROOT / "data" / PREDICTOR_RETURN_BASENAMES[lane]
    _fields, rows = _read(path)
    out = defaultdict(dict)
    for row in rows:
        if (
            row["reported_value"] != "UNRESOLVED"
            and row["outcome_independence"] == "TRUE"
        ):
            out[row["cluster_id"]][row["predictor"]] = row["reported_value"]
    return dict(out)


def _u2_conflict_status():
    _fields, rows = _read(
        ROOT / "data" / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
    )
    return {row["dependency_group"]: row["conflict_status"] for row in rows}


def _write_primary_architecture_returns(return_dir):
    u2_predictors = _predictor_values("U2")
    u6_predictors = _predictor_values("U6")
    u2_conflict = _u2_conflict_status()

    u2_positive = sorted(
        group for group, status in u2_conflict.items() if status == "POSITIVE"
    )
    assert len(u2_positive) == 8
    u2_mode = {
        group: ARCHITECTURE_CYCLE[i % len(ARCHITECTURE_CYCLE)]
        for i, group in enumerate(u2_positive)
    }

    u2_fields, u2_rows = _read(
        ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv"
    )
    for coder in ("CODER_A", "CODER_B"):
        selected = []
        for row in u2_rows:
            if row["coder_id"] != coder:
                continue
            group = row["cluster_id"]
            clean = dict(row)
            clean["conflict_status"] = u2_conflict[group]
            if group in u2_predictors:
                clean["architecture_mode"] = u2_mode[group]
                clean["module_substrate"] = u2_predictors[group]["module_substrate"]
                clean["conflict_timing_geometry"] = u2_predictors[group][
                    "conflict_timing_geometry"
                ]
                clean["conflict_spatial_geometry"] = u2_predictors[group][
                    "conflict_spatial_geometry"
                ]
            else:
                clean["architecture_mode"] = "UNRESOLVED"
                clean["module_substrate"] = "UNRESOLVED"
                clean["conflict_timing_geometry"] = "UNRESOLVED"
                clean["conflict_spatial_geometry"] = "UNRESOLVED"
            clean["notes"] = "synthetic end-to-end fixture"
            selected.append(clean)
        _write(
            return_dir / CODER_RETURN_BASENAMES[("U2", coder)],
            u2_fields,
            selected,
        )

    u6_fields, u6_rows = _read(
        ROOT / "data" / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"
    )
    u6_groups = sorted(u6_predictors)
    assert len(u6_groups) == 21
    u6_mode = {
        group: ARCHITECTURE_CYCLE[i % len(ARCHITECTURE_CYCLE)]
        for i, group in enumerate(u6_groups)
    }
    for coder in ("CODER_A", "CODER_B"):
        selected = []
        for row in u6_rows:
            if row["coder_id"] != coder:
                continue
            group = row["dependency_group"]
            clean = dict(row)
            clean["architecture_mode"] = u6_mode[group]
            clean["module_substrate"] = u6_predictors[group]["module_substrate"]
            clean["conflict_timing_geometry"] = u6_predictors[group][
                "conflict_timing_geometry"
            ]
            clean["conflict_spatial_geometry"] = u6_predictors[group][
                "conflict_spatial_geometry"
            ]
            clean["coding_status"] = "CODED"
            clean["notes"] = "synthetic end-to-end fixture"
            selected.append(clean)
        _write(
            return_dir / CODER_RETURN_BASENAMES[("U6", coder)],
            u6_fields,
            selected,
        )

    return {
        "U2": {
            group: {
                "conflict_status": u2_conflict[group],
                "architecture_mode": (
                    u2_mode[group] if group in u2_mode else "UNRESOLVED"
                ),
                "module_substrate": (
                    u2_predictors[group]["module_substrate"]
                    if group in u2_predictors
                    else "UNRESOLVED"
                ),
                "conflict_timing_geometry": (
                    u2_predictors[group]["conflict_timing_geometry"]
                    if group in u2_predictors
                    else "UNRESOLVED"
                ),
                "conflict_spatial_geometry": (
                    u2_predictors[group]["conflict_spatial_geometry"]
                    if group in u2_predictors
                    else "UNRESOLVED"
                ),
            }
            for group in u2_conflict
        },
        "U6": {
            group: {
                "architecture_mode": u6_mode[group],
                "module_substrate": u6_predictors[group]["module_substrate"],
                "conflict_timing_geometry": u6_predictors[group][
                    "conflict_timing_geometry"
                ],
                "conflict_spatial_geometry": u6_predictors[group][
                    "conflict_spatial_geometry"
                ],
            }
            for group in u6_groups
        },
    }


def _write_predictor_returns(return_dir):
    for lane in ("U2", "U6"):
        path = ROOT / "data" / PREDICTOR_RETURN_BASENAMES[lane]
        fields, rows = _read(path)
        for row in rows:
            if (
                row["reported_value"] != "UNRESOLVED"
                and row["outcome_independence"] == "TRUE"
            ):
                row["adjudication_status"] = "ADJUDICATED"
            else:
                row["adjudication_status"] = "REJECTED"
        _write(return_dir / PREDICTOR_RETURN_BASENAMES[lane], fields, rows)


def _write_primary_adjudication_returns(return_dir, frozen_values):
    for lane, template_name in ADJUDICATION_BASENAMES.items():
        if lane not in {"U2", "U6"}:
            continue
        fields, rows = _read(ROOT / "data" / template_name)
        key = "cluster_id" if lane == "U2" else "dependency_group"
        for row in rows:
            values = frozen_values[lane][row[key]]
            for field, value in values.items():
                row[field] = value
            row["adjudication_status"] = "ADJUDICATED"
            row["adjudication_basis"] = "CODER_CONSENSUS"
            row["notes"] = "synthetic consensus fixture"
        _write(return_dir / template_name, fields, rows)


def test_synthetic_human_returns_reach_real_v4_analysis_bundle(tmp_path):
    returns = tmp_path / "returns"
    frozen_values = _write_primary_architecture_returns(returns)
    _write_predictor_returns(returns)

    intake = tmp_path / "intake"
    intake_result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=intake,
    )
    assert intake_result["primary_return_status"] == "RELIABILITY_PASS"
    assert intake_result["predictor_return_status"] == "COMPLETE"
    assert intake_result["external_validation_return_status"] == "PENDING"

    adjudication_returns = tmp_path / "architecture_adjudication_returns"
    _write_primary_adjudication_returns(adjudication_returns, frozen_values)

    adjudicated = tmp_path / "primary_adjudication"
    write_architecture_adjudication_workspace(
        root=ROOT,
        intake_dir=intake,
        return_dir=adjudication_returns,
        scope="PRIMARY",
        out_dir=adjudicated,
    )

    composed = tmp_path / "composed"
    composed_result = compose_v4_human_input_workspace(
        root=ROOT,
        primary_adjudication_dir=adjudicated,
        predictor_intake_dir=intake,
        out_dir=composed,
    )
    assert composed_result["primary_model_assembly_ready"] is True
    assert composed_result["external_validation_included"] is False

    composed_receipt = json.loads(
        (composed / analysis_cli.COMPOSED_WORKSPACE_RECEIPT).read_text(
            encoding="utf-8"
        )
    )
    assert set(composed_receipt["files"]) == set(
        analysis_cli.PRIMARY_MUTABLE_BASENAMES
    )

    analysis = tmp_path / "analysis"
    result = analysis_cli.build_outputs(
        analysis,
        input_dir=composed,
    )

    assembly_path = Path(result["assembly"])
    assert assembly_path.is_file()
    _fields, assembly = _read(assembly_path)
    assert len(assembly) == 29
    assert {row["universe_id"] for row in assembly} == {
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    }

    main_input = json.loads(
        Path(result["main_stan_input"]).read_text(encoding="utf-8")
    )
    prior_input = json.loads(
        Path(result["prior_sensitivity_stan_input"]).read_text(encoding="utf-8")
    )
    assert main_input["stan_data"]["N"] == 29
    assert main_input["stan_data"]["slope_prior_sd"] == 0.75
    assert prior_input["stan_data"]["slope_prior_sd"] == 1.5
    assert main_input["stan_data"]["X"] == prior_input["stan_data"]["X"]
    assert main_input["stan_data"]["y"] == prior_input["stan_data"]["y"]

    assert result["temporal_generality_status"] == "NOT_READY"
    assert result["temporal_generality_input"] is None
    assert result["temporal_generality_prior_sensitivity_input"] is None

    receipt = json.loads(
        Path(result["analysis_inputs_receipt"]).read_text(encoding="utf-8")
    )
    assert receipt["primary_fit_ready"] is True
    assert receipt["temporal_generality_status"] == "NOT_READY"
    assert receipt["source_human_workspace_receipt_copied"] is True


def _freeze_v2_module():
    path = ROOT / "scripts" / "freeze_plant_u2_predictor_receipts_v2.py"
    spec = importlib.util.spec_from_file_location(
        "freeze_plant_u2_predictor_receipts_v2_end_to_end_test",
        path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_full_u2_v2_freeze(tmp_path):
    template = ROOT / "data" / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"
    rows = load_expansion_coding(template)
    values = {
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
    }
    for row in rows:
        row.update({
            "coding_status": "CODED",
            "reported_value": values[row["predictor"]],
            "evidence_type": "INTEGRATED_STATE_DESCRIPTION",
            "outcome_independence": "TRUE",
            "notes": "synthetic V2 end-to-end source-side evidence",
        })

    returned = tmp_path / "u2_predictor_expansion_return_v2.csv"
    _write(returned, EXPANSION_FIELDS, rows)
    freeze_dir = tmp_path / "u2_predictor_v2_freeze"
    result = _freeze_v2_module().freeze_v2(
        coding_return=returned,
        out_dir=freeze_dir,
    )
    assert result["n_groups_with_three_resolved_independent_predictors"] == 20
    return freeze_dir


def _write_predictor_returns_v2(return_dir, freeze_dir):
    u2_source = freeze_dir / U2_PREDICTOR_V2_BASENAME
    fields, rows = _read(u2_source)
    assert len(rows) == 60
    for row in rows:
        row["adjudication_status"] = (
            "ADJUDICATED"
            if row["reported_value"] != "UNRESOLVED"
            and row["outcome_independence"] == "TRUE"
            else "REJECTED"
        )
    _write(return_dir / U2_PREDICTOR_V2_BASENAME, fields, rows)

    u6_source = ROOT / "data" / PREDICTOR_RETURN_BASENAMES["U6"]
    fields, rows = _read(u6_source)
    for row in rows:
        row["adjudication_status"] = (
            "ADJUDICATED"
            if row["reported_value"] != "UNRESOLVED"
            and row["outcome_independence"] == "TRUE"
            else "REJECTED"
        )
    _write(return_dir / PREDICTOR_RETURN_BASENAMES["U6"], fields, rows)


def test_synthetic_u2_v2_human_returns_reach_real_v4_analysis_bundle(tmp_path):
    returns = tmp_path / "returns_v2"
    frozen_values = _write_primary_architecture_returns(returns)
    freeze_dir = _build_full_u2_v2_freeze(tmp_path)
    _write_predictor_returns_v2(returns, freeze_dir)

    intake = tmp_path / "intake_v2"
    intake_result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=intake,
        u2_v2_freeze_dir=freeze_dir,
    )
    assert intake_result["primary_return_status"] == "RELIABILITY_PASS"
    assert intake_result["predictor_return_status"] == "COMPLETE"

    intake_receipt = json.loads(
        (intake / "BALANCE_PLANT_HUMAN_RETURN_INTAKE_RECEIPT_V1.json").read_text(
            encoding="utf-8"
        )
    )
    assert intake_receipt["u2_predictor_receipt_version"] == "V2"
    assert intake_receipt["outputs"]["predictor_reviewed_frames"]["U2"] == (
        U2_PREDICTOR_V2_BASENAME
    )
    assert intake_receipt["outputs"]["predictor_frozen_frames"]["U2"] == (
        U2_PREDICTOR_V2_FROZEN_BASENAME
    )
    assert intake_receipt["outputs"]["predictor_freeze_receipts"]["U2"] == (
        U2_PREDICTOR_V2_FREEZE_RECEIPT
    )

    adjudication_returns = tmp_path / "architecture_adjudication_returns_v2"
    _write_primary_adjudication_returns(adjudication_returns, frozen_values)
    adjudicated = tmp_path / "primary_adjudication_v2"
    write_architecture_adjudication_workspace(
        root=ROOT,
        intake_dir=intake,
        return_dir=adjudication_returns,
        scope="PRIMARY",
        out_dir=adjudicated,
    )

    composed = tmp_path / "composed_v2"
    composed_result = compose_v4_human_input_workspace(
        root=ROOT,
        primary_adjudication_dir=adjudicated,
        predictor_intake_dir=intake,
        out_dir=composed,
    )
    assert composed_result["primary_model_assembly_ready"] is True

    composed_receipt = json.loads(
        (composed / analysis_cli.COMPOSED_WORKSPACE_RECEIPT).read_text(
            encoding="utf-8"
        )
    )
    assert composed_receipt["u2_predictor_receipt_version"] == "V2"
    expected = set(analysis_cli.PRIMARY_COMMON_BASENAMES) | set(
        analysis_cli.U2_V2_PROVENANCE_BASENAMES
    )
    assert set(composed_receipt["files"]) == expected
    assert U2_PREDICTOR_V2_BASENAME in composed_receipt["files"]
    assert U2_PREDICTOR_V2_FROZEN_BASENAME in composed_receipt["files"]
    assert U2_PREDICTOR_V2_FREEZE_RECEIPT in composed_receipt["files"]
    assert PREDICTOR_RETURN_BASENAMES["U2"] not in composed_receipt["files"]

    analysis = tmp_path / "analysis_v2"
    result = analysis_cli.build_outputs(analysis, input_dir=composed)

    _fields, assembly = _read(Path(result["assembly"]))
    assert len(assembly) == 29
    assert {row["universe_id"] for row in assembly} == {
        "U2_BARRETT_2002",
        "U6_POLLEN_THEFT_HARGREAVES_2009",
    }

    receipt = json.loads(
        Path(result["analysis_inputs_receipt"]).read_text(encoding="utf-8")
    )
    assert receipt["u2_predictor_receipt_version"] == "V2"
    assert receipt["u2_predictor_reviewed_basename"] == U2_PREDICTOR_V2_BASENAME
    assert receipt["u2_predictor_frozen_baseline_basename"] == (
        U2_PREDICTOR_V2_FROZEN_BASENAME
    )
    assert receipt["u2_predictor_freeze_receipt_basename"] == (
        U2_PREDICTOR_V2_FREEZE_RECEIPT
    )
    assert receipt["u2_predictor_reviewed_sha256"] == hashlib.sha256(
        (composed / U2_PREDICTOR_V2_BASENAME).read_bytes()
    ).hexdigest()
    assert receipt["u2_predictor_frozen_baseline_sha256"] == hashlib.sha256(
        (composed / U2_PREDICTOR_V2_FROZEN_BASENAME).read_bytes()
    ).hexdigest()
    assert receipt["u2_predictor_freeze_receipt_sha256"] == hashlib.sha256(
        (composed / U2_PREDICTOR_V2_FREEZE_RECEIPT).read_bytes()
    ).hexdigest()

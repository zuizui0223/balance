import csv
import importlib
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
    write_human_return_intake,
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

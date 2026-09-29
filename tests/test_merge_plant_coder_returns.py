import csv
import importlib
import json
import sys
from pathlib import Path

from balance_domain.plant_macro_agreement import FIELDS


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
merge_cli = importlib.import_module("merge_plant_coder_returns")
analysis_cli = importlib.import_module("build_plant_v4_analysis_inputs")

U2_SAMPLE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"


def _groups():
    with U2_SAMPLE.open(encoding="utf-8", newline="") as handle:
        return [row["dependency_group"] for row in csv.DictReader(handle)]


def _write_return(path, coder_id):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for i, group in enumerate(_groups()):
            writer.writerow({
                "cluster_id": group,
                "coder_id": coder_id,
                "conflict_status": (
                    "POSITIVE" if i < 8 else "NO_DEMONSTRATED_CONFLICT"
                ),
                "architecture_mode": (
                    "SHARED_INTEGRATED" if i % 2 == 0 else "TEMPORAL_SEPARATION"
                ),
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "notes": "",
            })


def test_u2_return_merge_is_immediately_usable_as_analysis_workspace_override(tmp_path):
    a = tmp_path / "coder_a.csv"
    b = tmp_path / "coder_b.csv"
    workspace = tmp_path / "workspace"
    _write_return(a, "CODER_A")
    _write_return(b, "CODER_B")

    out = merge_cli.merge_lane(
        lane="U2",
        coder_a=a,
        coder_b=b,
        out_dir=workspace,
    )

    merged = Path(out["merged"])
    receipt = json.loads(Path(out["receipt"]).read_text(encoding="utf-8"))
    assert merged.name == "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv"
    assert receipt["workspace_override_basename"] == merged.name
    assert receipt["n_rows"] == 40
    assert receipt["n_dependency_groups"] == 20

    resolved_paths = analysis_cli._paths(workspace)
    assert resolved_paths["u2_worksheet"] == merged

    readiness = analysis_cli.current_readiness(input_dir=workspace)
    assert readiness["primary_human_open_gates"]["u2_independent_double_coding"] is False
    assert readiness["primary_human_open_gates"]["u2_post_coding_adjudication"] is True
    assert readiness["primary_model_assembly_ready"] is False

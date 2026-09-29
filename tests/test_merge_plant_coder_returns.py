import csv
import importlib
import json
import sys
from pathlib import Path

from balance_domain.plant_macro_agreement import FIELDS, load_double_coding


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
merge_cli = importlib.import_module("merge_plant_coder_returns")

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


def test_u2_return_merge_is_canonical_double_coding_ledger(tmp_path):
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

    loaded = load_double_coding(merged)
    assert len(loaded) == 40
    assert {row["coder_id"] for row in loaded} == {"CODER_A", "CODER_B"}
    assert len({row["cluster_id"] for row in loaded}) == 20

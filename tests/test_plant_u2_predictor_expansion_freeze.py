import csv
import importlib.util
import json
from pathlib import Path

from balance_domain.plant_predictor_expansion import FIELDS, load_expansion_coding


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "freeze_plant_u2_predictor_receipts_v2.py"
TEMPLATE = ROOT / "data" / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "freeze_plant_u2_predictor_receipts_v2",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_return(path: Path):
    rows = load_expansion_coding(TEMPLATE)
    target = next(row for row in rows if row["predictor"] == "module_substrate")
    for row in rows:
        row["coding_status"] = "EVIDENCE_CEILING"
        row["notes"] = "no resolved outcome-independent source-side value"
    target.update({
        "coding_status": "CODED",
        "reported_value": "SINGLE_OR_CONTINUOUS",
        "evidence_type": "INTEGRATED_STATE_DESCRIPTION",
        "outcome_independence": "TRUE",
        "notes": "baseline source description supports one integrated substrate",
    })

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_freeze_cli_creates_screened_v2_surface_before_adjudication(tmp_path):
    module = _load_script()
    returned = tmp_path / "coding_return.csv"
    _write_return(returned)

    out = module.freeze_v2(
        coding_return=returned,
        out_dir=tmp_path / "frozen",
    )
    receipt = json.loads(Path(out["freeze_receipt"]).read_text(encoding="utf-8"))

    assert receipt["status"] == "FROZEN_SCREENED_AWAITING_INDEPENDENT_ADJUDICATION"
    assert receipt["n_receipts"] == 60
    assert receipt["n_resolved_receipts"] == 25
    assert receipt["adjudication_status"] == "SCREENED_ONLY"

    with Path(out["receipt_frame"]).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 60
    assert {row["adjudication_status"] for row in rows} == {"SCREENED"}
    updated = [
        row for row in rows
        if row["notes"].startswith("V2_PROSPECTIVE_EXPANSION_CODING:")
    ]
    assert len(updated) == 1
    assert updated[0]["reported_value"] == "SINGLE_OR_CONTINUOUS"
    assert updated[0]["outcome_independence"] == "TRUE"

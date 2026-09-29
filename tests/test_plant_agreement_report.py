import csv
from pathlib import Path

from balance_domain.plant_agreement_report import build_lane_agreement_report
from balance_domain.plant_macro_agreement import FIELDS


ROOT = Path(__file__).resolve().parents[1]
U2_SAMPLE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"


def _groups():
    with U2_SAMPLE.open(encoding="utf-8", newline="") as handle:
        return [row["dependency_group"] for row in csv.DictReader(handle)]


def _write_merged(path, *, disagreement_count=0):
    groups = _groups()
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for i, group in enumerate(groups):
            for coder in ("CODER_A", "CODER_B"):
                timing = "SIMULTANEOUS"
                if coder == "CODER_B" and i < disagreement_count:
                    timing = "SEQUENTIAL_WITHIN_UNIT"
                writer.writerow({
                    "cluster_id": group,
                    "coder_id": coder,
                    "conflict_status": "POSITIVE",
                    "architecture_mode": "SHARED_INTEGRATED",
                    "module_substrate": "SINGLE_OR_CONTINUOUS",
                    "conflict_timing_geometry": timing,
                    "conflict_spatial_geometry": "SAME_UNIT",
                    "notes": "",
                })


def test_u2_agreement_report_allows_adjudication_when_all_fields_pass(tmp_path):
    merged = tmp_path / "u2_merged.csv"
    _write_merged(merged, disagreement_count=0)
    out = build_lane_agreement_report(
        lane="U2",
        coding_path=merged,
        u2_sample_path=U2_SAMPLE,
    )
    assert out["n_dependency_groups"] == 20
    assert out["reliability_pass"] is True
    assert out["adjudication_allowed"] is True
    assert out["failed_fields"] == []
    assert out["next_step"] == "SOURCE_ADJUDICATION"
    assert all(
        stats["raw_agreement"] == 1.0
        for stats in out["fields"].values()
    )


def test_u2_agreement_report_triggers_repair_below_080_raw_agreement(tmp_path):
    merged = tmp_path / "u2_merged.csv"
    _write_merged(merged, disagreement_count=5)
    out = build_lane_agreement_report(
        lane="U2",
        coding_path=merged,
        u2_sample_path=U2_SAMPLE,
    )
    timing = out["fields"]["conflict_timing_geometry"]
    assert timing["raw_agreement"] == 0.75
    assert timing["codebook_repair_trigger"] is True
    assert timing["disagreement_groups"] == sorted(_groups()[:5])
    assert out["reliability_pass"] is False
    assert out["adjudication_allowed"] is False
    assert out["failed_fields"] == ["conflict_timing_geometry"]
    assert out["next_step"] == (
        "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS"
    )

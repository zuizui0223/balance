import csv
import json
import zipfile
from pathlib import Path

import pytest

from balance_domain.plant_architecture_adjudication import (
    ADJUDICATION_BASENAMES,
    build_architecture_adjudication_packets,
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


def _build_returns(return_dir, *, disagreements=None):
    disagreements = disagreements or {}
    generic_sources = {
        "U1": ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
        "U2": ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
    }
    for lane, source in generic_sources.items():
        fields, rows = _read_rows(source)
        assert tuple(fields) == FIELDS
        for coder in ("CODER_A", "CODER_B"):
            selected = []
            for index, row in enumerate(
                [row for row in rows if row["coder_id"] == coder]
            ):
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
                    coder == "CODER_B"
                    and index < disagreements.get(lane, 0)
                ):
                    clean["conflict_timing_geometry"] = "SEQUENTIAL_WITHIN_UNIT"
                selected.append(clean)
            _write_rows(
                return_dir / CODER_RETURN_BASENAMES[(lane, coder)],
                fields,
                selected,
            )

    source = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"
    fields, rows = _read_rows(source)
    assert tuple(fields) == PASS2_FIELDS
    for coder in ("CODER_A", "CODER_B"):
        selected = []
        for index, row in enumerate(
            [row for row in rows if row["coder_id"] == coder]
        ):
            clean = dict(row)
            clean.update({
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "coding_status": "CODED",
                "notes": "synthetic completed return",
            })
            if (
                coder == "CODER_B"
                and index < disagreements.get("U6", 0)
            ):
                clean["conflict_timing_geometry"] = "SEQUENTIAL_WITHIN_UNIT"
            selected.append(clean)
        _write_rows(
            return_dir / CODER_RETURN_BASENAMES[("U6", coder)],
            fields,
            selected,
        )


def _build_intake(tmp_path, *, disagreements=None):
    returns = tmp_path / "returns"
    intake = tmp_path / "intake"
    _build_returns(returns, disagreements=disagreements)
    result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=intake,
    )
    return intake, result


def _read_packet_worksheet(packet_path, lane):
    with zipfile.ZipFile(packet_path) as archive:
        name = next(
            item for item in archive.namelist()
            if item.endswith(ADJUDICATION_BASENAMES[lane])
        )
        text = archive.read(name).decode("utf-8")
    reader = csv.DictReader(text.splitlines())
    return list(reader)


def test_all_consensus_groups_are_mechanically_adjudicated_after_reliability_pass(tmp_path):
    intake, _ = _build_intake(tmp_path)
    out_dir = tmp_path / "packets"

    out = build_architecture_adjudication_packets(
        root=ROOT,
        intake_dir=intake,
        out_dir=out_dir,
    )

    assert out["primary_packets_ready"] is True
    expected = {"U1": 20, "U2": 20, "U6": 21}
    for lane, n_groups in expected.items():
        lane_out = out["lanes"][lane]
        assert lane_out["generated"] is True
        assert lane_out["n_consensus_autoadjudicated"] == n_groups
        assert lane_out["n_source_review_pending"] == 0
        assert lane_out["next_step"] == (
            "ARCHITECTURE_ADJUDICATION_COMPLETE_BY_CODER_CONSENSUS"
        )

        rows = _read_packet_worksheet(
            out_dir / lane_out["packet"],
            lane,
        )
        assert len(rows) == n_groups
        assert {row["adjudication_status"] for row in rows} == {"ADJUDICATED"}
        assert {row["adjudication_basis"] for row in rows} == {"CODER_CONSENSUS"}


def test_only_disagreement_groups_remain_pending_for_source_review(tmp_path):
    intake, _ = _build_intake(
        tmp_path,
        disagreements={"U1": 1, "U2": 2, "U6": 1},
    )
    out_dir = tmp_path / "packets"

    out = build_architecture_adjudication_packets(
        root=ROOT,
        intake_dir=intake,
        out_dir=out_dir,
    )

    expected = {
        "U1": (19, 1),
        "U2": (18, 2),
        "U6": (20, 1),
    }
    for lane, (n_consensus, n_pending) in expected.items():
        lane_out = out["lanes"][lane]
        assert lane_out["generated"] is True
        assert lane_out["n_consensus_autoadjudicated"] == n_consensus
        assert lane_out["n_source_review_pending"] == n_pending
        assert lane_out["next_step"] == "SOURCE_REVIEW_OF_DISAGREEMENTS"

        rows = _read_packet_worksheet(
            out_dir / lane_out["packet"],
            lane,
        )
        pending = [
            row for row in rows
            if row["adjudication_status"] == "PENDING"
        ]
        assert len(pending) == n_pending
        assert {
            row["adjudication_basis"] for row in pending
        } == {"AWAITING_SOURCE_REVIEW_OF_DISAGREEMENTS"}
        for row in pending:
            coded_fields = (
                [
                    "conflict_status",
                    "architecture_mode",
                    "module_substrate",
                    "conflict_timing_geometry",
                    "conflict_spatial_geometry",
                ]
                if lane in {"U1", "U2"}
                else [
                    "architecture_mode",
                    "module_substrate",
                    "conflict_timing_geometry",
                    "conflict_spatial_geometry",
                ]
            )
            assert all(row[field] == "UNRESOLVED" for field in coded_fields)


def test_low_agreement_lane_gets_no_adjudication_packet(tmp_path):
    intake, intake_result = _build_intake(
        tmp_path,
        disagreements={"U2": 5},
    )
    assert intake_result["primary_reliability_pass"] is False

    out_dir = tmp_path / "packets"
    out = build_architecture_adjudication_packets(
        root=ROOT,
        intake_dir=intake,
        out_dir=out_dir,
    )

    assert out["primary_packets_ready"] is False
    assert out["lanes"]["U2"]["generated"] is False
    assert out["lanes"]["U2"]["reason"] == (
        "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS"
    )
    assert out["lanes"]["U1"]["generated"] is True
    assert out["lanes"]["U6"]["generated"] is True


def test_tampered_stored_agreement_report_fails_before_packet_output(tmp_path):
    intake, _ = _build_intake(tmp_path)
    report = intake / "BALANCE_PLANT_U2_AGREEMENT_REPORT_V1.json"
    data = json.loads(report.read_text(encoding="utf-8"))
    data["reliability_pass"] = False
    report.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    out_dir = tmp_path / "packets"
    with pytest.raises(ValueError, match="no longer matches"):
        build_architecture_adjudication_packets(
            root=ROOT,
            intake_dir=intake,
            out_dir=out_dir,
        )

    assert not out_dir.exists()


def test_adjudication_packets_are_deterministic_for_same_intake(tmp_path):
    intake, _ = _build_intake(
        tmp_path,
        disagreements={"U2": 1},
    )
    first = tmp_path / "packets-1"
    second = tmp_path / "packets-2"

    one = build_architecture_adjudication_packets(
        root=ROOT,
        intake_dir=intake,
        out_dir=first,
    )
    two = build_architecture_adjudication_packets(
        root=ROOT,
        intake_dir=intake,
        out_dir=second,
    )

    for lane in ("U1", "U2", "U6"):
        assert one["lanes"][lane]["packet_sha256"] == (
            two["lanes"][lane]["packet_sha256"]
        )

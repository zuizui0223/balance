import csv
import hashlib
import json
from pathlib import Path

import pytest

from balance_domain.plant_human_return_intake import (
    CODER_RETURN_BASENAMES,
    PREDICTOR_RETURN_BASENAMES,
    required_return_paths,
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


def _build_coder_return_bundle(
    return_dir,
    *,
    u2_timing_disagreements=0,
    lanes=("U1", "U2", "U6"),
):
    generic_sources = {
        "U1": ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_WORKSHEET_V1.csv",
        "U2": ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv",
    }
    for lane, source in generic_sources.items():
        if lane not in lanes:
            continue
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


def _build_predictor_returns(return_dir, *, reject_one_u2=False):
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
        _write_rows(
            return_dir / PREDICTOR_RETURN_BASENAMES[lane],
            fields,
            rows,
        )


def _complete_bundle(return_dir, **kwargs):
    _build_coder_return_bundle(
        return_dir,
        u2_timing_disagreements=kwargs.get("u2_timing_disagreements", 0),
    )
    _build_predictor_returns(
        return_dir,
        reject_one_u2=kwargs.get("reject_one_u2", False),
    )


def test_canonical_return_paths_cover_three_independent_stages(tmp_path):
    paths = required_return_paths(tmp_path)
    assert set(paths) == {
        "U1_CODER_A",
        "U1_CODER_B",
        "U2_CODER_A",
        "U2_CODER_B",
        "U6_CODER_A",
        "U6_CODER_B",
        "U2_PREDICTOR",
        "U6_PREDICTOR",
    }
    assert len({path.name for path in paths.values()}) == 8


def test_complete_return_bundle_builds_one_intake_workspace(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _complete_bundle(returns)

    result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=out_dir,
    )

    assert result["primary_architecture_returns_received"] is True
    assert result["external_validation_returns_received"] is True
    assert result["predictor_returns_received"] is True
    assert result["primary_return_status"] == "RELIABILITY_PASS"
    assert result["external_validation_return_status"] == "RELIABILITY_PASS"
    assert result["primary_reliability_pass"] is True
    assert result["external_validation_reliability_pass"] is True
    assert result["predictor_primary_complete"] is True
    assert result["predictor_return_status"] == "COMPLETE"
    assert result["primary_architecture_next_step"] == "SOURCE_ADJUDICATION"
    assert result["external_validation_next_step"] == "SOURCE_ADJUDICATION"
    assert result["predictor_next_step"] == "PREDICTOR_ADJUDICATION_COMPLETE"
    assert result["ready_for_v4_assembly"] is False

    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))
    assert receipt["primary_reliability_pass"] is True
    assert receipt["predictor_adjudication"]["U2"][
        "n_clusters_with_three_adjudicated_receipts"
    ] == 8
    assert receipt["predictor_adjudication"]["U6"][
        "n_clusters_with_three_adjudicated_receipts"
    ] == 21
    assert receipt["agreement"]["U2"]["failed_fields"] == []
    assert receipt["agreement"]["U6"]["failed_fields"] == []
    assert (out_dir / receipt["outputs"]["merged_ledgers"]["U2"]).exists()
    assert (out_dir / receipt["outputs"]["agreement_reports"]["U6"]).exists()
    for family, mapping in receipt["outputs"].items():
        for lane, basename in mapping.items():
            path = out_dir / basename
            assert receipt["output_sha256"][family][lane] == (
                hashlib.sha256(path.read_bytes()).hexdigest()
            )
    for lane in ("U2", "U6"):
        reviewed = out_dir / receipt["outputs"]["predictor_reviewed_frames"][lane]
        assert reviewed.name == PREDICTOR_RETURN_BASENAMES[lane]
        assert reviewed.exists()
        assert reviewed.read_bytes() == (
            returns / PREDICTOR_RETURN_BASENAMES[lane]
        ).read_bytes()


def test_incomplete_bundle_fails_before_creating_output_directory(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _complete_bundle(returns)
    (returns / CODER_RETURN_BASENAMES[("U6", "CODER_B")]).unlink()

    with pytest.raises(ValueError, match="primary architecture return stage is incomplete"):
        write_human_return_intake(
            root=ROOT,
            return_dir=returns,
            out_dir=out_dir,
        )

    assert not out_dir.exists()


def test_low_primary_agreement_routes_to_same_group_independent_recode(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _complete_bundle(returns, u2_timing_disagreements=5)

    result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=out_dir,
    )
    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))

    assert result["primary_reliability_pass"] is False
    assert result["primary_architecture_next_step"] == (
        "CODEBOOK_REPAIR_AND_INDEPENDENT_RECODE_SAME_FROZEN_GROUPS"
    )
    assert receipt["agreement"]["U2"]["fields"][
        "conflict_timing_geometry"
    ]["raw_agreement"] == 0.75
    assert receipt["agreement"]["U2"]["failed_fields"] == [
        "conflict_timing_geometry"
    ]
    assert result["ready_for_v4_assembly"] is False


def test_rejected_primary_predictor_receipt_blocks_predictor_completion(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _complete_bundle(returns, reject_one_u2=True)

    result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=out_dir,
    )
    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))

    assert result["primary_reliability_pass"] is True
    assert result["predictor_primary_complete"] is False
    assert result["predictor_return_status"] == "INCOMPLETE"
    assert result["predictor_next_step"] == (
        "RESOLVE_REJECTED_OR_INCOMPLETE_PRIMARY_PREDICTOR_RECEIPTS"
    )
    assert receipt["predictor_adjudication"]["U2"]["n_rejected"] > 0
    assert receipt["predictor_adjudication"]["U2"][
        "n_clusters_with_three_adjudicated_receipts"
    ] == 7
    assert result["ready_for_v4_assembly"] is False



def test_primary_architecture_intake_does_not_wait_for_u1_or_predictor_review(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _build_coder_return_bundle(returns, lanes=("U2", "U6"))

    result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=out_dir,
    )
    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))

    assert result["primary_architecture_returns_received"] is True
    assert result["external_validation_returns_received"] is False
    assert result["predictor_returns_received"] is False
    assert result["primary_reliability_pass"] is True
    assert result["external_validation_reliability_pass"] is None
    assert result["external_validation_return_status"] == "PENDING"
    assert result["external_validation_next_step"] == (
        "AWAIT_U1_EXTERNAL_VALIDATION_RETURNS"
    )
    assert result["predictor_return_status"] == "PENDING"
    assert result["predictor_primary_complete"] is False
    assert result["predictor_next_step"] == "AWAIT_PREDICTOR_ADJUDICATION_RETURNS"
    assert set(receipt["outputs"]["merged_ledgers"]) == {"U2", "U6"}
    assert "U1" not in receipt["agreement"]
    assert receipt["outputs"]["predictor_readouts"] == {}
    assert result["ready_for_v4_assembly"] is False


def test_one_sided_predictor_return_fails_before_persistent_output(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _build_coder_return_bundle(returns)

    lane = "U2"
    source = ROOT / "data" / PREDICTOR_RETURN_BASENAMES[lane]
    fields, rows = _read_rows(source)
    for row in rows:
        row["adjudication_status"] = "REJECTED"
    _write_rows(
        returns / PREDICTOR_RETURN_BASENAMES[lane],
        fields,
        rows,
    )

    with pytest.raises(ValueError, match="predictor review return stage is incomplete"):
        write_human_return_intake(
            root=ROOT,
            return_dir=returns,
            out_dir=out_dir,
        )

    assert not out_dir.exists()



def test_existing_intake_workspace_is_never_overwritten(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _complete_bundle(returns)
    out_dir.mkdir()
    sentinel = out_dir / "sentinel.txt"
    sentinel.write_text("preserve me", encoding="utf-8")

    with pytest.raises(ValueError, match="output directory already exists"):
        write_human_return_intake(
            root=ROOT,
            return_dir=returns,
            out_dir=out_dir,
        )

    assert sentinel.read_text(encoding="utf-8") == "preserve me"



def test_machine_readable_intake_contract_matches_canonical_basenames():
    contract = json.loads(
        (ROOT / "data" / "BALANCE_PLANT_HUMAN_RETURN_INTAKE_CONTRACT_V1.json")
        .read_text(encoding="utf-8")
    )
    required = contract["required_architecture_return_files"]
    predictor = contract["predictor_return_pair"]

    assert required == {
        "U1_CODER_A": CODER_RETURN_BASENAMES[("U1", "CODER_A")],
        "U1_CODER_B": CODER_RETURN_BASENAMES[("U1", "CODER_B")],
        "U2_CODER_A": CODER_RETURN_BASENAMES[("U2", "CODER_A")],
        "U2_CODER_B": CODER_RETURN_BASENAMES[("U2", "CODER_B")],
        "U6_CODER_A": CODER_RETURN_BASENAMES[("U6", "CODER_A")],
        "U6_CODER_B": CODER_RETURN_BASENAMES[("U6", "CODER_B")],
    }
    assert predictor["U2_PREDICTOR"] == PREDICTOR_RETURN_BASENAMES["U2"]
    assert predictor["U6_PREDICTOR"] == PREDICTOR_RETURN_BASENAMES["U6"]
    stages = contract["intake_stages"]
    assert stages["PRIMARY_ARCHITECTURE"]["blocks_primary_v4"] is True
    assert stages["EXTERNAL_VALIDATION"]["blocks_primary_v4"] is False
    assert stages["PREDICTOR_REVIEW"]["blocks_primary_v4"] is True
    assert contract["workspace_policy"]["existing_output_directory_overwrite_allowed"] is False
    assert contract["workspace_policy"]["copy_validated_predictor_review_frames"] is True



def test_external_validation_can_be_intaken_without_primary_architecture(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _build_coder_return_bundle(returns, lanes=("U1",))

    result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=out_dir,
    )
    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))

    assert result["primary_architecture_returns_received"] is False
    assert result["primary_reliability_pass"] is None
    assert result["primary_return_status"] == "PENDING"
    assert result["primary_architecture_next_step"] == (
        "AWAIT_PRIMARY_ARCHITECTURE_RETURNS"
    )
    assert result["external_validation_returns_received"] is True
    assert result["external_validation_reliability_pass"] is True
    assert result["external_validation_return_status"] == "RELIABILITY_PASS"
    assert set(receipt["outputs"]["merged_ledgers"]) == {"U1"}


def test_predictor_review_can_be_intaken_without_any_architecture_returns(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _build_predictor_returns(returns)

    result = write_human_return_intake(
        root=ROOT,
        return_dir=returns,
        out_dir=out_dir,
    )
    receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))

    assert result["primary_architecture_returns_received"] is False
    assert result["external_validation_returns_received"] is False
    assert result["primary_reliability_pass"] is None
    assert result["external_validation_reliability_pass"] is None
    assert result["predictor_returns_received"] is True
    assert result["predictor_return_status"] == "COMPLETE"
    assert result["predictor_primary_complete"] is True
    assert receipt["outputs"]["merged_ledgers"] == {}
    assert set(receipt["outputs"]["predictor_reviewed_frames"]) == {"U2", "U6"}
    assert set(receipt["outputs"]["predictor_readouts"]) == {"U2", "U6"}
    for lane in ("U2", "U6"):
        reviewed = out_dir / receipt["outputs"]["predictor_reviewed_frames"][lane]
        assert reviewed.exists()
        assert reviewed.read_bytes() == (
            returns / PREDICTOR_RETURN_BASENAMES[lane]
        ).read_bytes()


def test_partial_external_validation_stage_fails_closed(tmp_path):
    returns = tmp_path / "returns"
    out_dir = tmp_path / "intake"
    _build_coder_return_bundle(returns, lanes=("U1",))
    (returns / CODER_RETURN_BASENAMES[("U1", "CODER_B")]).unlink()

    with pytest.raises(
        ValueError,
        match="external-validation architecture return stage is incomplete",
    ):
        write_human_return_intake(
            root=ROOT,
            return_dir=returns,
            out_dir=out_dir,
        )
    assert not out_dir.exists()


def test_no_complete_return_stage_fails_closed(tmp_path):
    returns = tmp_path / "returns"
    returns.mkdir()
    out_dir = tmp_path / "intake"

    with pytest.raises(ValueError, match="no complete human-return stage supplied"):
        write_human_return_intake(
            root=ROOT,
            return_dir=returns,
            out_dir=out_dir,
        )
    assert not out_dir.exists()

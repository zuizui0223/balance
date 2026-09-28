from pathlib import Path

import pytest

from balance_domain.plant_u1_structural_recovery import (
    FIELDS,
    build_u1_structural_recovery_readout,
    load_u1_structural_recovery_queue,
)


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "BALANCE_PLANT_U1_STRUCTURAL_CLASS_RECOVERY_QUEUE_V1.csv"


def test_u1_structural_recovery_queue_is_discovery_only():
    out = build_u1_structural_recovery_readout(QUEUE)
    assert out["n_candidates"] == 4
    assert out["priority_counts"] == {
        "HIGH": 2,
        "MEDIUM_HIGH": 1,
        "SPECIFICITY": 1,
    }
    assert out["universe_record_ids"] == ["U1_047", "U1_024", "U1_027", "U1_045"]
    assert out["all_conflict_states_unadjudicated"] is True
    assert out["all_architecture_states_unadjudicated"] is True
    assert out["primary_model_promotion_allowed"] is False


def test_queue_rows_do_not_preassign_conflict_or_architecture():
    rows = load_u1_structural_recovery_queue(QUEUE)
    assert all(row["current_conflict_state"] == "UNADJUDICATED" for row in rows)
    assert all(row["current_architecture_state"] == "UNADJUDICATED" for row in rows)
    assert all(row["queue_status"] == "TARGETED_FULL_TEXT_ADJUDICATION" for row in rows)
    assert all("primary_model_eligible" not in row for row in rows)


def test_validator_rejects_preadjudicated_state(tmp_path):
    source = QUEUE.read_text(encoding="utf-8")
    source = source.replace(
        ",UNADJUDICATED,UNADJUDICATED,",
        ",POSITIVE,UNADJUDICATED,",
        1,
    )
    path = tmp_path / "bad.csv"
    path.write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="cannot pre-adjudicate conflict"):
        load_u1_structural_recovery_queue(path)

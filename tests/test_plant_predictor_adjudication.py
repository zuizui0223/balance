import pytest

from balance_domain.plant_predictor_adjudication import (
    validate_predictor_adjudication_return,
)


def _frozen():
    return [{
        "receipt_id": "r1",
        "cluster_id": "plant_a",
        "predictor": "module_substrate",
        "reported_value": "SINGLE_OR_CONTINUOUS",
        "source_id": "source-1",
        "evidence_type": "INTEGRATED_STATE_EXPERIMENT",
        "outcome_independence": "TRUE",
        "adjudication_status": "SCREENED",
        "notes": "frozen source-side basis",
    }]


def test_predictor_review_can_adjudicate_without_rewriting_frozen_claim():
    frozen = _frozen()
    reviewed = [dict(frozen[0], adjudication_status="ADJUDICATED")]
    out = validate_predictor_adjudication_return(frozen, reviewed)
    assert out[0]["adjudication_status"] == "ADJUDICATED"
    assert out[0]["reported_value"] == "SINGLE_OR_CONTINUOUS"


@pytest.mark.parametrize(
    "field,value",
    [
        ("reported_value", "SERIAL_WITHIN_FLOWER"),
        ("source_id", "different-source"),
        ("notes", "rewritten note"),
        ("cluster_id", "other_cluster"),
        ("predictor", "conflict_timing_geometry"),
    ],
)
def test_predictor_review_cannot_rewrite_frozen_source_screen(field, value):
    frozen = _frozen()
    reviewed_row = dict(frozen[0], adjudication_status="ADJUDICATED")
    reviewed_row[field] = value
    with pytest.raises(ValueError, match="cannot modify frozen"):
        validate_predictor_adjudication_return(frozen, [reviewed_row])


def test_predictor_review_must_finish_with_adjudicated_or_rejected():
    frozen = _frozen()
    with pytest.raises(ValueError, match="must end ADJUDICATED or REJECTED"):
        validate_predictor_adjudication_return(frozen, [dict(frozen[0])])


def test_predictor_adjudication_requires_outcome_independent_source_evidence():
    frozen = _frozen()
    reviewed = [dict(
        frozen[0],
        adjudication_status="ADJUDICATED",
        outcome_independence="FALSE",
    )]
    with pytest.raises(ValueError, match="outcome_independence=TRUE"):
        validate_predictor_adjudication_return(frozen, reviewed)


def test_predictor_adjudication_rejects_outcome_derived_evidence_type():
    frozen = _frozen()
    reviewed = [dict(
        frozen[0],
        adjudication_status="ADJUDICATED",
        evidence_type="OUTCOME_DERIVED",
    )]
    with pytest.raises(ValueError, match="source-side evidence type"):
        validate_predictor_adjudication_return(frozen, reviewed)


def test_predictor_rejection_preserves_frozen_claim_without_licensing_it():
    frozen = _frozen()
    reviewed = [dict(
        frozen[0],
        adjudication_status="REJECTED",
        outcome_independence="UNCERTAIN",
    )]
    out = validate_predictor_adjudication_return(frozen, reviewed)
    assert out[0]["adjudication_status"] == "REJECTED"
    assert out[0]["reported_value"] == frozen[0]["reported_value"]

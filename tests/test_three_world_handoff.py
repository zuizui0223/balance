import pytest

from balance_domain.handoff import consume_conflict_handoff


def _handoff():
    return {
        "receipt_schema_version": "THREE_WORLD_CONFLICT_HANDOFF_V1",
        "status": "THREE_WORLD_CONFLICT_CONTEXT_IDENTIFIED",
        "context_id": "PEDICULARIS_POP_A_2027",
        "system": "Pedicularis rex",
        "population_id": "POP_A",
        "season_id": "2027",
        "fitness_scale_id": "INTACT_SEEDS_PER_FLOWER",
        "conflict_load": {
            "point": 0.4,
            "lower_95": 0.3,
            "upper_95": 0.5,
        },
        "source": {"repository": "sch"},
    }


def test_balance_consumes_exact_context_and_scale():
    result = consume_conflict_handoff(
        _handoff(),
        expected_context_id="PEDICULARIS_POP_A_2027",
        expected_fitness_scale_id="INTACT_SEEDS_PER_FLOWER",
    )
    assert result.context_id == "PEDICULARIS_POP_A_2027"
    assert result.conflict_load.lower == 0.3
    assert result.conflict_load.upper == 0.5
    assert result.source_repository == "sch"


def test_context_mismatch_fails_closed():
    with pytest.raises(ValueError, match="context_id"):
        consume_conflict_handoff(_handoff(), expected_context_id="OTHER_CONTEXT")


def test_scale_mismatch_fails_closed():
    with pytest.raises(ValueError, match="fitness_scale_id"):
        consume_conflict_handoff(_handoff(), expected_fitness_scale_id="RELATIVE_FITNESS")


def test_non_sch_source_fails_closed():
    receipt = _handoff()
    receipt["source"]["repository"] = "bita"
    with pytest.raises(ValueError, match="originate from sch"):
        consume_conflict_handoff(receipt)

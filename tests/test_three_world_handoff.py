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
            "source_field": "criticality_export.L_S_component",
        },
        "source": {
            "repository": "sch",
            "receipt_schema_version": "SCH_COMPONENT_CONFLICT_BUDGET_V1",
        },
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


def test_sch_source_schema_is_part_of_the_handoff_contract():
    receipt = _handoff()
    receipt["source"]["receipt_schema_version"] = "OTHER_SCHEMA"
    with pytest.raises(ValueError, match="SCH source receipt"):
        consume_conflict_handoff(receipt)


def test_explicit_conflict_source_field_must_match_sch_export():
    receipt = _handoff()
    receipt["conflict_load"]["source_field"] = "other.field"
    with pytest.raises(ValueError, match="source_field"):
        consume_conflict_handoff(receipt)


def test_missing_identifier_placeholders_do_not_become_literal_ids():
    for field, bad in (
        ("context_id", None),
        ("system", "None"),
        ("population_id", "null"),
        ("season_id", "REQUIRED_BEFORE_USE"),
        ("fitness_scale_id", "nan"),
    ):
        receipt = _handoff()
        receipt[field] = bad
        with pytest.raises(ValueError):
            consume_conflict_handoff(receipt)


def test_boolean_conflict_values_are_not_numeric_measurements():
    receipt = _handoff()
    receipt["conflict_load"]["point"] = True
    with pytest.raises(ValueError, match="boolean"):
        consume_conflict_handoff(receipt)


def test_positive_handoff_status_does_not_imply_ci_excludes_zero():
    receipt = _handoff()
    receipt["conflict_load"]["lower_95"] = 0.0
    result = consume_conflict_handoff(receipt)
    assert result.conflict_load.lower == 0.0

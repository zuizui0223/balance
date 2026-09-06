import json
import math
from pathlib import Path

from balance_domain import Interval, classify_bounded_receipt, consume_conflict_handoff


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "empirical" / "interface" / "THREE_WORLD_SYNTHETIC_FIXTURE_V1.json"


def test_one_context_survives_sch_balance_bita_compatible_projection():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    handoff = data["handoff"]
    decomp = data["bita_decomposition"]
    world = data["balance_worldlines"]

    conflict = consume_conflict_handoff(
        handoff,
        expected_context_id=decomp["context_id"],
        expected_fitness_scale_id=decomp["fitness_scale_id"],
    )

    receipt = classify_bounded_receipt(
        context_id=conflict.context_id,
        fitness_scale_id=conflict.fitness_scale_id,
        conflict_load=conflict.conflict_load,
        shared_optimum_fitness=Interval(*world["shared_optimum_fitness_95"]),
        differentiated_optimum_fitness=Interval(*world["differentiated_optimum_fitness_95"]),
        decoupling=Interval(*decomp["decoupling_95"]),
        architecture_cost=Interval(*decomp["architecture_cost_95"]),
    )

    assert receipt.direct_state == data["expected"]["direct_state"]
    assert math.isclose(receipt.direct_gap.lower, data["expected"]["direct_gap"])
    assert math.isclose(receipt.direct_gap.upper, data["expected"]["direct_gap"])
    assert receipt.bridge_zero_compatible is data["expected"]["bridge_zero_compatible"]

    point_phi = (
        decomp["point_decoupling"] * handoff["conflict_load"]["point"]
        - decomp["point_architecture_cost"]
    )
    assert math.isclose(point_phi, data["expected"]["point_decomposed_gap"])
    assert math.isclose(point_phi, data["expected"]["direct_gap"])


def test_fixture_rejects_a_different_bita_context():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    try:
        consume_conflict_handoff(
            data["handoff"],
            expected_context_id="PEDICULARIS_OTHER_POP_2027",
            expected_fitness_scale_id=data["bita_decomposition"]["fitness_scale_id"],
        )
    except ValueError as exc:
        assert "context_id" in str(exc)
    else:
        raise AssertionError("mismatched context must fail closed")

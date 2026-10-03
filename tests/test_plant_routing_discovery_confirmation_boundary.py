import json
from pathlib import Path

from balance_domain.plant_model_v4 import PRIMARY_UNIVERSES


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = ROOT / "data" / "BALANCE_PLANT_ROUTING_DISCOVERY_CONFIRMATION_BOUNDARY_V1.json"
MODEL_SPEC = ROOT / "data" / "BALANCE_PLANT_CONFIRMATORY_MODEL_SPEC_V4.json"
HYPOTHESES = ROOT / "data" / "BALANCE_PLANT_V4_DIRECTIONAL_HYPOTHESES_V1.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_routing_discovery_confirmation_boundary_matches_frozen_v4_contract():
    boundary = _load(BOUNDARY)
    spec = _load(MODEL_SPEC)
    hypotheses = _load(HYPOTHESES)

    pointer = "data/BALANCE_PLANT_ROUTING_DISCOVERY_CONFIRMATION_BOUNDARY_V1.json"
    assert spec["routing_discovery_confirmation_boundary"] == pointer
    assert hypotheses["routing_discovery_confirmation_boundary"] == pointer

    assert boundary["status"] == (
        "FROZEN_BEFORE_INDEPENDENT_U2_U6_ARCHITECTURE_RETURNS"
    )
    assert boundary["discovery_lane"]["primary_confirmatory_denominator"] is False
    assert boundary["discovery_lane"]["id"] == "U3_HETERANTHERY_MATCHED"

    confirmatory = boundary["confirmatory_lane"]
    assert confirmatory["primary_universes"] == list(PRIMARY_UNIVERSES)
    assert confirmatory["primary_universes"] == spec["primary_fitting_universes"]
    assert confirmatory["external_validation_universe"] == "U1_HAAS_LORTIE_2020"
    assert confirmatory["external_validation_universe"] in (
        spec["external_specificity_and_validation_universes"]
    )
    assert "U3" in spec["external_specificity_and_validation_universes"]
    assert "separate estimand" in (
        spec["external_specificity_and_validation_universes"]["U3"]
    )

    assert confirmatory["frozen_response"] == spec["primary_response"]["name"]
    assert confirmatory["frozen_predictors"] == [
        "module_opportunity2",
        "temporal_exposure3",
    ]
    assert set(confirmatory["frozen_predictors"]) <= set(
        spec["primary_predictor_contrasts"]
    )

    registered_ids = {row["id"] for row in hypotheses["hypotheses"]}
    boundary_ids = {
        row["id"] for row in confirmatory["frozen_directional_hypotheses"]
    }
    assert boundary_ids == {
        "H_T_ORDERED_NONSTRUCTURAL",
        "H_M_MODULAR_STRUCTURAL",
    }
    assert boundary_ids == registered_ids


def test_routing_discovery_lane_points_only_to_existing_canonical_evidence():
    boundary = _load(BOUNDARY)
    discovery = boundary["discovery_lane"]

    for rel in discovery["canonical_evidence"]:
        assert (ROOT / rel).is_file(), rel

    results = " ".join(discovery["frozen_results"])
    assert "binary pollen-fate conflict presence" in results
    assert "non-identifying proxies in both directions" in results
    assert "at least two routing states" in results

    prohibited = " ".join(discovery["prohibited_use"])
    assert "do not add U3 rows to the V4 primary response denominator" in prohibited
    assert "do not use U3 architecture outcomes to code U2 or U6 predictors" in prohibited
    assert "do not tune V4 response classes" in prohibited


def test_routing_boundary_freezes_discovery_to_confirmation_sequence_without_claim_upgrade():
    boundary = _load(BOUNDARY)
    sequence = boundary["inference_sequence"]

    assert sequence[0].startswith(
        "U3 establishes that conflict presence and visible morphology"
    )
    assert "conditional routing given conflict" in sequence[1]
    assert "pre-outcome candidate routing predictors" in sequence[2]
    assert "U2 and U6 provide the confirmatory response data" in sequence[3]
    assert "not to rescue, recode, or select" in sequence[4]

    assert boundary["claim_ceiling"] == (
        "discovery_confirmation_boundary_only_no_new_biological_effect_or_"
        "cross_universe_result"
    )

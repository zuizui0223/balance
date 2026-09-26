from pathlib import Path

from balance_domain.plant_u3_targeted_measurement import (
    build_u3_targeted_measurement_readout,
    load_u3_targeted_measurement_spec,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "BALANCE_PLANT_U3_TARGETED_MEASUREMENT_SPEC_V2.json"


def test_u3_targeted_measurement_spec_is_frozen_for_four_targets():
    data = load_u3_targeted_measurement_spec(SPEC)
    out = build_u3_targeted_measurement_readout(SPEC)
    assert out["n_targets"] == 4
    assert out["status"] == "FROZEN_BEFORE_NEW_EVIDENCE"
    assert out["target_taxa"] == [
        "Monochoria australasica",
        "Monochoria cyanea",
        "Osbeckia chinensis",
        "Senna covesii",
    ]
    assert out["route_counts"] == {
        "Monochoria australasica": 2,
        "Monochoria cyanea": 2,
        "Osbeckia chinensis": 2,
        "Senna covesii": 3,
    }


def test_monochoria_visit_only_shortcuts_are_explicitly_rejected():
    data = load_u3_targeted_measurement_spec(SPEC)
    for target_id in ("U3MEAS_MONAUS_001", "U3MEAS_MONCYA_001"):
        row = data["targets"][target_id]
        assert "general genus/family buzz-pollination statements" in row["explicitly_insufficient"]
        assert "visitor presence without pollen transfer or reproductive effect" in row["explicitly_insufficient"]


def test_osbeckia_contact_only_shortcuts_are_explicitly_rejected():
    data = load_u3_targeted_measurement_spec(SPEC)
    row = data["targets"]["U3MEAS_OSBCHI_001"]
    assert "pollen extraction alone" in row["explicitly_insufficient"]
    assert "stigma contact alone" in row["explicitly_insufficient"]
    assert row["gate"] == "CONTROL_POLLEN_FATE_CONFLICT"


def test_senna_covesii_routing_is_prospectively_identified_not_inferred_from_morphology():
    data = load_u3_targeted_measurement_spec(SPEC)
    row = data["targets"]["U3MEAS_SENCOV_001"]
    assert row["gate"] == "CONFLICT_CONDITIONED_ROUTING_ARCHITECTURE"
    assert row["position_groups"] == {
        "median": "four median fertile stamen positions",
        "abaxial": "three abaxial fertile stamen positions",
    }
    assert [r["route"] for r in row["admissible_routes"]] == [
        "POSITION_RESOLVED_SOURCE_TRACKING",
        "POSITION_SELECTIVE_MANIPULATION",
        "SHARED_ROUTING_EQUIVALENCE",
    ]
    assert "Irwin-Barneby remnant two-set morphology alone" in row["explicitly_insufficient"]
    assert "pooled pollen deposition without source resolution by stamen position" in row["explicitly_insufficient"]


def test_senna_covesii_shared_integration_requires_equivalence_not_null_significance():
    data = load_u3_targeted_measurement_spec(SPEC)
    row = data["targets"]["U3MEAS_SENCOV_001"]
    assert "equivalence" in row["shared_integrated_rule"].lower()
    assert "failure to reject" in row["shared_integrated_rule"].lower()
    assert "non-significant positional difference without an equivalence test" in row["explicitly_insufficient"]

    out = build_u3_targeted_measurement_readout(SPEC)
    assert out["senna_covesii_routing_contract_frozen"] is True
    assert out["senna_covesii_shared_integrated_requires_equivalence"] is True

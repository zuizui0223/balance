from pathlib import Path

from balance_domain.plant_u3_targeted_measurement import (
    build_u3_targeted_measurement_readout,
    load_u3_targeted_measurement_spec,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "BALANCE_PLANT_U3_TARGETED_MEASUREMENT_SPEC_V1.json"


def test_u3_targeted_measurement_spec_is_frozen_for_three_targets():
    data = load_u3_targeted_measurement_spec(SPEC)
    out = build_u3_targeted_measurement_readout(SPEC)
    assert out["n_targets"] == 3
    assert out["status"] == "FROZEN_BEFORE_NEW_EVIDENCE"
    assert out["target_taxa"] == [
        "Monochoria australasica",
        "Monochoria cyanea",
        "Osbeckia chinensis",
    ]
    assert all(n == 2 for n in out["route_counts"].values())


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

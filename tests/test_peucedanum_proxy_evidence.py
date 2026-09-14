import json
from pathlib import Path

import pytest

from balance_domain.peucedanum_proxy import analyze_peucedanum_proxy_criticality


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "empirical" / "peucedanum" / "PEUCEDANUM_ANTAGONIST_PROXY_CRITICALITY_INPUT_V1.json"


def _config():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    config["registered_sensitivity_model"]["draws"] = 1000
    return config


@pytest.mark.parametrize(
    "path",
    [
        ("proxy_axis", "left_value"),
        ("proxy_axis", "right_value"),
        ("definitions", "final_fruit_selection_gradient_beta", "left_mean"),
        ("definitions", "final_fruit_selection_gradient_beta", "left_se"),
        ("definitions", "final_fruit_selection_gradient_beta", "right_mean"),
        ("definitions", "final_fruit_selection_gradient_beta", "right_se"),
    ],
)
def test_boolean_proxy_measurements_are_not_numeric_evidence(path):
    config = _config()
    target = config
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = True
    with pytest.raises(ValueError, match="not boolean"):
        analyze_peucedanum_proxy_criticality(config)


@pytest.mark.parametrize(
    "path",
    [
        ("system",),
        ("input_version",),
        ("proxy_axis", "name"),
        ("proxy_axis", "units"),
        ("proxy_axis", "left_context"),
        ("proxy_axis", "right_context"),
        ("definitions", "final_fruit_selection_gradient_beta", "zero_semantics"),
    ],
)
@pytest.mark.parametrize("bad", ["None", "null", "nan", "REQUIRED_BEFORE_USE"])
def test_placeholder_proxy_provenance_and_semantics_fail_closed(path, bad):
    config = _config()
    target = config
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = bad
    with pytest.raises(ValueError, match="frozen before use"):
        analyze_peucedanum_proxy_criticality(config)


def test_registered_integer_controls_still_require_literal_numeric_values():
    config = _config()
    config["registered_sensitivity_model"]["draws"] = True
    with pytest.raises(ValueError, match="integer-valued"):
        analyze_peucedanum_proxy_criticality(config)

    config = _config()
    config["registered_sensitivity_model"]["random_seed"] = True
    with pytest.raises(ValueError, match="integer-valued"):
        analyze_peucedanum_proxy_criticality(config)

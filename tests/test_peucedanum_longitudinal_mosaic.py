import json
from pathlib import Path

from balance_domain.longitudinal_mosaic import classify_longitudinal_mosaic


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "empirical" / "peucedanum" / "PEUCEDANUM_LONGITUDINAL_MOSAIC_INPUT_V1.json"


def _result():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    pop = data["source_layers"]["2021_population_mosaic"]
    sel = data["source_layers"]["2025_selection_mosaic"]
    return classify_longitudinal_mosaic(
        flowering_time_predation_estimate=pop["flowering_time_to_predation"]["estimate"],
        flowering_time_predation_p=pop["flowering_time_to_predation"]["p_upper_bound"],
        predation_allocation_r2=pop["predation_risk_to_male_flower_proportion"]["r_squared"],
        predation_allocation_p=pop["predation_risk_to_male_flower_proportion"]["p_upper_bound"],
        selection_margin_by_context=sel["final_fruit_selection_gradient_beta"],
        ordered_contexts=sel["ordered_contexts"],
    )


def test_published_source_series_is_longitudinally_concordant():
    result = _result()
    assert result.classification == "LONGITUDINAL_MOSAIC_CONCORDANT"
    assert result.pressure_gradient_supported
    assert result.allocation_tracking_supported
    assert result.selection_reversal_supported
    assert result.high_pressure_contexts == ("HA", "HL")
    assert result.low_pressure_contexts == ("HC", "KD", "HD")


def test_claim_ceiling_does_not_count_source_layers_as_independent_studies():
    result = _result()
    assert "not_independent_studies_by_count" in result.claim_ceiling
    assert "not_direct_BALANCE_worldline" in result.claim_ceiling


def test_selection_without_earlier_pressure_layer_is_not_enough():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    pop = data["source_layers"]["2021_population_mosaic"]
    sel = data["source_layers"]["2025_selection_mosaic"]
    result = classify_longitudinal_mosaic(
        flowering_time_predation_estimate=0.01,
        flowering_time_predation_p=0.8,
        predation_allocation_r2=pop["predation_risk_to_male_flower_proportion"]["r_squared"],
        predation_allocation_p=pop["predation_risk_to_male_flower_proportion"]["p_upper_bound"],
        selection_margin_by_context=sel["final_fruit_selection_gradient_beta"],
        ordered_contexts=sel["ordered_contexts"],
    )
    assert result.classification == "LONGITUDINAL_MOSAIC_INCOMPLETE_OR_DISCORDANT"

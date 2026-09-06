import pytest

from balance_domain.peucedanum_raw import (
    PUBLISHED_2025,
    published_regime_reproduction_gate,
    validate_normalized_rows,
)


def _row(**updates):
    row = {
        "dataset_id": "demo",
        "source_doi": "10.5061/dryad.demo",
        "year": 2021,
        "population_id": "HL",
        "plant_id": "P1",
        "flowering_day": 210,
        "perfect_flower_count": 20,
        "male_flower_count": 30,
        "male_fraction": 0.6,
        "intact_fruit_count": 8,
        "seed_predation_rate": 0.4,
    }
    row.update(updates)
    return row


def test_normalized_rows_validate_without_imputing_optional_fields():
    inventory = validate_normalized_rows([
        _row(),
        _row(plant_id="P2", year=2022, population_id="HC", seed_predation_rate=""),
    ])
    assert inventory.n_records == 2
    assert inventory.years == (2021, 2022)
    assert inventory.populations == ("HC", "HL")
    assert inventory.seed_predation_rows == 1
    assert inventory.female_fitness_rows == 2


def test_inconsistent_derived_male_fraction_fails_closed():
    with pytest.raises(ValueError):
        validate_normalized_rows([_row(male_fraction=0.2)])


def test_seed_predation_must_be_a_proportion():
    with pytest.raises(ValueError):
        validate_normalized_rows([_row(seed_predation_rate=1.2)])


def test_published_summary_reproduces_registered_regime():
    result = published_regime_reproduction_gate(PUBLISHED_2025)
    assert result.qualitative_status == "PUBLISHED_REGIME_REPRODUCED"
    assert result.failed_checks == ()
    assert result.max_abs_difference_from_published == 0.0
    assert result.numeric_tolerance_registered is False


def test_regime_gate_detects_a_boundary_sign_failure():
    estimates = {metric: values.copy() for metric, values in PUBLISHED_2025.items()}
    estimates["beta"]["HC"] = -0.01
    result = published_regime_reproduction_gate(estimates)
    assert result.qualitative_status == "PUBLISHED_REGIME_NOT_REPRODUCED"
    assert "beta:HC:expected_positive" in result.failed_checks


def test_numeric_proximity_is_reported_but_not_used_before_source_model_reproduction():
    estimates = {metric: values.copy() for metric, values in PUBLISHED_2025.items()}
    estimates["beta"]["KD"] += 0.10
    result = published_regime_reproduction_gate(estimates)
    assert result.qualitative_status == "PUBLISHED_REGIME_REPRODUCED"
    assert result.max_abs_difference_from_published == pytest.approx(0.10)
    assert result.numeric_tolerance_registered is False

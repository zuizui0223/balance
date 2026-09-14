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


def test_large_finite_flower_counts_do_not_overflow_composition_check():
    inventory = validate_normalized_rows([
        _row(
            perfect_flower_count=1.0e308,
            male_flower_count=1.0e308,
            male_fraction=0.5,
        )
    ])
    assert inventory.n_records == 1

    with pytest.raises(ValueError, match="male_fraction is inconsistent"):
        validate_normalized_rows([
            _row(
                perfect_flower_count=1.0e308,
                male_flower_count=1.0e308,
                male_fraction=0.0,
            )
        ])


@pytest.mark.parametrize(
    "field",
    [
        "flowering_day",
        "perfect_flower_count",
        "male_flower_count",
        "seed_predation_rate",
        "intact_fruit_count",
        "male_fraction",
    ],
)
def test_boolean_raw_measurements_are_not_numeric_evidence(field):
    with pytest.raises(ValueError, match="not boolean"):
        validate_normalized_rows([_row(**{field: True})])


@pytest.mark.parametrize("field", ["dataset_id", "source_doi", "population_id", "plant_id"])
@pytest.mark.parametrize("bad", ["None", "null", "nan", "REQUIRED_BEFORE_USE"])
def test_placeholder_raw_provenance_fails_closed(field, bad):
    with pytest.raises(ValueError, match="frozen non-missing identifier"):
        validate_normalized_rows([_row(**{field: bad})])


def test_boolean_published_regime_estimate_is_rejected():
    estimates = {metric: values.copy() for metric, values in PUBLISHED_2025.items()}
    estimates["S"]["HA"] = True
    with pytest.raises(ValueError, match="not boolean"):
        published_regime_reproduction_gate(estimates)

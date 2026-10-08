"""Synthetic geometry test witnesses, never Pedicularis field observations."""
from copy import deepcopy

import pytest

from balance_domain.pedicularis_exposure_geometry import (
    ARMS, FIELDS, GEOMETRY_SCHEMA, audit_exposure_geometry,
)


def config():
    return {
        "schema_version": GEOMETRY_SCHEMA,
        "status": "FROZEN_BEFORE_EXPOSURE_OUTCOMES",
        "context_id": "SYNTHETIC_CONTEXT",
        "population_id": "SYNTHETIC_POPULATION",
        "season_id": "SYNTHETIC_SEASON",
        "protocol_version": "SYNTHETIC_PROTOCOL",
        "all_heights_share_an_instrument_calibrated_vertical_datum": True,
        "oviposition_site_definition_reviewed_before_outcome": True,
        "thresholds": {
            "max_each_position_error_mm": 0.1,
            "max_whorl_waterline_disagreement_mm": 0.2,
            "min_waterline_clearance_contrast_mm": 5.0,
            "max_within_flower_exsertion_difference": 0.01,
            "min_independent_compartments_with_contrast": 3,
            "min_independent_plants_with_contrast": 3,
        },
    }


def rows():
    data = []
    for plant in range(6):
        for flower in range(2):
            for time in range(2):
                data.append({
                    "context_id": "SYNTHETIC_CONTEXT",
                    "population_id": "SYNTHETIC_POPULATION",
                    "season_id": "SYNTHETIC_SEASON",
                    "protocol_version": "SYNTHETIC_PROTOCOL",
                    "plant_id": f"P{plant}",
                    "water_compartment_id": f"P{plant}_W1",
                    "flower_id": f"P{plant}_F{flower}",
                    "observation_time_id": "EARLY" if time == 0 else "LATE",
                    "assigned_water_arm": "OBSERVATIONAL",
                    "flower_length_mm": "25",
                    "bract_height_mm": "16",
                    "flower_tip_elevation_mm": "26",
                    "bract_rim_elevation_mm": "18",
                    "water_surface_elevation_mm": "14" if time == 0 else "4",
                    "oviposition_site_elevation_mm": "12",
                    "oviposition_site_directly_verified": "1",
                    "positions_calibrated": "1",
                    "outcome_blinded_when_measured": "1",
                })
    return data


def test_same_published_exsertion_can_have_different_waterline_clearance():
    result = audit_exposure_geometry(rows(), config())
    assert result["status"] == "GEOMETRIC_TWO_AXIS_SUPPORT_ONLY_NOT_CAUSAL"
    assert result["gate_reasons"] == []
    assert result["n_flower_time_records"] == 24
    assert result["n_distinct_whorl_water_compartments"] == 6
    assert result["n_distinct_flowers"] == 12
    assert result["n_contrasting_flowers"] == 12
    assert result["n_contrasting_whorls"] == 6
    assert result["n_independent_plants_with_contrasts"] == 6
    assert result["waterline_status_counts"] == {
        "SITE_ABOVE_WATERLINE_NOT_PROVEN_ACCESSIBLE": 12,
        "SITE_SUBMERGED_NOT_PROVEN_PROTECTED": 12,
    }
    assert result["ecological_effect_identified"] is False
    assert result["BALANCE_middle_world_identified"] is False


def test_geometry_without_waterline_change_is_not_support():
    data = rows()
    for row in data:
        row["water_surface_elevation_mm"] = "14"
    result = audit_exposure_geometry(data, config())
    assert result["status"] == "EXPOSURE_GEOMETRY_SUPPORT_HOLD"
    assert "insufficient_independent_waterline_contrasts" in result["gate_reasons"]


def test_pseudoreplication_across_same_whorl_does_not_add_independent_units():
    data = rows()[:4]
    result = audit_exposure_geometry(data, config())
    assert result["n_contrasting_flowers"] == 2
    assert result["n_contrasting_whorls"] == 1
    assert "insufficient_independent_plants_with_contrasts" in result["gate_reasons"]


def test_shared_whorl_water_must_agree_at_same_time():
    data = rows()
    data[2]["water_surface_elevation_mm"] = "10"
    result = audit_exposure_geometry(data, config())
    assert result["status"] == "EXPOSURE_GEOMETRY_SUPPORT_HOLD"
    assert "shared_whorl_waterline_measurements_inconsistent" in result["gate_reasons"]


def test_unverified_egg_deposition_site_is_not_assumed_accessible():
    data = rows()
    data[0]["oviposition_site_directly_verified"] = "0"
    result = audit_exposure_geometry(data, config())
    assert "unverified_oviposition_site_coordinates" in result["gate_reasons"]
    assert result["status"] == "EXPOSURE_GEOMETRY_SUPPORT_HOLD"


def test_wet_surface_above_rim_and_target_above_tip_rejected():
    data = rows()
    data[0]["water_surface_elevation_mm"] = "20"
    with pytest.raises(ValueError, match="above bract rim"):
        audit_exposure_geometry(data, config())
    data = rows()
    data[0]["oviposition_site_elevation_mm"] = "30"
    with pytest.raises(ValueError, match="above flower tip"):
        audit_exposure_geometry(data, config())


def test_no_adaptive_effect_data_allowed_in_geometry_csv():
    data = rows()
    data[0]["seed_predation_rate"] = "0.01"
    with pytest.raises(ValueError, match="unexpected geometry fields"):
        audit_exposure_geometry(data, config())


def test_mixed_plant_water_arms_and_flower_moves_rejected():
    data = rows()
    data[0]["assigned_water_arm"] = "INTACT_WET"
    with pytest.raises(ValueError, match="incompatible water-state arms"):
        audit_exposure_geometry(data, config())
    data = rows()
    data[1]["water_compartment_id"] = "P0_DIFFERENT"
    with pytest.raises(ValueError, match="flower changes water compartment"):
        audit_exposure_geometry(data, config())


def test_requires_prospectively_frozen_calibration_and_large_enough_contrast():
    frozen = config()
    frozen["status"] = "TEMPLATE_NOT_FROZEN"
    with pytest.raises(ValueError, match="prospectively frozen"):
        audit_exposure_geometry(rows(), frozen)
    frozen = config()
    frozen["thresholds"]["min_waterline_clearance_contrast_mm"] = 0.3
    with pytest.raises(ValueError, match="four-position-error"):
        audit_exposure_geometry(rows(), frozen)
    frozen = config()
    frozen["all_heights_share_an_instrument_calibrated_vertical_datum"] = False
    with pytest.raises(ValueError, match="common calibrated"):
        audit_exposure_geometry(rows(), frozen)


def test_observation_blinding_and_duplicate_flower_time():
    data = rows()
    data[0]["outcome_blinded_when_measured"] = "0"
    result = audit_exposure_geometry(data, config())
    assert "geometry_assessed_after_seeing_biological_outcomes" in result["gate_reasons"]
    data = rows()
    data[1] = dict(data[0])
    with pytest.raises(ValueError, match="duplicated flower/time"):
        audit_exposure_geometry(data, config())


def test_not_predicting_behaviour_from_exposure_sign():
    data = rows()
    data[0]["water_surface_elevation_mm"] = "12.15"
    # Site-water difference -0.15 mm < 2*0.1 mm measurement error.
    # But the other flower sharing the same whorl has 14 mm surface
    # at the same time; this is an independently reported method problem.
    result = audit_exposure_geometry(data, config())
    assert result["waterline_status_counts"]["WATERLINE_BOUNDARY_UNRESOLVED"] == 1
    assert "shared_whorl_waterline_measurements_inconsistent" in result["gate_reasons"]

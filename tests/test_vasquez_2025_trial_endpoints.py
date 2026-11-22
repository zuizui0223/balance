"""Unit and source-fail-closed tests for the Vasquez 2025 original 15-trial endpoint.

Synthetic arrays below are fixtures ONLY and are never included in the
published-source or original Zenodo reanalysis results.
"""
from pathlib import Path

import pytest

from scripts.reanalyse_vasquez_2025_trial_denominators import (
    BOOT_SEED,
    from_authenticated_rows,
    trial_descriptive_summary,
)

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=(ROOT/".github"/"workflows"/"vasquez-2025-zenodo-audit.yml")


def synthetic_trials():
    data=[]
    for species,n,base in (
        ("S.rostratum",6,1),
        ("S.dulcamara",9,2),
    ):
        for i in range(n):
            data.append({
                "source_species":species,
                "source_bee_id":str(i),
                "source_hive": "B1" if i%2 else "B2",
                "fraction_released_pct_of_measured_source":base*10,
                "pollen_transfer_efficiency_pct_of_removed":base,
                "source_to_four_stigmas_pct_of_production":base*base/10,
                "first_recipient_pct_of_four_stigmas":40,
            })
    return {"trials":data}


def test_synthetic_trial_means_not_pooled_60_stigmas():
    fake=synthetic_trials()
    result=trial_descriptive_summary(fake,bootstrap_samples=100)
    assert result["total_donor_trials"]==15
    assert result["nested_stigma_rows"]==60
    assert result["raw_trial_rows_in_repo"]==0
    assert result["species"]["S.rostratum"]["n_donor_bee_trials"]==6
    assert result["species"]["S.dulcamara"]["n_donor_bee_trials"]==9
    assert result["species"]["S.rostratum"]["mean_per_trial"][
        "source_to_four_stigmas_pct_of_production"
    ]==pytest.approx(.1)
    assert result["species"]["S.dulcamara"]["mean_per_trial"][
        "source_to_four_stigmas_pct_of_production"
    ]==pytest.approx(.4)
    contrast=result["predefined_trial_level_species_mean_differences"][
        "source_to_four_stigmas_pct_of_production"
    ]
    assert contrast["dulcamara_minus_rostratum_pct_points"]==pytest.approx(.3)
    assert contrast["bootstrap_replicates"]==100
    assert contrast["not_random_assignment_or_colony_robust_confidence"] is True
    assert result["statistical_limits"]["no_genetic_paternity"] is True


def test_fake_original_bytes_do_not_get_an_original_data_p_value():
    with pytest.raises(ValueError,match="SHA256 mismatch"):
        from_authenticated_rows(b"trial_number,flower_sp,donor_total\n1,S.rostratum,9\n")


def test_workflow_does_not_upload_raw_source_or_skip_trial_unit():
    workflow=WORKFLOW.read_text(encoding="utf-8")
    assert "scripts.audit_vasquez_2025_trial_structure" in workflow
    assert "scripts.reanalyse_vasquez_2025_trial_denominators" in workflow
    assert workflow.index("scripts.audit_vasquez_2025_trial_structure") < workflow.index(
        "scripts.reanalyse_vasquez_2025_trial_denominators"
    )
    assert 'vasquez-2025-actual-15-trial-denominators.json' in workflow
    assert "vasquez-raw-not-uploaded/data.csv" in workflow
    assert "source-dir" in workflow
    assert "retention-days: 21" in workflow

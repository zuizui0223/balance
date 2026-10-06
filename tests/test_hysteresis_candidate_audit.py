import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "BALANCE_HYSTERESIS_CANDIDATE_AUDIT_V1.csv"


def _rows():
    with AUDIT.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_named_hysteresis_audit_does_not_promote_surrogates():
    rows = _rows()
    assert len(rows) == 6
    assert all(row["promotion_status"] == "REJECTED" for row in rows)
    assert not any(
        row["shared_vs_differentiated_architecture"] == "yes"
        and row["state_boundary_empirical"] == "yes"
        and row["uncertainty_for_threshold_separation"] == "yes"
        for row in rows
    )


def test_hysteresis_audit_preserves_distinct_failure_modes():
    rows = {row["candidate_id"]: row for row in _rows()}
    assert "differentiation marker" in rows["HYS_HL60_DMSO_2006"]["exclusion_reason"]
    assert "forward_reverse" in rows["HYS_YEAST_PHO_2007"]["exclusion_reason"]
    assert "numerical model" in rows["HYS_LOCUST_DENSITY_2012"]["exclusion_reason"]
    assert "hydraulic" in rows["HYS_TREE_HYDRAULIC_2026"]["exclusion_reason"]
    assert "physiological memory" in rows["HYS_PRUNUS_WATER_1999"]["exclusion_reason"]
    assert "closest architecture-level candidate" in rows["HYS_BACILLUS_CELLTYPE_2025"]["exclusion_reason"]
    assert rows["HYS_BACILLUS_CELLTYPE_2025"]["state_boundary_empirical"] == (
        "empirical_colony_state_transitions_but_not_matched_forward_reverse_thresholds"
    )

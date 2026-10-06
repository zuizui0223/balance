import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "BALANCE_HYSTERESIS_CANDIDATE_AUDIT_V1.csv"


def _rows():
    with AUDIT.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_named_hysteresis_audit_does_not_promote_surrogates():
    rows = _rows()
    assert len(rows) == 9
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
    assert "epithelial versus mesenchymal" in rows["HYS_EMT_TGFB_2018"]["exclusion_reason"]
    assert "genetically enforced" in rows["HYS_PSEUDOMONAS_SIDEROPHORE_2022"]["exclusion_reason"]
    assert "forward and backward" in rows["HYS_OOCERAEA_DEFENCE_2025"]["exclusion_reason"]


def test_expanded_hysteresis_audit_spans_orthogonal_near_miss_directions():
    rows = {row["candidate_id"]: row for row in _rows()}

    # Strong empirical hysteresis, but not division-of-labour architecture.
    emt = rows["HYS_EMT_TGFB_2018"]
    assert emt["state_boundary_empirical"] == "empirical_bimodal_state_transition_and_reversion_protocol"
    assert emt["shared_vs_differentiated_architecture"] == "no"

    # Real generalist-versus-specialist architecture/payoff contrast, but no reversible same-unit sweep.
    pseudo = rows["HYS_PSEUDOMONAS_SIDEROPHORE_2022"]
    assert pseudo["shared_vs_differentiated_architecture"] == "yes_enforced_specialist_mix_vs_generalist_wildtype"
    assert pseudo["same_biological_unit"] == "fixed_engineered_genotypes"
    assert pseudo["forward_reverse_history"] == "no_forward_reverse_history"

    # Real context-dependent division of labour in one colony, but no threshold hysteresis experiment.
    ant = rows["HYS_OOCERAEA_DEFENCE_2025"]
    assert ant["shared_vs_differentiated_architecture"] == "partial_colony_task_specialization"
    assert ant["state_boundary_empirical"] == "empirical_context_dependent_division_of_labour"
    assert ant["forward_reverse_history"] == "no_forward_reverse_graded_sweep"

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "PEDICULARIS_FINAL_IDENTIFICATION_PROGRAM_V1.json"
CHAIN = ROOT / "docs" / "PEDICULARIS_THREE_WORLD_CHAIN_V1.md"


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_integrated_superfactorial_has_declared_40_cell_ecological_surface():
    m = _manifest()
    assert m["preferred_integrated_ecological_design"]["formula"] == "z(5) x D(2) x G(2) x P(2)"
    assert m["preferred_integrated_ecological_design"]["nominal_cells"] == 40
    assert m["independent_remaining_channel_assay"]["nominal_cells"] == 4
    assert m["context_contract"]["sample_size_status"] == "POWER_CALIBRATED_AFTER_STAGE0_VARIANCE_PILOT"


def test_each_paper_reads_a_distinct_registered_slice():
    m = _manifest()["paper_receipts"]
    assert m["SCH"]["nominal_cells_used"] == 20
    assert m["BALANCE"]["nominal_cells_used_if_D_binary"] == 10
    assert m["BITA"]["nominal_cells_used"] == 16
    assert "D_fixed" in m["SCH"]["slice"]
    assert "G_present_P_present" in m["BALANCE"]["slice"]
    assert "A x D2 x G2 x P2" in m["BITA"]["slice"]


def test_ownership_keeps_architecture_value_out_of_bita():
    m = _manifest()
    assert m["ownership"]["BITA"] == "trait_interaction_mechanism_allocation"
    assert "R_K_Phi" in m["ownership"]["SLK"]
    assert "do_not_call_residual_kappa_or_cost_by_subtraction" == m["paper_receipts"]["BITA"]["prohibited_label"]
    chain = CHAIN.read_text(encoding="utf-8")
    assert "Architecture-value transport (`R`, `K`, `s`, `Phi`) belongs to SLK" in chain
    assert "BITA does **not** re-estimate the architecture-value chain" in chain


def test_sch_predator_intervention_is_independent_of_water_defence_axis():
    m = _manifest()
    assert m["factors"]["G"]["must_be_independent_of_D"] is True
    assert "use_D_as_SCH_antagonist_G" in m["reuse_rules"]["forbidden"]
    chain = CHAIN.read_text(encoding="utf-8")
    assert "Water retained/drained must not be reused as SCH antagonist `G`" in chain


def test_balance_has_fail_closed_architecture_qualification_gate():
    m = _manifest()
    assert "qualify_BALANCE_D_world_as_a_prospectively_registered_accessible_architecture" in m["stage0_hard_gates"][-1]
    assert m["paper_receipts"]["BALANCE"]["historical_differentiation_not_inferred"] is True
    assert "BALANCE_architecture_qualification_failure" in m["stop_rules"][3]


def test_bita_levels_are_frozen_before_target_interaction_analysis():
    m = _manifest()
    assert m["factors"]["z"]["posthoc_outcome_based_level_selection_forbidden"] is True
    assert "freeze_BITA_low_high_A_contrast_before_target_interaction_analysis" in m["stage0_hard_gates"]
    chain = CHAIN.read_text(encoding="utf-8")
    assert "not chosen post hoc to maximize `Delta_AD W`" in chain

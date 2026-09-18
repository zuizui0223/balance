from pathlib import Path

from balance_domain.macro_ledger import load_macro_ledger
from balance_domain.macro_predictors import (
    adjudicated_independent_values,
    confirmatory_h1_h2_clusters,
    load_predictor_receipts,
)


ROOT = Path(__file__).resolve().parents[1]
PILOT_MACRO = ROOT / "data" / "BALANCE_MACRO_PILOT_LEDGER_V1.csv"
PILOT_RECEIPTS = ROOT / "data" / "BALANCE_MACRO_PREDICTOR_RECEIPTS_PILOT_V1.csv"


def test_pilot_predictor_receipts_validate():
    receipts = load_predictor_receipts(PILOT_RECEIPTS)
    assert len(receipts) == 15


def test_pilot_receipts_include_explicit_rejected_circular_evidence():
    receipts = load_predictor_receipts(PILOT_RECEIPTS)
    rejected = [r for r in receipts if r["adjudication_status"] == "REJECTED"]
    assert len(rejected) == 5
    assert all(r["outcome_independence"] == "FALSE" for r in rejected)


def test_adjudicated_independent_values_do_not_use_rejected_or_screened_rows():
    receipts = load_predictor_receipts(PILOT_RECEIPTS)
    values = adjudicated_independent_values(receipts)

    assert values[("Polemonium_viscosum_macro", "functional_coupling")] == "HIGH"
    assert values[("Darwin_finches_beak_song_macro", "functional_coupling")] == "HIGH"
    assert values[("Homarus_claw_dimorphism_macro", "alternative_accessibility")] == "HIGH"
    assert values[("coGFP_dual_color_macro", "alternative_accessibility")] == "HIGH"
    assert values[("coGFP_dual_color_macro", "functional_coupling")] == "HIGH"

    assert ("Solanum_rostratum_heteranthery_macro", "alternative_accessibility") not in values
    assert ("Yeast_GAL1_GAL3_macro", "alternative_accessibility") not in values
    assert ("Salmonella_HisA_TrpF_macro", "alternative_accessibility") not in values


def test_no_pilot_cluster_is_confirmatory_ready_before_macro_row_adjudication():
    rows = load_macro_ledger(PILOT_MACRO)
    receipts = load_predictor_receipts(PILOT_RECEIPTS)
    assert confirmatory_h1_h2_clusters(rows, receipts) == []

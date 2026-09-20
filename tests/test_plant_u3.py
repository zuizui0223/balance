from pathlib import Path

from balance_domain.plant_u3 import build_u3_readout, load_u3_universe


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"


def test_u3_exact_16_family_review_universe_validates():
    rows = load_u3_universe(U3)
    assert len(rows) == 16
    assert len({r["family"] for r in rows}) == 16
    assert len({r["order_apg3"] for r in rows}) == 12


def test_u3_contains_scrophulariaceae_not_bignoniaceae():
    rows = load_u3_universe(U3)
    families = {r["family"] for r in rows}
    assert "Scrophulariaceae" in families
    assert "Bignoniaceae" not in families


def test_u3_is_explicitly_positive_architecture_discovery_not_denominator():
    readout = build_u3_readout(U3)
    assert readout["n_family_cases"] == 16
    assert readout["n_orders"] == 12
    assert readout["matched_control_layer_ready"] is False
    assert readout["confirmatory_denominator_ready"] is False
    assert "not_prevalence" in readout["claim_ceiling"]


def test_u3_body_text_resolves_some_but_not_all_representative_taxa():
    readout = build_u3_readout(U3)
    assert readout["n_body_text_representative_families"] == 11
    assert readout["n_table_s1_representative_pending"] == 5

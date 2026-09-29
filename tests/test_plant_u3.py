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
    families = {r["family"] for r in load_u3_universe(U3)}
    assert "Scrophulariaceae" in families
    assert "Bignoniaceae" not in families


def test_u3_is_explicitly_positive_architecture_discovery_not_denominator():
    readout = build_u3_readout(U3)
    assert readout["n_family_cases"] == 16
    assert readout["n_orders"] == 12
    assert readout["matched_control_layer_ready"] is False
    assert readout["confirmatory_denominator_ready"] is False
    assert "not_prevalence" in readout["claim_ceiling"]


def test_u3_representative_taxa_keep_provenance_classes_separate():
    readout = build_u3_readout(U3)
    assert readout["n_body_text_representative_families"] == 11
    assert readout["n_independently_resolved_representative_families"] == 5
    assert readout["n_postreview_independently_resolved_representative_families"] == 0
    assert readout["n_total_resolved_representative_families"] == 16
    assert readout["n_table_s1_representative_pending"] == 0


def test_pre2010_independent_resolutions_do_not_claim_table_s1_access():
    rows = {r["family"]: r for r in load_u3_universe(U3)}
    assert rows["Lythraceae"]["representative_taxa"] == "Lagerstroemia indica"
    assert rows["Brassicaceae"]["representative_taxa"] == "Brassica rapa"
    assert rows["Bixaceae"]["representative_taxa"] == "Amoreuxia wrightii"
    assert rows["Malvaceae"]["representative_taxa"] == "Mollia lepidota"
    assert rows["Scrophulariaceae"]["representative_taxa"] == "Diascia anastrepta"
    for family in ("Lythraceae", "Brassicaceae", "Bixaceae", "Malvaceae", "Scrophulariaceae"):
        assert rows[family]["representative_taxa_status"] == "SOURCE_RESOLVED_INDEPENDENTLY"
        assert "Table S1" in rows[family]["notes"]


def test_scrophulariaceae_is_pre2010_independently_resolved():
    rows = {r["family"]: r for r in load_u3_universe(U3)}
    row = rows["Scrophulariaceae"]
    assert row["representative_taxa"] == "Diascia anastrepta"
    assert row["representative_taxa_status"] == "SOURCE_RESOLVED_INDEPENDENTLY"
    assert "Manning & Brothers 1986" in row["notes"]
    assert "not Table S1 transcription" in row["notes"]


def test_no_family_representative_remains_pending():
    rows = {r["family"]: r for r in load_u3_universe(U3)}
    pending = {
        family
        for family, row in rows.items()
        if row["representative_taxa_status"] == "TABLE_S1_REPRESENTATIVE_PENDING"
    }
    assert pending == set()
    malv = rows["Malvaceae"]
    assert malv["representative_taxa"] == "Mollia lepidota"
    assert malv["representative_taxa_status"] == "SOURCE_RESOLVED_INDEPENDENTLY"
    assert "not Table S1 transcription" in malv["notes"]

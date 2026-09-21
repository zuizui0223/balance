from pathlib import Path

from balance_domain.plant_u4 import build_u4_readout, load_u4_cases


ROOT = Path(__file__).resolve().parents[1]
U4 = ROOT / "data" / "BALANCE_PLANT_U4_CARNIVOROUS_CASES_V1.csv"


def test_u4_case_series_validates():
    rows = load_u4_cases(U4)
    assert len(rows) == 10
    assert len({r["dependency_group"] for r in rows}) == 10


def test_u4_retains_positive_negative_and_unresolved_conflict_states():
    rows = load_u4_cases(U4)
    states = {r["conflict_status"] for r in rows}
    assert states == {"POSITIVE", "NO_DEMONSTRATED_CONFLICT", "UNRESOLVED"}


def test_u4_exposes_signal_separation_as_distinct_mode():
    rows = load_u4_cases(U4)
    aur = next(r for r in rows if r["system_taxon"] == "Drosera auriculata")
    assert aur["architecture_mode"] == "SIGNAL_SEPARATION"
    assert aur["structural_module_division"] == "false"


def test_u4_direct_positive_cases_are_pinguicula_and_hookeri():
    readout = build_u4_readout(U4)
    assert readout["n_positive_conflict"] == 2
    assert readout["positive_taxa"] == [
        "Drosera hookeri",
        "Pinguicula vallisneriifolia",
    ]


def test_u4_is_never_a_prevalence_or_primary_model_dataset():
    readout = build_u4_readout(U4)
    assert "not_prevalence" in readout["claim_ceiling"]
    assert "not_primary_model_eligible" in readout["claim_ceiling"]

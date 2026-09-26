from pathlib import Path

from balance_domain.plant_u2_architecture import (
    build_u2_architecture_readout,
    load_u2_architecture_handoff,
)


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "data" / "BALANCE_PLANT_U2_ARCHITECTURE_HANDOFF_V1.csv"


def test_u2_architecture_handoff_contains_only_positive_conflict_groups():
    rows = load_u2_architecture_handoff(HANDOFF)
    assert len(rows) == 8
    assert all(r["conflict_status"] == "POSITIVE" for r in rows)


def test_u2_architecture_handoff_keeps_natural_and_experimental_states_separate():
    rows = load_u2_architecture_handoff(HANDOFF)
    eich = next(r for r in rows if r["dependency_group"] == "Eichhornia_paniculata")
    assert eich["natural_architecture_mode"] == "SHARED_INTEGRATED"
    assert eich["experimental_alternative_mode"] == "AMONG_FLOWER_MODULE_DIVISION"
    assert eich["resolution_causal_status"] == "DIRECT_EXPERIMENTAL_ALTERNATIVE"


def test_mimulus_has_direct_causal_resolution_evidence():
    rows = load_u2_architecture_handoff(HANDOFF)
    mim = next(r for r in rows if r["dependency_group"] == "Mimulus_aurantiacus")
    assert mim["natural_architecture_mode"] == "SPATIAL_SEPARATION"
    assert mim["resolution_causal_status"] == "DIRECT_CAUSAL_RESOLUTION"


def test_u2_direct_resolution_evidence_is_sparse():
    readout = build_u2_architecture_readout(HANDOFF)
    assert readout["n_positive_conflict_groups"] == 8
    assert readout["n_direct_resolution_evidence"] == 2
    assert readout["n_architecture_unresolved"] == 4
    assert readout["resolution_causal_status_counts"] == {
        "CONCORDANT_NOT_CAUSAL": 2,
        "DIRECT_CAUSAL_RESOLUTION": 1,
        "DIRECT_EXPERIMENTAL_ALTERNATIVE": 1,
        "NOT_IDENTIFIED": 4,
    }

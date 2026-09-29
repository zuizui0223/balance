from pathlib import Path

from balance_domain.plant_cross_universe_dependence import (
    build_cross_universe_dependence_readout,
    canonicalize_taxon,
    validate_overlap_registry,
)


ROOT = Path(__file__).resolve().parents[1]
U1 = ROOT / "data" / "BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv"
U2 = ROOT / "data" / "BALANCE_PLANT_U2_BARRETT_REVIEW_UNIVERSE_V1.csv"
U3_CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
U3_PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
U3_DEP = ROOT / "data" / "BALANCE_PLANT_U3_DEPENDENCE_V1.csv"
OVERLAP = ROOT / "data" / "BALANCE_PLANT_CROSS_UNIVERSE_OVERLAP_V2.csv"


def _readout():
    return build_cross_universe_dependence_readout(
        U1, U2, U3_CASES, U3_PAIRS, U3_DEP
    )


def test_canonicalizer_removes_historical_parenthetical_annotation():
    assert canonicalize_taxon(
        "Chamaecrista fasciculata (Todd: Cassia chamaecrista)"
    ) == "chamaecrista fasciculata"


def test_union_has_81_occurrences_but_77_exact_taxon_units():
    out = _readout()
    assert out["n_occurrence_rows"] == 81
    assert out["n_unique_canonical_taxa"] == 77
    assert out["n_repeated_exact_taxon_groups"] == 4
    assert out["n_cross_universe_same_species_groups"] == 3
    assert out["outcome_blind"] is True


def test_cross_universe_same_species_groups_are_exactly_frozen():
    out = _readout()
    by_taxon = {r["canonical_taxon"]: r for r in out["repeated_taxon_receipts"]}
    assert set(by_taxon) == {
        "ipomopsis aggregata",
        "mimulus aurantiacus",
        "monochoria australasica",
        "solanum rostratum",
    }
    assert by_taxon["ipomopsis aggregata"]["universe_membership"] == ["U1", "U2"]
    assert by_taxon["mimulus aurantiacus"]["universe_membership"] == ["U1", "U2"]
    assert by_taxon["solanum rostratum"]["universe_membership"] == ["U2", "U3_CASE"]
    assert by_taxon["solanum rostratum"]["u3_dependence_blocks"] == [
        "U3_DEP_SOLANUM_01"
    ]


def test_monochoria_shared_control_is_retained_as_same_taxon_dependence():
    out = _readout()
    row = next(
        r for r in out["repeated_taxon_receipts"]
        if r["canonical_taxon"] == "monochoria australasica"
    )
    assert row["dependence_kind"] == "REUSED_CONTROL_SAME_SPECIES"
    assert row["occurrence_count"] == 2
    assert row["u3_dependence_blocks"] == ["U3_DEP_MONOCHORIA_01"]


def test_frozen_overlap_registry_matches_live_source_universes():
    out = validate_overlap_registry(
        OVERLAP, U1, U2, U3_CASES, U3_PAIRS, U3_DEP
    )
    assert out["n_unique_canonical_taxa"] == 77
    assert out["dependence_rule"] == "CLUSTER_SAME_TAXON_DO_NOT_COUNT_AS_INDEPENDENT"


def test_dependence_certificate_does_not_claim_phylogenetic_covariance():
    out = _readout()
    assert "not_phylogenetic_covariance" in out["claim_ceiling"]
    assert "not_final_model_membership" in out["claim_ceiling"]

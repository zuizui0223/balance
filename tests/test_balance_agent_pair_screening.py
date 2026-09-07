import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "BALANCE_QUANT_SOURCE_REGISTRY_V1.csv"
SCREENING = ROOT / "data" / "BALANCE_AGENT_PAIR_SCREENING_V1.csv"


def _rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_caruso_nonduplicated_database_is_primary_search_universe():
    rows = {row["source_key"]: row for row in _rows(SOURCES)}
    caruso = rows["CARUSO_FLORAL_SELECTION_2019"]
    assert caruso["data_doi"] == "10.5061/dryad.2v8c5g0"
    assert "755_beta_plus_SE_records" in caruso["public_scope"]
    assert "36_articles" in caruso["public_scope"]
    assert caruso["screening_role"] == "PRIMARY_FLORAL_SELECTION_SEARCH_UNIVERSE"
    assert caruso["current_status"] == "METADATA_VERIFIED_NON_DUP_FILE_INGEST_PENDING"


def test_duplicated_caruso_workbook_is_never_independent_inventory():
    rows = {row["source_key"]: row for row in _rows(SOURCES)}
    duplicated = rows["CARUSO_FLORAL_DUPLICATED_2019"]
    assert duplicated["screening_role"] == "DEPENDENCE_AUDIT_ONLY"
    assert duplicated["current_status"] == "DO_NOT_USE_AS_INDEPENDENT_SOURCE_INVENTORY"


def test_candidate_expansion_sources_are_registered_with_bounded_roles():
    rows = {row["source_key"]: row for row in _rows(SOURCES)}
    assert rows["IRWIN_IPOMOPSIS_2006"]["screening_role"] == "SOURCE_REANALYSIS_REQUIRED_AGENT_PAIR"
    assert rows["KOLB_PRIMULA_2010"]["screening_role"] == "SEED_PREDATOR_MODERATOR_CANDIDATE"
    assert rows["EHRLEN_PRIMULA_2012"]["screening_role"] == "COMPONENT_CONFLICT_CANDIDATE"
    assert rows["GALEN_CUBA_POLEMONIUM_2001"]["screening_role"] == "DIRECT_FUNCTION_CONFLICT_PATTERN_CANDIDATE"
    assert rows["GALEN_POLEMONIUM_2011"]["screening_role"] == "DOSAGE_CONFLICT_MECHANISM_CANDIDATE"


def test_seed_screening_contains_positive_boundary_and_unresolved_examples():
    rows = _rows(SCREENING)
    classes = {row["screening_class"] for row in rows}
    assert "OPPOSED_AGENT_PAIR" in classes
    assert "ONE_AGENT_NULL_OR_UNRESOLVED" in classes
    assert "AGENT_IDENTITY_UNRESOLVED_CONFLICT" in classes
    assert "SOURCE_REANALYSIS_REQUIRED" in classes
    opposed = [row for row in rows if row["screening_class"] == "OPPOSED_AGENT_PAIR"]
    assert {row["system_taxon"] for row in opposed} == {
        "Dalechampia scandens",
        "Castilleja linariaefolia",
        "Pedicularis rex",
    }


def test_ipomopsis_is_not_prelabelled_as_positive_conflict():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    ipo = rows["Q1_IPOMOPSIS_CAMPBELL2022"]
    assert ipo["screening_class"] == "ONE_AGENT_NULL_OR_UNRESOLVED"
    assert ipo["pattern_promotion_status"] == "NO_POSITIVE_PROMOTION"
    assert ipo["raw_data_status"] == "public"


def test_gymnadenia_requires_agent_identity_before_antagonist_promotion():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    gym = rows["Q1_GYMNADENIA_CHAPURLAT2019"]
    assert gym["directional_relation"] == "opposed_for_three_compounds"
    assert gym["second_agent_identity_status"] == "unresolved_from_abstract"
    assert gym["screening_class"] == "AGENT_IDENTITY_UNRESOLVED_CONFLICT"
    assert gym["effect_size_status"] == "AGENT_AUDIT_REQUIRED"
    assert gym["pattern_promotion_status"] == "NO_ANTAGONIST_PROMOTION"


def test_irwin_and_primula_candidates_remain_below_positive_pair_promotion():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    irwin = rows["Q1_IPOMOPSIS_IRWIN2006"]
    assert irwin["screening_class"] == "SOURCE_REANALYSIS_REQUIRED"
    assert irwin["directional_relation"] == "year_dependent_mixed"
    assert irwin["pattern_promotion_status"] == "NO_POSITIVE_PROMOTION"

    kolb = rows["Q1_PRIMULA_KOLB2010"]
    assert kolb["screening_class"] == "ONE_AGENT_NULL_OR_UNRESOLVED"
    assert kolb["pollinator_component_status"] == "NOT_JOINTLY_IDENTIFIED"

    ehrlen = rows["Q1_PRIMULA_EHRLEN2012"]
    assert ehrlen["screening_class"] == "SOURCE_REANALYSIS_REQUIRED"
    assert ehrlen["directional_relation"] == "opposed_component_paths"
    assert ehrlen["pattern_promotion_status"] == "NO_POLLINATOR_AGENT_PAIR_PROMOTION"


def test_polemonium_supports_pattern_upgrade_but_not_q1_pooling():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    pole = rows["Q1_POLEMONIUM_GALENCUBA2001"]
    assert pole["directional_relation"] == "opposed"
    assert pole["screening_class"] == "SOURCE_REANALYSIS_REQUIRED"
    assert pole["pattern_promotion_status"] == "R_PATTERN_UPGRADE_SUPPORTED"
    assert pole["effect_size_status"] == "NONSTANDARD_EFFECT_REANALYSIS_REQUIRED"


def test_no_seed_pair_is_effect_size_ready_by_construction():
    rows = _rows(SCREENING)
    assert all(row["effect_size_status"] != "EFFECT_SIZE_READY" for row in rows)

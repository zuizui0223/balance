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
    assert caruso["screening_role"] == "PRIMARY_FLORAL_SELECTION_SEARCH_UNIVERSE"


def test_duplicated_caruso_workbook_is_never_independent_inventory():
    rows = {row["source_key"]: row for row in _rows(SOURCES)}
    duplicated = rows["CARUSO_FLORAL_DUPLICATED_2019"]
    assert duplicated["screening_role"] == "DEPENDENCE_AUDIT_ONLY"
    assert duplicated["current_status"] == "DO_NOT_USE_AS_INDEPENDENT_SOURCE_INVENTORY"


def test_candidate_expansion_sources_keep_bounded_roles():
    rows = {row["source_key"]: row for row in _rows(SOURCES)}
    assert rows["IRWIN_IPOMOPSIS_2006"]["screening_role"] == "SOURCE_REANALYSIS_REQUIRED_AGENT_PAIR"
    assert rows["KOLB_PRIMULA_2010"]["screening_role"] == "SEED_PREDATOR_MODERATOR_CANDIDATE"
    assert rows["EHRLEN_PRIMULA_2012"]["screening_role"] == "COMPONENT_CONFLICT_CANDIDATE"
    assert rows["GALEN_CUBA_POLEMONIUM_2001"]["screening_role"] == "DIRECT_FUNCTION_CONFLICT_PATTERN_CANDIDATE"


def test_three_q1b_sources_are_effect_ready_with_distinct_provenance():
    rows = {row["source_key"]: row for row in _rows(SOURCES)}
    frag = rows["EGAN_FRAGARIA_2021"]
    imp = rows["GORDEN_ADLER_IMPATIENS_2018"]
    gym = rows["SLETVOLD_GYMNADENIA_2015"]

    assert frag["screening_role"] == "DIFFUSE_OPPOSED_AGENT_FACTORIAL_SOURCE"
    assert frag["current_status"] == "TABLE_S2_S3_REPORTED_JOINT_COVARIANCE_RECONSTRUCTED_EFFECT_READY"
    assert imp["screening_role"] == "DIFFUSE_OPPOSED_AGENT_FACTORIAL_SOURCE"
    assert imp["current_status"] == "RAW_PLANT_STRATIFIED_BOOTSTRAP_JOINT_MULTICONTRAST_READY"
    assert gym["screening_role"] == "DIFFUSE_OPPOSED_AGENT_FACTORIAL_SOURCE"
    assert gym["current_status"] == "ESA_TABLE_A2_REPORTED_CONTRAST_COVARIANCE_RECONSTRUCTED_EFFECT_READY"
    assert "four_independent_treatment_group" in gym["public_scope"]
    assert {frag["publication_doi"], imp["publication_doi"], gym["publication_doi"]} == {
        "10.1002/evl3.262", "10.1002/ajb2.1182", "10.1890/14-0119.1"
    }


def test_simple_q1_keeps_three_non_q1b_opposed_agent_pairs():
    rows = _rows(SCREENING)
    opposed = [row for row in rows if row["screening_class"] == "OPPOSED_AGENT_PAIR"]
    assert {row["system_taxon"] for row in opposed} == {
        "Dalechampia scandens", "Castilleja linariaefolia", "Pedicularis rex"
    }


def test_gymnadenia_is_now_effect_ready_diffuse_q1b():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    gym = rows["Q1B_GYMNADENIA_SLETVOLD2015"]
    assert gym["trait_coordinate"] == "flowering_start_phenology"
    assert gym["second_agent_type"] == "herbivore"
    assert gym["same_fitness_interpretation_status"] == "common_female_fitness_factorial"
    assert gym["directional_relation"] == "opposed_pollinators_later_herbivores_earlier"
    assert gym["screening_class"] == "OPPOSED_AGENT_PAIR_DIFFUSE_FACTORIAL"
    assert gym["effect_size_status"] == "EFFECT_SIZE_READY_REPORTED_FACTORIAL_RECONSTRUCTION"
    assert "Table_A2_SE_reconstruction" in gym["covariance_status"]
    assert "P|H=0.1558" in gym["notes"]


def test_fragaria_is_effect_ready_diffuse_q1b():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    frag = rows["Q1B_FRAGARIA_EGAN2021"]
    assert frag["screening_class"] == "OPPOSED_AGENT_PAIR_DIFFUSE_FACTORIAL"
    assert frag["effect_size_status"] == "EFFECT_SIZE_READY_REPORTED_FACTORIAL_RECONSTRUCTION"
    assert frag["pattern_promotion_status"] == "R_PATTERN_PROMOTION_SUPPORTED"
    assert "no zero-covariance assumption" in frag["notes"]


def test_factorial_negative_controls_remain_outside_positive_q1b():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    tri = rows["Q1B_TRIFOLIUM_SANTANGELO2018"]
    lyt = rows["Q1B_LYTHRUM_THOMSEN2017"]
    assert tri["pattern_promotion_status"] == "NO_POSITIVE_PROMOTION"
    assert tri["effect_size_status"] == "NEGATIVE_CONTROL_REANALYSIS_READY"
    assert lyt["pattern_promotion_status"] == "NO_POSITIVE_PROMOTION"
    assert lyt["effect_size_status"] == "NEGATIVE_CONTROL_SOURCE_REPORTED"


def test_primula_discrete_morph_remains_separate_estimand():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    prim = rows["Q1M_PRIMULA_FARINOSA_AGREN2013"]
    assert prim["screening_class"] == "OPPOSED_AGENT_PAIR_DISCRETE_MORPH"
    assert prim["effect_size_status"] == "SEPARATE_DISCRETE_MORPH_ESTIMAND_REQUIRED"
    assert prim["pattern_promotion_status"] == "NO_Q1_OR_Q1B_POOLING_PROMOTION"


def test_gymnadenia_2019_residual_nonpollinator_result_is_not_antagonist_q1():
    source_rows = {row["source_key"]: row for row in _rows(SOURCES)}
    source = source_rows["CHAPURLAT_GYMNADENIA_2019"]
    assert source["screening_role"] == "RESIDUAL_NONPOLLINATOR_SELECTION_NOT_ANTAGONIST_Q1"
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    gym = rows["Q1_GYMNADENIA_CHAPURLAT2019"]
    assert gym["effect_size_status"] == "NOT_Q1_ANTAGONIST_ELIGIBLE"
    assert gym["pattern_promotion_status"] == "NO_ANTAGONIST_PROMOTION"


def test_ipomopsis_and_primula_veris_candidates_remain_below_positive_promotion():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    assert rows["Q1_IPOMOPSIS_CAMPBELL2022"]["pattern_promotion_status"] == "NO_POSITIVE_PROMOTION"
    assert rows["Q1_IPOMOPSIS_IRWIN2006"]["pattern_promotion_status"] == "NO_POSITIVE_PROMOTION"
    assert rows["Q1_PRIMULA_KOLB2010"]["pollinator_component_status"] == "NOT_JOINTLY_IDENTIFIED"
    assert rows["Q1_PRIMULA_EHRLEN2012"]["pattern_promotion_status"] == "NO_POLLINATOR_AGENT_PAIR_PROMOTION"


def test_polemonium_supports_pattern_upgrade_but_not_q1_pooling():
    rows = {row["screen_id"]: row for row in _rows(SCREENING)}
    pole = rows["Q1_POLEMONIUM_GALENCUBA2001"]
    assert pole["directional_relation"] == "opposed"
    assert pole["pattern_promotion_status"] == "R_PATTERN_UPGRADE_SUPPORTED"
    assert pole["effect_size_status"] == "NONSTANDARD_EFFECT_REANALYSIS_REQUIRED"


def test_screening_table_has_two_reported_effect_ready_q1b_rows_and_impatiens_is_raw_receipt_elsewhere():
    rows = _rows(SCREENING)
    ready = [row for row in rows if row["effect_size_status"] == "EFFECT_SIZE_READY_REPORTED_FACTORIAL_RECONSTRUCTION"]
    assert {row["system_taxon"] for row in ready} == {"Fragaria vesca", "Gymnadenia conopsea"}
    # Impatiens is not duplicated here: its effect-ready status is carried by the raw-bootstrap receipt/source registry.
    source_rows = {row["source_key"]: row for row in _rows(SOURCES)}
    assert source_rows["GORDEN_ADLER_IMPATIENS_2018"]["current_status"] == "RAW_PLANT_STRATIFIED_BOOTSTRAP_JOINT_MULTICONTRAST_READY"

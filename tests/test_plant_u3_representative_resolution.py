from pathlib import Path

import json
import pytest

from balance_domain.plant_u3_representative_resolution import (
    build_u3_representative_resolution_readout,
    load_u3_representative_resolution,
)


ROOT = Path(__file__).resolve().parents[1]
RESOLUTION = ROOT / "data" / "BALANCE_PLANT_U3_REPRESENTATIVE_RESOLUTION_V3.json"
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CANDIDATES = ROOT / "data" / "BALANCE_PLANT_U3_REPRESENTATIVE_CANDIDATE_AUDIT_V1.csv"


def test_canonical_rep_coverage_is_closed_while_exact_table_s1_identity_is_open():
    out = build_u3_representative_resolution_readout(
        RESOLUTION, UNIVERSE, CANDIDATES
    )
    assert out["canonical_representative_coverage_closed"] is True
    assert out["n_canonical_representative_families"] == 16
    assert out["exact_table_s1_identity_closed"] is False
    assert out["exact_table_s1_identity_unrecovered_families"] == [
        "Bixaceae",
        "Malvaceae",
        "Scrophulariaceae",
    ]
    assert out["exact_table_s1_identity_blocks_current_u3_analysis"] is False


def test_resolution_receipt_matches_canonical_three_family_representatives():
    payload = load_u3_representative_resolution(
        RESOLUTION, UNIVERSE, CANDIDATES
    )
    assert payload["resolutions"]["Malvaceae"]["representative"] == "Mollia lepidota"
    assert payload["resolutions"]["Bixaceae"]["representative"] == "Amoreuxia wrightii"
    assert (
        payload["resolutions"]["Scrophulariaceae"]["representative"]
        == "Diascia anastrepta"
    )
    assert all(
        payload["resolutions"][family]["table_s1_identity_claim"] is False
        for family in ("Malvaceae", "Bixaceae", "Scrophulariaceae")
    )


def test_exact_table_identity_cannot_silently_be_called_closed(tmp_path):
    payload = json.loads(RESOLUTION.read_text(encoding="utf-8"))
    payload["exact_table_s1_identity_closed"] = True
    path = tmp_path / "resolution.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="must remain explicitly open"):
        load_u3_representative_resolution(path, UNIVERSE, CANDIDATES)


def test_archival_identity_cannot_be_reintroduced_as_analysis_blocker(tmp_path):
    payload = json.loads(RESOLUTION.read_text(encoding="utf-8"))
    payload["exact_table_s1_identity_blocks_current_u3_analysis"] = True
    path = tmp_path / "resolution.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="must not be a current U3 analysis gate"):
        load_u3_representative_resolution(path, UNIVERSE, CANDIDATES)


def test_scrophulariaceae_uses_pre2010_independent_representative():
    payload = load_u3_representative_resolution(
        RESOLUTION, UNIVERSE, CANDIDATES
    )
    row = payload["resolutions"]["Scrophulariaceae"]
    assert row["representative"] == "Diascia anastrepta"
    assert row["status"] == "SOURCE_RESOLVED_INDEPENDENTLY"
    assert row["table_s1_identity_claim"] is False
    assert any("Manning & Brothers 1986" in item for item in row["evidence"])

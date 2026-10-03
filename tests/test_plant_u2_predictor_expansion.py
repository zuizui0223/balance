import csv
import json
from pathlib import Path

import pytest

from balance_domain.plant_confirmatory import load_plant_predictor_receipts
from balance_domain.plant_predictor_expansion import (
    FIELDS,
    build_v2_predictor_receipts,
    load_expansion_coding,
    validate_expansion_return,
    validate_expansion_template,
    write_v2_predictor_receipts,
)


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data" / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_CODING_V2.csv"
SOURCE = ROOT / "data" / "BALANCE_PLANT_U2_PREDICTOR_EXPANSION_SOURCE_PACKET_V2.csv"
V1 = ROOT / "data" / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
REACHABILITY = ROOT / "data" / "BALANCE_PLANT_V4_GENERALITY_REACHABILITY_V1.json"


def _template():
    return validate_expansion_template(load_expansion_coding(TEMPLATE))


def _ceiling_return():
    rows = []
    for row in _template():
        rows.append({
            **row,
            "coding_status": "EVIDENCE_CEILING",
            "notes": "primary source does not support a resolved outcome-independent value",
        })
    return rows


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_expansion_template_is_exact_frozen_12_group_population():
    rows = _template()
    contract = json.loads(REACHABILITY.read_text(encoding="utf-8"))
    expected = sorted(
        contract["prospective_reopening_contract"]["expansion_group_ids"]
    )

    assert len(rows) == 36
    assert sorted({row["cluster_id"] for row in rows}) == expected
    assert all(row["coding_status"] == "UNSTARTED" for row in rows)
    assert all(row["reported_value"] == "UNRESOLVED" for row in rows)
    assert all(row["evidence_type"] == "UNCLEAR" for row in rows)
    assert all(row["outcome_independence"] == "UNCERTAIN" for row in rows)

    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    assert len(source_rows) == 12
    assert sorted(row["dependency_group"] for row in source_rows) == expected
    assert all(
        "DO_NOT_VIEW_ARCHITECTURE_OUTPUTS_OR_CONFLICT_SCREEN_DECISIONS"
        in row["coder_instruction"]
        for row in source_rows
    )


def test_expansion_return_requires_all_36_slots_and_no_unstarted_rows():
    frozen = _template()
    with pytest.raises(ValueError, match="exactly match"):
        validate_expansion_return(frozen, _ceiling_return()[:-1])

    returned = _ceiling_return()
    returned[0]["coding_status"] = "UNSTARTED"
    with pytest.raises(ValueError, match="must end CODED or EVIDENCE_CEILING"):
        validate_expansion_return(frozen, returned)


def test_expansion_coded_row_requires_resolved_outcome_independent_source_evidence():
    frozen = _template()
    returned = _ceiling_return()
    returned[0].update({
        "coding_status": "CODED",
        "reported_value": "SINGLE_OR_CONTINUOUS",
        "evidence_type": "INTEGRATED_STATE_DESCRIPTION",
        "outcome_independence": "TRUE",
        "notes": "source-side baseline description",
    })
    validated = validate_expansion_return(frozen, returned)
    assert validated[0]["coding_status"] in {"CODED", "EVIDENCE_CEILING"}

    bad = [dict(row) for row in returned]
    coded = next(row for row in bad if row["coding_status"] == "CODED")
    coded["outcome_independence"] = "UNCERTAIN"
    with pytest.raises(ValueError, match="outcome_independence=TRUE"):
        validate_expansion_return(frozen, bad)


def test_expansion_evidence_ceiling_cannot_fill_predictor_value():
    frozen = _template()
    returned = _ceiling_return()
    returned[0]["reported_value"] = "SINGLE_OR_CONTINUOUS"
    with pytest.raises(ValueError, match="must remain UNRESOLVED"):
        validate_expansion_return(frozen, returned)


def test_expansion_cannot_rewrite_group_predictor_or_source_identity():
    frozen = _template()
    returned = _ceiling_return()
    returned[0]["source_id"] = "different source"
    with pytest.raises(ValueError, match="cannot modify frozen source_id"):
        validate_expansion_return(frozen, returned)


def test_v2_receipt_freeze_preserves_v1_and_overlays_only_expansion_slots(tmp_path):
    frozen = _template()
    returned = _ceiling_return()

    target = next(
        row for row in returned
        if row["predictor"] == "module_substrate"
    )
    target.update({
        "coding_status": "CODED",
        "reported_value": "SINGLE_OR_CONTINUOUS",
        "evidence_type": "INTEGRATED_STATE_DESCRIPTION",
        "outcome_independence": "TRUE",
        "notes": "source-side baseline supports one integrated substrate",
    })
    validated = validate_expansion_return(frozen, returned)
    v1 = load_plant_predictor_receipts(V1)
    v2 = build_v2_predictor_receipts(v1_rows=v1, expansion_rows=validated)

    assert len(v2) == len(v1) == 60
    v1_by_id = {row["receipt_id"]: row for row in v1}
    v2_by_id = {row["receipt_id"]: row for row in v2}

    for receipt_id, before in v1_by_id.items():
        after = v2_by_id[receipt_id]
        if before["reported_value"] != "UNRESOLVED":
            assert after == before

    updated = v2_by_id[target["receipt_id"]]
    assert updated["reported_value"] == "SINGLE_OR_CONTINUOUS"
    assert updated["outcome_independence"] == "TRUE"
    assert updated["adjudication_status"] == "SCREENED"
    assert updated["notes"].startswith("V2_PROSPECTIVE_EXPANSION_CODING:")

    path = tmp_path / "v2.csv"
    write_v2_predictor_receipts(path, v2)
    reloaded = load_plant_predictor_receipts(path)
    assert reloaded == v2



def test_expansion_return_requires_coder_specific_evidence_notes():
    frozen = _template()

    ceiling = _ceiling_return()
    ceiling[0]["notes"] = frozen[0]["notes"]
    with pytest.raises(ValueError, match="coder-specific ceiling notes"):
        validate_expansion_return(frozen, ceiling)

    coded = _ceiling_return()
    coded[0].update({
        "coding_status": "CODED",
        "reported_value": "SINGLE_OR_CONTINUOUS",
        "evidence_type": "INTEGRATED_STATE_DESCRIPTION",
        "outcome_independence": "TRUE",
        "notes": frozen[0]["notes"],
    })
    with pytest.raises(ValueError, match="coder-specific source-basis notes"):
        validate_expansion_return(frozen, coded)

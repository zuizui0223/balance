import csv

import pytest

from balance_domain.macro_predictors import (
    FIELDS,
    adjudicated_independent_values,
    confirmatory_h1_h2_clusters,
    load_predictor_receipts,
)


def _receipt(**updates):
    row = {
        "receipt_id": "r1",
        "cluster_id": "c1",
        "predictor": "alternative_accessibility",
        "reported_value": "HIGH",
        "source_id": "source_a",
        "evidence_type": "PRE_OUTCOME_MEASUREMENT",
        "outcome_independence": "TRUE",
        "adjudication_status": "ADJUDICATED",
        "notes": "",
    }
    row.update(updates)
    return row


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _macro(**updates):
    row = {
        "cluster_id": "c1",
        "adjudication_status": "ADJUDICATED",
        "multifunctionality_status": "YES",
        "conflict_status": "POSITIVE",
        "structural_differentiation": "true",
        "alternative_accessibility": "HIGH",
        "functional_coupling": "MEDIUM",
    }
    row.update(updates)
    return row


def test_outcome_derived_evidence_cannot_claim_independence(tmp_path):
    path = tmp_path / "receipts.csv"
    _write(
        path,
        [
            _receipt(
                evidence_type="OUTCOME_DERIVED",
                outcome_independence="TRUE",
            )
        ],
    )
    with pytest.raises(ValueError, match="must be marked outcome_independence=FALSE"):
        load_predictor_receipts(path)


def test_independent_adjudicated_receipts_must_agree():
    receipts = [
        _receipt(),
        _receipt(
            receipt_id="r2",
            source_id="source_b",
            reported_value="LOW",
        ),
    ]
    with pytest.raises(ValueError, match="conflicting independent adjudicated"):
        adjudicated_independent_values(receipts)


def test_screened_receipt_cannot_license_predictor():
    receipts = [_receipt(adjudication_status="SCREENED")]
    assert adjudicated_independent_values(receipts) == {}


def test_confirmatory_gate_requires_both_independent_h1_h2_receipts():
    receipts = [
        _receipt(),
        _receipt(
            receipt_id="r2",
            predictor="functional_coupling",
            reported_value="MEDIUM",
            evidence_type="INTEGRATED_STATE_EXPERIMENT",
        ),
    ]
    assert confirmatory_h1_h2_clusters([_macro()], receipts) == ["c1"]


def test_confirmatory_gate_fails_closed_when_one_predictor_is_missing():
    receipts = [_receipt()]
    assert confirmatory_h1_h2_clusters([_macro()], receipts) == []


def test_macro_and_receipt_values_must_match():
    receipts = [
        _receipt(),
        _receipt(
            receipt_id="r2",
            predictor="functional_coupling",
            reported_value="MEDIUM",
            evidence_type="INTEGRATED_STATE_EXPERIMENT",
        ),
    ]
    with pytest.raises(ValueError, match="macro ledger and independent receipt disagree"):
        confirmatory_h1_h2_clusters(
            [_macro(alternative_accessibility="LOW")],
            receipts,
        )

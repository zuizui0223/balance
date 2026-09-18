import csv

import pytest

from balance_domain.plant_macro_agreement import (
    FIELDS,
    build_agreement_report,
    load_double_coding,
)


def _row(cluster, coder, **updates):
    row = {
        "cluster_id": cluster,
        "coder_id": coder,
        "conflict_status": "POSITIVE",
        "architecture_mode": "SHARED_INTEGRATED",
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
        "notes": "",
    }
    row.update(updates)
    return row


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_perfect_agreement_is_one(tmp_path):
    path = tmp_path / "double.csv"
    _write(
        path,
        [
            _row("a", "A"),
            _row("a", "B"),
            _row("b", "A", architecture_mode="TEMPORAL_SEPARATION"),
            _row("b", "B", architecture_mode="TEMPORAL_SEPARATION"),
        ],
    )
    report = build_agreement_report(path)
    for stats in report["fields"].values():
        assert stats["raw_agreement"] == 1.0
        assert stats["cohen_kappa"] == 1.0
        assert stats["gwet_ac1"] == 1.0
        assert stats["codebook_repair_trigger"] is False


def test_disagreements_are_named_and_trigger_repair(tmp_path):
    path = tmp_path / "double.csv"
    _write(
        path,
        [
            _row("a", "A"),
            _row("a", "B", conflict_status="UNRESOLVED"),
            _row("b", "A"),
            _row("b", "B"),
            _row("c", "A"),
            _row("c", "B"),
            _row("d", "A"),
            _row("d", "B"),
        ],
    )
    report = build_agreement_report(path)
    conflict = report["fields"]["conflict_status"]
    assert conflict["raw_agreement"] == 0.75
    assert conflict["disagreement_clusters"] == ["a"]
    assert conflict["codebook_repair_trigger"] is True


def test_exactly_two_coders_are_required(tmp_path):
    path = tmp_path / "double.csv"
    _write(path, [_row("a", "A"), _row("a", "B"), _row("b", "C")])
    with pytest.raises(ValueError, match="exactly two coder IDs"):
        build_agreement_report(path)


def test_each_cluster_requires_both_coders(tmp_path):
    path = tmp_path / "double.csv"
    _write(path, [_row("a", "A"), _row("a", "B"), _row("b", "A")])
    with pytest.raises(ValueError, match="exactly two independent coder rows"):
        build_agreement_report(path)


def test_duplicate_cluster_coder_pair_is_rejected(tmp_path):
    path = tmp_path / "double.csv"
    _write(path, [_row("a", "A"), _row("a", "A")])
    with pytest.raises(ValueError, match="duplicate cluster/coder pair"):
        load_double_coding(path)

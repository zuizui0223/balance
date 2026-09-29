import csv
from pathlib import Path

import pytest

from balance_domain.plant_coder_return import (
    load_single_coder_return,
    merge_coder_returns,
    write_merged_coder_returns,
)
from balance_domain.plant_macro_agreement import FIELDS
from balance_domain.plant_u6 import PASS2_FIELDS


ROOT = Path(__file__).resolve().parents[1]
U1_SAMPLE = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"
U2_SAMPLE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"
U6_FREEZE = ROOT / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"


def _groups_from_csv(path, field):
    with path.open(encoding="utf-8", newline="") as handle:
        return [row[field] for row in csv.DictReader(handle)]


def _write_return(path, groups, coder_id):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for i, group in enumerate(groups):
            writer.writerow({
                "cluster_id": group,
                "coder_id": coder_id,
                "conflict_status": "POSITIVE" if i % 2 == 0 else "NO_DEMONSTRATED_CONFLICT",
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "notes": "",
            })


def _write_u6_return(path, manifest, coder_id, *, coding_status="CODED"):
    groups = manifest["included_dependency_groups"]
    source_map = manifest["source_reference_ids_by_dependency_group"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PASS2_FIELDS, lineterminator="\n")
        writer.writeheader()
        for group in groups:
            writer.writerow({
                "dependency_group": group,
                "source_reference_ids": ";".join(source_map[group]),
                "coder_id": coder_id,
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "coding_status": coding_status,
                "notes": "",
            })


def test_u1_returns_merge_only_when_both_coders_cover_frozen_20_groups(tmp_path):
    groups = _groups_from_csv(U1_SAMPLE, "dependency_group")
    a = tmp_path / "u1_a.csv"
    b = tmp_path / "u1_b.csv"
    _write_return(a, groups, "CODER_A")
    _write_return(b, groups, "CODER_B")

    merged = merge_coder_returns(
        lane="U1",
        coder_a_path=a,
        coder_b_path=b,
        u1_sample_path=U1_SAMPLE,
    )
    assert len(merged) == 40
    assert [row["cluster_id"] for row in merged[::2]] == sorted(groups)
    assert all(merged[i]["coder_id"] == "CODER_A" for i in range(0, 40, 2))
    assert all(merged[i]["coder_id"] == "CODER_B" for i in range(1, 40, 2))


def test_u2_single_return_rejects_missing_or_extra_frozen_group(tmp_path):
    groups = _groups_from_csv(U2_SAMPLE, "dependency_group")
    bad = tmp_path / "u2_a.csv"
    _write_return(bad, groups[:-1] + ["OUT_OF_FRAME"], "CODER_A")
    with pytest.raises(ValueError, match="disagree with frozen frame"):
        load_single_coder_return(
            bad,
            lane="U2",
            coder_id="CODER_A",
            u2_sample_path=U2_SAMPLE,
        )


def test_u2_single_return_rejects_wrong_coder_identity(tmp_path):
    groups = _groups_from_csv(U2_SAMPLE, "dependency_group")
    bad = tmp_path / "u2_wrong.csv"
    _write_return(bad, groups, "CODER_B")
    with pytest.raises(ValueError, match="must contain only CODER_A"):
        load_single_coder_return(
            bad,
            lane="U2",
            coder_id="CODER_A",
            u2_sample_path=U2_SAMPLE,
        )


def test_u6_returns_require_native_schema_all_21_groups_and_coded_status(tmp_path):
    import json

    manifest = json.loads(U6_FREEZE.read_text(encoding="utf-8"))
    groups = manifest["included_dependency_groups"]
    a = tmp_path / "u6_a.csv"
    b = tmp_path / "u6_b.csv"
    _write_u6_return(a, manifest, "CODER_A")
    _write_u6_return(b, manifest, "CODER_B")

    merged = merge_coder_returns(
        lane="U6",
        coder_a_path=a,
        coder_b_path=b,
        u6_freeze_path=U6_FREEZE,
    )
    assert len(merged) == 42
    assert {row["dependency_group"] for row in merged} == set(groups)
    assert all(row["coding_status"] == "CODED" for row in merged)
    assert tuple(merged[0]) == PASS2_FIELDS


def test_u6_return_rejects_unstarted_coder_rows(tmp_path):
    import json

    manifest = json.loads(U6_FREEZE.read_text(encoding="utf-8"))
    bad = tmp_path / "u6_unstarted.csv"
    _write_u6_return(bad, manifest, "CODER_A", coding_status="UNSTARTED")
    with pytest.raises(ValueError, match="coding_status=CODED"):
        load_single_coder_return(
            bad,
            lane="U6",
            coder_id="CODER_A",
            u6_freeze_path=U6_FREEZE,
        )


def test_u6_merged_writer_preserves_native_pass2_schema(tmp_path):
    import json

    manifest = json.loads(U6_FREEZE.read_text(encoding="utf-8"))
    a = tmp_path / "u6_a.csv"
    b = tmp_path / "u6_b.csv"
    merged_path = tmp_path / "u6_merged.csv"
    _write_u6_return(a, manifest, "CODER_A")
    _write_u6_return(b, manifest, "CODER_B")
    merged = merge_coder_returns(
        lane="U6",
        coder_a_path=a,
        coder_b_path=b,
        u6_freeze_path=U6_FREEZE,
    )
    write_merged_coder_returns(merged_path, merged, lane="U6")
    with merged_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert tuple(reader.fieldnames or ()) == PASS2_FIELDS
        assert len(rows) == 42


def test_merged_return_writer_roundtrips_through_canonical_schema(tmp_path):
    groups = _groups_from_csv(U2_SAMPLE, "dependency_group")
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    out_path = tmp_path / "merged.csv"
    _write_return(a, groups, "CODER_A")
    _write_return(b, groups, "CODER_B")

    merged = merge_coder_returns(
        lane="U2",
        coder_a_path=a,
        coder_b_path=b,
        u2_sample_path=U2_SAMPLE,
    )
    write_merged_coder_returns(out_path, merged)
    with out_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        assert tuple(rows[0]) == FIELDS
        assert len(rows) == 40

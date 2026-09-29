"""Validate and merge returned independent-coder worksheets for BALANCE plants."""
from __future__ import annotations

import csv
from pathlib import Path

from .plant_macro_agreement import FIELDS, load_double_coding
from .plant_u1 import load_u1_sample
from .plant_u2 import load_u2_double_code_sample
from .plant_u6 import load_u6_pass1_freeze_manifest


LANES = {"U1", "U2", "U6"}
CODERS = {"CODER_A", "CODER_B"}


def _expected_groups(
    lane: str,
    *,
    u1_sample_path: Path | None = None,
    u2_sample_path: Path | None = None,
    u6_freeze_path: Path | None = None,
) -> list[str]:
    if lane == "U1":
        if u1_sample_path is None:
            raise ValueError("U1 coder return requires u1_sample_path")
        return sorted(row["dependency_group"] for row in load_u1_sample(u1_sample_path))
    if lane == "U2":
        if u2_sample_path is None:
            raise ValueError("U2 coder return requires u2_sample_path")
        return sorted(
            row["dependency_group"]
            for row in load_u2_double_code_sample(u2_sample_path)
        )
    if lane == "U6":
        if u6_freeze_path is None:
            raise ValueError("U6 coder return requires u6_freeze_path")
        return list(
            load_u6_pass1_freeze_manifest(u6_freeze_path)[
                "included_dependency_groups"
            ]
        )
    raise ValueError(f"unknown plant coding lane {lane!r}")


def load_single_coder_return(
    path: Path,
    *,
    lane: str,
    coder_id: str,
    u1_sample_path: Path | None = None,
    u2_sample_path: Path | None = None,
    u6_freeze_path: Path | None = None,
) -> list[dict[str, str]]:
    """Validate one completed return file against its frozen lane/coder identity."""
    if lane not in LANES:
        raise ValueError(f"unknown plant coding lane {lane!r}")
    if coder_id not in CODERS:
        raise ValueError(f"unknown coder_id {coder_id!r}")

    rows = load_double_coding(path)
    if {row["coder_id"] for row in rows} != {coder_id}:
        raise ValueError(
            f"{lane} return must contain only {coder_id}, found "
            f"{sorted({row['coder_id'] for row in rows})}"
        )

    expected = _expected_groups(
        lane,
        u1_sample_path=u1_sample_path,
        u2_sample_path=u2_sample_path,
        u6_freeze_path=u6_freeze_path,
    )
    observed = sorted(row["cluster_id"] for row in rows)
    if observed != sorted(expected):
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        raise ValueError(
            f"{lane} {coder_id} return groups disagree with frozen frame; "
            f"missing={missing}, extra={extra}"
        )
    if len(rows) != len(expected):
        raise ValueError(
            f"{lane} {coder_id} return must contain exactly one row per frozen group"
        )
    return rows


def merge_coder_returns(
    *,
    lane: str,
    coder_a_path: Path,
    coder_b_path: Path,
    u1_sample_path: Path | None = None,
    u2_sample_path: Path | None = None,
    u6_freeze_path: Path | None = None,
) -> list[dict[str, str]]:
    """Merge two validated independent returns into canonical lane order."""
    a = load_single_coder_return(
        coder_a_path,
        lane=lane,
        coder_id="CODER_A",
        u1_sample_path=u1_sample_path,
        u2_sample_path=u2_sample_path,
        u6_freeze_path=u6_freeze_path,
    )
    b = load_single_coder_return(
        coder_b_path,
        lane=lane,
        coder_id="CODER_B",
        u1_sample_path=u1_sample_path,
        u2_sample_path=u2_sample_path,
        u6_freeze_path=u6_freeze_path,
    )
    by_key = {
        (row["cluster_id"], row["coder_id"]): row
        for row in a + b
    }
    expected = _expected_groups(
        lane,
        u1_sample_path=u1_sample_path,
        u2_sample_path=u2_sample_path,
        u6_freeze_path=u6_freeze_path,
    )
    out = []
    for group in expected:
        for coder in ("CODER_A", "CODER_B"):
            key = (group, coder)
            if key not in by_key:
                raise ValueError(f"missing merged coder row {key!r}")
            out.append(by_key[key])
    return out


def write_merged_coder_returns(path: Path, rows: list[dict[str, str]]) -> None:
    """Write canonical merged ledger after validating exact schema."""
    if not rows:
        raise ValueError("cannot write empty merged coder ledger")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

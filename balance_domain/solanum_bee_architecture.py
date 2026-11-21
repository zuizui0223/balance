"""Authenticate the Wilkins et al. supplements and describe one trial per bee."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path
from statistics import mean, stdev
from tempfile import NamedTemporaryFile
from urllib.request import HTTPRedirectHandler, build_opener


SOURCE = (Path(__file__).resolve().parents[1] / "data" /
          "BALANCE_WILKINS_2022_SOURCE_V1.json")
CSV_NAME = "442_2022_5246_MOESM3_ESM.csv"
R_NAME = "442_2022_5246_MOESM2_ESM.r"
COUNTS = (
    "HeadPollen", "ThoraxPollen", "AbdomenPollen", "CorbiculaPollen",
    "AntherPollen", "StigmaPollen", "BodyPollen", "PollinatingPollen", "TotalPollen",
)
CONTINUOUS = ("HeadWidth", "VisitTime")
COLUMNS = {"BeeID", "ColonyID", "Treatment", *COUNTS, *CONTINUOUS}
ARCHITECTURES = {"Cone": "joined", "Sham": "free"}
FRACTIONS = ("body_only_fraction", "composite_fraction")
COMPONENTS = {
    "BodyPollen": ("HeadPollen", "ThoraxPollen", "AbdomenPollen"),
    "PollinatingPollen": ("BodyPollen", "StigmaPollen"),
    "TotalPollen": ("PollinatingPollen", "CorbiculaPollen"),
}


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Fetch only the two publisher URLs in the committed receipt.


def read_verified_file(path: Path, *, download: bool = False) -> bytes:
    """Return pinned bytes and cache a new download only after verification."""
    files = json.loads(SOURCE.read_text(encoding="utf-8"))["files"]
    identity = files[path.name]
    fetch = download and not path.exists()
    if fetch:
        with build_opener(_NoRedirects()).open(identity["url"], timeout=30) as response:
            contents = response.read(identity["bytes"] + 1)
    else:
        contents = path.read_bytes()
    if (
        len(contents) != identity["bytes"]
        or hashlib.sha256(contents).hexdigest() != identity["sha256"]
    ):
        raise ValueError(f"{path.name}: size or SHA-256 differs from the publisher supplement")
    if fetch:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = NamedTemporaryFile(dir=path.parent, delete=False)
        try:
            with temp:
                temp.write(contents)
            os.replace(temp.name, path)
        finally:
            Path(temp.name).unlink(missing_ok=True)
    return contents


def _trial(raw: dict, index: int) -> dict:
    if raw.keys() != COLUMNS or any(value is None for value in raw.values()):
        raise ValueError(f"trial {index}: missing or unexpected column")
    row = dict(raw)
    for field in ("BeeID", "ColonyID"):
        row[field] = raw[field].strip()
        if row[field].casefold() in {"", "na", "n/a", "nan", "null", "none"}:
            raise ValueError(f"trial {index}: missing {field}")
    if raw["Treatment"] not in ARCHITECTURES:
        raise ValueError(f"trial {index}: unknown Treatment")
    for field in (*COUNTS, *CONTINUOUS):
        value = raw[field].strip()
        if field in {"AntherPollen", "HeadWidth"} and value == "":
            row[field] = None
        elif field in COUNTS:
            if not (value.isascii() and value.isdecimal()):
                raise ValueError(f"trial {index}: invalid count {field}")
            row[field] = int(value)
        else:
            try:
                number = float(value)
            except ValueError as exc:
                raise ValueError(f"trial {index}: invalid {field}") from exc
            if not math.isfinite(number) or number <= 0:
                raise ValueError(f"trial {index}: invalid {field}")
            row[field] = number
    for total, parts in COMPONENTS.items():
        if row[total] != sum(row[k] for k in parts):
            raise ValueError(f"trial {index}: inconsistent {total}")
    body_total = row["BodyPollen"] + row["CorbiculaPollen"]
    row["body_only_fraction"] = row["BodyPollen"] / body_total if body_total else None
    row["composite_fraction"] = (
        row["PollinatingPollen"] / row["TotalPollen"] if row["TotalPollen"] else None
    )
    return row


def _summarize(rows: list[dict]) -> dict:
    descriptives = {}
    support = {}
    for field in (*COUNTS, *FRACTIONS, *CONTINUOUS):
        values = [r[field] for r in rows if r[field] is not None]
        n = len(values)
        descriptives[field] = {
            "n": n,
            "mean": mean(values) if n else None,
            "se": stdev(values) / math.sqrt(n) if n > 1 else None,
        }
        if field in CONTINUOUS:
            support[field] = {
                "n": n, "min": min(values, default=None), "max": max(values, default=None),
            }
    measured = [r for r in rows if r["HeadWidth"] is not None]
    # Logged outcomes and logged body load must be positive. A zero-count
    # binomial numerator is valid whenever the trial denominator is positive.
    eligible = {
        "anther": sum(r["AntherPollen"] is not None and r["AntherPollen"] > 0 for r in measured),
        "basket": sum(r["CorbiculaPollen"] > 0 for r in measured),
        "composite_count": sum(r["PollinatingPollen"] > 0 for r in measured),
        "composite_fraction": sum(r["composite_fraction"] is not None for r in measured),
        "stigma": sum(r["StigmaPollen"] > 0 and r["BodyPollen"] > 0 for r in measured),
        "body_only_count": sum(r["BodyPollen"] > 0 for r in measured),
        "body_only_fraction": sum(r["body_only_fraction"] is not None for r in measured),
    }
    return {
        "n_bees": len(rows),
        "n_colonies": len({r["ColonyID"] for r in rows}),
        "bees_by_colony": dict(sorted(Counter(r["ColonyID"] for r in rows).items())),
        "missing": {k: sum(r[k] is None for r in rows) for k in ("AntherPollen", "HeadWidth")},
        "descriptives": descriptives, "support": support, "model_eligible_bees": eligible,
    }


def audit_rows(rows) -> dict:
    """Audit trial structure and per-bee arithmetic independently of provenance."""
    bees = set()
    parsed = []
    groups = defaultdict(list)
    for index, raw in enumerate(rows, 2):
        row = _trial(raw, index)
        if row["BeeID"] in bees:
            raise ValueError(f"trial {index}: duplicate BeeID {row['BeeID']}")
        bees.add(row["BeeID"])
        parsed.append(row)
        groups[ARCHITECTURES[row["Treatment"]]].append(row)
    if not parsed:
        raise ValueError("no bee trials")
    return {
        "pooled": _summarize(parsed),
        "by_architecture": {k: _summarize(v) for k, v in sorted(groups.items())},
        "identity_checks": {"rows_checked": len(parsed), "components": COMPONENTS},
        "descriptive_unit": "One value per bee; SE is the sample SD divided by sqrt(n), without colony adjustment.",
        "fraction_definitions": {
            "body_only_fraction": "BodyPollen / (BodyPollen + CorbiculaPollen)",
            "composite_fraction": "PollinatingPollen / TotalPollen",
        },
    }


def audit_source(directory: Path, *, download: bool = False) -> dict:
    manifest = json.loads(SOURCE.read_text(encoding="utf-8"))
    sources = {
        name: read_verified_file(directory / name, download=download)
        for name in (R_NAME, CSV_NAME)
    }
    files = {
        name: {
            "url": manifest["files"][name]["url"],
            "bytes": len(contents),
            "sha256": hashlib.sha256(contents).hexdigest(),
        }
        for name, contents in sources.items()
    }
    with StringIO(sources[CSV_NAME].decode("utf-8-sig"), newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("missing or duplicate CSV column")
        result = audit_rows(reader)
    return {
        "status": "VERIFIED_PUBLISHER_SUPPLEMENTS_BEE_TRIAL_DESCRIPTIVES",
        "provenance": {"doi": manifest["article"]["doi"], "files": files},
        "design": manifest["design"],
        **result,
    }

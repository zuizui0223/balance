"""Fail-closed Crossref DOI discovery for the U1 production source inventory."""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

FIELDS = (
    "inventory_id",
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "figshare_article_id",
    "author",
    "title",
    "journal",
    "publication_year",
    "volume",
    "page",
    "identity_status",
    "content_status",
)
USER_AGENT = "BALANCE-U1-production-doi-audit/1.0 (+https://github.com/zuizui0223/balance)"


def normalize_title(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def title_similarity(expected: str, observed: str) -> float:
    return difflib.SequenceMatcher(
        None, normalize_title(expected), normalize_title(observed)
    ).ratio()


def _issued_year(item: dict) -> int | None:
    for key in ("published-print", "published-online", "issued"):
        parts = item.get(key, {}).get("date-parts")
        if parts and parts[0]:
            try:
                return int(parts[0][0])
            except (TypeError, ValueError):
                pass
    return None


def score_crossref_item(row: dict[str, str], item: dict) -> dict:
    titles = item.get("title") or []
    observed_title = titles[0] if titles else ""
    similarity = title_similarity(row["title"], observed_title)
    expected_year = int(row["publication_year"])
    observed_year = _issued_year(item)
    year_match = observed_year == expected_year
    doi = str(item.get("DOI") or "").strip().lower()
    accepted = bool(doi) and similarity >= 0.96 and year_match
    return {
        "doi": doi,
        "observed_title": observed_title,
        "observed_year": observed_year,
        "title_similarity": similarity,
        "year_match": year_match,
        "accepted": accepted,
    }


def load_inventory(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U1 production source inventory columns must match canonical order")
        rows = list(reader)
    if len(rows) != 30:
        raise ValueError("U1 production source inventory must contain 30 study occurrences")
    if len({r["inventory_id"] for r in rows}) != len(rows):
        raise ValueError("inventory_id must be unique")
    if {r["universe_record_id"] for r in rows} != {
        f"U1_{i:03d}" for i in range(21, 48)
    }:
        raise ValueError("inventory must cover exactly U1_021 through U1_047")
    return rows


def _query_crossref(title: str, year: int) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "query.title": title,
            "filter": f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31",
            "rows": 5,
        }
    )
    url = "https://api.crossref.org/works?" + query
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as response:  # noqa: S310
        payload = json.load(response)
    return payload.get("message", {}).get("items", [])


def run_audit(inventory_path: Path, output_path: Path) -> dict:
    rows = load_inventory(inventory_path)
    receipts = []
    for row in rows:
        receipt = {
            "inventory_id": row["inventory_id"],
            "universe_record_id": row["universe_record_id"],
            "taxon_raw": row["taxon_raw"],
            "figshare_article_id": row["figshare_article_id"],
            "expected_title": row["title"],
            "expected_year": int(row["publication_year"]),
        }
        try:
            items = _query_crossref(row["title"], int(row["publication_year"]))
            scored = sorted(
                (score_crossref_item(row, item) for item in items),
                key=lambda x: x["title_similarity"],
                reverse=True,
            )
            receipt["candidates"] = scored
            accepted = [x for x in scored if x["accepted"]]
            receipt["status"] = (
                "AUTO_ACCEPTED_EXACT_YEAR_HIGH_TITLE_MATCH"
                if len(accepted) == 1
                else "MANUAL_REVIEW_REQUIRED"
            )
            receipt["accepted_doi"] = accepted[0]["doi"] if len(accepted) == 1 else None
        except Exception as exc:  # pragma: no cover - network path
            receipt["status"] = "QUERY_ERROR"
            receipt["error"] = repr(exc)
            receipt["accepted_doi"] = None
            receipt["candidates"] = []
        receipts.append(receipt)
        time.sleep(0.15)

    accepted = [r for r in receipts if r["accepted_doi"]]
    unresolved = [r for r in receipts if not r["accepted_doi"]]
    out = {
        "analysis": "balance_u1_production_source_crossref_doi_audit_v1",
        "n_inventory_occurrences": len(rows),
        "n_auto_accepted_doi": len(accepted),
        "n_manual_or_error": len(unresolved),
        "auto_accepted": {
            r["inventory_id"]: r["accepted_doi"] for r in accepted
        },
        "unresolved_inventory_ids": [r["inventory_id"] for r in unresolved],
        "receipts": receipts,
        "acceptance_rule": (
            "exact publication year and normalized title similarity >= 0.96; "
            "exactly one candidate must pass"
        ),
        "claim_ceiling": (
            "doi_discovery_only_not_full_text_retrieval_not_evidence_coding_"
            "not_independent_double_coding"
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_audit(args.inventory, args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

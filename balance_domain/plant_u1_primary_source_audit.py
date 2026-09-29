"""Recover DOI and public full-text candidates for the remaining U1 primary studies.

The 27 U1 taxa outside the frozen reliability first-20 already have exact
Haas-Lortie Figshare article IDs. This audit joins those IDs to Study List.csv,
then queries Crossref conservatively for DOI identity and Unpaywall for OA
locations. Ambiguous title matches fail closed as REVIEW rather than being
promoted automatically.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

FIGSHARE_API_URL = "https://api.figshare.com/v2/articles/12397772"
USER_AGENT = "BALANCE-U1-primary-source-audit/1.0 (+https://github.com/zuizui0223/balance)"
MAILTO = "balance-audit@users.noreply.github.com"

MAP_FIELDS = (
    "universe_record_id",
    "dependency_group",
    "taxon_raw",
    "figshare_article_ids",
    "analysis_rows",
    "source_identity_status",
    "source_content_status",
    "mapping_basis",
    "notes",
)

OUTPUT_FIELDS = (
    "article_id",
    "mapped_taxa",
    "author",
    "title",
    "journal",
    "publication_year",
    "crossref_status",
    "crossref_doi",
    "crossref_title",
    "title_similarity",
    "crossref_score",
    "unpaywall_status",
    "is_oa",
    "oa_host_type",
    "oa_version",
    "oa_license",
    "oa_url_for_pdf",
    "oa_url_for_landing_page",
)

_SPACE = re.compile(r"\s+")
_NONALNUM = re.compile(r"[^a-z0-9]+")


def normalize_title(value: str) -> str:
    value = value.casefold().replace("&", " and ")
    value = _NONALNUM.sub(" ", value)
    return _SPACE.sub(" ", value).strip()


def title_similarity(left: str, right: str) -> float:
    a, b = normalize_title(left), normalize_title(right)
    if not a or not b:
        return 0.0
    seq = SequenceMatcher(None, a, b).ratio()
    sa, sb = set(a.split()), set(b.split())
    jaccard = len(sa & sb) / len(sa | sb) if sa | sb else 0.0
    return max(seq, jaccard)


def classify_crossref_match(similarity: float, year_delta: int | None) -> str:
    if similarity >= 0.93 and (year_delta is None or year_delta <= 1):
        return "RESOLVED"
    if similarity >= 0.80 and (year_delta is None or year_delta <= 2):
        return "REVIEW"
    return "NOT_RESOLVED"


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def _fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
    )
    with urllib.request.urlopen(req, timeout=45) as response:  # noqa: S310
        return response.read()


def _load_map(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != MAP_FIELDS:
            raise ValueError("U1 production-source map columns drifted")
        rows = list(reader)
    if len(rows) != 27:
        raise ValueError("U1 production-source audit requires exactly 27 mapped taxa")
    return rows


def _mapped_article_ids(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in rows:
        for article_id in row["figshare_article_ids"].split(";"):
            article_id = article_id.strip()
            if not article_id.isdigit():
                raise ValueError(f"invalid Figshare article id {article_id!r}")
            out.setdefault(article_id, []).append(row["taxon_raw"].strip())
    return {k: sorted(set(v)) for k, v in sorted(out.items(), key=lambda x: int(x[0]))}


def _study_list_bytes() -> tuple[bytes, dict]:
    payload = _fetch_json(FIGSHARE_API_URL)
    files = payload.get("files", [])
    file_info = next(
        (
            x
            for x in files
            if isinstance(x, dict)
            and str(x.get("name", "")).strip().casefold() == "study list.csv"
        ),
        None,
    )
    if not file_info or not file_info.get("download_url"):
        raise ValueError("Figshare dataset did not expose Study List.csv")
    data = _fetch_bytes(str(file_info["download_url"]))
    receipt = {
        "figshare_article_id": str(payload.get("id", "")),
        "dataset_doi": str(payload.get("doi", "")),
        "study_list_file_id": str(file_info.get("id", "")),
        "study_list_name": str(file_info.get("name", "")),
        "study_list_download_url": str(file_info.get("download_url", "")),
        "study_list_size_bytes": len(data),
    }
    return data, receipt


def parse_study_list(data: bytes) -> dict[str, dict[str, str]]:
    text = data.decode("utf-8-sig", errors="strict")
    reader = csv.DictReader(io.StringIO(text))
    required = {"article id", "author", "title", "journal", "publication year"}
    if not required.issubset(set(reader.fieldnames or ())):
        raise ValueError("Study List.csv is missing required identity columns")
    out = {}
    for row in reader:
        article_id = (row.get("article id") or "").strip()
        if article_id:
            out[article_id] = {
                "author": (row.get("author") or "").strip(),
                "title": (row.get("title") or "").strip(),
                "journal": (row.get("journal") or "").strip(),
                "publication_year": (row.get("publication year") or "").strip(),
            }
    return out


def _crossref_year(item: dict) -> int | None:
    for field in ("published-print", "published-online", "issued", "created"):
        value = item.get(field)
        if not isinstance(value, dict):
            continue
        parts = value.get("date-parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
            try:
                return int(parts[0][0])
            except (TypeError, ValueError):
                pass
    return None


def choose_crossref_candidate(
    study_title: str,
    publication_year: int | None,
    items: list[dict],
) -> dict:
    candidates = []
    for item in items:
        titles = item.get("title")
        candidate_title = titles[0] if isinstance(titles, list) and titles else ""
        similarity = title_similarity(study_title, str(candidate_title))
        cyear = _crossref_year(item)
        year_delta = (
            abs(cyear - publication_year)
            if cyear is not None and publication_year is not None
            else None
        )
        status = classify_crossref_match(similarity, year_delta)
        candidates.append(
            {
                "status": status,
                "doi": str(item.get("DOI") or ""),
                "title": str(candidate_title),
                "similarity": similarity,
                "crossref_score": float(item.get("score") or 0.0),
                "crossref_year": cyear,
                "year_delta": year_delta,
            }
        )
    if not candidates:
        return {
            "status": "NOT_RESOLVED",
            "doi": "",
            "title": "",
            "similarity": 0.0,
            "crossref_score": 0.0,
            "crossref_year": None,
            "year_delta": None,
        }
    rank = {"RESOLVED": 2, "REVIEW": 1, "NOT_RESOLVED": 0}
    return max(
        candidates,
        key=lambda x: (
            rank[x["status"]],
            x["similarity"],
            -999 if x["year_delta"] is None else -x["year_delta"],
            x["crossref_score"],
        ),
    )


def resolve_crossref(title: str, year: int | None) -> dict:
    params = {
        "query.bibliographic": title,
        "rows": "6",
        "mailto": MAILTO,
    }
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    payload = _fetch_json(url)
    items = payload.get("message", {}).get("items", [])
    if not isinstance(items, list):
        items = []
    result = choose_crossref_candidate(title, year, items)
    result["query_url"] = url
    return result


def lookup_unpaywall(doi: str) -> dict:
    if not doi:
        return {
            "status": "NOT_QUERIED",
            "is_oa": "",
            "host_type": "",
            "version": "",
            "license": "",
            "url_for_pdf": "",
            "url_for_landing_page": "",
        }
    url = (
        "https://api.unpaywall.org/v2/"
        + urllib.parse.quote(doi, safe="")
        + "?"
        + urllib.parse.urlencode({"email": MAILTO})
    )
    try:
        payload = _fetch_json(url)
    except Exception as exc:  # pragma: no cover - network path
        return {
            "status": "LOOKUP_ERROR",
            "error": repr(exc),
            "is_oa": "",
            "host_type": "",
            "version": "",
            "license": "",
            "url_for_pdf": "",
            "url_for_landing_page": "",
        }
    loc = payload.get("best_oa_location")
    if not isinstance(loc, dict):
        loc = {}
    return {
        "status": "FOUND" if payload else "EMPTY",
        "is_oa": bool(payload.get("is_oa")),
        "host_type": str(loc.get("host_type") or ""),
        "version": str(loc.get("version") or ""),
        "license": str(loc.get("license") or ""),
        "url_for_pdf": str(loc.get("url_for_pdf") or ""),
        "url_for_landing_page": str(loc.get("url_for_landing_page") or ""),
    }


def run_audit(map_path: Path, output_json: Path, output_csv: Path) -> dict:
    map_rows = _load_map(map_path)
    article_taxa = _mapped_article_ids(map_rows)
    study_bytes, figshare_receipt = _study_list_bytes()
    studies = parse_study_list(study_bytes)

    missing = sorted(set(article_taxa) - set(studies), key=int)
    if missing:
        raise ValueError(f"mapped article IDs absent from Study List.csv: {missing}")

    records = []
    for article_id, taxa in article_taxa.items():
        study = studies[article_id]
        try:
            year = int(study["publication_year"])
        except ValueError:
            year = None
        try:
            crossref = resolve_crossref(study["title"], year)
        except Exception as exc:  # pragma: no cover - network path
            crossref = {
                "status": "LOOKUP_ERROR",
                "doi": "",
                "title": "",
                "similarity": 0.0,
                "crossref_score": 0.0,
                "error": repr(exc),
            }
        unpaywall = (
            lookup_unpaywall(crossref["doi"])
            if crossref.get("status") == "RESOLVED"
            else lookup_unpaywall("")
        )
        records.append(
            {
                "article_id": article_id,
                "mapped_taxa": taxa,
                **study,
                "crossref": crossref,
                "unpaywall": unpaywall,
            }
        )
        time.sleep(0.15)

    counts = {}
    for record in records:
        status = record["crossref"]["status"]
        counts[status] = counts.get(status, 0) + 1

    out = {
        "analysis": "balance_u1_primary_source_identity_and_oa_audit_v1",
        "figshare": figshare_receipt,
        "n_mapped_taxa": len(map_rows),
        "n_unique_primary_studies": len(records),
        "crossref_status_counts": dict(sorted(counts.items())),
        "n_resolved_doi": sum(
            r["crossref"]["status"] == "RESOLVED" and bool(r["crossref"]["doi"])
            for r in records
        ),
        "n_oa_fulltext_candidates": sum(
            bool(r["unpaywall"].get("url_for_pdf"))
            for r in records
        ),
        "records": records,
        "claim_ceiling": (
            "bibliographic_identity_and_public_access_location_audit_only_"
            "not_fulltext_content_adjudication_not_production_coding"
        ),
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for record in records:
            cr = record["crossref"]
            up = record["unpaywall"]
            writer.writerow(
                {
                    "article_id": record["article_id"],
                    "mapped_taxa": ";".join(record["mapped_taxa"]),
                    "author": record["author"],
                    "title": record["title"],
                    "journal": record["journal"],
                    "publication_year": record["publication_year"],
                    "crossref_status": cr.get("status", ""),
                    "crossref_doi": cr.get("doi", ""),
                    "crossref_title": cr.get("title", ""),
                    "title_similarity": f'{float(cr.get("similarity", 0.0)):.6f}',
                    "crossref_score": f'{float(cr.get("crossref_score", 0.0)):.6f}',
                    "unpaywall_status": up.get("status", ""),
                    "is_oa": up.get("is_oa", ""),
                    "oa_host_type": up.get("host_type", ""),
                    "oa_version": up.get("version", ""),
                    "oa_license": up.get("license", ""),
                    "oa_url_for_pdf": up.get("url_for_pdf", ""),
                    "oa_url_for_landing_page": up.get("url_for_landing_page", ""),
                }
            )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()
    result = run_audit(args.map, args.output_json, args.output_csv)
    compact = {
        "analysis": result["analysis"],
        "n_mapped_taxa": result["n_mapped_taxa"],
        "n_unique_primary_studies": result["n_unique_primary_studies"],
        "crossref_status_counts": result["crossref_status_counts"],
        "n_resolved_doi": result["n_resolved_doi"],
        "n_oa_fulltext_candidates": result["n_oa_fulltext_candidates"],
        "claim_ceiling": result["claim_ceiling"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

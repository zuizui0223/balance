"""Recover and inspect the Haas-Lortie 2020 U1 supplementary surfaces.

The local ChatGPT runtime may not have outbound network access, so this module is
intended to run in GitHub Actions. It discovers PeerJ supplement links from the
article and the stable supp-1/supp-2 landing endpoints, downloads file-like
resources, and emits a deterministic JSON receipt with CSV/DOCX summaries.

The audit is discovery only: it never promotes taxa into the canonical U1
universe. Repository adjudication must compare recovered supplement taxa
against the frozen 44-label network surface before the 47-taxon frame closes.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

ARTICLE_URL = "https://peerj.com/articles/9049/"
LANDING_URLS = (
    "https://peerj.com/articles/9049/supp-1/",
    "https://peerj.com/articles/9049/supp-2/",
)
USER_AGENT = "BALANCE-U1-supplement-audit/1.0 (+https://github.com/zuizui0223/balance)"

FILE_SUFFIXES = (".csv", ".docx", ".xlsx", ".xls", ".tsv", ".txt", ".zip")
LINK_RE = re.compile(r"""href=["']([^"']+)["']""", re.IGNORECASE)
SCI_NAME_RE = re.compile(
    r"\b([A-Z][a-z]{2,})\s+([a-z][a-z-]{2,})(?:\s+(?:ssp\.|subsp\.|var\.)\s+([a-z][a-z-]{2,}))?\b"
)


def discover_relevant_links(html: str, base_url: str) -> list[str]:
    """Return stable unique supplement/file links from an HTML page."""
    out: list[str] = []
    seen: set[str] = set()
    for raw in LINK_RE.findall(html):
        url = urllib.parse.urljoin(base_url, raw.replace("&amp;", "&"))
        low = url.lower().split("?", 1)[0]
        relevant = (
            "/supp-1" in low
            or "/supp-2" in low
            or "figshare" in low
            or low.endswith(FILE_SUFFIXES)
        )
        if relevant and url not in seen:
            seen.add(url)
            out.append(url)
    return out


def extract_scientific_names(text: str) -> dict[str, int]:
    """Extract conservative binomial/trinomial-looking names and counts."""
    names = []
    for genus, species, infra in SCI_NAME_RE.findall(text):
        name = f"{genus} {species}"
        if infra:
            name += f" {infra}"
        names.append(name)
    return dict(sorted(Counter(names).items()))


def summarize_csv_bytes(data: bytes) -> dict:
    text = data.decode("utf-8-sig", errors="replace")
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.reader(io.StringIO(text), dialect)
    rows = list(reader)
    header = rows[0] if rows else []
    body = rows[1:] if rows else []
    return {
        "kind": "delimited_text",
        "row_count_including_header": len(rows),
        "data_row_count": len(body),
        "columns": header,
        "first_rows": body[:5],
        "scientific_name_candidates": extract_scientific_names(text),
    }


def _docx_text(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        xml = zf.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    text_nodes = []
    for elem in root.iter():
        if elem.tag.endswith("}t") and elem.text:
            text_nodes.append(elem.text)
    return "\n".join(text_nodes)


def summarize_docx_bytes(data: bytes) -> dict:
    text = _docx_text(data)
    return {
        "kind": "docx",
        "character_count": len(text),
        "text_preview": text[:2000],
        "scientific_name_candidates": extract_scientific_names(text),
    }


def summarize_payload(data: bytes, final_url: str, content_type: str) -> dict:
    low = final_url.lower().split("?", 1)[0]
    ctype = content_type.lower()
    if low.endswith((".csv", ".tsv", ".txt")) or "csv" in ctype:
        return summarize_csv_bytes(data)
    if low.endswith(".docx") or "wordprocessingml" in ctype:
        return summarize_docx_bytes(data)
    return {"kind": "binary_or_unparsed"}


def _fetch(url: str) -> tuple[bytes, str, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as response:  # noqa: S310 - frozen HTTPS sources
        data = response.read()
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        content_disposition = response.headers.get("Content-Disposition", "")
    return data, final_url, content_type, content_disposition


def _safe_name(index: int, final_url: str, content_type: str) -> str:
    path_name = Path(urllib.parse.urlparse(final_url).path).name
    if path_name and "." in path_name:
        return f"{index:02d}_{path_name}"
    if "csv" in content_type.lower():
        ext = ".csv"
    elif "wordprocessingml" in content_type.lower():
        ext = ".docx"
    elif "html" in content_type.lower():
        ext = ".html"
    else:
        ext = ".bin"
    return f"{index:02d}_supplement{ext}"


def run_audit(output_path: Path, workdir: Path) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)

    queue = [ARTICLE_URL, *LANDING_URLS]
    queued = set(queue)
    visited: set[str] = set()
    receipts = []

    while queue and len(visited) < 30:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            data, final_url, content_type, disposition = _fetch(url)
        except Exception as exc:  # pragma: no cover - network path
            receipts.append(
                {"requested_url": url, "status": "FETCH_ERROR", "error": repr(exc)}
            )
            continue

        receipt = {
            "requested_url": url,
            "final_url": final_url,
            "content_type": content_type,
            "content_disposition": disposition,
            "size_bytes": len(data),
            "status": "FETCHED",
        }

        is_html = "html" in content_type.lower() or data.lstrip().startswith(b"<")
        if is_html:
            html = data.decode("utf-8", errors="replace")
            links = discover_relevant_links(html, final_url)
            receipt["discovered_links"] = links
            receipt["scientific_name_candidates"] = extract_scientific_names(html)
            for link in links:
                if link not in queued and link not in visited:
                    queued.add(link)
                    queue.append(link)
        else:
            filename = _safe_name(len(receipts), final_url, content_type)
            saved = workdir / filename
            saved.write_bytes(data)
            receipt["saved_path"] = str(saved)
            try:
                receipt["summary"] = summarize_payload(data, final_url, content_type)
            except Exception as exc:  # pragma: no cover - malformed external file
                receipt["summary"] = {"kind": "parse_error", "error": repr(exc)}
        receipts.append(receipt)

    parsed = [
        r
        for r in receipts
        if r.get("summary", {}).get("kind") in {"delimited_text", "docx"}
    ]
    all_names: Counter[str] = Counter()
    for receipt in parsed:
        all_names.update(receipt["summary"].get("scientific_name_candidates", {}))

    out = {
        "analysis": "balance_u1_haas_lortie_supplement_discovery_v1",
        "article_url": ARTICLE_URL,
        "landing_urls": list(LANDING_URLS),
        "n_urls_visited": len(visited),
        "n_receipts": len(receipts),
        "n_parsed_supplement_files": len(parsed),
        "receipts": receipts,
        "combined_scientific_name_candidates": dict(sorted(all_names.items())),
        "claim_ceiling": (
            "supplement_discovery_and_content_inventory_only_not_canonical_taxon_"
            "promotion_not_first20_freeze_not_conflict_adjudication"
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    result = run_audit(args.output, args.workdir)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Recover and inspect the Haas-Lortie 2020 U1 supplementary surfaces.

GitHub Actions is used as the network-capable execution environment. The
primary route is the public Figshare API for dataset 12397772; PeerJ landing
pages are retained only as fallback discovery surfaces.

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
FIGSHARE_API_URL = "https://api.figshare.com/v2/articles/12397772"
USER_AGENT = "BALANCE-U1-supplement-audit/1.1 (+https://github.com/zuizui0223/balance)"

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


def discover_figshare_files(payload: object) -> list[dict[str, str]]:
    """Extract deterministic file name/download URL pairs from Figshare JSON."""
    if not isinstance(payload, dict):
        raise ValueError("Figshare article payload must be a JSON object")
    raw_files = payload.get("files")
    if not isinstance(raw_files, list):
        raise ValueError("Figshare article payload must contain a files list")

    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in raw_files:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        download_url = str(item.get("download_url") or "").strip()
        if not name or not download_url or download_url in seen:
            continue
        seen.add(download_url)
        out.append({"name": name, "download_url": download_url})
    return sorted(out, key=lambda x: (x["name"].casefold(), x["download_url"]))


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


def summarize_payload(
    data: bytes,
    final_url: str,
    content_type: str,
    *,
    filename_hint: str = "",
) -> dict:
    low = (filename_hint or final_url).lower().split("?", 1)[0]
    ctype = content_type.lower()
    if low.endswith((".csv", ".tsv", ".txt")) or "csv" in ctype:
        return summarize_csv_bytes(data)
    if low.endswith(".docx") or "wordprocessingml" in ctype:
        return summarize_docx_bytes(data)
    return {"kind": "binary_or_unparsed"}


def _fetch(url: str) -> tuple[bytes, str, str, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as response:  # noqa: S310 - frozen HTTPS sources
        data = response.read()
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        content_disposition = response.headers.get("Content-Disposition", "")
    return data, final_url, content_type, content_disposition


def _safe_name(
    index: int,
    final_url: str,
    content_type: str,
    *,
    filename_hint: str = "",
) -> str:
    hint = Path(filename_hint).name if filename_hint else ""
    if hint and "." in hint:
        return f"{index:02d}_{hint}"
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


def _fetch_figshare_inventory() -> tuple[list[dict[str, str]], dict]:
    data, final_url, content_type, disposition = _fetch(FIGSHARE_API_URL)
    payload = json.loads(data.decode("utf-8"))
    files = discover_figshare_files(payload)
    receipt = {
        "requested_url": FIGSHARE_API_URL,
        "final_url": final_url,
        "content_type": content_type,
        "content_disposition": disposition,
        "size_bytes": len(data),
        "status": "FETCHED",
        "source_type": "FIGSHARE_API_INVENTORY",
        "dataset_title": str(payload.get("title") or ""),
        "dataset_doi": str(payload.get("doi") or ""),
        "files": files,
    }
    return files, receipt


def run_audit(output_path: Path, workdir: Path) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)

    receipts: list[dict] = []
    queue: list[tuple[str, str, str]] = []
    queued: set[str] = set()

    try:
        figshare_files, figshare_receipt = _fetch_figshare_inventory()
        receipts.append(figshare_receipt)
        for item in figshare_files:
            url = item["download_url"]
            if url not in queued:
                queued.add(url)
                queue.append((url, item["name"], "FIGSHARE_FILE"))
    except Exception as exc:  # pragma: no cover - network path
        receipts.append(
            {
                "requested_url": FIGSHARE_API_URL,
                "status": "FETCH_ERROR",
                "source_type": "FIGSHARE_API_INVENTORY",
                "error": repr(exc),
            }
        )

    for url in (ARTICLE_URL, *LANDING_URLS):
        if url not in queued:
            queued.add(url)
            queue.append((url, "", "PEERJ_FALLBACK"))

    visited: set[str] = set()
    while queue and len(visited) < 60:
        url, filename_hint, source_type = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            data, final_url, content_type, disposition = _fetch(url)
        except Exception as exc:  # pragma: no cover - network path
            receipts.append(
                {
                    "requested_url": url,
                    "status": "FETCH_ERROR",
                    "source_type": source_type,
                    "filename_hint": filename_hint,
                    "error": repr(exc),
                }
            )
            continue

        receipt = {
            "requested_url": url,
            "final_url": final_url,
            "content_type": content_type,
            "content_disposition": disposition,
            "size_bytes": len(data),
            "status": "FETCHED",
            "source_type": source_type,
        }
        if filename_hint:
            receipt["filename_hint"] = filename_hint

        is_html = "html" in content_type.lower() or data.lstrip().startswith(b"<")
        if is_html:
            html = data.decode("utf-8", errors="replace")
            links = discover_relevant_links(html, final_url)
            receipt["discovered_links"] = links
            receipt["scientific_name_candidates"] = extract_scientific_names(html)
            for link in links:
                if link not in queued and link not in visited:
                    queued.add(link)
                    queue.append((link, "", "DISCOVERED_LINK"))
        else:
            filename = _safe_name(
                len(receipts),
                final_url,
                content_type,
                filename_hint=filename_hint,
            )
            saved = workdir / filename
            saved.write_bytes(data)
            receipt["saved_path"] = str(saved)
            try:
                receipt["summary"] = summarize_payload(
                    data,
                    final_url,
                    content_type,
                    filename_hint=filename_hint,
                )
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
        "analysis": "balance_u1_haas_lortie_supplement_discovery_v2",
        "article_url": ARTICLE_URL,
        "landing_urls": list(LANDING_URLS),
        "figshare_api_url": FIGSHARE_API_URL,
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

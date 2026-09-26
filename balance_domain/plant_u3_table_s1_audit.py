"""Recover Supporting Table S1 for Vallejo-Marin et al. (2010).

The article page exposes the supplement filename but Wiley may reject simple
automated downloads. This audit tries the article-discovered href plus several
stable Wiley URL forms with browser-like headers, preserves every receipt, and
extracts legacy .doc text with antiword when bytes are recovered.

The audit is discovery-only. It never promotes a representative species into
the canonical U3 universe without a source-secure recovered table row.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

ARTICLE_URL = "https://nph.onlinelibrary.wiley.com/doi/10.1111/j.1469-8137.2010.03430.x"
WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"
FILENAME = "NPH_3430_sm_TableS1.doc"
TARGET_FAMILIES = ("Malvaceae", "Bixaceae", "Scrophulariaceae")
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"
)

CANDIDATE_URLS = (
    "https://nph.onlinelibrary.wiley.com/action/downloadSupplement"
    "?doi=10.1111%2Fj.1469-8137.2010.03430.x&file=NPH_3430_sm_TableS1.doc",
    "https://onlinelibrary.wiley.com/action/downloadSupplement"
    "?doi=10.1111%2Fj.1469-8137.2010.03430.x&file=NPH_3430_sm_TableS1.doc",
    "https://nph.onlinelibrary.wiley.com/doi/suppl/"
    "10.1111/j.1469-8137.2010.03430.x/supinfo/NPH_3430_sm_TableS1.doc",
    "https://onlinelibrary.wiley.com/doi/suppl/"
    "10.1111/j.1469-8137.2010.03430.x/supinfo/NPH_3430_sm_TableS1.doc",
)

HREF_RE = re.compile(r"""href=["']([^"']*NPH_3430_sm_TableS1\.doc[^"']*)["']""", re.I)
SCI_NAME_RE = re.compile(
    r"\b([A-Z][a-z]{2,})\s+([a-z][a-z-]{2,})"
    r"(?:\s+(?:ssp\.|subsp\.|var\.)\s+([a-z][a-z-]{2,}))?\b"
)


def extract_scientific_names(text: str) -> list[str]:
    names: set[str] = set()
    for genus, species, infra in SCI_NAME_RE.findall(text):
        name = f"{genus} {species}"
        if infra:
            name += f" {infra}"
        names.add(name)
    return sorted(names, key=str.casefold)


def extract_family_contexts(text: str, radius: int = 1200) -> dict[str, dict]:
    compact = re.sub(r"[ \t]+", " ", text)
    out: dict[str, dict] = {}
    for family in TARGET_FAMILIES:
        match = re.search(re.escape(family), compact, flags=re.I)
        if not match:
            out[family] = {
                "found": False,
                "context": "",
                "scientific_name_candidates": [],
            }
            continue
        start = max(0, match.start() - radius)
        end = min(len(compact), match.end() + radius)
        context = compact[start:end].strip()
        out[family] = {
            "found": True,
            "context": context,
            "scientific_name_candidates": extract_scientific_names(context),
        }
    return out


def discover_supplement_hrefs(article_html: str, base_url: str = ARTICLE_URL) -> list[str]:
    urls = []
    seen = set()
    for raw in HREF_RE.findall(article_html):
        url = urllib.parse.urljoin(base_url, html.unescape(raw))
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def _opener():
    jar = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def _request(opener, url: str, *, referer: str | None = None) -> tuple[bytes, str, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,application/xhtml+xml,application/msword,"
            "application/octet-stream;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    with opener.open(req, timeout=60) as response:
        return (
            response.read(),
            response.geturl(),
            response.headers.get("Content-Type", ""),
        )


def _looks_like_document(data: bytes, content_type: str) -> bool:
    if len(data) < 1024:
        return False
    sample = data[:512].lstrip().lower()
    if sample.startswith(b"<!doctype html") or sample.startswith(b"<html"):
        return False
    ctype = content_type.casefold()
    if "text/html" in ctype:
        return False
    return True


def parse_wayback_cdx(payload: bytes) -> list[dict[str, str]]:
    """Parse CDX JSON rows into unique archived snapshot records."""
    raw = json.loads(payload.decode("utf-8"))
    if not isinstance(raw, list) or not raw:
        return []
    header = raw[0]
    if not isinstance(header, list):
        return []
    out = []
    seen = set()
    for row in raw[1:]:
        if not isinstance(row, list) or len(row) != len(header):
            continue
        rec = {str(k): str(v) for k, v in zip(header, row)}
        timestamp = rec.get("timestamp", "")
        original = rec.get("original", "")
        if not timestamp or not original:
            continue
        key = (timestamp, original)
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out


def discover_wayback_snapshots(opener, original_url: str) -> list[dict[str, str]]:
    query = urllib.parse.urlencode(
        {
            "url": original_url,
            "output": "json",
            "fl": "timestamp,original,mimetype,statuscode,digest,length",
            "filter": "statuscode:200",
            "collapse": "digest",
        }
    )
    data, _, _ = _request(opener, f"{WAYBACK_CDX_URL}?{query}")
    return parse_wayback_cdx(data)


def _wayback_raw_url(snapshot: dict[str, str]) -> str:
    timestamp = snapshot["timestamp"]
    original = snapshot["original"]
    return f"https://web.archive.org/web/{timestamp}id_/{original}"


def _antiword(path: Path) -> str:
    proc = subprocess.run(
        ["antiword", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"antiword failed: {proc.stderr.strip()}")
    return proc.stdout


def run_audit(output: Path, workdir: Path) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    opener = _opener()
    receipts = []
    discovered = []

    try:
        article_bytes, article_final, article_type = _request(opener, ARTICLE_URL)
        article_html = article_bytes.decode("utf-8", errors="replace")
        discovered = discover_supplement_hrefs(article_html, article_final)
        receipts.append(
            {
                "url": ARTICLE_URL,
                "status": "FETCHED_ARTICLE",
                "final_url": article_final,
                "content_type": article_type,
                "size_bytes": len(article_bytes),
                "discovered_supplement_urls": discovered,
            }
        )
    except Exception as exc:  # pragma: no cover - network path
        receipts.append(
            {"url": ARTICLE_URL, "status": "ARTICLE_FETCH_ERROR", "error": repr(exc)}
        )

    queue = []
    seen = set()
    for url in [*discovered, *CANDIDATE_URLS]:
        if url not in seen:
            seen.add(url)
            queue.append(url)

    recovered = None
    recovered_text = ""

    # Archive fallback is independent of the publisher's live anti-bot response.
    # We query each stable supplement URL and try raw archived payloads first.
    archive_index = 0
    for original_url in list(queue):
        try:
            snapshots = discover_wayback_snapshots(opener, original_url)
            receipts.append(
                {
                    "url": original_url,
                    "status": "WAYBACK_CDX_FETCHED",
                    "snapshot_count": len(snapshots),
                    "snapshots": snapshots,
                }
            )
        except Exception as exc:  # pragma: no cover - network path
            receipts.append(
                {
                    "url": original_url,
                    "status": "WAYBACK_CDX_ERROR",
                    "error": repr(exc),
                }
            )
            continue
        for snapshot in snapshots:
            archive_index += 1
            archive_url = _wayback_raw_url(snapshot)
            try:
                data, final_url, ctype = _request(opener, archive_url)
                receipt = {
                    "url": archive_url,
                    "original_url": original_url,
                    "status": "WAYBACK_FETCHED",
                    "final_url": final_url,
                    "content_type": ctype,
                    "size_bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "document_like": _looks_like_document(data, ctype),
                    "snapshot": snapshot,
                }
                if receipt["document_like"] and recovered is None:
                    raw = workdir / f"wayback_{archive_index:02d}_{FILENAME}"
                    raw.write_bytes(data)
                    receipt["saved_path"] = str(raw)
                    try:
                        recovered_text = _antiword(raw)
                        txt = workdir / f"wayback_{archive_index:02d}_TableS1.txt"
                        txt.write_text(recovered_text, encoding="utf-8")
                        receipt["text_path"] = str(txt)
                        receipt["antiword_status"] = "PASS"
                        recovered = receipt
                    except Exception as exc:
                        receipt["antiword_status"] = "FAIL"
                        receipt["antiword_error"] = repr(exc)
                receipts.append(receipt)
            except Exception as exc:  # pragma: no cover - network path
                receipts.append(
                    {
                        "url": archive_url,
                        "original_url": original_url,
                        "status": "WAYBACK_FETCH_ERROR",
                        "snapshot": snapshot,
                        "error": repr(exc),
                    }
                )
        if recovered is not None:
            break

    for index, url in enumerate(queue, start=1):
        try:
            data, final_url, ctype = _request(opener, url, referer=ARTICLE_URL)
            receipt = {
                "url": url,
                "status": "FETCHED",
                "final_url": final_url,
                "content_type": ctype,
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "document_like": _looks_like_document(data, ctype),
            }
            if receipt["document_like"] and recovered is None:
                raw = workdir / f"{index:02d}_{FILENAME}"
                raw.write_bytes(data)
                receipt["saved_path"] = str(raw)
                try:
                    recovered_text = _antiword(raw)
                    txt = workdir / f"{index:02d}_TableS1.txt"
                    txt.write_text(recovered_text, encoding="utf-8")
                    receipt["text_path"] = str(txt)
                    receipt["antiword_status"] = "PASS"
                    recovered = receipt
                except Exception as exc:
                    receipt["antiword_status"] = "FAIL"
                    receipt["antiword_error"] = repr(exc)
            receipts.append(receipt)
        except urllib.error.HTTPError as exc:  # pragma: no cover - network path
            receipts.append(
                {
                    "url": url,
                    "status": "HTTP_ERROR",
                    "code": exc.code,
                    "reason": str(exc.reason),
                }
            )
        except Exception as exc:  # pragma: no cover - network path
            receipts.append({"url": url, "status": "FETCH_ERROR", "error": repr(exc)})

    contexts = extract_family_contexts(recovered_text) if recovered_text else {
        family: {"found": False, "context": "", "scientific_name_candidates": []}
        for family in TARGET_FAMILIES
    }

    result = {
        "analysis": "balance_u3_vallejo_marin_table_s1_recovery_v1",
        "article_url": ARTICLE_URL,
        "supplement_filename": FILENAME,
        "target_families": list(TARGET_FAMILIES),
        "wayback_cdx_url": WAYBACK_CDX_URL,
        "recovered_document": recovered is not None,
        "receipts": receipts,
        "family_contexts": contexts,
        "all_scientific_name_candidates": (
            extract_scientific_names(recovered_text) if recovered_text else []
        ),
        "claim_ceiling": (
            "supporting_table_recovery_only_not_representative_promotion_"
            "until_exact_family_rows_are_adjudicated"
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_audit(args.output, args.workdir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

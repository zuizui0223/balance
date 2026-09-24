"""Fetch and inspect the Vallejo-Marin et al. 2010 heteranthery Table S1.

Wiley's supplement endpoint may reject non-browser clients. This audit tries a
small frozen set of publisher URL forms after establishing an article-session
cookie, records every HTTP outcome, and accepts a payload only if it looks like
a legacy Word document rather than an HTML block page.

The output is retrieval evidence only. Representative taxa are promoted into
the U3 universe only after the recovered Table S1 text is inspected.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ARTICLE_URL = "https://nph.onlinelibrary.wiley.com/doi/10.1111/j.1469-8137.2010.03430.x"
FILENAME = "NPH_3430_sm_TableS1.doc"
URLS = (
    "https://nph.onlinelibrary.wiley.com/action/downloadSupplement"
    "?doi=10.1111%2Fj.1469-8137.2010.03430.x&file=NPH_3430_sm_TableS1.doc",
    "https://onlinelibrary.wiley.com/action/downloadSupplement"
    "?doi=10.1111%2Fj.1469-8137.2010.03430.x&file=NPH_3430_sm_TableS1.doc",
    "https://nph.onlinelibrary.wiley.com/doi/suppl/"
    "10.1111/j.1469-8137.2010.03430.x/supinfo/NPH_3430_sm_TableS1.doc",
    "https://onlinelibrary.wiley.com/doi/suppl/"
    "10.1111/j.1469-8137.2010.03430.x/supinfo/NPH_3430_sm_TableS1.doc",
)
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)


def _curl(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["curl", "--silent", "--show-error", "--location", "--compressed", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _looks_like_word(data: bytes) -> bool:
    if len(data) < 10_000:
        return False
    head = data[:512].lstrip().lower()
    if head.startswith(b"<!doctype html") or head.startswith(b"<html"):
        return False
    # Old .doc files normally use OLE Compound File magic.
    return data.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))


def run(output: Path, workdir: Path) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    cookie = workdir / "cookies.txt"
    article_html = workdir / "article.html"

    article = _curl(
        [
            "--user-agent", UA,
            "--cookie-jar", str(cookie),
            "--output", str(article_html),
            "--write-out", "%{http_code}\\t%{url_effective}\\t%{content_type}",
            ARTICLE_URL,
        ]
    )

    attempts = []
    accepted: Path | None = None
    for idx, url in enumerate(URLS, start=1):
        payload = workdir / f"attempt_{idx}.bin"
        headers = workdir / f"attempt_{idx}.headers.txt"
        proc = _curl(
            [
                "--user-agent", UA,
                "--referer", ARTICLE_URL,
                "--cookie", str(cookie),
                "--cookie-jar", str(cookie),
                "--header", "Accept: application/msword,application/octet-stream,*/*;q=0.8",
                "--dump-header", str(headers),
                "--output", str(payload),
                "--write-out", "%{http_code}\\t%{url_effective}\\t%{content_type}",
                url,
            ]
        )
        data = payload.read_bytes() if payload.exists() else b""
        attempts.append(
            {
                "url": url,
                "curl_returncode": proc.returncode,
                "curl_write_out": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "size_bytes": len(data),
                "ole_word_magic": data.startswith(bytes.fromhex("D0CF11E0A1B11AE1")),
                "looks_like_word": _looks_like_word(data),
            }
        )
        if _looks_like_word(data):
            accepted = workdir / FILENAME
            accepted.write_bytes(data)
            break

    receipt = {
        "analysis": "balance_u3_table_s1_retrieval_v1",
        "article_url": ARTICLE_URL,
        "filename": FILENAME,
        "article_session": {
            "curl_returncode": article.returncode,
            "curl_write_out": article.stdout.strip(),
            "stderr": article.stderr.strip(),
            "size_bytes": article_html.stat().st_size if article_html.exists() else 0,
        },
        "attempts": attempts,
        "retrieval_status": "RECOVERED" if accepted else "BLOCKED",
        "accepted_path": str(accepted) if accepted else None,
        "claim_ceiling": (
            "publisher_supporting_file_retrieval_only_not_representative_taxon_"
            "promotion_until_table_text_is_inspected"
        ),
    }
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output, args.workdir)
    print(json.dumps(result, indent=2))
    if result["retrieval_status"] != "RECOVERED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

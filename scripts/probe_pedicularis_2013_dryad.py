#!/usr/bin/env python3
"""Fail-closed metadata-only locator for Xia et al. 2013 Dryad deposition.

Does not treat DOI mention or DOI resolution as possession of source rows.
Never downloads, infers or fits unpublished biological data. Network requests
are confined to the documented public Dryad API and DOI-encoded fixed locator.
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DOI = "10.5061/dryad.6cv06"
ORIGIN = "https://datadryad.org"
ENCODED = urllib.parse.quote("doi:" + DOI, safe="")
DATASET_API = ORIGIN + "/api/v2/datasets/" + ENCODED
MAX_META_BYTES = 2_000_000


def _get_json(url: str):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "datadryad.org":
        raise ValueError("refusing API request outside published Dryad origin")
    if not parsed.path.startswith("/api/v2/"):
        raise ValueError("refusing unregistered non-API URL")
    req = urllib.request.Request(
        url, headers={
            "Accept": "application/json",
            "User-Agent": "balance-research-source-audit/1.0",
        }
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        n = response.headers.get("Content-Length")
        if n is not None and int(n) > MAX_META_BYTES:
            raise ValueError("Dryad metadata size exceeds safety bound")
        body = response.read(MAX_META_BYTES + 1)
        if len(body) > MAX_META_BYTES:
            raise ValueError("Dryad metadata size exceeds safety bound")
    return json.loads(body)


def _uri(href):
    if not isinstance(href, str):
        raise ValueError("Dryad API link href is absent")
    absolute = urllib.parse.urljoin(ORIGIN, href)
    parsed = urllib.parse.urlsplit(absolute)
    if parsed.scheme != "https" or parsed.hostname != "datadryad.org":
        raise ValueError("Dryad API link points outside the allowed origin")
    if not parsed.path.startswith("/api/v2/"):
        raise ValueError("Dryad response links to an unknown API path")
    return absolute


def inspect_source(fetch=_get_json) -> dict:
    """Return one metadata receipt. No dataset content or reanalysis."""
    output = {
        "schema_version": "PEDICULARIS_2013_DRYAD_SOURCE_DISCOVERY_V1",
        "article_doi": "10.1098/rsbl.2013.0387",
        "declared_repository_doi": DOI,
        "lookup_url": DATASET_API,
        "status": "DRYAD_METADATA_NOT_VERIFIED_HOLD",
        "field_data_retrieved": False,
        "biological_effect_reanalysed": False,
        "claim_ceiling": "metadata_only_not_raw_data_or_independent_scientific_result",
    }
    try:
        metadata = fetch(DATASET_API)
        if not isinstance(metadata, dict):
            raise ValueError("metadata not a JSON object")
        identifier = metadata.get("identifier")
        if not isinstance(identifier, str) or identifier.lower() != "doi:" + DOI.lower():
            raise ValueError("returned metadata DOI does not match 2013 source")
        title = str(metadata.get("title", ""))
        if "pedicularis" not in title.lower() or "predation" not in title.lower():
            raise ValueError("Dryad metadata title does not describe 2013 Pedicularis study")
        links = metadata.get("_links")
        if not isinstance(links, dict):
            raise ValueError("Dryad metadata lacks version-link mapping")
        version_href = (links.get("stash:version") or {}).get("href")
        version_url = _uri(version_href)
        version = fetch(version_url)
        if not isinstance(version, dict):
            raise ValueError("Dryad dataset version metadata missing")
        vid = version.get("id")
        if not isinstance(vid, int) or isinstance(vid, bool) or vid <= 0:
            raise ValueError("Dryad version identifier invalid")
        files_url = _uri(f"/api/v2/versions/{vid}/files")
        raw_files = fetch(files_url)
        embedded = raw_files.get("_embedded", {}) if isinstance(raw_files, dict) else {}
        files = embedded.get("stash:files", [])
        if not isinstance(files, list):
            raise ValueError("Dryad API file listing malformed")
        source_files = []
        for item in files:
            if not isinstance(item, dict):
                raise ValueError("Dryad file item invalid")
            path = item.get("path")
            size = item.get("size")
            if not isinstance(path, str) or not path or not isinstance(size, int) or size < 0:
                raise ValueError("Dryad file lacks path/size")
            source_files.append({
                "path": path,
                "size_bytes": size,
                "mime_type": item.get("mimeType"),
                "file_id": item.get("id"),
                "digest": item.get("digest"),
                "digest_type": item.get("digestType"),
            })
        output.update({
            "status": ("DRYAD_METADATA_AND_FILE_MANIFEST_VERIFIED"
                       if source_files else "DRYAD_FILES_UNLISTED_HOLD"),
            "dataset_title": title,
            "dataset_identifier": identifier,
            "version_id": vid,
            "version_url": version_url,
            "files_url": files_url,
            "file_count": len(source_files),
            "source_file_manifest": source_files,
        })
    except (ValueError, KeyError, TypeError, json.JSONDecodeError,
            urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        output["status"] = "DRYAD_METADATA_NOT_VERIFIED_HOLD"
        output["diagnostic_error_type"] = type(exc).__name__
        output["diagnostic_message"] = str(exc)[:240]
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("refusing to overwrite source discovery receipt")
    result = inspect_source()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

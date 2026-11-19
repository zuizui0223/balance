"""Source-access audit tests; synthetic CSV fixtures are not Clarkia observations."""
import json
import io
from pathlib import Path
import urllib.error

import pytest

from scripts.audit_clarkia_kay2020_dryad import (
    MAX_FILE_BYTES, audit_source_retrieval, read_receipt, verify_file_bytes,
    default_downloader,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "BALANCE_CLARKIA_KAY2020_DRYAD_RECEIPT_V1.json"


def test_kay_archive_receipt_is_preoutcome_not_fabricated_raw_data():
    receipt = read_receipt()
    assert receipt["article"]["doi"] == "10.1098/rspb.2020.2593"
    assert receipt["dryad"]["doi"] == "10.5061/dryad.8cz8w9gmp"
    assert receipt["article"]["n_independent_study_programmes"] == 1
    assert receipt["dryad"]["n_listed_files"] == 29
    assert receipt["dryad"]["missing_critical_file_note"].startswith("Usage notes cite")


def test_critical_greenhouse_csv_stays_missing_even_with_every_listed_file():
    receipt = read_receipt()
    samples = {
        item["file_id"]: (
            b"flower_id,patch,treatment,visits\n1,a,control,3\n"
            if item["filename"].endswith(".csv")
            else b"x = read.csv('source.csv')\n" if item["filename"].endswith(".R")
            else b"Original manifest bytes\n"
        )
        for item in receipt["dryad"]["files"]
        if item["listed"]
    }
    report = audit_source_retrieval(
        receipt, download=True, fetcher=lambda file_id: samples[file_id]
    )
    assert len(report["datafiles_accessed"]) == 9
    assert report["field_visit_and_seed_files_retrievable"] is True
    assert report["field_visit_to_seed_focal_flower_join_identified"] is False
    assert report["greenhouse_export_original_raw_csv_retrievable"] is False
    assert report["greenhouse_export_status"] == (
        "HOLD_CRITICAL_ORIGINAL_CSV_NOT_LISTED_BY_DRYAD_VERSION"
    )
    assert report["raw_observation_effect_refits_performed"] == 0
    assert report["experiment_year_cross_join"] == "PROHIBITED"


def test_offline_run_is_explicitly_no_data_and_no_false_success():
    report = audit_source_retrieval(read_receipt(), download=False)
    assert report["datafiles_accessed"] == []
    assert report["field_visit_and_seed_files_retrievable"] is False
    assert report["greenhouse_export_original_raw_csv_retrievable"] is False
    assert len([r for r in report["files"] if r["status"] == "NOT_ATTEMPTED_OFFLINE"]) == 9
    assert len([r for r in report["files"]
                if r["status"] == "MISSING_FROM_PUBLISHED_FILE_LIST"]) == 1


def test_http_403_does_not_claim_data_retrieval():
    def forbidden(_):
        raise urllib.error.HTTPError(
            "https://datadryad.org/api/v2/files/1/download",
            403, "Forbidden", None, None
        )
    report = audit_source_retrieval(
        read_receipt(), download=True, fetcher=forbidden
    )
    assert report["datafiles_accessed"] == []
    assert len([r for r in report["files"] if r["status"] == "HTTP_403_DOWNLOAD_HOLD"]) == 9


@pytest.mark.parametrize("bad", [
    b"", b"<html>sorry, forbidden</html>",
    b"<!doctype html><html>error</html>",
    b'{"error":"not authorized"}',
    b"this is not a csv", b"\xff\xfe\x00\x00",
    b"a,a\n1,2\n", b"x,y\n1\n", b"x,y\n"
])
def test_csv_file_byte_verification_fails_closed(bad):
    with pytest.raises(ValueError):
        verify_file_bytes("CungSeeds.csv", bad)


def test_source_file_receipt_cannot_silently_register_missing_greenhouse_csv(tmp_path):
    receipt = json.loads(SOURCE.read_text(encoding="utf-8"))
    source = next(
        f for f in receipt["dryad"]["files"]
        if f["filename"] == "BombusTrials2018.csv"
    )
    source["listed"] = True
    source["file_id"] = 999999
    path = tmp_path / "invalid_receipt.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ValueError, match="Missing-input gate"):
        read_receipt(path)


def test_csv_schema_metadata_no_row_data_exposed():
    result = verify_file_bytes(
        "CungSeeds.csv",
        b"patch,flower_id,treatment,viable_seeds\nA,1,C,20\nB,2,T,30\n"
    )
    assert result["rows"] == 2
    assert result["columns"] == [
        "patch", "flower_id", "treatment", "viable_seeds"
    ]
    assert result["bytes"] > 0
    assert len(result["sha256"]) == 64
    assert "A,1" not in json.dumps(result)


def test_source_download_not_allowed_to_claim_genetic_paternity():
    receipt = read_receipt()
    assert receipt["source_readout"]["greenhouse_2018"]["male_genetic_paternity_measured"] is False
    assert receipt["source_readout"]["greenhouse_2018"]["late_pollen_realized_efficacy_q_measured"] is False
    assert receipt["validation_contract"]["not_a_direct_q_threshold_test"] is True


def test_public_file_stream_fallback_recovers_after_api_401(monkeypatch):
    observed = []

    def fetch(req, timeout):
        observed.append(req.full_url)
        if "/api/v2/files/" in req.full_url:
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", None, None)
        return io.BytesIO(b"a,b\\n1,2\\n")

    monkeypatch.setattr("urllib.request.urlopen", fetch)
    raw = default_downloader(532300)
    assert raw == b"a,b\\n1,2\\n"
    assert observed == [
        "https://datadryad.org/api/v2/files/532300/download",
        "https://datadryad.org/downloads/file_stream/532300",
    ]


def test_two_public_endpoints_both_denied_are_explicit_holds(monkeypatch):
    def fetch(req, timeout):
        code = 401 if "/api/v2/files/" in req.full_url else 403
        raise urllib.error.HTTPError(req.full_url, code, "Blocked", None, None)

    monkeypatch.setattr("urllib.request.urlopen", fetch)
    report = audit_source_retrieval(read_receipt(), download=True)
    blocked = [x for x in report["files"]
               if x["status"] == "BOTH_PUBLIC_ENDPOINTS_FAILED_HOLD"]
    assert len(blocked) == 9
    assert all(x["endpoint_failures"] == "HTTP_401/HTTP_403" for x in blocked)
    assert report["datafiles_accessed"] == []

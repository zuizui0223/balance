"""Mock-only tests for 2013 Dryad archive provenance; never fake raw data."""
import copy
from scripts.probe_pedicularis_2013_dryad import inspect_source, DATASET_API


def fake_api(url):
    if url == DATASET_API:
        return {
            "identifier": "doi:10.5061/dryad.6cv06",
            "title": "Data from: Evidence of a component Allee effect driven by "
                     "predispersal seed predation in Pedicularis rex",
            "_links": {"stash:version": {"href": "/api/v2/versions/12345"}}
        }
    if url == "https://datadryad.org/api/v2/versions/12345":
        return {"id": 12345}
    if url == "https://datadryad.org/api/v2/versions/12345/files":
        return {"_embedded": {"stash:files": [
            {"id": 321, "path": "plant_patch_data.csv", "size": 53000,
             "mimeType": "text/csv", "digest": "abc", "digestType": "md5"}
        ]}}
    raise AssertionError("unexpected API URL: " + url)


def test_manifest_only_does_not_promote_field_data():
    out = inspect_source(fetch=fake_api)
    assert out["status"] == "DRYAD_METADATA_AND_FILE_MANIFEST_VERIFIED"
    assert out["file_count"] == 1
    assert out["source_file_manifest"][0]["path"] == "plant_patch_data.csv"
    assert out["field_data_retrieved"] is False
    assert out["biological_effect_reanalysed"] is False


def test_mismatched_doi_and_paper_fail_closed():
    def mismatch(url):
        obj = fake_api(url)
        if url == DATASET_API:
            obj["identifier"] = "doi:10.5061/dryad.other"
        return obj
    r = inspect_source(fetch=mismatch)
    assert r["status"] == "DRYAD_METADATA_NOT_VERIFIED_HOLD"
    assert r["diagnostic_error_type"] == "ValueError"


def test_unexpected_external_link_is_rejected():
    def bad_url(url):
        obj = fake_api(url)
        if url == DATASET_API:
            obj["_links"]["stash:version"]["href"] = "https://attacker.example/api/v2/versions/12345"
        return obj
    r = inspect_source(fetch=bad_url)
    assert r["status"] == "DRYAD_METADATA_NOT_VERIFIED_HOLD"
    assert "outside" in r["diagnostic_message"]


def test_empty_file_manifest_is_not_source_qualification():
    def empty_files(url):
        obj = fake_api(url)
        if url.endswith("/files"):
            obj["_embedded"]["stash:files"] = []
        return obj
    r = inspect_source(fetch=empty_files)
    assert r["status"] == "DRYAD_FILES_UNLISTED_HOLD"
    assert r["field_data_retrieved"] is False


def test_version_body_can_omit_id_and_canonical_link_still_qualifies():
    def no_body_version_id(url):
        value = fake_api(url)
        if url == "https://datadryad.org/api/v2/versions/12345":
            value.pop("id", None)
        return value
    result = inspect_source(fetch=no_body_version_id)
    assert result["status"] == "DRYAD_METADATA_AND_FILE_MANIFEST_VERIFIED"
    assert result["version_id"] == 12345
    assert result["field_data_retrieved"] is False


def test_version_body_id_mismatch_is_rejected():
    def mismatch(url):
        obj = fake_api(url)
        if url == "https://datadryad.org/api/v2/versions/12345":
            obj["id"] = 12344
        return obj
    result = inspect_source(fetch=mismatch)
    assert result["status"] == "DRYAD_METADATA_NOT_VERIFIED_HOLD"
    assert "mismatches" in result["diagnostic_message"]

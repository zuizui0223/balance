import csv
import importlib
import io
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
builder = importlib.import_module("build_plant_coder_packets")


def _zip_bytes(path):
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def test_coder_packets_have_identical_evidence_and_coder_specific_worksheets(tmp_path):
    outputs = builder.build_all(tmp_path)
    a_zip, a_receipt = outputs["CODER_A"]
    b_zip, b_receipt = outputs["CODER_B"]

    a = _zip_bytes(a_zip)
    b = _zip_bytes(b_zip)

    assert json.loads(a_receipt.read_text(encoding="utf-8"))["coder_id"] == "CODER_A"
    assert json.loads(b_receipt.read_text(encoding="utf-8"))["coder_id"] == "CODER_B"

    shared = {
        "data/BALANCE_PLANT_MACRO_CODEBOOK_V1.csv",
        "docs/BALANCE_PLANT_DOUBLE_CODING_PROTOCOL_V1.md",
        "U1/BALANCE_PLANT_U1_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
        "U2/BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv",
        "U6/BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv",
    }
    for name in shared:
        assert a[name] == b[name]

    for lane in ("U1", "U2", "U6"):
        a_name = next(
            name for name in a
            if name.startswith(f"{lane}/") and "WORKSHEET_CODER_A_" in name
        )
        b_name = next(
            name for name in b
            if name.startswith(f"{lane}/") and "WORKSHEET_CODER_B_" in name
        )

        a_rows = list(csv.DictReader(io.StringIO(a[a_name].decode("utf-8"))))
        b_rows = list(csv.DictReader(io.StringIO(b[b_name].decode("utf-8"))))
        assert a_rows and b_rows
        assert {row["coder_id"] for row in a_rows} == {"CODER_A"}
        assert {row["coder_id"] for row in b_rows} == {"CODER_B"}
        assert [row["cluster_id"] for row in a_rows] == [
            row["cluster_id"] for row in b_rows
        ]


def test_coder_packets_exclude_screening_adjudication_agreement_and_receipt_artifacts(tmp_path):
    outputs = builder.build_all(tmp_path)
    forbidden = (
        "SCREENING",
        "CONFLICT_SCREEN",
        "ADJUDICATION",
        "AGREEMENT",
        "PREDICTOR_RECEIPT",
        "REACTIVATION",
    )
    for coder, (zip_path, _receipt_path) in outputs.items():
        with zipfile.ZipFile(zip_path) as archive:
            names = archive.namelist()
            assert "PACKET_RECEIPT.json" in names
            for name in names:
                if name == "PACKET_RECEIPT.json":
                    continue
                upper = name.upper()
                assert all(fragment not in upper for fragment in forbidden), (coder, name)


def test_coder_packets_do_not_contain_the_other_coder_id_in_worksheet_rows(tmp_path):
    outputs = builder.build_all(tmp_path)
    for coder, (zip_path, _receipt_path) in outputs.items():
        other = "CODER_B" if coder == "CODER_A" else "CODER_A"
        with zipfile.ZipFile(zip_path) as archive:
            worksheet_names = [name for name in archive.namelist() if "WORKSHEET_" in name]
            assert len(worksheet_names) == 3
            for name in worksheet_names:
                rows = list(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8"))))
                assert {row["coder_id"] for row in rows} == {coder}
                assert all(other not in json.dumps(row) for row in rows)


def test_packet_receipts_preserve_frozen_forbidden_input_contract(tmp_path):
    outputs = builder.build_all(tmp_path)
    expected = json.loads(
        (ROOT / "data" / "BALANCE_PLANT_CODER_HANDOFF_MANIFEST_V1.json").read_text(
            encoding="utf-8"
        )
    )["shared"]["forbidden_inputs"]

    for coder, (_zip_path, receipt_path) in outputs.items():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["coder_id"] == coder
        assert receipt["forbidden_inputs"] == expected
        assert receipt["claim_ceiling"] == "independent_coder_handoff_only_no_biological_result"

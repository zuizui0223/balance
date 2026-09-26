from pathlib import Path

import csv
import pytest

from balance_domain.plant_u3_table_s1_candidates import (
    FIELDS,
    build_u3_table_s1_candidate_readout,
    load_u3_table_s1_candidates,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_TABLE_S1_CANDIDATES_V1.csv"


def test_candidate_reduction_keeps_all_three_families_open_without_claiming_identity():
    rows = load_u3_table_s1_candidates(LEDGER)
    out = build_u3_table_s1_candidate_readout(LEDGER)
    assert len(rows) == 7
    assert out["archival_open_families"] == ["Bixaceae", "Malvaceae", "Scrophulariaceae"]
    assert out["exact_table_s1_identity_closed"] is False
    assert out["n_archival_open_species_level_candidates"] == 2


def test_bixaceae_is_narrowed_to_amoreuxia_and_coclospermum_is_rejected():
    rows = load_u3_table_s1_candidates(LEDGER)
    amo = next(r for r in rows if r["candidate_taxon"] == "Amoreuxia spp.")
    coc = next(r for r in rows if r["candidate_taxon"] == "Cochlospermum spp.")
    assert amo["selection_status"] == "ARCHIVAL_OPEN"
    assert amo["heteranthery_morphology_status"] == "PASS"
    assert coc["selection_status"] == "REJECTED"
    assert coc["heteranthery_morphology_status"] == "FAIL"


def test_malvaceae_does_not_promote_mollia_speciosa_from_plausibility():
    rows = load_u3_table_s1_candidates(LEDGER)
    spec = next(r for r in rows if r["candidate_taxon"] == "Mollia speciosa")
    assert spec["selection_status"] == "ARCHIVAL_OPEN"
    assert spec["candidate_grain"] == "SPECIES"
    assert spec["blocker"] == "EXACT_2010_TABLE_S1_IDENTITY_NOT_RECOVERED"


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_open_candidate_cannot_hide_failed_morphology(tmp_path):
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    row = next(r for r in rows if r["selection_status"] == "ARCHIVAL_OPEN")
    row["heteranthery_morphology_status"] = "FAIL"
    path = tmp_path / "candidates.csv"
    _write(path, rows)
    with pytest.raises(ValueError, match="ARCHIVAL_OPEN candidate cannot fail morphology"):
        load_u3_table_s1_candidates(path)

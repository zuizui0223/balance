from pathlib import Path

import csv
import pytest

from balance_domain.plant_u3_evidence_ceiling import (
    FIELDS,
    build_u3_evidence_ceiling_readout,
    load_u3_evidence_ceiling,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_EVIDENCE_CEILING_V1.csv"


def test_current_u3_evidence_ceiling_has_three_explicit_open_targets():
    rows = load_u3_evidence_ceiling(LEDGER)
    out = build_u3_evidence_ceiling_readout(LEDGER)
    assert len(rows) == 3
    assert out["decision_counts"] == {"OPEN": 3}
    assert out["open_taxa"] == [
        "Monochoria australasica",
        "Monochoria cyanea",
        "Osbeckia chinensis",
    ]
    assert out["evidence_ceiling_closed"] is False


def test_monochoria_open_gate_is_species_level_effective_pollination():
    out = build_u3_evidence_ceiling_readout(LEDGER)
    for taxon in ("Monochoria australasica", "Monochoria cyanea"):
        assert out["open_gates"][taxon] == "DIRECT_SPECIES_LEVEL_EFFECTIVE_ANIMAL_POLLINATION"


def test_osbeckia_open_gate_is_control_pollen_fate_measurement():
    out = build_u3_evidence_ceiling_readout(LEDGER)
    assert out["open_gates"]["Osbeckia chinensis"] == "CONTROL_POLLEN_FATE_CONFLICT"


def test_open_ceiling_cannot_drop_missing_evidence(tmp_path):
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows[0]["missing_evidence"] = ""
    path = tmp_path / "ceil.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="OPEN ceiling requires explicit missing evidence"):
        load_u3_evidence_ceiling(path)

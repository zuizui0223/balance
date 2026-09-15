import csv
import importlib.util
import json
from pathlib import Path

import pytest

from balance_domain.pattern_ledger import build_pattern_readout_from_rows, load_pattern_ledger


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_balance_pattern_map_figure3.py"
LEDGER = ROOT / "data" / "BALANCE_PATTERN_LEDGER_V1.csv"
READOUT = ROOT / "data" / "BALANCE_PATTERN_READOUT_V1.json"


def _module():
    spec = importlib.util.spec_from_file_location("balance_fig3", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _raw_rows():
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or ()), list(reader)


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_figure3_counts_match_frozen_pattern_readout():
    mod = _module()
    rows, clusters, counts = mod._load()
    assert len({c for c, _, _ in clusters}) == 17
    assert sum(1 for c, _, p in clusters if p in mod.MIDDLE) == 9
    assert sum(1 for c, _, p in clusters if p == "BOUNDARY_CROSSING") == 2
    assert sum(1 for c, _, p in clusters if p == "UNRESOLVED") == 5


def test_figure3_preserves_expected_domain_pattern_matrix():
    mod = _module()
    _, _, counts = mod._load()
    assert counts[("plant", "CONFLICT_WITHOUT_SPLITTING")] == 7
    assert counts[("plant", "SANDWICHED_TRANSITION_MOSAIC")] == 1
    assert counts[("plant", "BOUNDARY_CROSSING")] == 1
    assert counts[("plant", "UNRESOLVED")] == 3
    assert counts[("protein_function", "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE")] == 1
    assert counts[("protein_function", "UNRESOLVED")] == 1
    assert counts[("gene_regulatory_architecture", "DIRECT_DIFFERENTIATION")] == 1
    assert counts[("genome_architecture_ecological_strategy", "BOUNDARY_CROSSING")] == 1
    assert counts[("vertebrate_morphology", "UNRESOLVED")] == 1


def test_figure3_explicitly_prohibits_prevalence_interpretation():
    svg = _module().build_svg()
    assert "recurrence map, not an estimate of natural prevalence" in svg
    assert "17 independent clusters; 9 middle-regime signatures" in svg
    assert "do not estimate natural prevalence or direct BALANCE occupancy" in svg


def test_figure3_rejects_duplicate_cluster_rows_before_counting(tmp_path):
    mod = _module()
    fieldnames, rows = _raw_rows()
    malformed = [dict(rows[0]), dict(rows[0])]
    ledger = tmp_path / "duplicate.csv"
    _write_rows(ledger, fieldnames, malformed)
    mod.LEDGER = ledger
    with pytest.raises(ValueError, match="duplicate cluster_id"):
        mod._load()


def test_figure3_requires_ledger_and_frozen_readout_to_match(tmp_path):
    mod = _module()
    drifted = json.loads(READOUT.read_text(encoding="utf-8"))
    drifted["n_independent_clusters"] += 1
    readout = tmp_path / "drifted.json"
    readout.write_text(json.dumps(drifted), encoding="utf-8")
    mod.READOUT = readout
    with pytest.raises(ValueError, match="ledger and frozen readout disagree"):
        mod._load()


def test_figure3_rejects_new_pattern_class_without_explicit_display_row(tmp_path):
    mod = _module()
    fieldnames, rows = _raw_rows()
    altered = [dict(row) for row in rows]
    altered[0]["pattern_class"] = "HYSTERESIS_OR_PATH_DEPENDENCE"
    ledger = tmp_path / "new-pattern.csv"
    _write_rows(ledger, fieldnames, altered)
    validated = load_pattern_ledger(ledger)
    readout = tmp_path / "new-pattern.json"
    readout.write_text(
        json.dumps(build_pattern_readout_from_rows(validated)),
        encoding="utf-8",
    )
    mod.LEDGER = ledger
    mod.READOUT = readout
    with pytest.raises(ValueError, match="no registered display row"):
        mod._load()


def test_figure3_rejects_new_domain_without_explicit_display_column(tmp_path):
    mod = _module()
    fieldnames, rows = _raw_rows()
    altered = [dict(row) for row in rows]
    altered[0]["domain"] = "new_domain"
    ledger = tmp_path / "new-domain.csv"
    _write_rows(ledger, fieldnames, altered)
    validated = load_pattern_ledger(ledger)
    readout = tmp_path / "new-domain.json"
    readout.write_text(
        json.dumps(build_pattern_readout_from_rows(validated)),
        encoding="utf-8",
    )
    mod.LEDGER = ledger
    mod.READOUT = readout
    with pytest.raises(ValueError, match="no registered display column"):
        mod._load()

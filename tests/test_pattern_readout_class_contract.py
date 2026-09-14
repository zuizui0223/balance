import csv
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_balance_pattern_readout.py"
LEDGER = ROOT / "data" / "BALANCE_PATTERN_LEDGER_V1.csv"


def _load_builder():
    spec = importlib.util.spec_from_file_location("balance_pattern_readout_class_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_pattern_classes_are_the_seven_preregistered_reality_classes():
    builder = _load_builder()
    assert builder.PATTERN_CLASSES == {
        "CONFLICT_WITHOUT_SPLITTING",
        "SANDWICHED_TRANSITION_MOSAIC",
        "BOUNDARY_CROSSING",
        "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE",
        "HYSTERESIS_OR_PATH_DEPENDENCE",
        "DIRECT_DIFFERENTIATION",
        "UNRESOLVED",
    }


def test_builder_rejects_unregistered_pattern_class(tmp_path):
    builder = _load_builder()
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or ())
        row = dict(next(reader))

    row["pattern_class"] = "CONFLICT_WITHOUT_SPLITTNG"
    path = tmp_path / "unknown-pattern.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)

    with pytest.raises(ValueError, match="not a registered reality-pattern class"):
        builder.build(path)

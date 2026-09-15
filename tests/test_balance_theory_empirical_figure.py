import copy
import csv
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_balance_theory_empirical_figure.py"


def _module():
    spec = importlib.util.spec_from_file_location("balance_fig", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sources(module):
    pattern = json.loads(module.PATTERN.read_text(encoding="utf-8"))
    pool = json.loads(module.POOL.read_text(encoding="utf-8"))
    with module.LAYER_MAP.open(encoding="utf-8", newline="") as handle:
        layer_map = list(csv.DictReader(handle))
    return pattern, pool, layer_map


def test_flagship_figure_uses_frozen_counts_and_keeps_direct_gap_empty():
    svg = _module().build_svg()
    assert "strict positives = 3" in svg
    assert "design-matched negatives = 2" in svg
    assert "recurrence = 3 independent positives" in svg
    assert "pool = conditional positive-case summary" in svg
    assert "pattern-ledger clusters = 17" in svg
    assert "middle-regime signatures = 9" in svg
    assert "0 direct matched receipts" in svg
    assert "W*S, W*D, ρ, Φ, ξ, dB not identified" in svg


def test_flagship_figure_keeps_boundaries_outside_strict_q1b():
    svg = _module().build_svg()
    assert "estimand boundaries = 2" in svg
    assert "attribution failures = 1" in svg
    assert "rather than inflate k" in svg
    assert "Q1B pool ≠ design-wide mean or BALANCE occupancy" in svg


def test_flagship_figure_freezes_moderator_gate():
    svg = _module().build_svg()
    assert "moderator meta-regression prohibited until k≥5" in svg
    assert "conditional positive-case summary: k=3" in svg


def test_flagship_source_claim_contracts_are_explicit():
    module = _module()
    pattern, pool, layer_map = _sources(module)
    direct = module._validate_source_contracts(pattern, pool, layer_map)
    assert direct["status"] == "NOT_IDENTIFIED"
    assert direct["allowed_inference"] == "no_direct_claim"
    assert direct["prohibited_inference"] == "WSstar_gt_WDstar_rho_Phi_xi_dB"


@pytest.mark.parametrize(
    "surface, field",
    [
        ("pattern", "analysis"),
        ("pattern", "claim_ceiling"),
        ("pool", "analysis"),
        ("pool", "pool_gate"),
        ("pool", "claim_ceiling"),
    ],
)
def test_flagship_rejects_json_source_contract_drift(surface, field):
    module = _module()
    pattern, pool, layer_map = _sources(module)
    target = pattern if surface == "pattern" else pool
    target[field] = "DRIFTED"
    with pytest.raises(ValueError, match="frozen flagship source contract"):
        module._validate_source_contracts(pattern, pool, layer_map)


@pytest.mark.parametrize(
    "field",
    ["status", "current_evidence", "allowed_inference", "prohibited_inference"],
)
def test_flagship_rejects_direct_worldline_claim_drift(field):
    module = _module()
    pattern, pool, layer_map = _sources(module)
    altered = copy.deepcopy(layer_map)
    direct = next(row for row in altered if row["theory_object"] == "shared_vs_differentiated_worldline")
    direct[field] = "DRIFTED"
    with pytest.raises(ValueError, match="frozen flagship source contract"):
        module._validate_source_contracts(pattern, pool, altered)


def test_flagship_rejects_duplicate_direct_worldline_layer_rows():
    module = _module()
    pattern, pool, layer_map = _sources(module)
    altered = copy.deepcopy(layer_map)
    direct = next(row for row in altered if row["theory_object"] == "shared_vs_differentiated_worldline")
    altered.append(copy.deepcopy(direct))
    with pytest.raises(ValueError, match="exactly one direct-worldline"):
        module._validate_source_contracts(pattern, pool, altered)

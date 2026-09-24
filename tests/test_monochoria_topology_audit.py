from pathlib import Path

import csv
import pytest

from balance_domain.monochoria_topology_audit import (
    CANDIDATE_TAXA,
    FIELDS,
    compare_candidate_topology,
    gene_pair_counts,
    load_topology_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_MONOCHORIA_TOPOLOGY_V1.csv"


class _Terminal:
    def __init__(self, name):
        self.name = name


class _Node:
    def __init__(self, name):
        self.name = name


class _FakeTree:
    def __init__(self, mrca_depths, distances):
        names = {
            "Pontederia korsakowii",
            "Pontederia vaginalis",
            *CANDIDATE_TAXA,
        }
        self._terminals = [_Terminal(name) for name in sorted(names)]
        self._nodes = {
            (case, candidate): _Node(f"{case}|{candidate}")
            for case in ("Pontederia korsakowii", "Pontederia vaginalis")
            for candidate in CANDIDATE_TAXA
        }
        self._depths = {
            self._nodes[key]: depth for key, depth in mrca_depths.items()
        }
        self._distances = distances

    def get_terminals(self):
        return self._terminals

    def depths(self, unit_branch_lengths=False):
        assert unit_branch_lengths is True
        return self._depths

    def common_ancestor(self, case, candidate):
        return self._nodes[(case, candidate)]

    def distance(self, case, candidate):
        return self._distances[(case, candidate)]


def test_topology_ledger_has_registered_outgroup_cases_candidates_and_references():
    rows = load_topology_ledger(LEDGER)
    by_taxon = {row["taxon"]: row for row in rows}
    assert len(rows) == 10
    assert by_taxon["Pontederia cordata"]["role"] == "OUTGROUP"
    assert by_taxon["Pontederia australasica"]["role"] == "CANDIDATE"
    assert by_taxon["Pontederia cyanea"]["role"] == "CANDIDATE"
    assert by_taxon["Pontederia korsakowii"]["role"] == "CASE"
    assert by_taxon["Pontederia vaginalis"]["role"] == "CASE"
    assert sum(row["role"] == "REFERENCE" for row in rows) == 5


def test_equal_mrca_depth_is_topological_tie_even_if_branch_lengths_differ():
    case = "Pontederia korsakowii"
    tree = _FakeTree(
        {
            (case, "Pontederia australasica"): 3,
            (case, "Pontederia cyanea"): 3,
            ("Pontederia vaginalis", "Pontederia australasica"): 2,
            ("Pontederia vaginalis", "Pontederia cyanea"): 2,
        },
        {
            (case, "Pontederia australasica"): 0.01,
            (case, "Pontederia cyanea"): 0.02,
            ("Pontederia vaginalis", "Pontederia australasica"): 0.03,
            ("Pontederia vaginalis", "Pontederia cyanea"): 0.04,
        },
    )
    out = compare_candidate_topology(tree, case)
    assert out["topology_outcome"] == "EQUAL_MRCA_DEPTH"
    assert out["topology_winner"] is None


def test_more_recent_mrca_wins_before_branch_length_distance():
    case = "Pontederia korsakowii"
    tree = _FakeTree(
        {
            (case, "Pontederia australasica"): 2,
            (case, "Pontederia cyanea"): 4,
            ("Pontederia vaginalis", "Pontederia australasica"): 2,
            ("Pontederia vaginalis", "Pontederia cyanea"): 2,
        },
        {
            (case, "Pontederia australasica"): 0.001,
            (case, "Pontederia cyanea"): 0.2,
            ("Pontederia vaginalis", "Pontederia australasica"): 0.1,
            ("Pontederia vaginalis", "Pontederia cyanea"): 0.1,
        },
    )
    out = compare_candidate_topology(tree, case)
    assert out["topology_outcome"] == "MORE_RECENT_MRCA"
    assert out["topology_winner"] == "Pontederia cyanea"


def test_gene_pair_counts_uses_only_joint_unambiguous_sites():
    aligned = {
        "g1": {
            "a": "ACGTN-",
            "b": "ATGTA-",
            "c": "ACGTT-",
        }
    }
    counts = gene_pair_counts(aligned, ["a", "b", "c"])
    assert counts["g1"][("a", "b")] == (1, 4)
    assert counts["g1"][("a", "c")] == (0, 4)
    assert counts["g1"][("b", "c")] == (1, 5)


def test_topology_ledger_rejects_duplicate_accession(tmp_path):
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows[1]["accession"] = rows[0]["accession"]
    path = tmp_path / "ledger.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="accession must be unique"):
        load_topology_ledger(path)

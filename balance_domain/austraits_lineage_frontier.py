"""Candidate same-genus structural-state contrasts from public AusTraits v7.

This is **not** ancestral reconstruction, a counted independent origin, or a
historical functional-trade-off test. It exports genus-level counts only, never
the source's raw species/trait records, and guards every missing state.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from .austraits_architecture_macro import SEX_MODES, POLLEN, _safe_species_value
from .austraits_organizational_hierarchy import FLOWER_STATES


def _group_by_genus(states: dict[str, str]) -> dict[str, dict[str, set[str]]]:
    groups = defaultdict(lambda: defaultdict(set))
    for name, state in states.items():
        genus = name.split()[0]
        groups[genus][state].add(name)
    return groups


def _eligible_pairs(
    states: dict[str, str], negative_state: str,
    positive_states: set[str], *,
    minimum_each: int = 2,
) -> tuple[list[dict], dict[str, dict[str, set[str]]]]:
    """Require >=2 distinct species on each side, before examining pollen."""
    groups = _group_by_genus(states)
    out = []
    for genus, counts in groups.items():
        shared_species = counts.get(negative_state, set())
        separated_species = set().union(
            *(counts.get(state, set()) for state in positive_states)
        )
        if len(shared_species) < minimum_each or len(separated_species) < minimum_each:
            continue
        state_counts = {
            state: len(names) for state, names in sorted(counts.items())
        }
        out.append({
            "genus": genus,
            "species_with_qualifying_states": sum(state_counts.values()),
            "shared_state_species": len(shared_species),
            "separated_state_species": len(separated_species),
            "source_state_counts": state_counts,
            # These are species labels, not reconstructed polarity or times.
            "not_a_reconstructed_transition": True,
        })
    out.sort(
        key=lambda x: (
            -min(x["shared_state_species"], x["separated_state_species"]),
            -x["species_with_qualifying_states"],
            x["genus"],
        )
    )
    return out, groups


def _pollen_coverage(candidate: dict, states: dict[str, str],
                     pollen: dict[str, str], negative: str,
                     positive: set[str]) -> dict:
    genus = candidate["genus"]
    # No source author reconciliation beyond the strict binomial qualifier.
    matching = {
        name: state for name, state in states.items()
        if name.split()[0] == genus and name in pollen
        and (state == negative or state in positive)
    }
    mode_counts = Counter(pollen[name] for name in matching)
    cross = Counter(
        f"{pollen[name]} | "
        + ("SHARED" if state == negative else "SEPARATED")
        for name, state in matching.items()
    )
    within_environment = {
        mode: {
            "shared": sum(
                state == negative and pollen[name] == mode
                for name, state in matching.items()
            ),
            "separated": sum(
                state in positive and pollen[name] == mode
                for name, state in matching.items()
            ),
        }
        for mode in ("INSECT", "WIND")
    }
    return {
        "exact_species_with_independent_pollen_annotation": len(matching),
        "pollen_mode_counts": dict(sorted(mode_counts.items())),
        "sex_state_by_pollen": dict(sorted(cross.items())),
        "within_mode_shared_and_separated_species": {
            mode: (
                per["shared"] >= 1 and per["separated"] >= 1
            ) for mode, per in within_environment.items()
        },
        "both_pollen_modes_documented_in_genus": (
            mode_counts["INSECT"] > 0 and mode_counts["WIND"] > 0
        ),
    }


def analyze_candidate_lineages(rows: list[dict[str, str]]) -> dict:
    """Exhaustive qualified genus-level candidate screen; no P-value."""
    sex, sex_q = _safe_species_value(rows, "sex_type", SEX_MODES)
    flower, flower_q = _safe_species_value(
        rows, "flower_structural_sex_type", FLOWER_STATES
    )
    pollen, pollen_q = _safe_species_value(rows, "pollination_syndrome", POLLEN)

    def summarize(
        data: dict[str, str], negative: str, positive: set[str],
        label: str,
    ) -> dict:
        pairs, groups = _eligible_pairs(data, negative, positive)
        decorated = []
        for candidate in pairs:
            enriched = dict(candidate)
            enriched["pollen_coverage"] = _pollen_coverage(
                candidate, data, pollen, negative, positive
            )
            decorated.append(enriched)
        return {
            "comparison": label,
            "source_exact_species": len(data),
            "qualified_genera": len(groups),
            "candidate_genera_meeting_two_per_state": len(pairs),
            "candidates_with_both_pollen_modes": sum(
                x["pollen_coverage"]["both_pollen_modes_documented_in_genus"]
                for x in decorated
            ),
            "candidates_with_any_source_pollen_data": sum(
                x["pollen_coverage"]["exact_species_with_independent_pollen_annotation"] > 0
                for x in decorated
            ),
            "top_candidate_genera": decorated[:30],
            "not_ancestral_or_phylogenetic_transitions": True,
        }

    species = summarize(
        sex, "SHARED_SEX_SYSTEM",
        {"SEX_SEPARATED_AMONG_FLOWERS", "SEX_SEPARATED_AMONG_INDIVIDUALS"},
        "whole-plant reproductive-sex system contrasts among congeners",
    )
    flower_result = summarize(
        flower, "BISEXUAL_FLOWER", {"UNISEXUAL_FLOWER"},
        "flower-level bisexual vs unisexual floral state among congeners",
    )
    return {
        "schema": "BALANCE_AUSTRAITS_SOURCE_ARCHITECTURE_LINEAGE_CANDIDATES_V1",
        "status": "SOURCE_CANDIDATE_SCREEN_NOT_ORIGIN_INFERENCE",
        "source": "AusTraits v7, same six previously frozen traits",
        "qualification_rule": (
            "exact binomial, one source-consistent state per trait, "
            ">=2 distinct species on each architecture-state side per genus"
        ),
        "species_sex_system_candidate_lineages": species,
        "flower_structural_sex_candidate_lineages": flower_result,
        "source_quality": {
            "sex": sex_q,
            "flower": flower_q,
            "pollen": pollen_q,
        },
        "prohibited_inference": [
            "a candidate genus is a monophyletic lineage",
            "multiple species imply multiple evolutionary origins",
            "current pollen modes establish the ancestral environment",
            "trait state differences establish functionally opposing optima",
            "structure differences demonstrate selected new modules",
            "a source-selected genus is a population-level occurrence frequency",
        ],
        "source_trait_records_redistributed": False,
    }

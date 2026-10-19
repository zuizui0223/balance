"""Independent structural-level contrasts in the frozen AusTraits v7 archive.

This is an exploratory *morphology* layer, deliberately separate from:
  - sex_type: sex-system organization at a whole-plant level;
  - flower_structural_sex_type: bisexual/unisexual flower condition;
  - direct same-coordinate functional conflict or historic module origin.
It only consumes the same six source traits already frozen and acquired.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Mapping

# The import is resolved after this parent module is initialized; its
# analyze_selected_csv imports this layer locally to avoid a circular import.
from .austraits_architecture_macro import (
    POLLEN,
    SEX_MODES,
    _safe_species_value,
)

FLOWER_STATES = {
    "bisexual": "BISEXUAL_FLOWER",
    "unisexual": "UNISEXUAL_FLOWER",
    "incompletely_unisexual": "PARTIAL_UNISEXUAL_FLOWER",
}
CONSISTENT_ORGANIZATIONS = {
    ("SHARED_SEX_SYSTEM", "BISEXUAL_FLOWER"): "WITHIN_FLOWER_SHARED",
    ("SEX_SEPARATED_AMONG_FLOWERS", "UNISEXUAL_FLOWER"): "AMONG_FLOWERS_SEPARATED",
    ("SEX_SEPARATED_AMONG_INDIVIDUALS", "UNISEXUAL_FLOWER"): "AMONG_INDIVIDUALS_SEPARATED",
}
POLLEN_MODES = ("INSECT", "WIND")


def _count(rows: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(rows).items()))


def _mean(vals: list[float]) -> float | None:
    return sum(vals) / len(vals) if vals else None


def _frozen_support(
    rows_by_mode: Mapping[str, list[str]], *,
    minimum_species: int = 20, minimum_genera: int = 5,
) -> bool:
    return all(
        len(rows_by_mode.get(m, [])) >= minimum_species
        and len({x.split()[0] for x in rows_by_mode.get(m, [])}) >= minimum_genera
        for m in POLLEN_MODES
    )


def _source_independent_genus_balance(sex: dict[str, str], pollen: dict[str, str]) -> dict:
    """Genus-equal-weight descriptive check, NOT a phylogenetic model."""
    by_genus: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for name in sorted(sex.keys() & pollen.keys()):
        group = name.split()[0]
        mode = pollen[name]
        by_genus[group][mode].append(float(sex[name] != "SHARED_SEX_SYSTEM"))
    means = {
        mode: [
            _mean(by_mode[mode])
            for by_mode in by_genus.values()
            if by_mode.get(mode)
        ]
        for mode in POLLEN_MODES
    }
    overlap = [
        g for g, obs in by_genus.items()
        if obs.get("INSECT") and obs.get("WIND")
    ]
    within = [
        _mean(by_genus[g]["WIND"]) - _mean(by_genus[g]["INSECT"])
        for g in overlap
    ]
    # Positivity: a genus with only one pollination mode cannot identify
    # any within-genus response to a change in pollination system.
    equal_diff = (
        _mean(means["WIND"]) - _mean(means["INSECT"])
        if means["WIND"] and means["INSECT"] else None
    )
    return {
        "estimand": "genus-equal-weight source-selected sex-system contrast",
        "genera_by_mode": {m: len(means[m]) for m in POLLEN_MODES},
        "equal_genus_fraction_separated": {
            m: _mean(means[m]) for m in POLLEN_MODES
        },
        "wind_minus_insect_equal_genus": equal_diff,
        "genera_with_both_modes": len(overlap),
        "within_genus_signs": {
            "positive": sum(x > 1e-12 for x in within),
            "negative": sum(x < -1e-12 for x in within),
            "zero": sum(abs(x) <= 1e-12 for x in within),
        },
        "within_genus_mean": _mean(within),
        "claim": "descriptive weighting diagnostic, not ancestry-adjusted selection",
    }


def analyze_organizational_hierarchy(rows: list[dict[str, str]]) -> dict:
    """Report real source overlap, morphology-level association and mismatches."""
    sex, sex_quality = _safe_species_value(rows, "sex_type", SEX_MODES)
    flower, flower_quality = _safe_species_value(
        rows, "flower_structural_sex_type", FLOWER_STATES
    )
    pollen, pollen_quality = _safe_species_value(
        rows, "pollination_syndrome", POLLEN
    )

    # A flower's sex phenotype and plant-wide sex system are not identical.
    # Record discrepancies in separate sources as disagreements, never as
    # false observations or evidence for a transition in evolutionary time.
    both = sorted(sex.keys() & flower.keys())
    organizational = {}
    status = Counter()
    for name in both:
        plant_sex, flower_sex = sex[name], flower[name]
        key = (plant_sex, flower_sex)
        if flower_sex == "PARTIAL_UNISEXUAL_FLOWER":
            resolved = "FLOWER_PARTIAL_STATE"
        else:
            resolved = CONSISTENT_ORGANIZATIONS.get(
                key, "CROSS_LEVEL_LABEL_DISCORDANCE"
            )
        organizational[name] = resolved
        status[resolved] += 1

    # Flower-level biological data are a different independent check
    # from previously reported species sex_system x pollination_syndrome.
    floral_pollen = sorted(flower.keys() & pollen.keys())
    flor_by_mode: dict[str, list[str]] = defaultdict(list)
    flor_cross = Counter()
    for name in floral_pollen:
        mode = pollen[name]
        flor_by_mode[mode].append(name)
        flor_cross[f"{mode} | {flower[name]}"] += 1

    def fraction_unisexual(mode: str) -> float | None:
        qualified = [
            name for name in flor_by_mode.get(mode, [])
            if flower[name] in ("BISEXUAL_FLOWER", "UNISEXUAL_FLOWER")
        ]
        if not qualified:
            return None
        return sum(
            flower[name] == "UNISEXUAL_FLOWER" for name in qualified
        ) / len(qualified)

    eligible = {
        mode: [
            name for name in flor_by_mode.get(mode, [])
            if flower[name] in ("BISEXUAL_FLOWER", "UNISEXUAL_FLOWER")
        ]
        for mode in POLLEN_MODES
    }
    readiness = _frozen_support(eligible)

    triple = sorted(sex.keys() & flower.keys() & pollen.keys())
    triple_modes = Counter(
        f"{pollen[name]} | {organizational[name]}" for name in triple
    )
    # Of the three-way overlap, only already directly supported
    # organization labels may contribute to a hierarchy-mode description.
    complete = {
        mode: [
            name for name in triple
            if pollen[name] == mode
            and organizational[name] in CONSISTENT_ORGANIZATIONS.values()
        ]
        for mode in POLLEN_MODES
    }
    triple_ready = _frozen_support(complete)

    out = {
        "schema": "BALANCE_AUSTRAITS_STRUCTURE_LEVELS_POST_OPEN_V1",
        "status": "EXPLORATORY_RETRIEVED_MORPHOLOGY_NOT_CONFLICT",
        "source_distinctions": {
            "sex_type": "whole-organism sex system",
            "flower_structural_sex_type": "flower-level structural sex",
            "pollination_syndrome": "pollination opportunity, not measured selective gradient",
        },
        "flower_source_quality": flower_quality,
        "sex_system_source_quality": sex_quality,
        "pollen_source_quality": pollen_quality,
        "sex_system_x_flower_structure": {
            "same_exact_binomial_species": len(both),
            "classification": _count(list(organizational.values())),
            "cross_level_unresolved_or_discordant": (
                status["CROSS_LEVEL_LABEL_DISCORDANCE"]
                + status["FLOWER_PARTIAL_STATE"]
            ),
        },
        "flower_structure_x_pollen_mode": {
            "same_exact_binomial_species": len(floral_pollen),
            "source_by_mode": {
                mode: {
                    "all_flower_states_species": len(flor_by_mode.get(mode, [])),
                    "qualified_bisexual_unisexual_species": len(eligible[mode]),
                    "qualified_genera": len({s.split()[0] for s in eligible[mode]}),
                    "unisexual_flower_fraction": fraction_unisexual(mode),
                }
                for mode in POLLEN_MODES
            },
            "cross_table": dict(sorted(flor_cross.items())),
            "status": (
                "EXPLORATORY_DESCRIPTIVE_COMPARISON"
                if readiness else "HOLD_INSUFFICIENT_COMMON_SUPPORT"
            ),
            "wind_minus_insect_unisexual_fraction": (
                fraction_unisexual("WIND") - fraction_unisexual("INSECT")
                if readiness else None
            ),
        },
        "sex_system_x_flower_structure_x_pollen": {
            "same_exact_binomial_species": len(triple),
            "source_organization_by_pollen": dict(sorted(triple_modes.items())),
            "consistent_structure_by_mode": {
                mode: {
                    "species": len(complete[mode]),
                    "genera": len({s.split()[0] for s in complete[mode]}),
                }
                for mode in POLLEN_MODES
            },
            "status": (
                "EXPLORATORY_DESCRIPTIVE_COMPARISON"
                if triple_ready else "HOLD_INSUFFICIENT_COMMON_SUPPORT"
            ),
        },
        "genus_balanced_sex_system_pollen": _source_independent_genus_balance(
            sex, pollen
        ),
        "not_direct_functional_conflict": True,
        "not_historical_origins": True,
    }
    return out

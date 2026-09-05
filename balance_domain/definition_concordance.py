"""Compare critical regions recovered under multiple operational definitions.

This Chapter-2 utility is agnostic about biology. Each definition supplies a
signed margin over the same ordered contexts, where zero is the definition's
boundary. The analyzer distinguishes common, overlapping, separated, and
non-identifiable critical regions without inventing numeric context values from
ordinal labels.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class CrossingBracket:
    definition: str
    left_context: str
    right_context: str
    left_index: int
    right_index: int
    left_margin: float
    right_margin: float
    exact_context: bool
    numeric_critical_context: float | None
    status: str

    @property
    def index_interval(self) -> tuple[int, int]:
        return (self.left_index, self.right_index)


@dataclass(frozen=True)
class DefinitionConcordance:
    brackets: tuple[CrossingBracket, ...]
    classification: str
    common_index_interval: tuple[int, int] | None
    common_contexts: tuple[str, ...]
    max_pairwise_numeric_gap: float | None


def _sign(value: float, tolerance: float) -> int:
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def crossing_bracket(
    definition: str,
    contexts: Sequence[str],
    margins: Mapping[str, float],
    *,
    context_values: Mapping[str, float] | None = None,
    tolerance: float = 1e-12,
) -> CrossingBracket:
    if len(contexts) < 2:
        raise ValueError("at least two ordered contexts are required")
    if len(set(contexts)) != len(contexts):
        raise ValueError("context labels must be unique")
    tol = _finite(tolerance, "tolerance")
    if tol < 0:
        raise ValueError("tolerance must be >= 0")

    values = []
    for context in contexts:
        if context not in margins:
            raise ValueError(f"definition {definition!r} lacks context {context!r}")
        values.append(_finite(margins[context], f"margin[{context}]"))

    exact = [i for i, value in enumerate(values) if _sign(value, tol) == 0]
    changes: list[tuple[int, int]] = []
    for i in range(len(values) - 1):
        s0 = _sign(values[i], tol)
        s1 = _sign(values[i + 1], tol)
        if s0 != 0 and s1 != 0 and s0 != s1:
            changes.append((i, i + 1))

    if exact:
        if len(exact) != 1 or changes:
            raise ValueError(f"definition {definition!r} has multiple/ambiguous zero regions")
        i = exact[0]
        numeric = None
        if context_values is not None:
            if contexts[i] not in context_values:
                raise ValueError(f"context_values lacks {contexts[i]!r}")
            numeric = _finite(context_values[contexts[i]], f"context_values[{contexts[i]}]")
        return CrossingBracket(
            definition=definition,
            left_context=contexts[i],
            right_context=contexts[i],
            left_index=i,
            right_index=i,
            left_margin=values[i],
            right_margin=values[i],
            exact_context=True,
            numeric_critical_context=numeric,
            status="EXACT_ZERO_CONTEXT",
        )

    if len(changes) != 1:
        if not changes:
            raise ValueError(f"definition {definition!r} has no zero crossing")
        raise ValueError(f"definition {definition!r} has multiple zero crossings")

    i, j = changes[0]
    numeric = None
    if context_values is not None:
        for idx in (i, j):
            if contexts[idx] not in context_values:
                raise ValueError(f"context_values lacks {contexts[idx]!r}")
        e0 = _finite(context_values[contexts[i]], f"context_values[{contexts[i]}]")
        e1 = _finite(context_values[contexts[j]], f"context_values[{contexts[j]}]")
        if e1 == e0:
            raise ValueError("crossing endpoints must have distinct numeric context values")
        m0, m1 = values[i], values[j]
        numeric = e0 + (0.0 - m0) * (e1 - e0) / (m1 - m0)

    return CrossingBracket(
        definition=definition,
        left_context=contexts[i],
        right_context=contexts[j],
        left_index=i,
        right_index=j,
        left_margin=values[i],
        right_margin=values[j],
        exact_context=False,
        numeric_critical_context=numeric,
        status="UNIQUE_ADJACENT_ZERO_CROSSING",
    )


def compare_definition_brackets(
    brackets: Sequence[CrossingBracket],
    contexts: Sequence[str],
    *,
    numeric_tolerance: float | None = None,
) -> DefinitionConcordance:
    if len(brackets) < 2:
        raise ValueError("at least two definitions are required for concordance")
    if len(set(contexts)) != len(contexts):
        raise ValueError("context labels must be unique")

    left = max(bracket.left_index for bracket in brackets)
    right = min(bracket.right_index for bracket in brackets)
    overlap = left <= right
    identical = len({bracket.index_interval for bracket in brackets}) == 1

    numeric = [b.numeric_critical_context for b in brackets if b.numeric_critical_context is not None]
    max_gap = None
    numeric_agreement = None
    if len(numeric) == len(brackets):
        max_gap = max(numeric) - min(numeric)
        if numeric_tolerance is not None:
            tol = _finite(numeric_tolerance, "numeric_tolerance")
            if tol < 0:
                raise ValueError("numeric_tolerance must be >= 0")
            numeric_agreement = max_gap <= tol

    if identical:
        classification = "SAME_COARSE_CRITICAL_BRACKET"
    elif overlap:
        classification = "OVERLAPPING_CRITICAL_BRACKETS"
    else:
        classification = "PARALLEL_DEFINITION_BRACKETS"

    if numeric_agreement is True:
        classification = "SAME_NUMERIC_CRITICAL_CONTEXT_WITHIN_TOLERANCE"
    elif numeric_agreement is False:
        classification = "PARALLEL_NUMERIC_CRITICAL_CONTEXTS"

    if overlap:
        common_interval = (left, right)
        common_contexts = tuple(contexts[left : right + 1])
    else:
        common_interval = None
        common_contexts = ()

    return DefinitionConcordance(
        brackets=tuple(brackets),
        classification=classification,
        common_index_interval=common_interval,
        common_contexts=common_contexts,
        max_pairwise_numeric_gap=max_gap,
    )


def analyze_definitions(
    contexts: Sequence[str],
    definitions: Mapping[str, Mapping[str, float]],
    *,
    context_values: Mapping[str, float] | None = None,
    tolerance: float = 1e-12,
    numeric_tolerance: float | None = None,
) -> DefinitionConcordance:
    brackets = [
        crossing_bracket(
            name,
            contexts,
            margins,
            context_values=context_values,
            tolerance=tolerance,
        )
        for name, margins in definitions.items()
    ]
    return compare_definition_brackets(brackets, contexts, numeric_tolerance=numeric_tolerance)

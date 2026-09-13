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


def _ordered_contexts(contexts: Sequence[str]) -> tuple[str, ...]:
    values = tuple(contexts)
    if len(values) < 2:
        raise ValueError("at least two ordered contexts are required")
    if any(not isinstance(context, str) or not context.strip() for context in values):
        raise ValueError("context labels must be non-empty strings")
    if len(set(values)) != len(values):
        raise ValueError("context labels must be unique")
    return values


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
    if not isinstance(definition, str) or not definition.strip():
        raise ValueError("definition label must be a non-empty string")
    contexts = _ordered_contexts(contexts)
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

        # Scale margins before forming the crossing fraction. The naive
        # denominator m1-m0 can overflow for finite opposite-sign values such as
        # -1e308 and +1e308, incorrectly collapsing the crossing toward e0.
        m0, m1 = values[i], values[j]
        margin_scale = max(abs(m0), abs(m1))
        sm0 = m0 / margin_scale
        sm1 = m1 / margin_scale
        fraction = _finite(-sm0 / (sm1 - sm0), "crossing fraction")
        numeric = _finite(
            (1.0 - fraction) * e0 + fraction * e1,
            "interpolated numeric critical context",
        )

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


def _validate_bracket_against_contexts(
    bracket: CrossingBracket,
    contexts: tuple[str, ...],
) -> None:
    if not isinstance(bracket.definition, str) or not bracket.definition.strip():
        raise ValueError("bracket definition label must be non-empty")
    if type(bracket.left_index) is not int or type(bracket.right_index) is not int:
        raise ValueError("bracket indices must be integers")
    if not 0 <= bracket.left_index <= bracket.right_index < len(contexts):
        raise ValueError("bracket indices lie outside the supplied ordered contexts")
    if bracket.left_context != contexts[bracket.left_index]:
        raise ValueError("bracket left_context does not match supplied ordered contexts")
    if bracket.right_context != contexts[bracket.right_index]:
        raise ValueError("bracket right_context does not match supplied ordered contexts")
    if bracket.exact_context:
        if bracket.left_index != bracket.right_index:
            raise ValueError("exact-context bracket must occupy one context index")
    elif bracket.right_index != bracket.left_index + 1:
        raise ValueError("non-exact crossing bracket must span adjacent contexts")
    _finite(bracket.left_margin, "bracket left_margin")
    _finite(bracket.right_margin, "bracket right_margin")
    if bracket.numeric_critical_context is not None:
        _finite(bracket.numeric_critical_context, "numeric_critical_context")


def compare_definition_brackets(
    brackets: Sequence[CrossingBracket],
    contexts: Sequence[str],
    *,
    numeric_tolerance: float | None = None,
) -> DefinitionConcordance:
    if len(brackets) < 2:
        raise ValueError("at least two definitions are required for concordance")
    contexts = _ordered_contexts(contexts)
    for bracket in brackets:
        _validate_bracket_against_contexts(bracket, contexts)

    numeric_tol = None
    if numeric_tolerance is not None:
        numeric_tol = _finite(numeric_tolerance, "numeric_tolerance")
        if numeric_tol < 0:
            raise ValueError("numeric_tolerance must be >= 0")

    left = max(bracket.left_index for bracket in brackets)
    right = min(bracket.right_index for bracket in brackets)
    overlap = left <= right
    identical = len({bracket.index_interval for bracket in brackets}) == 1

    numeric = [
        bracket.numeric_critical_context
        for bracket in brackets
        if bracket.numeric_critical_context is not None
    ]
    if numeric_tol is not None and len(numeric) != len(brackets):
        raise ValueError(
            "numeric_tolerance requires a numeric critical context for every definition"
        )

    max_gap = None
    numeric_agreement = None
    if len(numeric) == len(brackets):
        max_gap = _finite(max(numeric) - min(numeric), "max_pairwise_numeric_gap")
        if numeric_tol is not None:
            numeric_agreement = max_gap <= numeric_tol

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
    return compare_definition_brackets(
        brackets,
        contexts,
        numeric_tolerance=numeric_tolerance,
    )

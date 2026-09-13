"""Quantitative receipts for 2x2 pollination x antagonist selection designs.

The Chapter-2 quantitative R layer distinguishes a simple bivariate agent pair
from a *diffuse factorial* design, where each agent-mediated selection contrast
depends on the state of the other agent. In the latter case one must retain the
full vector of dependent contrasts rather than cherry-pick one convenient pair.

For treatment-specific selection slopes ordered as

    b = (
        beta_open_antagonist_present,
        beta_supplemented_antagonist_present,
        beta_open_antagonist_absent,
        beta_supplemented_antagonist_absent,
    ),

the registered mediated-selection vector is

    theta = C b

with rows of ``C`` corresponding to

    pollinator | antagonist present
    pollinator | antagonist absent
    antagonist | ambient/open pollination
    antagonist | supplemented pollination.

A quantitative receipt is *not* ready from marginal standard errors alone.
Readiness requires the joint covariance of the four treatment slopes from the
fitted model, or a covariance estimated by a raw-data bootstrap. The function
therefore refuses to label a covariance matrix as usable unless its provenance
is explicitly registered as ``joint_model`` or ``raw_bootstrap``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


TREATMENT_ORDER = (
    "open_antagonist_present",
    "supplemented_antagonist_present",
    "open_antagonist_absent",
    "supplemented_antagonist_absent",
)

CONTRAST_ORDER = (
    "pollinator_given_antagonist_present",
    "pollinator_given_antagonist_absent",
    "antagonist_given_open_pollination",
    "antagonist_given_supplemented_pollination",
)

# Rows operate on TREATMENT_ORDER.
_CONTRAST_MATRIX = (
    (1.0, -1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0, -1.0),
    (1.0, 0.0, -1.0, 0.0),
    (0.0, 1.0, 0.0, -1.0),
)

# Difference in an agent effect between the two contexts. The same 2x2
# interaction is obtained from either pair of mediated contrasts.
_INTERACTION_VECTOR = (1.0, -1.0, -1.0, 1.0)
_ALLOWED_COVARIANCE_SOURCES = {"joint_model", "raw_bootstrap"}


@dataclass(frozen=True)
class FactorialSelectionReceipt:
    """Registered point estimates and joint uncertainty for a 2x2 design."""

    treatment_slopes: tuple[float, float, float, float]
    mediated_contrasts: tuple[float, float, float, float]
    contrast_covariance: tuple[tuple[float, float, float, float], ...] | None
    contrast_standard_errors: tuple[float, float, float, float] | None
    interaction_contrast: float
    interaction_standard_error: float | None
    covariance_source: str | None
    state: str

    @property
    def effect_size_ready(self) -> bool:
        """Whether joint uncertainty is registered for multicontrast synthesis."""

        return self.state == "JOINT_MULTICONTRAST_READY"


def _finite_vector(values: Sequence[float], *, name: str) -> tuple[float, ...]:
    vals = tuple(float(value) for value in values)
    if len(vals) != 4:
        raise ValueError(f"{name} must contain exactly four values")
    if not all(math.isfinite(value) for value in vals):
        raise ValueError(f"{name} values must be finite")
    return vals


def _require_positive_semidefinite(
    covariance: tuple[tuple[float, float, float, float], ...], *, tolerance: float
) -> None:
    """Validate PSD on a dimensionless covariance matrix.

    Symmetry plus non-negative diagonal entries are necessary but not sufficient
    for a covariance matrix. This tolerance-aware Cholesky-style decomposition
    additionally rejects indefinite matrices without adding a numerical
    dependency such as NumPy. Callers normalize the covariance first so the
    decision is invariant to a common positive change of measurement scale.
    """

    factor = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(i + 1):
            residual = covariance[i][j] - sum(
                factor[i][k] * factor[j][k] for k in range(j)
            )
            if i == j:
                if residual < -tolerance:
                    raise ValueError("slope_covariance must be positive semidefinite")
                factor[i][j] = math.sqrt(max(0.0, residual))
            elif factor[j][j] > tolerance:
                factor[i][j] = residual / factor[j][j]
            elif abs(residual) > tolerance:
                raise ValueError("slope_covariance must be positive semidefinite")


def _validate_covariance(
    covariance: Sequence[Sequence[float]], *, tolerance: float
) -> tuple[tuple[tuple[float, float, float, float], ...], float]:
    """Return a validated covariance and its absolute element scale.

    ``tolerance`` is interpreted relatively. The matrix is divided by its
    maximum absolute entry before symmetry/PSD checks, so multiplying a
    covariance by any positive scalar cannot change whether it is accepted as a
    covariance matrix. The all-zero covariance is a valid singular PSD case.
    """
    rows = tuple(tuple(float(value) for value in row) for row in covariance)
    if len(rows) != 4 or any(len(row) != 4 for row in rows):
        raise ValueError("slope_covariance must be a 4x4 matrix")
    if not all(math.isfinite(value) for row in rows for value in row):
        raise ValueError("slope_covariance values must be finite")

    scale = max(abs(value) for row in rows for value in row)
    if scale == 0.0:
        return rows, scale  # type: ignore[return-value]

    normalized = tuple(
        tuple(value / scale for value in row)
        for row in rows
    )
    for i in range(4):
        if normalized[i][i] < -tolerance:
            raise ValueError("slope_covariance diagonal entries must be non-negative")
        for j in range(4):
            if abs(normalized[i][j] - normalized[j][i]) > tolerance:
                raise ValueError("slope_covariance must be symmetric")
    _require_positive_semidefinite(normalized, tolerance=tolerance)  # type: ignore[arg-type]
    return rows, scale  # type: ignore[return-value]


def _linear_transform(
    matrix: Sequence[Sequence[float]], vector: Sequence[float]
) -> tuple[float, ...]:
    return tuple(
        sum(float(weight) * float(value) for weight, value in zip(row, vector))
        for row in matrix
    )


def _quadratic_cross(
    left: Sequence[float],
    covariance: Sequence[Sequence[float]],
    right: Sequence[float],
) -> float:
    return sum(
        float(left[i]) * float(covariance[i][j]) * float(right[j])
        for i in range(4)
        for j in range(4)
    )


def _quadratic_roundoff_tolerance(
    weights: Sequence[float], *, covariance_scale: float, relative_tolerance: float
) -> float:
    """Scale a relative matrix tolerance to one quadratic form.

    ``|w' E w| <= max|E_ij| (sum |w_i|)^2`` gives a conservative conversion
    from an elementwise covariance tolerance to the units of a derived
    variance.
    """
    l1 = sum(abs(float(weight)) for weight in weights)
    return relative_tolerance * covariance_scale * l1 * l1


def analyze_factorial_agent_selection(
    treatment_slopes: Sequence[float],
    *,
    slope_covariance: Sequence[Sequence[float]] | None = None,
    covariance_source: str | None = None,
    tolerance: float = 1e-10,
) -> FactorialSelectionReceipt:
    """Transform four treatment slopes into the registered dependent contrasts.

    ``treatment_slopes`` must follow :data:`TREATMENT_ORDER`. Point contrasts
    can always be computed. Joint uncertainty, however, is calculated only
    when a full 4x4 covariance matrix is supplied with provenance
    ``joint_model`` or ``raw_bootstrap``.

    ``tolerance`` is a dimensionless relative numerical tolerance for covariance
    validation. PSD readiness is therefore invariant to a common positive
    rescaling of the covariance matrix.

    Supplying four standard errors as a diagonal matrix merely to assume zero
    covariance is outside the registered analysis contract; this function does
    not infer such a covariance from standard errors.
    """

    tol = float(tolerance)
    if not math.isfinite(tol) or tol <= 0:
        raise ValueError("tolerance must be finite and positive")

    slopes = _finite_vector(treatment_slopes, name="treatment_slopes")
    contrasts = _linear_transform(_CONTRAST_MATRIX, slopes)
    interaction = sum(
        weight * value for weight, value in zip(_INTERACTION_VECTOR, slopes)
    )

    if slope_covariance is None:
        if covariance_source is not None:
            raise ValueError("covariance_source requires slope_covariance")
        return FactorialSelectionReceipt(
            treatment_slopes=slopes,  # type: ignore[arg-type]
            mediated_contrasts=contrasts,  # type: ignore[arg-type]
            contrast_covariance=None,
            contrast_standard_errors=None,
            interaction_contrast=interaction,
            interaction_standard_error=None,
            covariance_source=None,
            state="POINT_ESTIMATES_ONLY_NOT_READY",
        )

    if covariance_source not in _ALLOWED_COVARIANCE_SOURCES:
        allowed = ", ".join(sorted(_ALLOWED_COVARIANCE_SOURCES))
        raise ValueError(f"covariance_source must be one of: {allowed}")

    covariance, covariance_scale = _validate_covariance(
        slope_covariance, tolerance=tol
    )
    transformed = tuple(
        tuple(
            _quadratic_cross(left, covariance, right)
            for right in _CONTRAST_MATRIX
        )
        for left in _CONTRAST_MATRIX
    )

    variances = []
    for i, weights in enumerate(_CONTRAST_MATRIX):
        variance = transformed[i][i]
        variance_tol = _quadratic_roundoff_tolerance(
            weights,
            covariance_scale=covariance_scale,
            relative_tolerance=tol,
        )
        if variance < -variance_tol:
            raise ValueError("transformed contrast variance is negative")
        variances.append(max(0.0, variance))
    standard_errors = tuple(math.sqrt(value) for value in variances)

    interaction_variance = _quadratic_cross(
        _INTERACTION_VECTOR, covariance, _INTERACTION_VECTOR
    )
    interaction_tol = _quadratic_roundoff_tolerance(
        _INTERACTION_VECTOR,
        covariance_scale=covariance_scale,
        relative_tolerance=tol,
    )
    if interaction_variance < -interaction_tol:
        raise ValueError("interaction contrast variance is negative")
    interaction_se = math.sqrt(max(0.0, interaction_variance))

    return FactorialSelectionReceipt(
        treatment_slopes=slopes,  # type: ignore[arg-type]
        mediated_contrasts=contrasts,  # type: ignore[arg-type]
        contrast_covariance=transformed,  # type: ignore[arg-type]
        contrast_standard_errors=standard_errors,  # type: ignore[arg-type]
        interaction_contrast=interaction,
        interaction_standard_error=interaction_se,
        covariance_source=covariance_source,
        state="JOINT_MULTICONTRAST_READY",
    )

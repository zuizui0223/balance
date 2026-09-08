"""Reconstruct dependent 2x2 factorial contrast covariance from reported statistics.

Some published factorial studies report all four context-specific mediated
selection contrasts, their marginal standard errors, a shared diagonal
contrast, and the 1-df factorial interaction test, but do not publish the raw
4x4 covariance matrix.  When these quantities close the 2x2 contrast algebra,
the joint covariance is identified rather than guessed.

The registered contrast order is

    a = pollinator | antagonist present
    b = pollinator | antagonist absent
    c = antagonist | open/ambient pollination
    d = antagonist | supplemented pollination

For a 2x2 factorial square,

    a + d = b + c = y
    a - b = c - d = q

where ``y`` is the reported diagonal contrast and ``q`` is the interaction
contrast.  If a 1-df F statistic tests ``q = 0``, then

    Var(q) = q^2 / F.

Together with the four marginal contrast variances and ``Var(y)``, these
relations uniquely identify every off-diagonal covariance.  This module uses
that identity only when all reported point estimates close algebraically and
the reconstructed covariance is positive semidefinite.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


REPORTED_CONTRAST_ORDER = (
    "pollinator_given_antagonist_present",
    "pollinator_given_antagonist_absent",
    "antagonist_given_open_pollination",
    "antagonist_given_supplemented_pollination",
)


@dataclass(frozen=True)
class ReportedFactorialContrastReceipt:
    mediated_contrasts: tuple[float, float, float, float]
    contrast_standard_errors: tuple[float, float, float, float]
    contrast_covariance: tuple[tuple[float, float, float, float], ...]
    combined_contrast: float
    combined_standard_error: float
    interaction_contrast: float
    interaction_standard_error: float
    interaction_f: float
    covariance_source: str
    state: str

    @property
    def effect_size_ready(self) -> bool:
        return self.state == "REPORTED_FACTORIAL_JOINT_COVARIANCE_READY"


def _finite_four(values: Sequence[float], *, name: str) -> tuple[float, float, float, float]:
    vals = tuple(float(value) for value in values)
    if len(vals) != 4:
        raise ValueError(f"{name} must contain exactly four values")
    if not all(math.isfinite(value) for value in vals):
        raise ValueError(f"{name} values must be finite")
    return vals  # type: ignore[return-value]


def _validate_psd(
    covariance: tuple[tuple[float, float, float, float], ...], *, tolerance: float
) -> None:
    factor = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(i + 1):
            residual = covariance[i][j] - sum(
                factor[i][k] * factor[j][k] for k in range(j)
            )
            if i == j:
                if residual < -tolerance:
                    raise ValueError("reconstructed covariance is not positive semidefinite")
                factor[i][j] = math.sqrt(max(0.0, residual))
            elif factor[j][j] > tolerance:
                factor[i][j] = residual / factor[j][j]
            elif abs(residual) > tolerance:
                raise ValueError("reconstructed covariance is not positive semidefinite")


def reconstruct_reported_factorial_contrasts(
    mediated_contrasts: Sequence[float],
    contrast_standard_errors: Sequence[float],
    *,
    combined_contrast: float,
    combined_standard_error: float,
    interaction_f: float,
    closure_tolerance: float = 5e-6,
    covariance_tolerance: float = 1e-8,
) -> ReportedFactorialContrastReceipt:
    """Recover the joint covariance from a closed set of reported contrasts.

    ``mediated_contrasts`` and ``contrast_standard_errors`` follow
    :data:`REPORTED_CONTRAST_ORDER`.  The source must additionally report the
    diagonal contrast ``combined_contrast`` with its SE and a positive 1-df F
    statistic for the factorial interaction.  No covariance is set to zero by
    assumption.
    """

    effects = _finite_four(mediated_contrasts, name="mediated_contrasts")
    ses = _finite_four(contrast_standard_errors, name="contrast_standard_errors")
    if any(se < 0 for se in ses):
        raise ValueError("contrast standard errors must be non-negative")

    y = float(combined_contrast)
    sy = float(combined_standard_error)
    f = float(interaction_f)
    if not all(math.isfinite(value) for value in (y, sy, f)):
        raise ValueError("combined contrast, SE and interaction F must be finite")
    if sy < 0:
        raise ValueError("combined standard error must be non-negative")
    if f <= 0:
        raise ValueError("interaction_f must be positive")
    if closure_tolerance <= 0 or covariance_tolerance <= 0:
        raise ValueError("tolerances must be positive")

    a, b, c, d = effects
    if abs((a + d) - y) > closure_tolerance:
        raise ValueError("reported contrasts do not close on a + d = combined")
    if abs((b + c) - y) > closure_tolerance:
        raise ValueError("reported contrasts do not close on b + c = combined")

    q_left = a - b
    q_right = c - d
    if abs(q_left - q_right) > closure_tolerance:
        raise ValueError("reported contrasts do not close on the factorial interaction")
    if abs(q_left) <= closure_tolerance:
        raise ValueError("zero interaction estimate plus F does not identify interaction variance")

    interaction_variance = (q_left * q_left) / f
    interaction_se = math.sqrt(interaction_variance)

    va, vb, vc, vd = (se * se for se in ses)
    vy = sy * sy

    # Directly identified from Var(a+d), Var(b+c), Var(a-b), Var(c-d).
    cov_ad = (vy - va - vd) / 2.0
    cov_bc = (vy - vb - vc) / 2.0
    cov_ab = (va + vb - interaction_variance) / 2.0
    cov_cd = (vc + vd - interaction_variance) / 2.0

    # The exact factorial identity a + d - b - c == 0 identifies the two
    # remaining cross-covariances.
    cov_ac = va + cov_ad - cov_ab
    cov_bd = vb + cov_bc - cov_ab

    covariance = (
        (va, cov_ab, cov_ac, cov_ad),
        (cov_ab, vb, cov_bc, cov_bd),
        (cov_ac, cov_bc, vc, cov_cd),
        (cov_ad, cov_bd, cov_cd, vd),
    )

    # The factorial identity must be a null direction of the covariance.
    identity = (1.0, -1.0, -1.0, 1.0)
    for row in covariance:
        residual = sum(weight * value for weight, value in zip(identity, row))
        if abs(residual) > max(covariance_tolerance, closure_tolerance):
            raise ValueError("reconstructed covariance violates the factorial identity")

    _validate_psd(covariance, tolerance=covariance_tolerance)

    return ReportedFactorialContrastReceipt(
        mediated_contrasts=effects,
        contrast_standard_errors=ses,
        contrast_covariance=covariance,
        combined_contrast=y,
        combined_standard_error=sy,
        interaction_contrast=q_left,
        interaction_standard_error=interaction_se,
        interaction_f=f,
        covariance_source="reported_contrasts_plus_combined_se_plus_interaction_f",
        state="REPORTED_FACTORIAL_JOINT_COVARIANCE_READY",
    )

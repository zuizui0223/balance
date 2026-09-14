from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

from .boundary import _finite_numeric


@dataclass(frozen=True)
class BoundarySensitivity:
    sch_boundary_shift: float
    bita_boundary_shift: float
    width_shift: float


@dataclass(frozen=True)
class DeepestPointSensitivity:
    location_shift: float
    depth_shift: float


def _fraction(value: float) -> Fraction:
    """Represent one already-validated finite float exactly."""
    return Fraction.from_float(value)


def _finite_result(value: Fraction, name: str) -> float:
    """Convert an exact derived sensitivity only when float-representable."""
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(
            f"{name} must remain finite; rescale perturbation or coordinate units"
        ) from exc
    if not isfinite(out):
        raise ValueError(
            f"{name} must remain finite; rescale perturbation or coordinate units"
        )
    if value != 0 and out == 0.0:
        raise ValueError(
            f"{name} underflowed to zero; rescale perturbation or coordinate units"
        )
    return out


def boundary_sensitivity(*, a0: float, L_prime0: float, b2: float, rho_prime2: float) -> BoundarySensitivity:
    a0 = _finite_numeric(a0, "a0")
    L_prime0 = _finite_numeric(L_prime0, "L_prime0")
    b2 = _finite_numeric(b2, "b2")
    rho_prime2 = _finite_numeric(rho_prime2, "rho_prime2")
    if L_prime0 == 0:
        raise ValueError("L_prime0 must be nonzero")
    if rho_prime2 == 0:
        raise ValueError("rho_prime2 must be nonzero")

    # Carry the algebra in exact rationals derived from the input floats. This
    # avoids intermediate overflow and lets us distinguish a representable
    # finite sensitivity from a genuinely unrepresentable one.
    de0_exact = -_fraction(a0) / _fraction(L_prime0)
    de2_exact = -_fraction(b2) / _fraction(rho_prime2)
    width_exact = de2_exact - de0_exact
    return BoundarySensitivity(
        sch_boundary_shift=_finite_result(de0_exact, "SCH boundary sensitivity"),
        bita_boundary_shift=_finite_result(de2_exact, "BITA boundary sensitivity"),
        width_shift=_finite_result(width_exact, "width sensitivity"),
    )


def deepest_point_sensitivity(
    *,
    a: float,
    b: float,
    L_prime: float,
    rho_prime: float,
) -> DeepestPointSensitivity:
    a = _finite_numeric(a, "a")
    b = _finite_numeric(b, "b")
    L_prime = _finite_numeric(L_prime, "L_prime")
    rho_prime = _finite_numeric(rho_prime, "rho_prime")

    a_exact = _fraction(a)
    b_exact = _fraction(b)
    L_exact = _fraction(L_prime)
    rho_exact = _fraction(rho_prime)
    denom = L_exact - rho_exact
    if denom == 0:
        raise ValueError("L_prime-rho_prime must be nonzero")

    # Exact rational algebra prevents false inf/inf or inf-inf intermediates
    # for large but finite coefficients whose final sensitivities are finite.
    location_exact = -(a_exact - b_exact) / denom
    depth_exact = (-a_exact * rho_exact + b_exact * L_exact) / denom
    return DeepestPointSensitivity(
        location_shift=_finite_result(location_exact, "deepest-point location sensitivity"),
        depth_shift=_finite_result(depth_exact, "deepest-point depth sensitivity"),
    )

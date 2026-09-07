from dataclasses import dataclass


@dataclass(frozen=True)
class BoundarySensitivity:
    sch_boundary_shift: float
    bita_boundary_shift: float
    width_shift: float


@dataclass(frozen=True)
class DeepestPointSensitivity:
    location_shift: float
    depth_shift: float


def boundary_sensitivity(*, a0: float, L_prime0: float, b2: float, rho_prime2: float) -> BoundarySensitivity:
    if L_prime0 == 0:
        raise ValueError("L_prime0 must be nonzero")
    if rho_prime2 == 0:
        raise ValueError("rho_prime2 must be nonzero")
    de0 = -a0 / L_prime0
    de2 = -b2 / rho_prime2
    return BoundarySensitivity(
        sch_boundary_shift=de0,
        bita_boundary_shift=de2,
        width_shift=de2 - de0,
    )


def deepest_point_sensitivity(
    *,
    a: float,
    b: float,
    L_prime: float,
    rho_prime: float,
) -> DeepestPointSensitivity:
    denom = L_prime - rho_prime
    if denom == 0:
        raise ValueError("L_prime-rho_prime must be nonzero")
    location = -(a - b) / denom
    depth = (-a * rho_prime + b * L_prime) / denom
    return DeepestPointSensitivity(location_shift=location, depth_shift=depth)

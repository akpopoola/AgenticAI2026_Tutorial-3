"""Materials science: X-ray diffraction and alloy lattice helpers."""
from __future__ import annotations

import math

CU_KA_ANGSTROM = 1.540598      # Cu-Ka1


def bragg_d_spacing(two_theta_deg: float, wavelength_A: float = CU_KA_ANGSTROM, order: int = 1) -> float:
    """Bragg's law: n*lambda = 2*d*sin(theta). Returns d in angstrom."""
    if not 0.0 < two_theta_deg < 180.0:
        raise ValueError("two_theta_deg must be between 0 and 180")
    if wavelength_A <= 0 or order < 1:
        raise ValueError("wavelength must be positive and order >= 1")
    return order * wavelength_A / (2.0 * math.sin(math.radians(two_theta_deg / 2.0)))


def cubic_lattice_parameter(d_A: float, h: int, k: int, l: int) -> float:
    """a = d * sqrt(h^2 + k^2 + l^2) for a cubic crystal."""
    if d_A <= 0 or (h, k, l) == (0, 0, 0):
        raise ValueError("d must be positive and (h,k,l) must not be (0,0,0)")
    return d_A * math.sqrt(h * h + k * k + l * l)


def scherrer_crystallite_size(fwhm_deg: float, two_theta_deg: float, wavelength_A: float = CU_KA_ANGSTROM, K: float = 0.9) -> float:
    """Scherrer: tau = K*lambda / (beta*cos(theta)). beta (FWHM) in degrees of 2-theta. Returns nm."""
    if fwhm_deg <= 0:
        raise ValueError("fwhm_deg must be positive")
    if not 0.0 < two_theta_deg < 180.0:
        raise ValueError("two_theta_deg must be between 0 and 180")
    beta = math.radians(fwhm_deg)
    theta = math.radians(two_theta_deg / 2.0)
    return (K * wavelength_A / (beta * math.cos(theta))) / 10.0  # angstrom -> nm


def vegard_lattice_parameter(a_A: float, a_B: float, fraction_B: float) -> float:
    """Vegard's law for a solid solution A(1-x)B(x): a = (1-x)*a_A + x*a_B (angstrom)."""
    if not 0.0 <= fraction_B <= 1.0:
        raise ValueError("fraction_B must be between 0 and 1")
    if a_A <= 0 or a_B <= 0:
        raise ValueError("lattice parameters must be positive")
    return (1.0 - fraction_B) * a_A + fraction_B * a_B

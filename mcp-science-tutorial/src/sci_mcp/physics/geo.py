"""Geophysics: simple seismic rock-physics relations."""
from __future__ import annotations


def gardner_density(vp_m_s: float) -> float:
    """Gardner's relation: rho = 0.31 * Vp^0.25 with Vp in m/s, rho in g/cm3."""
    if not 1000.0 <= vp_m_s <= 8000.0:
        raise ValueError("vp_m_s should be 1000-8000 m/s for Gardner's relation to be meaningful")
    return 0.31 * vp_m_s**0.25


def acoustic_impedance(vp_m_s: float, rho_g_cc: float) -> float:
    """Z = rho * Vp, returned in kg/m2/s (rho converted from g/cm3)."""
    if vp_m_s <= 0 or rho_g_cc <= 0:
        raise ValueError("vp and rho must be positive")
    return rho_g_cc * 1000.0 * vp_m_s


def reflection_coefficient(z1: float, z2: float) -> float:
    """Normal-incidence R = (Z2 - Z1) / (Z2 + Z1); layer 1 is above layer 2."""
    if z1 <= 0 or z2 <= 0:
        raise ValueError("impedances must be positive")
    return (z2 - z1) / (z2 + z1)


def two_way_time_ms(depth_m: float, vp_m_s: float) -> float:
    """Two-way travel time in milliseconds for a reflector at depth_m with average velocity vp_m_s."""
    if depth_m < 0 or vp_m_s <= 0:
        raise ValueError("depth must be >= 0 and velocity positive")
    return 2.0 * depth_m / vp_m_s * 1000.0

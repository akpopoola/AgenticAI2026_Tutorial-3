"""Petrophysics: porosity and saturation from well-log measurements."""
from __future__ import annotations


def density_porosity(rhob: float, rho_matrix: float = 2.65, rho_fluid: float = 1.0) -> float:
    """phi_D = (rho_ma - rho_b) / (rho_ma - rho_f). Densities in g/cm3. Result is a fraction (0-1)."""
    if not 1.0 <= rhob <= 3.2:
        raise ValueError(f"rhob={rhob} g/cm3 is outside the plausible log range 1.0-3.2")
    if rho_matrix <= rho_fluid:
        raise ValueError("rho_matrix must be greater than rho_fluid")
    phi = (rho_matrix - rhob) / (rho_matrix - rho_fluid)
    return min(max(phi, 0.0), 1.0)


def sonic_porosity_wyllie(dt: float, dt_matrix: float = 55.5, dt_fluid: float = 189.0) -> float:
    """Wyllie time-average: phi_S = (dt - dt_ma) / (dt_f - dt_ma). Slowness in microseconds/ft."""
    if dt <= 0:
        raise ValueError("dt must be positive (us/ft)")
    if dt_fluid <= dt_matrix:
        raise ValueError("dt_fluid must exceed dt_matrix")
    phi = (dt - dt_matrix) / (dt_fluid - dt_matrix)
    return min(max(phi, 0.0), 1.0)


def neutron_density_porosity(phi_neutron: float, phi_density: float) -> float:
    """RMS combination, a common shortcut that damps the gas effect: sqrt((phiN^2 + phiD^2)/2)."""
    for name, v in (("phi_neutron", phi_neutron), ("phi_density", phi_density)):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{name} must be a fraction between 0 and 1, got {v}")
    return ((phi_neutron**2 + phi_density**2) / 2.0) ** 0.5


def archie_water_saturation(phi: float, rt: float, rw: float, a: float = 1.0, m: float = 2.0, n: float = 2.0) -> float:
    """Archie: Sw = ((a * Rw) / (phi^m * Rt))^(1/n). Rt, Rw in ohm-m."""
    if not 0.0 < phi <= 1.0:
        raise ValueError("phi must be a fraction in (0, 1]")
    if rt <= 0 or rw <= 0:
        raise ValueError("rt and rw must be positive")
    sw = ((a * rw) / (phi**m * rt)) ** (1.0 / n)
    return min(sw, 1.0)

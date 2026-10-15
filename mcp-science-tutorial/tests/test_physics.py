import math

import pytest

from sci_mcp.physics import geo, materials as mat, porosity as por


def test_bragg_aluminium_111():
    d = mat.bragg_d_spacing(38.47)
    assert d == pytest.approx(2.338, abs=0.002)
    assert mat.cubic_lattice_parameter(d, 1, 1, 1) == pytest.approx(4.050, abs=0.005)


def test_scherrer():
    assert mat.scherrer_crystallite_size(0.35, 38.2) == pytest.approx(24.02, abs=0.02)


def test_vegard():
    assert mat.vegard_lattice_parameter(4.05, 3.61, 0.3) == pytest.approx(3.918)


def test_gardner_and_reflection():
    rho = geo.gardner_density(3000)
    assert rho == pytest.approx(0.31 * 3000**0.25)
    z1, z2 = geo.acoustic_impedance(2800, 2.3), geo.acoustic_impedance(5200, 2.65)
    assert geo.reflection_coefficient(z1, z2) == pytest.approx((z2 - z1) / (z2 + z1))
    assert geo.two_way_time_ms(1500, 3000) == pytest.approx(1000.0)


def test_porosity():
    assert por.density_porosity(2.35) == pytest.approx(0.181818, abs=1e-5)
    assert por.sonic_porosity_wyllie(82) == pytest.approx(0.1985, abs=1e-3)
    assert por.archie_water_saturation(0.2, 20, 0.05) == pytest.approx(math.sqrt(0.05 / (0.04 * 20)))
    assert por.density_porosity(2.9) == 0.0  # clamped


@pytest.mark.parametrize("fn,args", [(por.density_porosity, (9.9,)), (geo.gardner_density, (5,)), (mat.bragg_d_spacing, (0,))])
def test_validation_rejects_bad_input(fn, args):
    with pytest.raises(ValueError):
        fn(*args)

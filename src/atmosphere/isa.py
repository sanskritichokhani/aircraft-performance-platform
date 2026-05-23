import numpy as np

T0 = 288.15        # sea level temperature (K)
P0 = 101325        # sea level pressure (Pa)
rho0 = 1.225       # sea level density (kg/m^3)
L = 0.0065         # temperature lapse rate (K/m)
R = 287            # gas constant for air

def temperature(h):
    """ISA temperature model (troposphere)"""
    return T0 - L * h


def pressure(h):
    """ISA pressure model (simplified troposphere)"""
    T = temperature(h)
    return P0 * (T / T0) ** (9.81 / (R * L))


def density(h):
    """ISA density from ideal gas law"""
    T = temperature(h)
    P = pressure(h)
    return P / (R * T)

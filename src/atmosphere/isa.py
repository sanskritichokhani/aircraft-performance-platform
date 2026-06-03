import numpy as np

# ISA constants
T0    = 288.15   # K   — sea-level temperature
P0    = 101325   # Pa  — sea-level pressure
rho0  = 1.225    # kg/m³
L     = 0.0065   # K/m — troposphere lapse rate
R     = 287.05   # J/(kg·K)
g     = 9.80665  # m/s²
H_trop = 11000   # m   — tropopause altitude
T_trop = 216.65  # K   — temperature at tropopause (isothermal above)

def temperature(h):
    """ISA temperature — troposphere + lower stratosphere."""
    if np.isscalar(h):
        return T_trop if h >= H_trop else T0 - L * h
    h = np.asarray(h)
    return np.where(h >= H_trop, T_trop, T0 - L * h)

def pressure(h):
    """ISA pressure — troposphere + lower stratosphere."""
    if np.isscalar(h):
        if h < H_trop:
            T = T0 - L * h
            return P0 * (T / T0) ** (g / (R * L))
        else:
            P_trop = P0 * (T_trop / T0) ** (g / (R * L))
            return P_trop * np.exp(-g * (h - H_trop) / (R * T_trop))
    h = np.asarray(h, dtype=float)
    P = np.zeros_like(h)
    trop = h < H_trop
    T_t = T0 - L * h[trop]
    P[trop] = P0 * (T_t / T0) ** (g / (R * L))
    P_trop = P0 * (T_trop / T0) ** (g / (R * L))
    P[~trop] = P_trop * np.exp(-g * (h[~trop] - H_trop) / (R * T_trop))
    return P

def density(h):
    """ISA density from ideal gas law."""
    return pressure(h) / (R * temperature(h))

def speed_of_sound(h):
    """Speed of sound — new function, needed for Mach calculations."""
    gamma = 1.4
    return np.sqrt(gamma * R * temperature(h))
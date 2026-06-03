"""
Range performance analysis.

Implements Breguet range equation with:
- mission-defined takeoff weight
- Mach-swept cruise optimization
- transonic wave drag correction
- payload-range diagram generation
"""

import numpy as np
from src.aircraft.aircraft import Aircraft
from src.atmosphere.isa import density, speed_of_sound


def cruise_range_mach_sweep(
    aircraft: Aircraft,
    payload_kg: float,
    fuel_kg: float,
    altitude_m: float | None = None,
    mach_range: tuple = (0.60, 0.90),
    n_points: int = 200
) -> dict:
    """
    Compute estimated range across a Mach sweep for a defined mission.

    Args:
        aircraft:   Aircraft instance
        payload_kg: Mission payload (kg)
        fuel_kg:    Fuel loaded (kg)
        altitude_m: Cruise altitude (m). Defaults to aircraft design altitude.
        mach_range: (min_mach, max_mach) sweep bounds
        n_points:   Number of Mach points

    Returns:
        dict with arrays: mach, velocity_mps, range_km, ld_ratio, cl
    """
    if altitude_m is None:
        altitude_m = aircraft.cruise_altitude_m

    tow_kg   = aircraft.takeoff_weight(payload_kg, fuel_kg)
    w_init   = tow_kg * 9.80665                        # N
    w_final  = (tow_kg - fuel_kg) * 9.80665            # N
    rho      = density(altitude_m)
    a_sound  = speed_of_sound(altitude_m)

    machs    = np.linspace(mach_range[0], mach_range[1], n_points)
    velocities = machs * a_sound

    ranges_km = []
    ld_ratios = []
    cls       = []

    for mach, v in zip(machs, velocities):
        cl = aircraft.cl_at_condition(w_init, rho, v)
        cd = aircraft.cd_at_cl(cl)

        # Transonic wave drag — activates above Mcrit (~0.78 for 737-800)
        if mach > 0.78:
            cd_wave = 20.0 * (mach - 0.78) ** 4
            cd += cd_wave

        ld = cl / cd

        # Breguet range equation (meters)
        R_m = (v / aircraft.tsfc_kg_n_s) * ld * np.log(w_init / w_final)
        ranges_km.append(R_m / 1000.0)
        ld_ratios.append(ld)
        cls.append(cl)

    return {
        "mach":         machs,
        "velocity_mps": velocities,
        "range_km":     np.array(ranges_km),
        "ld_ratio":     np.array(ld_ratios),
        "cl":           np.array(cls),
        "altitude_m":   altitude_m,
        "payload_kg":   payload_kg,
        "fuel_kg":      fuel_kg,
    }


def payload_range_diagram(
    aircraft: Aircraft,
    altitude_m: float | None = None,
    n_fuel_points: int = 50
) -> dict:
    """
    Generate payload-range diagram — the key commercial performance chart.

    Three critical points define the envelope:
        A: Max payload, fuel fills remaining MTOW margin
        B: Max payload + max fuel (only if MTOW allows)
        C: Max fuel, payload reduced to MTOW limit
        D: Max fuel, zero payload (ferry range)

    Args:
        aircraft:   Aircraft instance
        altitude_m: Cruise altitude (m)
        n_points:   Resolution of the fuel sweep

    Returns:
        dict with 'ranges_km' and 'payloads_kg' arrays
    """
    if altitude_m is None:
        altitude_m = aircraft.cruise_altitude_m

    ranges_km   = []
    payloads_kg = []

    # Sweep fuel load from minimum viable to maximum
    min_fuel = 1000.0
    fuel_loads = np.linspace(min_fuel, aircraft.max_fuel_kg, n_fuel_points)

    for fuel_kg in fuel_loads:
        payload_kg = aircraft.max_payload_for_fuel(fuel_kg)
        try:
            result = cruise_range_mach_sweep(
                aircraft, payload_kg, fuel_kg, altitude_m, n_points=60
            )
            best_range = result["range_km"].max()
            ranges_km.append(best_range)
            payloads_kg.append(payload_kg)
        except ValueError:
            continue

    return {
        "ranges_km":   np.array(ranges_km),
        "payloads_kg": np.array(payloads_kg),
    }

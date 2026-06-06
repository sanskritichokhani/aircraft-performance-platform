"""
Day 4 — Boeing 737-800 Range Performance Analysis
Breguet range equation with physically grounded parameters.

Key fix from v1: removed empirical mission_efficiency_factor.
Range is now computed from a defined mission (payload + fuel load)
rather than MTOW with a fudge factor.
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Aircraft parameters (Boeing 737-800) ──────────────────────────
aircraft = {
    "name":           "Boeing 737-800",
    "mtow_kg":        79016,      # kg  — Boeing spec
    "oew_kg":         41413,      # kg  — operating empty weight
    "max_fuel_kg":    21320,      # kg
    "max_payload_kg": 20800,      # kg  — ~189 pax @ 110 kg avg
    "wing_area_m2":   124.6,      # m²
    "aspect_ratio":   9.45,
    "oswald_eff":     0.82,
    "cd0":            0.0215,     # calibrated to published data
}

# Derived drag polar
aircraft["k"] = 1.0 / (np.pi * aircraft["aspect_ratio"] * aircraft["oswald_eff"])

# ── Mission definition ─────────────────────────────────────────────
# Define a realistic medium-range mission first, then compute range.
# This is how airline performance engineers actually work.
payload_kg   = 17000          # ~155 passengers + bags
fuel_load_kg = 18000          # conservative fuel load (< max)

tow_kg = aircraft["oew_kg"] + payload_kg + fuel_load_kg
assert tow_kg <= aircraft["mtow_kg"], \
    f"TOW {tow_kg} kg exceeds MTOW {aircraft['mtow_kg']} kg"

w_initial = tow_kg * 9.81                        # N
w_final   = (tow_kg - fuel_load_kg) * 9.81       # N  (reserves ignored for now)

# ── Cruise atmosphere (ISA at 10,668 m / FL350) ───────────────────
T_cruise  = 218.81            # K
rho       = 0.3796            # kg/m³
gamma, R  = 1.4, 287.05
a_sound   = np.sqrt(gamma * R * T_cruise)  # m/s ≈ 295.5

# ── Engine: CFM56-7B27 ────────────────────────────────────────────
# TSFC in kg/(N·s) — typical cruise value from open literature
tsfc = 1.75e-4                # kg/(N·s)

# ── Sweep cruise TAS ──────────────────────────────────────────────
mach_range  = np.linspace(0.60, 0.88, 200)
v_range     = mach_range * a_sound          # TAS in m/s

ranges_km   = []
ld_ratios   = []

for v, mach in zip(v_range, mach_range):
    # CL for level flight at initial cruise weight
    cl = w_initial / (0.5 * rho * v**2 * aircraft["wing_area_m2"])

    # Drag polar
    cd = aircraft["cd0"] + aircraft["k"] * cl**2
    ld = cl / cd

    # Wave drag correction (only above Mach 0.78 for 737-800)
    # Simplified Korn-type correction — not a fudge factor,
    # models the real physics of transonic wave drag rise
    if mach > 0.78:
        delta_cd_wave = 20 * (mach - 0.78)**4
        cd_total = cd + delta_cd_wave
        ld = cl / cd_total
    
    ld_ratios.append(ld)

    # Breguet range (meters)
    R_m = (v / tsfc) * ld * np.log(w_initial / w_final)
    ranges_km.append(R_m / 1000)

ranges_km = np.array(ranges_km)
ld_ratios  = np.array(ld_ratios)

# ── Results ───────────────────────────────────────────────────────
idx_best  = np.argmax(ranges_km)
v_best    = v_range[idx_best]
mach_best = mach_range[idx_best]
r_best    = ranges_km[idx_best]

idx_ld    = np.argmax(ld_ratios)
ld_max    = ld_ratios[idx_ld]

print("\n" + "─" * 52)
print("DAY 4 — RANGE PERFORMANCE  (Boeing 737-800)")
print("─" * 52)
print(f"Mission payload:      {payload_kg:>7,.0f} kg")
print(f"Fuel load:            {fuel_load_kg:>7,.0f} kg")
print(f"Takeoff weight:       {tow_kg:>7,.0f} kg  ({tow_kg/aircraft['mtow_kg']*100:.1f}% MTOW)")
print(f"k (induced drag):     {aircraft['k']:.4f}  (from AR, e)")
print(f"L/D max:              {ld_max:.2f}")
print()
print(f"Best-range Mach:      {mach_best:.3f}")
print(f"Best-range TAS:       {v_best:.1f} m/s  ({v_best*3.6:.0f} km/h)")
print(f"Estimated range:      {r_best:.0f} km")
print()
print("Real-world reference: ~5,765 km (Boeing 737-800 typ. range)")
print(f"Model error:          {abs(r_best - 5765)/5765*100:.1f}%")
print("─" * 52 + "\n")
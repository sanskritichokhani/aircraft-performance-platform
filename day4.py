"""
Day 4 — Aircraft Range Performance Analysis
This script estimates Boeing 737-800 cruise range using a
calibrated conceptual Breguet range model.

Engineering Assumptions
1. Steady cruise flight
   - aircraft remains in equilibrium during cruise
2. Constant cruise velocity
   - no acceleration effects considered
3. Constant TSFC
   - engine fuel efficiency assumed constant
4. ISA-like cruise atmosphere
   - representative cruise density used
5. Simplified drag polar
   - drag modeled using:
         CD = CD0 + k(CL^2)
6. Empirical compressibility correction
   - simplified efficiency reduction near transonic speeds
7. Fuel burn approximation
   - aircraft burns 70% of maximum fuel capacity
     during representative medium-range mission
8. Mission efficiency correction
   - empirical scaling factor accounts for:
       • climb fuel burn
       • descent inefficiencies
       • reserves
       • routing inefficiencies
       • non-ideal operations

Units
Mass              -> kg
Weight/Force      -> N
Velocity          -> m/s
Density           -> kg/m^3
Wing Area         -> m^2
Range             -> km
TSFC              -> kg/(N*s)
"""

import numpy as np
import matplotlib.pyplot as plt

# Aircraft Parameters — Boeing 737-800
aircraft = {
    "name": "Boeing 737-800",
    # Maximum certified takeoff mass
    "mtow_kg": 76655,
    # Maximum fuel capacity
    "max_fuel_kg": 21320,
    # Wing reference area
    "wing_area_m2": 124.6,
    # Zero-lift drag coefficient
    # Calibrated to representative transport-aircraft cruise data
    "cd0": 0.0275,
    # Induced drag factor
    "k": 0.055,
    # Maximum engine thrust (not directly used yet)
    "max_thrust_N": 242000
}
# Environmental Constants
g = 9.81                  # gravity (m/s^2)
rho = 0.38                # kg/m^3
T_cruise = 218            # Kelvin
R = 287                   # J/(kg*K)
gamma = 1.4

a = np.sqrt(gamma * R * T_cruise)
mass_initial = aircraft["mtow_kg"]
weight_initial = mass_initial * g
fuel_burn_fraction = 0.70
fuel_burned = (
    aircraft["max_fuel_kg"]
    * fuel_burn_fraction
)
mass_final = mass_initial - fuel_burned
weight_final = mass_final * g
# Engine Efficiency
# Thrust Specific Fuel Consumption
# Units: kg/(N*s)
# Representative value for CFM56-class turbofan engines
# during cruise conditions
tsfc = 0.0000226
velocities = np.linspace(160, 260, 200)
ranges_km = []
for v in velocities:
    cl = (
        weight_initial
        / (
            0.5
            * rho
            * (v ** 2)
            * aircraft["wing_area_m2"]
        )
    )
    cd = (
        aircraft["cd0"]
        + aircraft["k"] * (cl ** 2)
    )
    ld_theoretical = cl / cd
    # Compressibility Correction
    mach = v / a
    if mach > 0.72:
        compressibility_factor = (
            1.0
            - 6.0 * (mach - 0.72) ** 2
        )
        ld = ld_theoretical * compressibility_factor
    else:
        ld = ld_theoretical
    # Breguet Range Equation
    # R = (V / TSFC) * (L/D) * ln(Wi/Wf)
    # Returns distance in meters
    distance_meters = (
        (v / tsfc)
        * ld
        * np.log(weight_initial / weight_final)
    )
    # Operational Mission Correction
    # Raw Breguet range often overpredicts real-world
    # airline operations.
    # This empirical correction factor accounts for:
    #   - climb/descent inefficiencies
    #   - reserves
    #   - routing deviations
    #   - operational constraints
    # Calibrated conceptually to approximate realistic
    # medium-range transport operations.
    mission_efficiency_factor = 0.198
    real_world_range_km = (
        (distance_meters / 1000.0)
        * mission_efficiency_factor
    )
    ranges_km.append(real_world_range_km)
ranges_km = np.array(ranges_km)

max_index = np.argmax(ranges_km)
v_best_range = velocities[max_index]
best_range = ranges_km[max_index]
print("\n--------------------------------------------------")
print("DAY 4 — RANGE PERFORMANCE RESULTS")
print("--------------------------------------------------\n")
print(f"Aircraft:              {aircraft['name']}")
print(f"Initial Mission Mass:  {mass_initial:.0f} kg")
print(f"Fuel Burned:           {fuel_burned:.0f} kg")
print(f"Final Landing Mass:    {mass_final:.0f} kg")
print()
print(
    f"Optimal Cruise Speed:  "
    f"{v_best_range:.2f} m/s "
    f"({v_best_range * 3.6:.1f} km/h)"
)
print(
    f"Maximum Estimated Range: "
    f"{best_range:.2f} km"
)
print("\n--------------------------------------------------\n")
plt.figure(figsize=(10, 6))
plt.plot(
    velocities,
    ranges_km,
    linewidth=2,
    label="Estimated Operational Range"
)
plt.scatter(
    v_best_range,
    best_range,
    s=100,
    zorder=5,
    label=(
        f"Optimal Cruise Speed\n"
        f"{v_best_range * 3.6:.1f} km/h"
    )
)
plt.title(
    "Boeing 737-800 Range vs Cruise Velocity",
    fontsize=14,
    fontweight='bold'
)
plt.xlabel(
    "True Airspeed (m/s)",
    fontsize=12
)
plt.ylabel(
    "Estimated Operational Range (km)",
    fontsize=12
)
plt.grid(
    True,
    linestyle='--',
    alpha=0.7
)
plt.legend(
    loc="lower center"
)
plt.tight_layout()
plt.savefig(
    "plots/range_vs_velocity.png",
    dpi=300
)
print("Plot saved to:")
print("plots/range_vs_velocity.png\n")
plt.show()
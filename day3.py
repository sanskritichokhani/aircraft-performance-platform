import numpy as np
import matplotlib.pyplot as plt

"""
Aircraft Performance Analysis

Assumptions:
- steady level flight
- ISA sea-level atmosphere
- incompressible flow
- constant aircraft mass
- simplified drag polar
- no wind effects
"""

from src.aircraft.aircraft import load_aircraft
from src.performance.performance import (
    lift_coefficient,
    drag_coefficient,
    drag_force,
    thrust_required,
    power_required
)

aircraft = load_aircraft("src/aircraft/b737.json")

rho = 1.225
weight = aircraft["mass_kg"] * 9.81
wing_area = aircraft["wing_area"]

velocities = np.linspace(50, 300, 300)

cl = lift_coefficient(weight, rho, velocities, wing_area)
cd = drag_coefficient(aircraft["cd0"], aircraft["k"], cl)
drags = drag_force(rho, velocities, wing_area, cd)

thrusts = thrust_required(drags)
powers = power_required(drags, velocities)

min_drag_index = np.argmin(drags)
v_min_drag = velocities[min_drag_index]
d_min = drags[min_drag_index]

print(f"Minimum drag speed: {v_min_drag:.2f} m/s")

min_power_index = np.argmin(powers)
v_min_power = velocities[min_power_index]
p_min = powers[min_power_index]

print(f"Minimum power speed: {v_min_power:.2f} m/s")

plt.figure(figsize=(10,6))

plt.plot(velocities, thrusts, label="Thrust Required Curve")
plt.scatter(v_min_drag, d_min, color='red', zorder=5, 
            label=f"Min Thrust Speed ({v_min_drag:.1f} m/s)")

plt.title("Thrust Required vs Velocity")
plt.xlabel("Velocity (m/s)")
plt.ylabel("Thrust Required (N)")
plt.grid(True)
plt.legend()

plt.savefig("plots/thrust_required.png")

plt.figure(figsize=(10,6))

plt.plot(velocities, powers, label="Power Required Curve")
plt.scatter(v_min_power, p_min, color='red', zorder=5, 
            label=f"Min Power Speed ({v_min_power:.1f} m/s)")

plt.title("Power Required vs Velocity")
plt.xlabel("Velocity (m/s)")
plt.ylabel("Power Required (W)")
plt.grid(True)
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("plots/power_required.png")
plt.show()

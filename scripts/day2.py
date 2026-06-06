import numpy as np
import matplotlib.pyplot as plt

from src.aircraft.aircraft import load_aircraft
from src.performance.performance import (
    lift_coefficient,
    drag_coefficient,
    drag_force
)

# Load aircraft
aircraft = load_aircraft("src/aircraft/b737.json")

# Constants
rho = 1.225
weight = aircraft["mass_kg"] * 9.81
wing_area = aircraft["wing_area"]

# Velocity range
velocities = np.linspace(50, 300, 200)

drags = []

for v in velocities:

    cl = lift_coefficient(weight, rho, v, wing_area)

    cd = drag_coefficient(
        aircraft["cd0"],
        aircraft["k"],
        cl
    )

    drag = drag_force(
        rho,
        v,
        wing_area,
        cd
    )

    drags.append(drag)

# Plot
plt.figure(figsize=(10,6))

plt.plot(velocities, drags)

plt.title("Drag vs Velocity")
plt.xlabel("Velocity (m/s)")
plt.ylabel("Drag Force (N)")

plt.grid(True)

plt.savefig("plots/drag_vs_velocity.png")

plt.show()
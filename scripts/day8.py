"""
Day 8 — Performance Optimization & Sensitivity Analysis

Engineering questions answered:
1. What altitude maximizes range for a given mission weight?
2. How sensitive is range to payload and fuel load choices?
3. How does optimal cruise Mach shift as fuel burns off?

Tools introduced: scipy.optimize
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

from src.aircraft.aircraft import Aircraft
from src.atmosphere.isa import density, speed_of_sound
from src.performance.range_analysis import (
    cruise_range_mach_sweep,
    payload_range_diagram,
    thrust_available_ratio
)

ac = Aircraft.from_json("src/aircraft/b737_800.json")

# STUDY 1 — Optimal cruise altitude
# Question: at a given takeoff weight, what altitude gives max range?

payload_kg = 17000
fuel_kg    = 18000

altitudes   = np.linspace(6000, 13000, 60)
best_ranges = []

MIN_THRUST_RATIO = 0.35

for alt in altitudes:
    t_ratio = thrust_available_ratio(alt)
    if t_ratio < MIN_THRUST_RATIO:
        best_ranges.append(np.nan)
        continue
    result = cruise_range_mach_sweep(ac, payload_kg, fuel_kg,
                                     altitude_m=alt, n_points=80)
    best_ranges.append(result["range_km"].max())

best_ranges  = np.array(best_ranges)
valid_mask   = ~np.isnan(best_ranges)
idx_opt_alt  = np.argmax(best_ranges[valid_mask])
optimal_alt  = altitudes[valid_mask][idx_opt_alt]
optimal_range = best_ranges[valid_mask][idx_opt_alt]

print("STUDY 1 — ALTITUDE OPTIMIZATION")
print(f"Optimal cruise altitude: {optimal_alt:.0f} m  "
      f"({optimal_alt*3.28084:.0f} ft)")
print(f"Maximum range at optimum: {optimal_range:.0f} km")
print(f"Range at FL350 (10,668m): "
      f"{best_ranges[np.argmin(abs(altitudes-10668))]:.0f} km")

# STUDY 2 — Payload / fuel sensitivity
# Question: how does range change across the payload-fuel trade space?

payload_sweep = np.linspace(5000, ac.max_payload_kg, 20)
fuel_sweep    = np.linspace(5000, ac.max_fuel_kg,    20)

range_matrix  = np.zeros((len(fuel_sweep), len(payload_sweep)))

for i, fuel in enumerate(fuel_sweep):
    for j, payload in enumerate(payload_sweep):
        try:
            tow = ac.takeoff_weight(payload, fuel)
            result = cruise_range_mach_sweep(ac, payload, fuel,
                                             altitude_m=optimal_alt,
                                             n_points=40)
            range_matrix[i, j] = result["range_km"].max()
        except ValueError:
            range_matrix[i, j] = np.nan   # MTOW exceeded

print("STUDY 2 — SENSITIVITY ANALYSIS")
valid = range_matrix[~np.isnan(range_matrix)]
print(f"Range across mission space: {valid.min():.0f} – {valid.max():.0f} km")
print(f"MTOW-limited combinations: "
      f"{np.isnan(range_matrix).sum()} / {range_matrix.size}")

# STUDY 3 — Cruise Mach vs aircraft weight
# Question: as fuel burns off mid-cruise, how does optimal Mach shift?
tow_kg        = ac.takeoff_weight(payload_kg, fuel_kg)
zfw_kg        = ac.oew_kg + payload_kg          # zero fuel weight
weight_range  = np.linspace(tow_kg, zfw_kg, 40) # heavy → light
fuel_remaining = weight_range - zfw_kg           # kg, goes 18000 → 0

opt_machs = []

rho_cruise = density(optimal_alt)
a_cruise   = speed_of_sound(optimal_alt)

for w_kg in weight_range:
    def neg_range_factor(mach):
        v  = mach * a_cruise
        cl = (w_kg * 9.80665) / (0.5 * rho_cruise * v**2 * ac.wing_area_m2)
        cd = ac.cd_at_cl(cl)
        if mach > 0.78:
            cd += 20.0 * (mach - 0.78)**4
        return -(v / ac.tsfc_kg_n_s) * (cl / cd)

    res = minimize_scalar(neg_range_factor, bounds=(0.65, 0.88),
                          method="bounded")
    opt_machs.append(res.x)

opt_machs = np.array(opt_machs)

print("STUDY 3 — CRUISE MACH vs WEIGHT")
print(f"Optimal Mach at TOW (full fuel):   {opt_machs[0]:.3f}")
print(f"Optimal Mach at ZFW (tanks empty): {opt_machs[-1]:.3f}")
print(f"Mach shift across cruise:          {opt_machs[-1]-opt_machs[0]:+.3f}")

# PLOTS

fig = plt.figure(figsize=(16, 5))
fig.suptitle("Boeing 737-800 — Day 8 Optimization & Sensitivity",
             fontsize=14, fontweight="bold")

# Plot 1: Range vs altitude
ax1 = fig.add_subplot(1, 3, 1)
ax1.plot(best_ranges, altitudes / 1000, linewidth=2)
ax1.axhline(optimal_alt / 1000, color="red", linestyle="--", alpha=0.7,
            label=f"Optimum {optimal_alt:.0f} m")
ax1.axhline(10.668, color="gray", linestyle=":", alpha=0.7,
            label="FL350 (typical)")
ax1.set_xlabel("Range (km)")
ax1.set_ylabel("Cruise Altitude (km)")
ax1.set_title("Range vs Cruise Altitude")
ax1.legend(fontsize=8)
ax1.grid(True, linestyle="--", alpha=0.6)

# Plot 2: Sensitivity contour
ax2 = fig.add_subplot(1, 3, 2)
P, F = np.meshgrid(payload_sweep / 1000, fuel_sweep / 1000)
cf = ax2.contourf(P, F, range_matrix, levels=15, cmap="viridis")
plt.colorbar(cf, ax=ax2, label="Range (km)")
ax2.contour(P, F, range_matrix, levels=15, colors="white",
            alpha=0.3, linewidths=0.5)
ax2.set_xlabel("Payload (tonnes)")
ax2.set_ylabel("Fuel Load (tonnes)")
ax2.set_title("Range Sensitivity\n(Payload vs Fuel)")
# Mark the study mission point
ax2.scatter([payload_kg/1000], [fuel_kg/1000],
            color="red", s=80, zorder=5, label="Study mission")
ax2.legend(fontsize=8)

# Plot 3: Optimal Mach vs fuel burned
ax3 = fig.add_subplot(1, 3, 3)
ax3.plot(fuel_remaining / 1000, opt_machs, linewidth=2, color="darkorange")
ax3.set_xlabel("Fuel Remaining (tonnes)")
ax3.set_ylabel("Optimal Cruise Mach")
ax3.set_title("Cruise Mach vs Fuel State\n(Step-Climb Logic)")
ax3.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("plots/day8_optimization.png", dpi=300)
plt.show()
"""
Day 6 — Flight Phase Analysis & Energy State
Automatically segments flight trajectory into phases,
computes per-phase performance metrics, and analyzes
the aircraft's energy state throughout the mission.

Engineering Concepts:
- Specific energy: E = (V²/2 + g·h) per unit mass (J/kg)
- Phase detection via vertical speed thresholds
- Operational efficiency by flight phase
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from src.analytics.flight_analysis import (
    load_flight_data,
    detect_flight_phases,
    phase_summary
)

df = load_flight_data("data/sample_flight.csv")
df = detect_flight_phases(df)

# ── Specific energy (J/kg) ───────────────────────────────────────
g = 9.80665
df["specific_energy"] = (
    0.5 * df["velocity_mps"]**2 + g * df["altitude_m"]
)

summary = phase_summary(df)

print("\n" + "─"*52)
print("DAY 6 — FLIGHT PHASE & ENERGY ANALYSIS")
print("─"*52)
for phase, metrics in summary.items():
    print(f"\n{phase.upper()}")
    print(f"  Duration:          {metrics['duration_min']:.1f} min")
    print(f"  Avg speed:         {metrics['avg_speed_mps']:.1f} m/s")
    print(f"  Altitude change:   {metrics['alt_change_m']:.0f} m")
    print(f"  Avg vertical spd:  {metrics['avg_vs_mps']:.2f} m/s")
print("─"*52 + "\n")

# ── Color map for phases ─────────────────────────────────────────
phase_colors = {
    "ground":  "#aaaaaa",
    "climb":   "#2196F3",
    "cruise":  "#4CAF50",
    "descent": "#FF9800"
}

fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
fig.suptitle("Flight Phase Analysis — Boeing 737-800 Mission",
             fontsize=14, fontweight='bold')

time_min = df["time_sec"] / 60

# Plot 1: Altitude with phase coloring
ax1 = axes[0]
for phase, color in phase_colors.items():
    mask = df["phase"] == phase
    ax1.fill_between(time_min, 0, df["altitude_m"],
                     where=mask, alpha=0.3, color=color, label=phase)
ax1.plot(time_min, df["altitude_m"], "k-", linewidth=1.5)
ax1.set_ylabel("Altitude (m)")
ax1.legend(loc="upper right", fontsize=9)
ax1.grid(True, linestyle="--", alpha=0.5)

# Plot 2: Velocity
ax2 = axes[1]
for phase, color in phase_colors.items():
    mask = df["phase"] == phase
    ax2.scatter(time_min[mask], df["velocity_mps"][mask],
                s=4, color=color, alpha=0.7)
ax2.set_ylabel("Velocity (m/s)")
ax2.grid(True, linestyle="--", alpha=0.5)

# Plot 3: Specific energy
ax3 = axes[2]
ax3.plot(time_min, df["specific_energy"] / 1000, linewidth=2, color="#9C27B0")
ax3.set_ylabel("Specific Energy (kJ/kg)")
ax3.set_xlabel("Time (minutes)")
ax3.grid(True, linestyle="--", alpha=0.5)

# Add this to your print block after the phase summary
e_climb_start  = df[df["phase"] == "climb"]["specific_energy"].iloc[0]  / 1000
e_cruise_start = df[df["phase"] == "cruise"]["specific_energy"].iloc[0] / 1000
e_cruise_end   = df[df["phase"] == "cruise"]["specific_energy"].iloc[-1]/ 1000
e_land         = df[df["phase"] == "descent"]["specific_energy"].iloc[-1]/1000

print("SPECIFIC ENERGY PROFILE (kJ/kg)")
print(f"  Takeoff:        {e_climb_start:.1f}")
print(f"  Top of climb:   {e_cruise_start:.1f}")
print(f"  Top of descent: {e_cruise_end:.1f}")
print(f"  Landing:        {e_land:.1f}")
print("─"*52)

plt.tight_layout()
plt.savefig("plots/phase_energy_analysis.png", dpi=300)
plt.show()
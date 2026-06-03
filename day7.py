"""
Day 7 — OOP Refactor + Aircraft Class Demonstration

Validates the Aircraft dataclass, shows derived parameters,
and runs the range model through the new clean interface.
"""

from src.aircraft.aircraft import Aircraft
from src.performance.range_analysis import cruise_range_mach_sweep, payload_range_diagram
import matplotlib.pyplot as plt
import numpy as np

# ── Load aircraft ─────────────────────────────────────────────────
ac = Aircraft.from_json("src/aircraft/b737_800.json")
print(ac)

# ── Mission range (same as Day 4, now through clean interface) ────
result = cruise_range_mach_sweep(
    aircraft   = ac,
    payload_kg = 17000,
    fuel_kg    = 18000,
)

idx_best  = np.argmax(result["range_km"])
print(f"Best-range Mach:  {result['mach'][idx_best]:.3f}")
print(f"Estimated range:  {result['range_km'][idx_best]:.0f} km")
print(f"L/D at best range: {result['ld_ratio'][idx_best]:.2f}")

# ── Payload-range diagram ─────────────────────────────────────────
pr = payload_range_diagram(ac)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(f"{ac.name} — Day 7 Performance Analysis",
             fontsize=14, fontweight="bold")

# Left: Range vs Mach
axes[0].plot(result["mach"], result["range_km"], linewidth=2)
axes[0].axvline(result["mach"][idx_best], color="red",
                linestyle="--", alpha=0.7, label=f"Best range M={result['mach'][idx_best]:.3f}")
axes[0].axhline(5765, color="gray", linestyle=":", alpha=0.7, label="Boeing ref. 5,765 km")
axes[0].set_xlabel("Cruise Mach")
axes[0].set_ylabel("Estimated Range (km)")
axes[0].set_title("Range vs Cruise Mach")
axes[0].legend()
axes[0].grid(True, linestyle="--", alpha=0.6)

# Right: Payload-range diagram
axes[1].plot(pr["ranges_km"], pr["payloads_kg"] / 1000, linewidth=2, color="darkorange")
axes[1].set_xlabel("Range (km)")
axes[1].set_ylabel("Payload (tonnes)")
axes[1].set_title("Payload-Range Diagram")
axes[1].grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("plots/day7_performance.png", dpi=300)
plt.show()

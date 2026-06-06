"""
Day 5 — Flight Operations Analytics
This script analyzes representative aircraft
trajectory data using operational flight analytics.
Capabilities:
- altitude profile analysis
- velocity profile analysis
- trajectory visualization
- cruise analysis
- climb/descent analytics
- operational metrics
Engineering Assumptions

1. Flight trajectory is representative ADS-B style data
2. Velocity values represent true airspeed estimates
3. Atmospheric/wind effects are ignored
4. Cruise phase defined as:
   altitude > 10,000 m
5. Time intervals assumed accurate and sequential
Units
Time        -> seconds
Altitude    -> meters
Velocity    -> m/s
Distance    -> km
Climb Rate  -> m/s
"""
import matplotlib.pyplot as plt
from src.analytics.flight_analysis import (
    load_flight_data,
    compute_basic_metrics,
    compute_average_cruise_speed,
    compute_max_rate_of_climb,
    compute_average_descent_rate,
    compute_total_flight_time_minutes
)
df = load_flight_data(
    "data/sample_flight.csv"
)
metrics = compute_basic_metrics(df)
avg_cruise_speed = compute_average_cruise_speed(df)
max_climb_rate = compute_max_rate_of_climb(df)
avg_descent_rate = compute_average_descent_rate(df)
flight_time_min = compute_total_flight_time_minutes(df)
print("DAY 5 — FLIGHT OPERATIONS ANALYTICS")
print(
    f"Maximum Altitude: "
    f"{metrics['max_altitude_m']:.0f} m"
)
print(
    f"Maximum Velocity: "
    f"{metrics['max_velocity_mps']:.1f} m/s"
)
print(
    f"Total Distance: "
    f"{metrics['total_distance_km']:.1f} km"
)
print(
    f"Total Flight Time: "
    f"{flight_time_min:.1f} minutes"
)
print()
print(
    f"Average Cruise Speed: "
    f"{avg_cruise_speed:.1f} m/s"
)
print(
    f"Maximum Climb Rate: "
    f"{max_climb_rate:.1f} m/s"
)
print(
    f"Average Descent Rate: "
    f"{avg_descent_rate:.1f} m/s"
)
plt.figure(figsize=(10, 6))
plt.plot(
    df["time_sec"] / 60,
    df["altitude_m"],
    linewidth=2
)
plt.title(
    "Flight Altitude Profile",
    fontsize=14,
    fontweight='bold'
)
plt.xlabel(
    "Time (minutes)",
    fontsize=12
)
plt.ylabel(
    "Altitude (m)",
    fontsize=12
)
plt.grid(
    True,
    linestyle='--',
    alpha=0.7
)
plt.tight_layout()
plt.savefig(
    "plots/altitude_profile.png",
    dpi=300
)
plt.figure(figsize=(10, 6))
plt.plot(
    df["time_sec"] / 60,
    df["velocity_mps"],
    linewidth=2
)
plt.title(
    "Flight Velocity Profile",
    fontsize=14,
    fontweight='bold'
)
plt.xlabel(
    "Time (minutes)",
    fontsize=12
)
plt.ylabel(
    "Velocity (m/s)",
    fontsize=12
)
plt.grid(
    True,
    linestyle='--',
    alpha=0.7
)
plt.tight_layout()
plt.savefig(
    "plots/velocity_profile.png",
    dpi=300
)
plt.figure(figsize=(10, 6))
plt.plot(
    df["distance_km"],
    df["altitude_m"],
    linewidth=2
)
plt.title(
    "Flight Trajectory Profile",
    fontsize=14,
    fontweight='bold'
)
plt.xlabel(
    "Distance (km)",
    fontsize=12
)
plt.ylabel(
    "Altitude (m)",
    fontsize=12
)
plt.grid(
    True,
    linestyle='--',
    alpha=0.7
)
plt.tight_layout()
plt.savefig(
    "plots/trajectory_profile.png",
    dpi=300
)
vertical_speed = (
    df["altitude_m"].diff()
    /
    df["time_sec"].diff()
)
plt.figure(figsize=(10, 6))
plt.plot(
    df["time_sec"] / 60,
    vertical_speed,
    linewidth=2
)
plt.title(
    "Vertical Speed Profile",
    fontsize=14,
    fontweight='bold'
)
plt.xlabel(
    "Time (minutes)",
    fontsize=12
)
plt.ylabel(
    "Vertical Speed (m/s)",
    fontsize=12
)
plt.grid(
    True,
    linestyle='--',
    alpha=0.7
)
plt.tight_layout()
plt.savefig(
    "plots/vertical_speed_profile.png",
    dpi=300
)
print("Plots saved successfully to:")
print("plots/altitude_profile.png")
print("plots/velocity_profile.png")
print("plots/trajectory_profile.png")
print("plots/vertical_speed_profile.png\n")
plt.show()
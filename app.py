"""
Aircraft Performance & Flight Operations Analytics Platform
Interactive dashboard — Streamlit frontend

Run with:
    streamlit run app.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from src.aircraft.aircraft import Aircraft
from src.atmosphere.isa import temperature, pressure, density, speed_of_sound
from src.performance.range_analysis import (
    cruise_range_mach_sweep,
    payload_range_diagram,
    thrust_available_ratio,
)
from src.analytics.flight_analysis import (
    load_flight_data,
    detect_flight_phases,
    phase_summary,
)

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Aircraft Performance Analytics",
    page_icon="✈️",
    layout="wide",
)

# ── Load aircraft ─────────────────────────────────────────────────
AIRCRAFT_OPTIONS = {
    "Boeing 737-800":   "src/aircraft/b737_800.json",
    "Airbus A320neo":   "src/aircraft/a320neo.json",
    "Boeing 777-300ER": "src/aircraft/b777_300er.json",
}

st.sidebar.title("✈️ Aircraft Performance")
selected_name = st.sidebar.selectbox(
    "Select Aircraft", list(AIRCRAFT_OPTIONS.keys())
)

@st.cache_resource
def load_ac(name):
    return Aircraft.from_json(AIRCRAFT_OPTIONS[name])

ac = load_ac(selected_name)
st.sidebar.markdown(f"**{ac.name}**")
st.sidebar.markdown(
    f"MTOW: {ac.mtow_kg/1000:.0f} t · "
    f"Range: ~{ac.cruise_mach:.3f} M"
)
st.sidebar.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────

payload_t = st.sidebar.slider(
    "Payload (tonnes)",
    min_value=5.0,
    max_value=float(ac.max_payload_kg / 1000),
    value=float(ac.max_payload_kg * 0.80 / 1000),  # default 80% max payload
    step=0.5
)
fuel_t = st.sidebar.slider(
    "Fuel Load (tonnes)",
    min_value=5.0,
    max_value=float(ac.max_fuel_kg / 1000),
    value=float(ac.max_fuel_kg * 0.85 / 1000),     # default 85% max fuel
    step=0.5
)

st.sidebar.markdown(
    f"**Design cruise altitude:** "
    f"{ac.cruise_altitude_m*3.28084:.0f} ft / "
    f"{ac.cruise_altitude_m/1000:.1f} km"
)


payload_kg  = payload_t  * 1000
fuel_kg     = fuel_t     * 1000
altitude_m  = ac.cruise_altitude_m
altitude_ft = int(altitude_m * 3.28084)

# MTOW check
try:
    tow_kg = ac.takeoff_weight(payload_kg, fuel_kg)
    mtow_pct = tow_kg / ac.mtow_kg * 100
    st.sidebar.metric("Takeoff Weight", f"{tow_kg/1000:.1f} t",
                      f"{mtow_pct:.1f}% MTOW")
    mtow_ok = True
except ValueError as e:
    st.sidebar.error(str(e))
    mtow_ok = False

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Project:** Aircraft Performance Analytics Platform  \n"
    "**Author:** Sanskriti Chokhani  \n"
    "**Stack:** Python · NumPy · SciPy · Streamlit  \n"
    "[GitHub](https://github.com/sanskritichokhani/aircraft-performance-platform)"
)

# ── Main title ────────────────────────────────────────────────────
st.title("Aircraft Performance & Flight Operations Analytics")
st.markdown(
    "A Python-based aerospace engineering platform integrating ISA atmosphere "
    "modeling, aerodynamic performance analysis, Breguet range estimation, "
    "and flight operations analytics."
)

# ── Tabs ──────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 ISA Atmosphere",
    "✈️ Aerodynamics",
    "📏 Range Analysis",
    "📊 Flight Operations",
    "⚙️ Optimization",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — ISA Atmosphere
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.header("International Standard Atmosphere Model")

    # Aircraft-specific ceiling (service ceiling, not just cruise alt)
    SERVICE_CEILINGS = {
        "Boeing 737-800":   41000,
        "Airbus A320neo":   39800,
        "Boeing 777-300ER": 43100,
    }
    service_ceiling_ft = SERVICE_CEILINGS.get(selected_name, 43000)
    design_cruise_ft   = int(ac.cruise_altitude_m * 3.28084)

    altitude_ft = st.slider(
        "Inspect altitude (ft)",
        min_value=0,
        max_value=service_ceiling_ft,
        value=design_cruise_ft,        # auto-sets to aircraft's cruise alt
        step=500,
        key=f"isa_alt_{selected_name}" # forces reset when aircraft changes
    )
    altitude_m = altitude_ft * 0.3048

    altitudes = np.linspace(0, 20000, 300)
    temps     = temperature(altitudes)
    pressures = pressure(altitudes)
    densities = density(altitudes)
    sounds    = speed_of_sound(altitudes)

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(temps, altitudes / 1000, linewidth=2)
        ax.axhline(11.0, color="gray", linestyle="--",
                   alpha=0.6, label="Tropopause (11 km)")
        ax.axhline(altitude_m / 1000, color="red", linestyle="--",
                   alpha=0.7, label=f"Selected: {altitude_ft} ft")
        ax.set_xlabel("Temperature (K)")
        ax.set_ylabel("Altitude (km)")
        ax.set_title("Temperature Profile")
        ax.legend(fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(densities, altitudes / 1000, linewidth=2, color="darkorange")
        ax.axhline(11.0, color="gray", linestyle="--", alpha=0.6,
                   label="Tropopause")
        ax.axhline(altitude_m / 1000, color="red", linestyle="--",
                   alpha=0.7, label=f"Selected: {altitude_ft} ft")
        ax.set_xlabel("Density (kg/m³)")
        ax.set_ylabel("Altitude (km)")
        ax.set_title("Density Profile")
        ax.legend(fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Metrics at selected altitude
    st.markdown("---")
    st.subheader(f"Conditions at {altitude_ft:,} ft ({altitude_m:.0f} m)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperature", f"{temperature(altitude_m):.1f} K")
    c2.metric("Pressure",    f"{pressure(altitude_m)/1000:.2f} kPa")
    c3.metric("Density",     f"{density(altitude_m):.4f} kg/m³")
    c4.metric("Speed of Sound", f"{speed_of_sound(altitude_m):.1f} m/s")

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Aerodynamics
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.header("Aerodynamic Performance Analysis")
    st.markdown(f"Drag polar and L/D ratio for the {ac.name}.")

    rho_sl    = 1.225
    weight_n  = tow_kg * 9.80665 if mtow_ok else ac.mtow_kg * 9.80665
    velocities = np.linspace(50, 320, 300)

    cls  = weight_n / (0.5 * rho_sl * velocities**2 * ac.wing_area_m2)
    cds  = ac.cd_at_cl(cls)
    lds  = cls / cds
    drags = 0.5 * rho_sl * velocities**2 * ac.wing_area_m2 * cds

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(velocities, lds, linewidth=2, color="green")
        ax.axhline(ac.ld_max, color="red", linestyle="--",
                   label=f"L/D max = {ac.ld_max:.2f}")
        ax.set_xlabel("Velocity (m/s)")
        ax.set_ylabel("L/D Ratio")
        ax.set_title("Lift-to-Drag Ratio vs Velocity")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(velocities, drags / 1000, linewidth=2, color="navy")
        ax.set_xlabel("Velocity (m/s)")
        ax.set_ylabel("Drag Force (kN)")
        ax.set_title("Drag vs Velocity")
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("L/D Maximum",   f"{ac.ld_max:.2f}")
    c2.metric("Optimal CL",    f"{ac.cl_opt:.3f}")
    c3.metric("Induced drag k", f"{ac.k:.4f}")

# ══════════════════════════════════════════════════════════════════
# TAB 3 — Range Analysis
# ══════════════════════════════════════════════════════════════════
range_altitude_m = ac.cruise_altitude_m 
with tab3:
    st.header("Range Performance Analysis")

    if not mtow_ok:
        st.error("MTOW exceeded — adjust payload or fuel in sidebar.")
    else:
        with st.spinner("Computing range..."):
            result = cruise_range_mach_sweep(ac, payload_kg, fuel_kg,
                                             altitude_m=range_altitude_m)
            pr     = payload_range_diagram(ac, altitude_m=range_altitude_m)

        idx_best  = np.argmax(result["range_km"])
        best_mach = result["mach"][idx_best]
        best_range = result["range_km"][idx_best]

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(result["mach"], result["range_km"], linewidth=2)
            ax.axvline(best_mach, color="red", linestyle="--",
                       label=f"Best M={best_mach:.3f}")
            ax.axhline(5765, color="gray", linestyle=":",
                       label="Boeing ref. 5,765 km")
            ax.set_xlabel("Cruise Mach")
            ax.set_ylabel("Range (km)")
            ax.set_title("Range vs Cruise Mach")
            ax.legend(fontsize=8)
            ax.grid(True, linestyle="--", alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col2:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(pr["ranges_km"], pr["payloads_kg"] / 1000,
                    linewidth=2, color="darkorange")
            ax.set_xlabel("Range (km)")
            ax.set_ylabel("Payload (tonnes)")
            ax.set_title("Payload-Range Diagram")
            ax.grid(True, linestyle="--", alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Best-range Mach", f"{best_mach:.3f}")
        c2.metric("Estimated Range", f"{best_range:.0f} km")
        c3.metric("vs Boeing ref.", f"{(best_range-5765)/5765*100:+.1f}%")

# ══════════════════════════════════════════════════════════════════
# TAB 4 — Flight Operations
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.header("Flight Operations Analytics")

    uploaded = st.file_uploader(
        "Upload flight trajectory CSV (columns: time_sec, altitude_m, "
        "velocity_mps, distance_km)",
        type="csv"
    )

    # Default to sample data if nothing uploaded
    data_source = uploaded if uploaded else "data/sample_flight.csv"
    df = load_flight_data(data_source)
    df = detect_flight_phases(df)

    if uploaded:
        st.success("Custom trajectory loaded.")
    else:
        st.info("Using sample flight trajectory. Upload your own CSV above.")

    summary = phase_summary(df)

    # Phase metrics
    cols = st.columns(3)
    for i, (phase, metrics) in enumerate(summary.items()):
        cols[i].metric(f"{phase.capitalize()} Duration",
                       f"{metrics['duration_min']:.0f} min")
        cols[i].metric("Avg Speed", f"{metrics['avg_speed_mps']:.0f} m/s")
        cols[i].metric("Alt Change", f"{metrics['alt_change_m']:+.0f} m")

    # Plots
    phase_colors = {"ground":"#aaaaaa","climb":"#2196F3",
                    "cruise":"#4CAF50","descent":"#FF9800"}
    time_min = df["time_sec"] / 60

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

    ax = axes[0]
    for phase, color in phase_colors.items():
        mask = df["phase"] == phase
        ax.fill_between(time_min, 0, df["altitude_m"],
                        where=mask, alpha=0.3, color=color, label=phase)
    ax.plot(time_min, df["altitude_m"], "k-", linewidth=1.5)
    ax.set_ylabel("Altitude (m)")
    ax.set_title("Flight Profile — Phase Analysis")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.5)

    ax = axes[1]
    g = 9.80665
    df["specific_energy_kJ"] = (
        0.5 * df["velocity_mps"]**2 + g * df["altitude_m"]
    ) / 1000
    ax.plot(time_min, df["specific_energy_kJ"],
            linewidth=2, color="#9C27B0")
    ax.set_ylabel("Specific Energy (kJ/kg)")
    ax.set_xlabel("Time (minutes)")
    ax.set_title("Specific Mechanical Energy")
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ══════════════════════════════════════════════════════════════════
# TAB 5 — Optimization
# ══════════════════════════════════════════════════════════════════
with tab5:
    st.header("Performance Optimization")
    st.markdown(
        "Sensitivity of range to payload and fuel load combinations. "
        "White region exceeds MTOW."
    )

    if not mtow_ok:
        st.error("MTOW exceeded — adjust sidebar first.")
    else:
        with st.spinner("Running sensitivity study (this takes ~10 seconds)..."):
            from scipy.optimize import minimize_scalar

            payload_sweep = np.linspace(5000, ac.max_payload_kg, 15)
            fuel_sweep    = np.linspace(5000, ac.max_fuel_kg, 15)
            range_matrix  = np.zeros((len(fuel_sweep), len(payload_sweep)))

            for i, f in enumerate(fuel_sweep):
                for j, p in enumerate(payload_sweep):
                    try:
                        ac.takeoff_weight(p, f)
                        res = cruise_range_mach_sweep(ac, p, f,
                                                      altitude_m=ac.cruise_altitude_m,
                                                      n_points=30)
                        range_matrix[i, j] = res["range_km"].max()
                    except ValueError:
                        range_matrix[i, j] = np.nan

        fig, ax = plt.subplots(figsize=(8, 5))
        P, F = np.meshgrid(payload_sweep / 1000, fuel_sweep / 1000)
        cf = ax.contourf(P, F, range_matrix, levels=12, cmap="viridis")
        plt.colorbar(cf, ax=ax, label="Range (km)")
        ax.contour(P, F, range_matrix, levels=12,
                   colors="white", alpha=0.3, linewidths=0.5)
        ax.scatter([payload_kg/1000], [fuel_kg/1000],
                   color="red", s=100, zorder=5, label="Current mission")
        ax.set_xlabel("Payload (tonnes)")
        ax.set_ylabel("Fuel Load (tonnes)")
        ax.set_title("Range Sensitivity — Payload vs Fuel")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        valid = range_matrix[~np.isnan(range_matrix)]
        c1, c2, c3 = st.columns(3)
        c1.metric("Min range in study", f"{valid.min():.0f} km")
        c2.metric("Max range in study", f"{valid.max():.0f} km")
        c3.metric("MTOW-limited combos",
                  f"{np.isnan(range_matrix).sum()} / {range_matrix.size}")
import pandas as pd


def load_flight_data(filepath):
    """
    Load flight trajectory CSV data.
    """

    return pd.read_csv(filepath)


def compute_basic_metrics(df):
    """
    Compute fundamental operational metrics.
    """

    max_altitude = df["altitude_m"].max()

    max_velocity = df["velocity_mps"].max()

    total_distance = df["distance_km"].max()

    total_time = df["time_sec"].max()

    return {
        "max_altitude_m": max_altitude,
        "max_velocity_mps": max_velocity,
        "total_distance_km": total_distance,
        "total_time_sec": total_time
    }


def compute_average_cruise_speed(df):
    """
    Estimate average cruise velocity.

    Cruise phase defined as:
    altitude > 10,000 m
    """

    cruise_phase = df[df["altitude_m"] > 10000]

    return cruise_phase["velocity_mps"].mean()


def compute_max_rate_of_climb(df):
    """
    Estimate maximum climb rate.

    Returns:
        climb rate in m/s
    """

    altitude_change = df["altitude_m"].diff()

    time_change = df["time_sec"].diff()

    climb_rate = altitude_change / time_change

    return climb_rate.max()

def compute_total_flight_time_minutes(df):
    """
    Compute total flight duration in minutes.
    """

    return df["time_sec"].max() / 60

def get_unique_flights(df):
    """
    Return unique flight IDs.
    """

    return df["flight_id"].unique()


def filter_flight(df, flight_id):
    """
    Extract a single flight trajectory.
    """

    return df[df["flight_id"] == flight_id]

def compute_average_descent_rate(df):
    """
    Average descent rate during the actual descent phase only.
    Descent phase: altitude decreasing AND below cruise threshold.
    """
    altitude_change = df["altitude_m"].diff()
    time_change     = df["time_sec"].diff()
    vertical_speed  = altitude_change / time_change

    # Only below 10,000m AND descending — excludes cruise fluctuations
    descent_mask = (vertical_speed < -0.5) & (df["altitude_m"] < 10000)
    descent_phase = vertical_speed[descent_mask]

    if descent_phase.empty:
        return 0.0
    return abs(descent_phase.mean())


def detect_flight_phases(df):
    """
    Segment flight into: ground, climb, cruise, descent.
    Returns df with added 'phase' column.
    """
    import numpy as np
    df = df.copy()

    alt   = df["altitude_m"]
    vs    = alt.diff() / df["time_sec"].diff()  # vertical speed m/s

    conditions = [
        alt < 300,
        (vs > 1.0)  & (alt < 9500),
        alt >= 9500,
        (vs < -1.0) & (alt < 9500),
    ]
    choices = ["ground", "climb", "cruise", "descent"]
    df["phase"] = np.select(conditions, choices, default="cruise")
    return df


def phase_summary(df):
    """
    Per-phase performance metrics.
    Call detect_flight_phases(df) first.
    """
    summary = {}
    for phase in ["climb", "cruise", "descent"]:
        p = df[df["phase"] == phase]
        if len(p) < 2:
            continue
        duration_min   = (p["time_sec"].max() - p["time_sec"].min()) / 60
        avg_speed_mps  = p["velocity_mps"].mean()
        alt_change_m   = p["altitude_m"].iloc[-1] - p["altitude_m"].iloc[0]
        avg_vs         = (p["altitude_m"].diff() / p["time_sec"].diff()).mean()
        summary[phase] = {
            "duration_min":  round(duration_min, 1),
            "avg_speed_mps": round(avg_speed_mps, 1),
            "alt_change_m":  round(alt_change_m, 0),
            "avg_vs_mps":    round(avg_vs, 2),
        }
    return summary
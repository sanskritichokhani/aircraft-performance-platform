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


def compute_average_descent_rate(df):
    """
    Estimate average descent rate.

    Returns:
        descent rate in m/s
    """

    altitude_change = df["altitude_m"].diff()

    time_change = df["time_sec"].diff()

    vertical_speed = altitude_change / time_change

    descent_phase = vertical_speed[vertical_speed < 0]

    return abs(descent_phase.mean())


def compute_total_flight_time_minutes(df):
    """
    Compute total flight duration in minutes.
    """

    return df["time_sec"].max() / 60
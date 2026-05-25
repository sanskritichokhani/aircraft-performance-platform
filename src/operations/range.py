import numpy as np

def lift_to_drag_ratio(cl, cd):
    """
    Compute aerodynamic efficiency.
    """
    return cl / cd


def breguet_range(velocity, specific_fuel_consumption, lift_to_drag, initial_weight, final_weight):
    return (velocity / specific_fuel_consumption) * lift_to_drag * np.log(initial_weight / final_weight)

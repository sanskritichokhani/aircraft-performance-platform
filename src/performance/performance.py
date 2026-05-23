import numpy as np

g = 9.81

def lift_coefficient(weight, rho, velocity, wing_area):
    return (2 * weight) / (rho * velocity**2 * wing_area)


def drag_coefficient(cd0, k, cl):
    return cd0 + k * cl**2


def drag_force(rho, velocity, wing_area, cd):
    return 0.5 * rho * velocity**2 * wing_area * cd

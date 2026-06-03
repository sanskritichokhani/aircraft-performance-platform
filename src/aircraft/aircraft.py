"""
Aircraft performance model.

Provides the Aircraft dataclass with validated parameters,
derived quantities, and performance methods.
All parameters in SI units.
"""

import json
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Aircraft:
    """
    Aircraft performance model with validated parameters.

    Attributes are loaded from a JSON config file.
    Derived quantities (k, L/D max) are computed automatically.
    """

    name:               str
    mtow_kg:            float   # maximum takeoff weight
    oew_kg:             float   # operating empty weight
    max_fuel_kg:        float   # maximum fuel capacity
    max_payload_kg:     float   # maximum payload
    wing_area_m2:       float   # reference wing area
    aspect_ratio:       float   # wing aspect ratio
    oswald_efficiency:  float   # Oswald span efficiency factor
    cd0:                float   # zero-lift drag coefficient
    cl_max:             float   # maximum lift coefficient
    cruise_mach:        float   # design cruise Mach number
    cruise_altitude_m:  float   # design cruise altitude
    tsfc_kg_n_s:        float   # thrust-specific fuel consumption

    # Derived — computed automatically, not in JSON
    k:      float = field(init=False, repr=False)
    ld_max: float = field(init=False, repr=False)
    cl_opt: float = field(init=False, repr=False)

    def __post_init__(self):
        self._validate()
        self.k      = 1.0 / (np.pi * self.aspect_ratio * self.oswald_efficiency)
        self.cl_opt = np.sqrt(self.cd0 / self.k)
        self.ld_max = self.cl_opt / (2 * self.cd0)

    def _validate(self):
        assert self.oew_kg + self.max_fuel_kg <= self.mtow_kg, (
            f"OEW ({self.oew_kg} kg) + max fuel ({self.max_fuel_kg} kg) "
            f"exceeds MTOW ({self.mtow_kg} kg)"
        )
        assert 0.0 < self.cd0 < 0.1,        f"CD0={self.cd0} is outside plausible range"
        assert 0.0 < self.oswald_efficiency <= 1.0, "Oswald efficiency must be (0, 1]"
        assert 0.5 < self.cruise_mach < 1.0, f"Cruise Mach={self.cruise_mach} implausible"

    @classmethod
    def from_json(cls, path: str | Path) -> "Aircraft":
        """Load aircraft parameters from a JSON config file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls(**data)

    # ── Performance methods ───────────────────────────────────────

    def cl_at_condition(self, weight_n: float, rho: float, v_mps: float) -> float:
        """CL required for level flight at given weight, density, speed."""
        return weight_n / (0.5 * rho * v_mps**2 * self.wing_area_m2)

    def cd_at_cl(self, cl: float) -> float:
        """Drag coefficient from drag polar."""
        return self.cd0 + self.k * cl**2

    def ld_at_cl(self, cl: float) -> float:
        """Lift-to-drag ratio at given CL."""
        return cl / self.cd_at_cl(cl)

    def max_payload_for_fuel(self, fuel_kg: float) -> float:
        """Maximum allowable payload for a given fuel load."""
        return min(
            self.max_payload_kg,
            self.mtow_kg - self.oew_kg - fuel_kg
        )

    def takeoff_weight(self, payload_kg: float, fuel_kg: float) -> float:
        """Compute takeoff weight and validate against MTOW."""
        tow = self.oew_kg + payload_kg + fuel_kg
        if tow > self.mtow_kg:
            raise ValueError(
                f"TOW {tow:.0f} kg exceeds MTOW {self.mtow_kg:.0f} kg. "
                f"Reduce payload or fuel."
            )
        return tow

    def __str__(self) -> str:
        return (
            f"{self.name}\n"
            f"  MTOW:      {self.mtow_kg:>8,.0f} kg\n"
            f"  OEW:       {self.oew_kg:>8,.0f} kg\n"
            f"  Max fuel:  {self.max_fuel_kg:>8,.0f} kg\n"
            f"  Wing area: {self.wing_area_m2:>8.1f} m²\n"
            f"  AR:        {self.aspect_ratio:>8.2f}\n"
            f"  CD0:       {self.cd0:>8.4f}\n"
            f"  k:         {self.k:>8.4f}  (derived)\n"
            f"  L/D max:   {self.ld_max:>8.2f}  (derived)\n"
            f"  Cruise M:  {self.cruise_mach:>8.3f}\n"
        )
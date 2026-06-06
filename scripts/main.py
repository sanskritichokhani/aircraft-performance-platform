import numpy as np
import matplotlib.pyplot as plt

from src.atmosphere.isa import temperature, pressure, density

# Altitude range (0 to 12 km)
altitudes = np.linspace(0, 12000, 200)

temps = [temperature(h) for h in altitudes]
pressures = [pressure(h) for h in altitudes]
densities = [density(h) for h in altitudes]

# Plot 1: Temperature
plt.figure()
plt.plot(altitudes, temps)
plt.title("ISA Temperature vs Altitude")
plt.xlabel("Altitude (m)")
plt.ylabel("Temperature (K)")
plt.savefig("plots/temperature.png")

# Plot 2: Pressure
plt.figure()
plt.plot(altitudes, pressures)
plt.title("ISA Pressure vs Altitude")
plt.xlabel("Altitude (m)")
plt.ylabel("Pressure (Pa)")
plt.savefig("plots/pressure.png")

# Plot 3: Density
plt.figure()
plt.plot(altitudes, densities)
plt.title("ISA Density vs Altitude")
plt.xlabel("Altitude (m)")
plt.ylabel("Density (kg/m^3)")
plt.savefig("plots/density.png")

plt.show()
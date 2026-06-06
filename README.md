# Aircraft Performance & Flight Operations Analytics Platform

A Python-based aerospace engineering platform for aircraft performance modeling,
mission analysis, and flight operations analytics.
---
## Running Locally
```bash
https://aircraft-performance-platform.streamlit.app/
```
---
## What This Does
This platform integrates five engineering modules into a unified interactive dashboard:
| Module | What it computes |
|--------|-----------------|
| ISA Atmosphere | Temperature, pressure, density, speed of sound vs altitude |
| Aerodynamics | Drag polar, L/D ratio, minimum drag speed |
| Range Analysis | Breguet range equation, payload-range diagram |
| Flight Operations | Phase detection, specific energy analysis |
| Optimization | Altitude optimization, payload-fuel sensitivity, cruise Mach vs weight |
---
## Aircraft Supported
| Aircraft | MTOW | Design Range | Cruise Mach |
|----------|------|-------------|-------------|
| Boeing 737-800 | 79,016 kg | ~5,765 km | M 0.785 |
| Airbus A320neo | 79,000 kg | ~6,300 km | M 0.780 |
| Boeing 777-300ER | 351,534 kg | ~13,650 km | M 0.840 |
---
## Engineering Approach
### Atmosphere Model
International Standard Atmosphere (ISA) covering troposphere (0–11,000 m)
and lower stratosphere, with correct isothermal layer above tropopause.
### Aerodynamic Model
Drag polar: `CD = CD0 + k·CL²`  
Induced drag factor derived from wing geometry: `k = 1/(π·AR·e)`  
Not hardcoded — computed from aircraft parameters.
### Range Model
Breguet range equation:  
`R = (V/TSFC) · (L/D) · ln(Wi/Wf)`
Key implementation decisions:
- TSFC in SI units: `kg/(N·s)` — common source of unit errors
- Mission initialized from defined payload + fuel load, not MTOW
- Wave drag correction above Mach 0.78 (Mcrit for narrow-body transports)
- Model validated: **4.4% error vs Boeing 737-800 published range**
### Optimization
- Cruise altitude sweep with thrust lapse approximation: `T/T_sl ≈ (ρ/ρ_sl)^0.7`
- Payload-fuel sensitivity: 400-point contour study showing MTOW constraint boundary
- Cruise Mach optimizer: `scipy.minimize_scalar` on Breguet range factor `V·(L/D)`
### Flight Phase Analysis
Automatic segmentation into ground / climb / cruise / descent phases
using vertical speed thresholds. Specific mechanical energy computed as:
`E = V²/2 + g·h` (J/kg)
---
## Model Limitations
This is a conceptual-level model. Known limitations:
- **No wind modeling** — assumes still air throughout
- **Constant TSFC** — real engines vary with throttle and altitude
- **Single cruise altitude** — no step-climb simulation
- **Thrust ceiling** — simplified lapse rate, not a full engine deck
- **No reserve fuel** — Breguet uses all loaded fuel
- **Incompressible aerodynamics** — wave drag is a simplified correction only
These limitations are consistent with conceptual design tools used in early
aircraft development phases.
---
## Project Structure
```
aircraft-performance-platform/
├── app.py                          # Streamlit dashboard (entry point)
├── requirements.txt
├── src/
│   ├── aircraft/
│   │   ├── aircraft_model.py       # Aircraft dataclass with validation
│   │       ├── b737_800.json
│   │       ├── a320neo.json
│   │       └── b777_300er.json
│   ├── atmosphere/
│   │   └── isa.py                  # ISA model (troposphere + stratosphere)
│   ├── performance/
│   │   └── range_analysis.py       # Breguet range + payload-range diagram
│   └── analytics/
│       └── flight_analysis.py      # Phase detection + energy analysis
├── data/
│   ├── sample_flight.csv
│   └── multi_flight_data.csv
└── scripts/                        # Development scripts (Days 2–8)
    ├── day2.py  ...  day8.py
```
---
## Technical Stack
| Tool | Purpose |
|------|---------|
| Python 3.11+ | Core language |
| NumPy | Vectorized physics calculations |
| Pandas | Flight data processing |
| Matplotlib | Engineering visualizations |
| SciPy | Cruise Mach optimization |
| Streamlit | Interactive dashboard |
---
## Validation
| Metric | Model | Reference | Error |
|--------|-------|-----------|-------|
| 737-800 range (typical mission) | 6,016 km | 5,765 km | +4.4% |
| ISA temp at FL350 | 216.7 K | 216.65 K | <0.1% |
| ISA density at FL350 | 0.3796 kg/m³ | 0.3796 kg/m³ | <0.1% |

*UIUC Aerospace Engineering · AE Class of 2029*
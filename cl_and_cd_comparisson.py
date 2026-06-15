import numpy as np
import pprint

# Assuming 'airplane' is already defined with Layout 1 parameters
# from designTool.standard_airplane import standard_airplane
from designTool.standard_airplane import standard_airplane
from designTool.auxiliary import atmosphere

# Create a default airplane instance for the analysis
airplane = standard_airplane('crusair1')
from designTool.geometry import geometry as compute_geometry

# Compute geometry fields expected by the aerodynamic routine
compute_geometry(airplane)

from designTool.aerodynamics import aerodynamics

# Layout 1 Parameters
Mach_cruise = 0.77
altitude_cruise = 10668.0
MTOW = 280000 * 9.80665 # 280,000 kg to Newtons
W_cruise = 0.95 * MTOW
S_w = 450.0
AR_w = 9.3

# Calculate atmospheric properties at 10668m (Standard Atmosphere)
atm = atmosphere(altitude_cruise)
rho = atm['density']
a = atm['speed_of_sound']
mi = atm['dyn_viscosity']
V_cruise = Mach_cruise * a
q = 0.5 * rho * V_cruise**2

# Calculate expected Cruise CL
CL_cruise = W_cruise / (q * S_w)

# Calculate cruise Reynolds number using mean aerodynamic chord
Re_cruise = rho * V_cruise * airplane['geometry']['cm_w'] / mi

# Execute the aerodynamic analysis
CD_cruise, CLmax, dragDict = aerodynamics(
    airplane, 
    Mach=Mach_cruise, 
    altitude=altitude_cruise, 
    CL=CL_cruise,
    n_engines_failed=0.0,
    highlift_config='clean',
    lg_down=0.0,
    h_ground=0.0
)

# 1. Cruise L/D
LD_cruise = CL_cruise / CD_cruise

# 2. Maximum L/D
CD0 = dragDict['CD0'] # Extract from tool output
e = dragDict['e']     # Extract from tool output
K = 1.0 / (np.pi * e * AR_w)
LD_max = 1.0 / (2.0 * np.sqrt(CD0 * K))

# Print Results
print("=== Exercise 8 Results ===")
print(f"Cruise CL: {CL_cruise:.4f}")
print(f"Cruise CD: {CD_cruise:.4f}")
print(f"Cruise Reynolds: {Re_cruise:.3e}")
print(f"Cruise L/D: {LD_cruise:.2f}")
print(f"Max L/D: {LD_max:.2f}")
print("==========================")
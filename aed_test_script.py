# Sample script on how to use the aerodynamics function from designTool.
# Remember to save this script in the same directory as designTool.py

# IMPORTS
from designTool.standard_airplane import standard_airplane
from designTool.geometry import geometry
from designTool.aerodynamics import aerodynamics
import numpy as np
import pprint
from designTool.auxiliary import atmosphere
import matplotlib.pyplot as plt

# Load a sample case already defined in designTools.py:
airplane = standard_airplane('crusair1')
airplane2 = standard_airplane('crusair2')

# Execute the geometry function
geometry(airplane)
geometry(airplane2)

# Calculando o CL
# Considerando cruzeiro (L = W)
# CL = 2W/(rho*V^2*S)
def calculo_CL(airplane):
    S_w = airplane['inputs']['S_w']
    alt = airplane["inputs"]['altitude_cruise']
    atm = atmosphere(alt)
    rho = atm['density']
    a = atm['speed_of_sound']
    Mach = airplane["inputs"]['Mach_cruise']
    Vtas = Mach*a

    W0 = airplane["inputs"]['W0_guess']
    W = 0.95*W0 # O EXERCICIO PEDE 95% DE W0

    CL = 2*W/(rho*(Vtas**2)*S_w);

    print("\nCL CALCULADO", CL)
    
    return CL

# Cruise conditions for aerodynamic analysis

# CALCULO DOS DOIS CLs
CL =  calculo_CL(airplane)
CL2 = calculo_CL(airplane2)

Mach = airplane["inputs"]['Mach_cruise']
altitude = airplane["inputs"]['altitude_cruise']
n_engines_failed = 0.00000000000000
highlift_config = 'clean'
lg_down = 0.00000000000000
h_ground = 0.00000000000000

# Grafico CD vs Mach
Mach_vector = np.arange(0.6,0.9,0.001)
CD_vector = []
for Mach_i in Mach_vector:
    CD,_,_ = aerodynamics(airplane, Mach_i, altitude, CL,
                                       n_engines_failed=n_engines_failed, highlift_config=highlift_config,
                                       lg_down=lg_down, h_ground=h_ground)
    CD_vector.append(CD)
    
plt.plot(Mach_vector, CD_vector, 'k-',label= 'CD')
plt.title('CD x Mach - Condição de cruzeiro')
plt.xlabel('Mach')
plt.ylabel('CD')
plt.grid(True, linestyle=':')
CD_cruise,_,CD_Mdd_dict = aerodynamics(airplane, 0.85, altitude, CL,
                                   n_engines_failed=n_engines_failed, highlift_config=highlift_config,
                                   lg_down=lg_down, h_ground=h_ground)
plt.scatter(0.85, CD_cruise, color='red', s=30, zorder=2, label=f'Requisito: CD={CD_cruise:.4f} ,M=0.85')
plt.axhline(y=CD_cruise, color='red', linestyle='--', alpha=0.3)
plt.axvline(x=0.85, color='red', linestyle='--', alpha=0.3)


CD_Mdd,_,_ = aerodynamics(airplane, CD_Mdd_dict['Mach_dd'], altitude, CL,
                                   n_engines_failed=n_engines_failed, highlift_config=highlift_config,
                                   lg_down=lg_down, h_ground=h_ground)
plt.scatter(CD_Mdd_dict['Mach_dd'], CD_Mdd, color='blue', s=30, zorder=2, label=f'M divergência: CD={CD_Mdd:.4f} ,M={CD_Mdd_dict['Mach_dd']:.4f}')
plt.axhline(y=CD_Mdd, color='blue', linestyle='--', alpha=0.3)
plt.axvline(x=CD_Mdd_dict['Mach_dd'], color='blue', linestyle='--', alpha=0.3)

plt.legend(bbox_to_anchor=(+0.5, -0.4),loc='lower center', shadow=False, fontsize='small')
plt.show()

# Execute the aerodynamic analysis
CD, CLmax, dragDict = aerodynamics(airplane, Mach, altitude, CL,
                                   n_engines_failed=n_engines_failed, highlift_config=highlift_config,
                                   lg_down=lg_down, h_ground=h_ground)

# Print results
print("Cruise conditions")
print("CD = ",CD)
print("CLmax = ",CLmax)
print("dragDict = " + pprint.pformat(dragDict))
print("")

# Takeoff climb conditions for aerodynamic analysis
Mach = 0.30000000000000
altitude = 0.00000000000000
CL = 1.52777777777778
n_engines_failed = 1.00000000000000
highlift_config = 'takeoff'
lg_down = 0.00000000000000
h_ground = 0.00000000000000

# Execute the aerodynamic analysis
CD, CLmax, dragDict = aerodynamics(airplane, Mach, altitude, CL,
                                   n_engines_failed=n_engines_failed, highlift_config=highlift_config,
                                   lg_down=lg_down, h_ground=h_ground)

# Print results
print("Takeoff climb conditions")
print("CD = ",CD)
print("CLmax = ",CLmax)
print("dragDict = " + pprint.pformat(dragDict))
print("")

# Approach conditions for aerodynamic analysis
Mach = 0.30000000000000
altitude = 0.00000000000000
CL = 1.09630629111149
n_engines_failed = 1.00000000000000
highlift_config = 'approach'
lg_down = 1.00000000000000
h_ground = 0.00000000000000

# Execute the aerodynamic analysis
CD, CLmax, dragDict = aerodynamics(airplane, Mach, altitude, CL,
                                   n_engines_failed=n_engines_failed, highlift_config=highlift_config,
                                   lg_down=lg_down, h_ground=h_ground)

# Print results
print("Approach conditions")
print("CD = ",CD)
print("CLmax = ",CLmax)
print("dragDict = " + pprint.pformat(dragDict))
print("")

# Landing conditions for aerodynamic analysis
Mach = 0.30000000000000
altitude = 0.00000000000000
CL = 1.53846153846154
n_engines_failed = 0.00000000000000
highlift_config = 'landing'
lg_down = 1.00000000000000
h_ground = 10.66800000000000

# Execute the aerodynamic analysis
CD, CLmax, dragDict = aerodynamics(airplane, Mach, altitude, CL,
                                   n_engines_failed=n_engines_failed, highlift_config=highlift_config,
                                   lg_down=lg_down, h_ground=h_ground)

# Print results
print("Landing conditions")
print("CD = ",CD)
print("CLmax = ",CLmax)
print("dragDict = " + pprint.pformat(dragDict))
print("")


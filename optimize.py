# IMPORTS
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution, NonlinearConstraint
from designTool.standard_airplane import standard_airplane
from designTool.analyze import analyze
from designTool.constants import gravity

xlist = []
flist = []


def run_airplane(x):
    airplane = standard_airplane('crusair1')
    airplane['inputs']['S_w'] = x[0]
    airplane['inputs']['AR_w'] = x[1]
    airplane['inputs']['taper_w'] = x[2]
    airplane['inputs']['sweep_w'] = x[3] * np.pi / 180.0
    airplane['inputs']['tcr_w'] = x[4]
    airplane['inputs']['xr_w'] = x[5]

    analyze(airplane, print_log=False, plot=False)
    return airplane


# Objective function
def objfun(x):
    airplane = run_airplane(x)

    # Minimizar MTOW (W0) em toneladas [t]
    f = airplane['thrust_matching']['W0'] / gravity / 1000.0

    xlist.append(x)
    flist.append(f)

    return f


# Constraint function
def confun(x):
    airplane = run_airplane(x)

    T0_avail = airplane['thrust_matching']['T0']
    T0_req = 1.05 * max(airplane['thrust_matching']['T0req'].values())

    g1 = airplane['thrust_matching']['deltaS_wlan']                     # Margem de área de pouso [m²]
    g2 = airplane['balance']['tank_excess']                             # Excesso de volume no tanque [-]
    g3 = (T0_avail - T0_req) / 1000.0                                   # Excesso de tração [kN]
    g4 = airplane['geometry']['b_w']                                    # Envergadura [m]
    g5 = airplane['balance']['SM_aft']                                  # Margem estática traseira [-]
    g6 = airplane['balance']['SM_fwd']                                  # Margem estática dianteira [-]
    g7 = airplane['balance']['CLv']                                     # CL da empenagem vertical OEI [-]
    g8 = airplane['landing_gear']['frac_nlg_aft']                       # Fração de peso no NLG (CG traseiro) [-]
    g9 = airplane['landing_gear']['frac_nlg_fwd']                       # Fração de peso no NLG (CG dianteiro) [-]
    g10 = airplane['landing_gear']['alpha_tipback'] * 180.0 / np.pi     # Ângulo de tipback [deg]
    g11 = airplane['landing_gear']['phi_overturn'] * 180.0 / np.pi      # Ângulo de overturn [deg]
    g12 = airplane['landing_gear']['alpha_tailstrike'] * 180.0 / np.pi  # Ângulo de tailstrike [deg]

    return [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12]


# Lower and upper bounds for the constraints
# g1 >= 0, g2 >= 0, g3 >= 0, g4 <= 65, g5 >= 0.05, g6 <= 0.40,
# g7 <= 0.75, g8 >= 0.05, g9 <= 0.18, g10 >= 15, g11 <= 63, g12 >= 10
lb = np.array([0.0,    0.0,    0.0, -np.inf,   0.05, -np.inf, -np.inf,   0.05, -np.inf,   15.0, -np.inf,   10.0])
ub = np.array([np.inf, np.inf, np.inf,  65.0, np.inf,    0.40,    0.75, np.inf,    0.18, np.inf,    63.0, np.inf])

# Create the NonlinearConstraint object
nonlinear_constraint = NonlinearConstraint(confun, lb, ub)

# Define bounds for the 6 selected design variables 
# [S_w, AR_w, taper_w, sweep_w (deg), tcr_w, xr_w]
bounds = [
    (340.0, 440.0),  # S_w [m²]
    (8.0,   12.0),   # AR_w [-]
    (0.12,  0.35),   # taper_w [-]
    (32.0,  36.0),   # sweep_w [deg]
    (0.11,  0.16),   # tcr_w [-]
    (19.5,  23.5),   # xr_w [m]
]

# Run differential_evolution with the nonlinear constraint
t0 = time.time()
result = differential_evolution(objfun, bounds,
                                constraints=nonlinear_constraint,
                                maxiter=200,
                                popsize=10,
                                tol=1e-4,
                                seed=42,
                                polish=False
                                )

elapsed_time = time.time() - t0

# Baseline crusair1
x0 = np.array([394.0, 10.7, 0.129, 33.0, 0.14, 21.5])
var_names = ['S_w [m2]', 'AR_w [-]', 'taper_w [-]', 'sweep_w [deg]', 'tcr_w [-]', 'xr_w [m]']
con_names = ['g1: deltaS_wlan [m2]', 'g2: tank_excess [-]', 'g3: thrust_margin [kN]',
             'g4: b_w [m]', 'g5: SM_aft [-]', 'g6: SM_fwd [-]', 'g7: CLv [-]',
             'g8: frac_nlg_aft [-]', 'g9: frac_nlg_fwd [-]', 'g10: tipback [deg]',
             'g11: overturn [deg]', 'g12: tailstrike [deg]']

print(result)
print(f"\nComputational Cost -> Time: {elapsed_time:.2f} s | Generations (nit): {result.nit} | Evaluations (nfev): {result.nfev}")

# Save optimization history before running baseline/sensitivity evaluations (slsqp_start.py line 137)
xk = xlist.copy()
fk = flist.copy()


f0 = objfun(x0)
print("\n--- Design Variables: Baseline vs Optimal (with Bounds) ---")
for i, name in enumerate(var_names):
    print(f"{name:<15} | Base: {x0[i]:8.4f} | Opt: {result.x[i]:8.4f} | Bounds: [{bounds[i][0]}, {bounds[i][1]}]")

print(f"\nObjective W0 [t] | Base: {f0:8.4f} | Opt: {result.fun:8.4f} | Diff: {result.fun - f0:+.4f} t")

print("\n--- Constraints: Baseline vs Optimal (with Limits) ---")
g0 = confun(x0)
g_opt = confun(result.x)
for i, cname in enumerate(con_names):
    print(f"{cname:<24} | Base: {g0[i]:8.4f} | Opt: {g_opt[i]:8.4f} | Limits: [{lb[i]}, {ub[i]}]")

# Plot optimization history
x_history = np.array(xlist)  # Converte a lista de vetores numa matriz

fig_vars, axes = plt.subplots(len(var_names), 1, figsize=(9, 2 * len(var_names)), sharex=True)

for i, name in enumerate(var_names):
    axes[i].plot(x_history[:, i], 'o-', markersize=2, color='tab:blue')
    axes[i].set_ylabel(name, fontsize=9)
    axes[i].grid(True, alpha=0.3)

axes[-1].set_xlabel('Número de Avaliações', fontsize=10)
fig_vars.suptitle('Differential Evolution History: Design Variables', fontsize=14, y=0.99)
fig_vars.tight_layout()
fig_vars.savefig('results_optimization/design_variables_history.png', dpi=200)
plt.show()

fig_obj, ax = plt.subplots(figsize=(9, 4.5))

ax.plot(flist, 'o-', color='crimson', markersize=3)
ax.set_ylabel('W0 [t]', fontsize=10)
ax.set_xlabel('Número de Avaliações', fontsize=10)
ax.set_title('Convergência da Função Objetivo (MTOW)', fontsize=13)
ax.grid(True, alpha=0.3)

fig_obj.tight_layout()
fig_obj.savefig('results_optimization/objective_function_history.png', dpi=200)
plt.show()
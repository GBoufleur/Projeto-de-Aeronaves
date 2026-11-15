import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution, NonlinearConstraint
from designTool.standard_airplane import standard_airplane
from designTool.geometry import geometry
from designTool.analyze import analyze
from designTool.constants import gravity

# =========================================
# DESIGN VARIABLES & CONSTRAINTS SETUP

# (name, baseline, (lower_bound, upper_bound))
DESIGN_VARS = [
    ('S_w [m2]',      394.0,  (365.0, 405.0)),
    ('AR_w [-]',      10.7,   (10.0,   12.0)),
    ('taper_w [-]',   0.129,  (0.11,  0.20)),
    ('sweep_w [deg]', 33.0,   (29.0,  33.50)),
    ('tcr_w [-]',     0.14,   (0.12,  0.13)),
    ('tct_w [-]',     0.10,   (0.09,  0.11)),
    ('xr_w [m]',      21.5,   (21.0,  23.0)),
    ('x_mlg [MAC]',   0.6188, (0.53,  0.56)),
]

var_names = [v[0] for v in DESIGN_VARS]
x0 = np.array([v[1] for v in DESIGN_VARS])
bounds = [v[2] for v in DESIGN_VARS]

con_names = [
    'g1: deltaS_wlan [m2]', 'g2: tank_excess [-]', 'g3: thrust_margin [kN]',
    'g4: b_w [m]', 'g5: SM_aft [-]', 'g6: SM_fwd [-]', 'g7: CLv [-]',
    'g8: frac_nlg_aft [-]', 'g9: frac_nlg_fwd [-]', 'g10: tipback [deg]',
    'g11: overturn [deg]', 'g12: tailstrike [deg]',
]

# g1 >= 0, g2 >= 0, g3 >= 0, g4 <= 64.5, g5 >= 0.05, g6 <= 0.40,
# g7 <= 0.75, g8 >= 0.05, g9 <= 0.18, g10 >= 15, g11 <= 63, g12 >= 10
lb = np.array([0.0,    0.0,    0.0, -np.inf,   0.05, -np.inf, -np.inf,   0.05, -np.inf,   15.0, -np.inf,   10.0])
ub = np.array([np.inf, np.inf, np.inf,  64.5, np.inf,    0.40,    0.75, np.inf,    0.18, np.inf,    63.0, np.inf])

xlist = []
flist = []


# =========================================
# MODEL EVALUATION

def run_airplane(x, print_log=False, plot=False):
    """Configures crusair1 with design vector x and runs analyze."""
    airplane = standard_airplane('crusair1')
    inp = airplane['inputs']
    inp['S_w'] = x[0]
    inp['AR_w'] = x[1]
    inp['taper_w'] = x[2]
    inp['sweep_w'] = x[3] * np.pi / 180.0
    inp['tcr_w'] = x[4]
    inp['tct_w'] = x[5]
    inp['xr_w'] = x[6]

    geometry(airplane)
    inp['x_mlg'] = airplane['geometry']['xm_w'] + x[7] * airplane['geometry']['cm_w']

    analyze(airplane, print_log=print_log, plot=plot)
    return airplane


# Objective function
def objfun(x):
    airplane = run_airplane(x)
    f = airplane['thrust_matching']['W0'] / gravity / 1000.0
    xlist.append(x)
    flist.append(f)
    return f


# Constraint function
def confun(x):
    airplane = run_airplane(x)
    tm = airplane['thrust_matching']
    bal = airplane['balance']
    lg = airplane['landing_gear']

    T0_avail = tm['T0']
    T0_req = 1.05 * max(tm['T0req'].values())

    return [
        tm['deltaS_wlan'],                      # Margem de área de pouso [m²]
        bal['tank_excess'],                     # Excesso de volume no tanque [-]
        (T0_avail - T0_req) / 1000.0,           # Excesso de tração [kN]
        airplane['geometry']['b_w'],            # Envergadura [m]
        bal['SM_aft'],                          # Margem estática traseira [-]
        bal['SM_fwd'],                          # Margem estática dianteira [-]
        bal['CLv'],                             # CL da empenagem vertical OEI [-]
        lg['frac_nlg_aft'],                     # Fração de peso no NLG (CG traseiro) [-]
        lg['frac_nlg_fwd'],                     # Fração de peso no NLG (CG dianteiro) [-]
        lg['alpha_tipback'] * 180.0 / np.pi,    # Ângulo de tipback [deg]
        lg['phi_overturn'] * 180.0 / np.pi,     # Ângulo de overturn [deg]
        lg['alpha_tailstrike'] * 180.0 / np.pi, # Ângulo de tailstrike [deg]
    ]


# =========================================
# OPTIMIZATION

nonlinear_constraint = NonlinearConstraint(confun, lb, ub)

maxiter = 200
gen = [0]

def progress_callback(*args, **kwargs):
    gen[0] += 1
    print(f'\rOtimização: {100 * gen[0] / maxiter:5.1f}% ({gen[0]}/{maxiter})', end='', flush=True)

t0 = time.time()
result = differential_evolution(objfun, bounds,
                                constraints=nonlinear_constraint,
                                maxiter=maxiter,
                                popsize=8,
                                tol=1e-3,
                                seed=42,
                                polish=False,
                                callback=progress_callback
                                )
print()

elapsed_time = time.time() - t0


# =========================================
# RESULTS

print(result)
print(f"\nComputational Cost -> Time: {elapsed_time:.2f} s | Generations (nit): {result.nit} | Evaluations (nfev): {result.nfev}")

# Save optimization history before running baseline/sensitivity evaluations
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


# =========================================
# PLOTS

x_history = np.array(xlist)

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

# Analyze and plot the optimal airplane
run_airplane(result.x, print_log=True, plot=True)
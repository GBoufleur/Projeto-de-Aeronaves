# IMPORTS
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pymoo.core.problem import Problem
from pymoo.operators.sampling.lhs import LHS
from designTool.standard_airplane import standard_airplane
from designTool.analyze import analyze
from designTool.constants import gravity


# Function to generate correlation values (from aux_tools_doe.py)
def corrdot(*args, **kwargs):
    corr_r = args[0].corr(args[1], 'pearson')
    corr_text = f"{corr_r:2.2f}".replace("0.", ".")
    ax = plt.gca()
    ax.set_axis_off()
    marker_size = abs(corr_r) * 10000
    ax.scatter([.5], [.5], marker_size, [corr_r], alpha=0.6, cmap="coolwarm",
               vmin=-1, vmax=1, transform=ax.transAxes)
    font_size = abs(corr_r) * 40 + 5
    ax.annotate(corr_text, [.5, .5], xycoords="axes fraction",
                ha='center', va='center', fontsize=font_size)


# =========================================
# SETUP

# Define design function
def des_funcs(Xinp):
    S_w, AR_w, taper_w, sweep_w, tcr_w, tct_w, xr_w, Cht, Cvt, x_mlg = Xinp

    airplane = standard_airplane('crusair1')
    airplane['inputs']['S_w'] = S_w
    airplane['inputs']['AR_w'] = AR_w
    airplane['inputs']['taper_w'] = taper_w
    airplane['inputs']['sweep_w'] = sweep_w * np.pi / 180.0
    airplane['inputs']['tcr_w'] = tcr_w
    airplane['inputs']['tct_w'] = tct_w
    airplane['inputs']['xr_w'] = xr_w
    airplane['inputs']['Cht'] = Cht
    airplane['inputs']['Cvt'] = Cvt
    airplane['inputs']['x_mlg'] = x_mlg

    analyze(airplane, print_log=False, plot=False)

    # Outputs in kgf (kg)
    Wf = airplane['thrust_matching']['W_fuel'] / gravity
    W0 = airplane['thrust_matching']['W0'] / gravity

    return Wf, W0

var_names = ['S_w', 'AR_w', 'taper_w', 'sweep_w', 'tcr_w', 'tct_w', 'xr_w', 'Cht', 'Cvt', 'x_mlg']
var_units = ['m2', '-', '-', 'deg', '-', '-', 'm', '-', '-', 'm']

# Lower and upper bounds of each input variable
lb = [340.0,  8.0, 0.12, 30.0, 0.11, 0.08, 19.5, 0.50, 0.04, 32.5]
ub = [440.0, 12.0, 0.35, 36.0, 0.16, 0.11, 23.5, 0.85, 0.08, 36.5]

# =========================================
# 1. LOCAL SENSITIVITY ANALYSIS 

# Baseline crusair1 values (x*)
x_base = np.array([394.0, 10.7, 0.129, 33.0, 0.14, 0.10, 21.5, 0.60, 0.05, 34.7])
Wf_star, W0_star = des_funcs(x_base)

# Relative perturbation of +5%
rel_step = 0.05

print("\n" + "=" * 95)
print("SENSITIVITY ANALYSIS TABLE (perturbation = +5%)")
print(f"Baseline: Wf* = {Wf_star:.1f} kg | W0* = {W0_star:.1f} kg")
print("=" * 95)
print(f"{'Input':<10} | {'x*':>8} | {'dx':>8} | {'dWf/dx [kg/un]':>16} | {'dW0/dx [kg/un]':>16} | {'(dWf/Wf*)/(dx/x*)':>18} | {'(dW0/W0*)/(dx/x*)':>18}")
print("-" * 95)

for i, name in enumerate(var_names):
    x_pert = x_base.copy()
    dx = rel_step * x_base[i]
    x_pert[i] += dx
    Wf_p, W0_p = des_funcs(x_pert)

    dWf = Wf_p - Wf_star
    dW0 = W0_p - W0_star

    # Absolute sensitivity: dy / dx 
    abs_sens_Wf = dWf / dx
    abs_sens_W0 = dW0 / dx

    # Relative sensitivity: (dy / y*) / (dx / x*) (Slide 6)
    rel_sens_Wf = (dWf / Wf_star) / (dx / x_base[i])
    rel_sens_W0 = (dW0 / W0_star) / (dx / x_base[i])

    print(f"{name:<10} | {x_base[i]:8.3f} | {dx:8.4f} | {abs_sens_Wf:16.2f} | {abs_sens_W0:16.2f} | {rel_sens_Wf:18.4f} | {rel_sens_W0:18.4f}")

# =========================================
# 2. TORNADO CHART: -5% VS +5% 
W0_minus = np.zeros(len(var_names))
W0_plus = np.zeros(len(var_names))

for i in range(len(var_names)):
    xm = x_base.copy()
    xp = x_base.copy()
    xm[i] *= (1.0 - rel_step)
    xp[i] *= (1.0 + rel_step)
    _, W0_minus[i] = des_funcs(xm)
    _, W0_plus[i] = des_funcs(xp)

impact_range = np.abs(W0_plus - W0_minus)
order = np.argsort(impact_range)

fig, ax = plt.subplots(figsize=(9, 5.5))
y_pos = np.arange(len(var_names))
ax.barh(y_pos, W0_minus[order] - W0_star, left=W0_star, color='mediumslateblue', edgecolor='black', label='-5%')
ax.barh(y_pos, W0_plus[order] - W0_star, left=W0_star, color='salmon', edgecolor='black', label='+5%')
ax.axvline(W0_star, color='black', linewidth=1.2)
ax.set(yticks=y_pos, 
       yticklabels=[var_names[i] for i in order],
       xlabel='MTOW [kgf]', 
       title='Tornado Chart: -5% vs +5% values')

ax.legend()
ax.grid(True, axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig('results_optimization/tornado_sensitivity.png', dpi=200)

# =========================================
# 3. DOE - LATIN HYPERCUBE SAMPLING 
n_samples = 200
sampler = LHS()
plot_type = 1

np.random.seed(123)
n_var = len(lb)
problem = Problem(n_var=n_var, xl=lb, xu=ub)
X = sampler(problem, n_samples).get("X")

Wf_samples = np.zeros(n_samples)
W0_samples = np.zeros(n_samples)
for ii in range(n_samples):
    Wf_samples[ii], W0_samples[ii] = des_funcs(X[ii, :])

# Create DataFrame with the variables that affect MTOW/Wf (Slide 26)
df = pd.DataFrame({
    'S_w': X[:, 0],
    'AR_w': X[:, 1],
    'taper_w': X[:, 2],
    'sweep_w': X[:, 3],
    'tcr_w': X[:, 4],
    'tct_w': X[:, 5],
    'Cht': X[:, 7],
    'W_fuel': Wf_samples / 1000.0,
    'MTOW': W0_samples / 1000.0
}).dropna()

print("\n=== Correlação de Pearson no DOE (LHS, N = 200) ===")
print(df.corr(method='pearson')[['W_fuel', 'MTOW']].drop(['W_fuel', 'MTOW']))

sns.set(style='white', font_scale=1.1)

if plot_type == 0:
    fig = sns.pairplot(df, corner=True)
elif plot_type == 1:
    fig = sns.PairGrid(df, diag_sharey=False)
    fig.map_lower(sns.regplot, lowess=True, line_kws={'color': 'black'})
    fig.map_diag(sns.histplot)
    fig.map_upper(corrdot)

plt.tight_layout()
fig.savefig('results_optimization/Pearson.png')
plt.show()

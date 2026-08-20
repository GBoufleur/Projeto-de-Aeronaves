from copy import deepcopy
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from designTool.standard_airplane import standard_airplane
from designTool.geometry import geometry
from designTool.weight import weight
from designTool.performance import performance
from designTool.aerodynamics import aerodynamics
from designTool.auxiliary import atmosphere
from designTool.constants import gravity


def linear_root(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    idx = np.where(np.signbit(y[:-1]) != np.signbit(y[1:]))[0]
    if len(idx) == 0:
        exact = np.where(np.isclose(y, 0.0))[0]
        return float(x[exact[0]]) if len(exact) else None
    i = idx[0]
    return float(x[i] - y[i] * (x[i + 1] - x[i]) / (y[i + 1] - y[i]))


def contiguous_intervals(values, labels):
    out = []
    start = 0
    for i in range(1, len(labels)):
        if labels[i] != labels[start]:
            out.append((float(values[start]), float(values[i - 1]), labels[start]))
            start = i
    out.append((float(values[start]), float(values[-1]), labels[start]))
    return out


def run():
    outdir = Path('results_Sw_performance')
    outdir.mkdir(exist_ok=True)
    sw_values = np.arange(300.0, 501.0, 1.0)
    criteria = ['Takeoff', 'Cruise', 'High speed cruise', 'FAR 25.111', 'FAR 25.121a', 'FAR 25.121b', 'FAR 25.121c', 'FAR 25.119', 'FAR 25.121d']
    rows = []

    for sw in sw_values:
        airplane = deepcopy(standard_airplane('crusair1'))
        airplane['inputs']['S_w'] = float(sw)
        geometry(airplane)
        t_weight = airplane['inputs']['engine']['Tmax'] * airplane['inputs']['n_engines']
        w0_guess = airplane['inputs']['W0_guess']
        W0, W_empty, W_fuel, W_cruise = weight(w0_guess, t_weight, airplane)
        T0, T0req, deltaS_wlan, CLmaxTO = performance(W0, W_cruise, airplane)
        _, CLmaxLD, _ = aerodynamics(airplane, Mach=0.2, altitude=airplane['inputs']['altitude_landing'], CL=0.5, n_engines_failed=0, highlift_config='landing', lg_down=1, h_ground=airplane['inputs']['h_ground'])
        atm = atmosphere(airplane['inputs']['altitude_cruise'])
        v = airplane['inputs']['Mach_cruise'] * atm['speed_of_sound']
        CL = 2.0 * W_cruise / atm['density'] / sw / v**2
        CD, _, drag = aerodynamics(airplane, Mach=airplane['inputs']['Mach_cruise'], altitude=airplane['inputs']['altitude_cruise'], CL=CL, n_engines_failed=0, highlift_config='clean', lg_down=0, h_ground=0)
        critical = max(T0req, key=T0req.get)
        row = {
            'Sw_m2': sw,
            'span_m': airplane['geometry']['b_w'],
            'MAC_m': airplane['geometry']['cm_w'],
            'Sh_m2': airplane['geometry']['S_h'],
            'Sv_m2': airplane['geometry']['S_v'],
            'MTOW_t': W0 / gravity / 1000.0,
            'Wempty_t': W_empty / gravity / 1000.0,
            'Wfuel_t': W_fuel / gravity / 1000.0,
            'Wcruise_t': W_cruise / gravity / 1000.0,
            'MLW_t': airplane['inputs']['MLW_frac'] * W0 / gravity / 1000.0,
            'MLW_frac': airplane['inputs']['MLW_frac'],
            'CLmaxTO': CLmaxTO,
            'CLmaxLD': CLmaxLD,
            'CL_cruise': CL,
            'CD_cruise': CD,
            'CD0_cruise': drag['CD0'],
            'CDwave_cruise': drag['CDwave'],
            'K_cruise': drag['K'],
            'LD_cruise': CL / CD,
            'deltaS_landing_m2': deltaS_wlan,
            'Sw_landing_required_m2': sw - deltaS_wlan,
            'critical': critical,
            'T0_envelope_kN': max(T0req.values()) / 1000.0,
            'T0_design_5pct_kN': T0 / 1000.0,
        }
        for key in criteria:
            row[key] = T0req[key] / 1000.0
        rows.append(row)

    fields = list(rows[0].keys())
    with (outdir / 'Sw_performance_results.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    sw = np.array([r['Sw_m2'] for r in rows])
    delta_landing = np.array([r['deltaS_landing_m2'] for r in rows])
    landing_root = linear_root(sw, delta_landing)
    to_minus_hsc = np.array([r['Takeoff'] - r['High speed cruise'] for r in rows])
    crossover = linear_root(sw, to_minus_hsc)
    envelope = np.array([r['T0_envelope_kN'] for r in rows])
    design = np.array([r['T0_design_5pct_kN'] for r in rows])
    critical = [r['critical'] for r in rows]
    intervals = contiguous_intervals(sw, critical)
    min_i = int(np.argmin(design))
    code_e_sw = 65.0**2 / standard_airplane('crusair1')['inputs']['AR_w']

    fig, ax = plt.subplots(figsize=(11, 7))
    for key in criteria:
        ax.plot(sw, [r[key] for r in rows], linewidth=1.6, label=key)
    ax.plot(sw, envelope, linewidth=3.0, color='black', label='Envoltória crítica')
    ax.plot(sw, design, linewidth=2.0, color='black', linestyle='--', label='Envoltória + 5%')
    if landing_root is not None:
        ax.axvline(landing_root, color='firebrick', linewidth=2.2, linestyle='--', label=rf'Pouso a MLW ({landing_root:.1f} m²)')
        ax.axvspan(landing_root, sw.max(), color='green', alpha=0.06)
    ax.set_xlabel(r'Área de asa $S_w$ [m²]')
    ax.set_ylabel(r'Tração estática total requerida $T_0$ [kN]')
    ax.set_xlim(300, 500)
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / 'thrust_vs_Sw.png', dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.axhline(0.0, color='black', linewidth=1.2)
    ax.plot(sw, delta_landing, linewidth=2.4, label='Margem de pouso a MLW')
    if landing_root is not None:
        ax.axvline(landing_root, color='firebrick', linewidth=1.8, linestyle='--', label=rf'$\Delta S_{{w,lan}}=0$ ({landing_root:.1f} m²)')
        ax.axvspan(landing_root, sw.max(), color='green', alpha=0.06)
    ax.set_xlabel(r'Área de asa $S_w$ [m²]')
    ax.set_ylabel(r'Margem de pouso $\Delta S_{w,lan}$ [m²]')
    ax.set_xlim(300, 500)
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / 'landing_margin_vs_Sw.png', dpi=220)
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(10, 5.8))
    ax1.plot(sw, [r['MTOW_t'] for r in rows], linewidth=2.3, label='MTOW')
    ax1.set_xlabel(r'Área de asa $S_w$ [m²]')
    ax1.set_ylabel('MTOW [t]')
    ax1.grid(True, alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(sw, [r['span_m'] for r in rows], linewidth=2.0, linestyle='--', label='Envergadura')
    ax2.axhline(65.0, linewidth=1.6, linestyle=':', color='firebrick')
    ax2.set_ylabel('Envergadura [m]')
    lines = ax1.get_lines() + ax2.get_lines()[:1]
    ax1.legend(lines, [x.get_label() for x in lines], loc='best')
    fig.tight_layout()
    fig.savefig(outdir / 'mtow_span_vs_Sw.png', dpi=220)
    plt.close(fig)

    base = min(rows, key=lambda r: abs(r['Sw_m2'] - 450.0))
    with (outdir / 'analysis_summary.txt').open('w', encoding='utf-8') as f:
        f.write(f"MLW_frac = {base['MLW_frac']:.4f}\n")
        f.write(f"Landing root MLW = {landing_root:.3f} m2\n")
        # f.write(f"Takeoff/HSC crossover Sw = {crossover:.3f} m2\n")
        if crossover is None:
            f.write("Takeoff/HSC crossover Sw = none in 300-500 m2 range\n")
        else:
            f.write(f"Takeoff/HSC crossover Sw = {crossover:.3f} m2\n")
        f.write(f"Minimum 5pct envelope at Sw = {sw[min_i]:.1f} m2, T0 = {design[min_i]:.3f} kN\n")
        f.write(f"Code E upper-area threshold at AR=9.3 = {code_e_sw:.3f} m2\n")
        f.write("Critical intervals:\n")
        for a, b, c in intervals:
            f.write(f"{a:.1f} to {b:.1f} m2: {c}\n")
        f.write("Reference Sw=450 m2:\n")
        for key in ['MTOW_t', 'Wempty_t', 'Wfuel_t', 'MLW_t', 'span_m', 'Sh_m2', 'Sv_m2', 'CLmaxTO', 'CLmaxLD', 'LD_cruise', 'deltaS_landing_m2', 'Takeoff', 'High speed cruise', 'T0_design_5pct_kN']:
            f.write(f"{key} = {base[key]}\n")

    print((outdir / 'analysis_summary.txt').read_text(encoding='utf-8'))


if __name__ == '__main__':
    run()

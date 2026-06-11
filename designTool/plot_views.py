# GENERAL IMPORTS
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# -----------------------------------------------------------------------
# Helper: linear interpolation (same as auxiliary.lin_interp)
# -----------------------------------------------------------------------
def _lin_interp(x0, x1, y0, y1, x):
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


# -----------------------------------------------------------------------
# Helper: simplified fuselage outline sampled in 2-D
# Returns (x_array, half_width_array, half_height_array)
# -----------------------------------------------------------------------
def _fuselage_profile(L_f, D_f, x_tailstrike, n=200):
    xx = np.array([0.0, 1.24/41.72, 3.54/41.72, 7.55/41.72,
                   x_tailstrike/L_f, 1.0])
    hh = np.array([0.0, 2.27/4.0, 3.56/4.0, 1.0, 1.0, 1.07/4.0])
    ww = np.array([0.0, 1.83/4.0, 3.49/4.0, 1.0, 1.0, 0.284/4.0])

    x_norm  = np.linspace(0, 1, n)
    h_norm  = np.interp(x_norm, xx, hh)
    w_norm  = np.interp(x_norm, xx, ww)

    x_dim        = x_norm  * L_f
    half_height  = h_norm  * D_f / 2
    half_width   = w_norm  * D_f / 2

    return x_dim, half_width, half_height


# -----------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------
def plot_geometry_views(airplane, figname='views.png'):
    """
    Plots three orthographic views of the airplane:
      • Top view    (x–y plane, seen from above)
      • Side view   (x–z plane, seen from the right)
      • Front view  (y–z plane, seen from the nose)

    All axes use equal scales.
    """

    from .auxiliary import lin_interp  # use package's own lin_interp when available

    # ------------------------------------------------------------------ #
    # Unpack inputs
    # ------------------------------------------------------------------ #
    inp = airplane['inputs']
    geo = airplane['geometry']

    xr_w    = inp['xr_w'];  zr_w = inp['zr_w']
    tcr_w   = inp['tcr_w']; tct_w = inp['tct_w']
    cr_w    = geo['cr_w'];  ct_w  = geo['ct_w']
    xt_w    = geo['xt_w'];  yt_w  = geo['yt_w'];  zt_w = geo['zt_w']
    b_w     = geo['b_w']
    xm_w    = geo['xm_w'];  ym_w  = geo['ym_w'];  zm_w = geo['zm_w']
    cm_w    = geo['cm_w']

    xr_h = geo['xr_h'];   zr_h = inp['zr_h']
    tcr_h = inp['tcr_h']; tct_h = inp['tct_h']
    cr_h  = geo['cr_h'];  ct_h  = geo['ct_h']
    xt_h  = geo['xt_h'];  yt_h  = geo['yt_h'];  zt_h = geo['zt_h']
    b_h   = geo['b_h']
    xm_h  = geo['xm_h'];  ym_h  = geo['ym_h'];  zm_h = geo['zm_h']
    cm_h  = geo['cm_h']

    xr_v  = geo['xr_v'];  zr_v = inp['zr_v']
    tcr_v = inp['tcr_v']; tct_v = inp['tct_v']
    cr_v  = geo['cr_v'];  ct_v  = geo['ct_v']
    xt_v  = geo['xt_v'];  zt_v  = geo['zt_v'];  b_v = geo['b_v']

    L_f  = inp['L_f'];  D_f  = inp['D_f']
    x_n  = inp['x_n'];  y_n  = inp['y_n']
    z_n  = inp['z_n'];  L_n  = inp['L_n'];  D_n = inp['D_n']

    has_winglet   = inp['winglet']
    flap_type     = inp['flap_type']
    slat_type     = inp['slat_type']
    c_flap_c_wing = inp['c_flap_c_wing']
    b_flap_b_wing = inp['b_flap_b_wing']
    c_slat_c_wing = inp['c_slat_c_wing']
    b_slat_b_wing = inp['b_slat_b_wing']
    c_ail_c_wing  = inp['c_ail_c_wing']
    b_ail_b_wing  = inp['b_ail_b_wing']
    c_tank_c_w    = inp['c_tank_c_w']
    x_tank_c_w    = inp['x_tank_c_w']
    b_tank_b_w_s  = inp['b_tank_b_w_start']
    b_tank_b_w_e  = inp['b_tank_b_w_end']

    x_nlg = inp['x_nlg']
    x_mlg = inp['x_mlg'];  y_mlg = inp['y_mlg']
    z_lg  = inp['z_lg']
    x_tailstrike = inp['x_tailstrike']
    z_tailstrike = inp['z_tailstrike']

    # CG / NP (optional)
    xcg_fwd = airplane.get('balance', {}).get('xcg_fwd')
    xcg_aft = airplane.get('balance', {}).get('xcg_aft')
    xnp     = airplane.get('balance', {}).get('xnp')

    # ------------------------------------------------------------------ #
    # Pre-compute control surfaces
    # ------------------------------------------------------------------ #

    # Aileron
    ail_tip_margin = 0.02
    yr_a = (1.0 - (ail_tip_margin + b_ail_b_wing)) * b_w / 2
    yt_a = (1.0 - ail_tip_margin) * b_w / 2
    cr_a = lin_interp(0, b_w/2, cr_w, ct_w, yr_a) * c_ail_c_wing
    ct_a = lin_interp(0, b_w/2, cr_w, ct_w, yt_a) * c_ail_c_wing
    xr_a = lin_interp(0, b_w/2, xr_w+cr_w, xt_w+ct_w, yr_a) - cr_a
    xt_a = lin_interp(0, b_w/2, xr_w+cr_w, xt_w+ct_w, yt_a) - ct_a
    zr_a = lin_interp(0, b_w/2, zr_w, zt_w, yr_a)
    zt_a = lin_interp(0, b_w/2, zr_w, zt_w, yt_a)

    # Fuel tank
    yr_tk = b_tank_b_w_s * b_w / 2
    yt_tk = b_tank_b_w_e * b_w / 2
    cr_tk = lin_interp(0, b_w/2, cr_w, ct_w, yr_tk) * c_tank_c_w
    ct_tk = lin_interp(0, b_w/2, cr_w, ct_w, yt_tk) * c_tank_c_w
    xr_tk = lin_interp(0, b_w/2, xr_w, xt_w, yr_tk) + cr_tk * x_tank_c_w / c_tank_c_w
    xt_tk = lin_interp(0, b_w/2, xr_w, xt_w, yt_tk) + ct_tk * x_tank_c_w / c_tank_c_w
    zr_tk = lin_interp(0, b_w/2, zr_w, zt_w, yr_tk)
    zt_tk = lin_interp(0, b_w/2, zr_w, zt_w, yt_tk)

    # Flap
    if flap_type is not None:
        yr_f = D_f / 2
        yt_f = b_flap_b_wing * b_w / 2
        cr_f = lin_interp(0, b_w/2, cr_w, ct_w, yr_f) * c_flap_c_wing
        ct_f = lin_interp(0, b_w/2, cr_w, ct_w, yt_f) * c_flap_c_wing
        xr_f = lin_interp(0, b_w/2, xr_w+cr_w, xt_w+ct_w, yr_f) - cr_f
        xt_f = lin_interp(0, b_w/2, xr_w+cr_w, xt_w+ct_w, yt_f) - ct_f
        zr_f = lin_interp(0, b_w/2, zr_w, zt_w, yr_f)
        zt_f = lin_interp(0, b_w/2, zr_w, zt_w, yt_f)

    # Slat
    if slat_type is not None:
        yr_s = D_f / 2
        yt_s = b_slat_b_wing * b_w / 2
        cr_s = lin_interp(0, b_w/2, cr_w, ct_w, yr_s) * c_slat_c_wing
        ct_s = lin_interp(0, b_w/2, cr_w, ct_w, yt_s) * c_slat_c_wing
        xr_s = lin_interp(0, b_w/2, xr_w, xt_w, yr_s)
        xt_s = lin_interp(0, b_w/2, xr_w, xt_w, yt_s)
        zr_s = lin_interp(0, b_w/2, zr_w, zt_w, yr_s)
        zt_s = lin_interp(0, b_w/2, zr_w, zt_w, yt_s)

    # Elevator
    ele_tip_margin  = 0.1
    ele_root_margin = 0.1
    hist_b_e = 1 - ele_root_margin - ele_tip_margin
    hist_c_e = 0.25
    ct_e_loc = (1-ele_tip_margin)  * (ct_h - cr_h) + cr_h
    cr_e_loc = (1-hist_b_e-ele_tip_margin) * (ct_h - cr_h) + cr_h
    ct_e = ct_e_loc * hist_c_e
    cr_e = cr_e_loc * hist_c_e
    xr_e = (1-hist_b_e-ele_tip_margin) * (xt_h - xr_h) + xr_h + cr_e_loc*(1-hist_c_e)
    xt_e = (1-ele_tip_margin) * (xt_h - xr_h) + xr_h + ct_e_loc*(1-hist_c_e)
    yr_e = (1-hist_b_e-ele_tip_margin) * b_h / 2
    yt_e = (1-ele_tip_margin) * b_h / 2
    zr_e = (1-hist_b_e-ele_tip_margin) * (zt_h - zr_h) + zr_h
    zt_e = (1-ele_tip_margin) * (zt_h - zr_h) + zr_h

    # Rudder
    ver_base_margin = 0.1
    ver_tip_margin  = 1 - 0.1
    hist_c_v2 = 0.32
    cr_v_loc = ver_base_margin * (ct_v - cr_v) + cr_v
    ct_v_loc = ver_tip_margin  * (ct_v - cr_v) + cr_v
    cr_v2 = cr_v_loc * hist_c_v2
    ct_v2 = ct_v_loc * hist_c_v2
    xr_v2 = ver_base_margin * (xt_v - xr_v) + xr_v + cr_v_loc*(1-hist_c_v2)
    xt_v2 = ver_tip_margin  * (xt_v - xr_v) + xr_v + ct_v_loc*(1-hist_c_v2)
    zr_v2 = ver_base_margin * (zt_v - zr_v) + zr_v
    zt_v2 = ver_tip_margin  * (zt_v - zr_v) + zr_v

    # Fuselage profile data
    xf, fw, fh = _fuselage_profile(L_f, D_f, x_tailstrike)

    # Landing gear wheel size
    w_lg  = 0.05 * D_f
    d_lg  = 4 * w_lg

    # ------------------------------------------------------------------ #
    # Figure layout: 2×2 grid  (top-left = top, top-right = side,
    #                            bottom-left = front, bottom-right = legend)
    # ------------------------------------------------------------------ #
    fig = plt.figure(figsize=(16, 14))
    fig.patch.set_facecolor('#f9f9f9')

    ax_top   = fig.add_subplot(2, 2, 1)   # Vista Superior  (x-y)
    ax_side  = fig.add_subplot(2, 2, 2)   # Vista Lateral   (x-z)
    ax_front = fig.add_subplot(2, 2, 3)   # Vista Frontal   (y-z)
    ax_leg   = fig.add_subplot(2, 2, 4)   # Legenda / info

    for ax in (ax_top, ax_side, ax_front):
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', linewidth=0.4, alpha=0.6)
        ax.tick_params(labelsize=8)

    # ------------------------------------------------------------------
    # Colours and linewidths
    # ------------------------------------------------------------------
    C_WING  = '#1f77b4'  # blue
    C_HT    = '#2ca02c'  # green
    C_VT    = '#ff7f0e'  # orange
    C_FUS   = 'black'
    C_NAC   = '#ff7f0e'
    C_FLAP  = '#d62728'  # red
    C_SLAT  = '#9467bd'  # purple
    C_AIL   = '#2ca02c'
    C_TANK  = '#e377c2'  # magenta
    C_ELEV  = '#17becf'
    C_RUD   = '#bcbd22'
    C_LG    = '#7f7f7f'
    C_REF   = 'black'    # dashed reference lines

    LW_SURF = 1.5
    LW_CS   = 1.0
    LW_FUS  = 1.2
    LW_AUX  = 0.7

    # ==================================================================
    # TOP VIEW  (x horizontal → right, y vertical → up = right side)
    # Chord direction along x; span along y.
    # ==================================================================
    ax = ax_top

    # --- Fuselage top outline ---
    ax.fill_between(xf,  fw, -fw, alpha=0.08, color=C_FUS)
    ax.plot(xf,  fw, color=C_FUS, lw=LW_FUS)
    ax.plot(xf, -fw, color=C_FUS, lw=LW_FUS)

    # --- Wing (both sides) ---
    for sign in (+1, -1):
        ax.plot([xr_w, xt_w, xt_w+ct_w, xr_w+cr_w, xr_w],
                [sign*0.0, sign*yt_w, sign*yt_w, sign*0.0, sign*0.0],
                color=C_WING, lw=LW_SURF)

    # Winglet (top view: only a mark at wing tip)
    if has_winglet:
        ttw = 0.21
        for sign in (+1, -1):
            ax.plot([xt_w, xt_w+(1-ttw)*ct_w, xt_w+ct_w, xt_w+ct_w, xt_w],
                    [sign*yt_w]*5,
                    color=C_WING, lw=LW_SURF, linestyle='--')

    # --- Horizontal tail ---
    for sign in (+1, -1):
        ax.plot([xr_h, xt_h, xt_h+ct_h, xr_h+cr_h, xr_h],
                [sign*0.0, sign*yt_h, sign*yt_h, sign*0.0, sign*0.0],
                color=C_HT, lw=LW_SURF)

    # --- Vertical tail (top: shows VT root chord as a line at y=0) ---
    ax.plot([xr_v, xr_v+cr_v], [0, 0], color=C_VT, lw=LW_SURF, linestyle=':',
            label='_nolegend_')
    ax.plot([xt_v, xt_v+ct_v], [0, 0], color=C_VT, lw=LW_SURF, linestyle=':')

    # --- Nacelles ---
    for sign in (+1, -1):
        ax.add_patch(mpatches.Ellipse((x_n + L_n/2, sign*y_n),
                                       L_n, D_n,
                                       angle=0, fill=False,
                                       edgecolor=C_NAC, lw=LW_SURF))

    # --- Fuel tank ---
    for sign in (+1, -1):
        ax.plot([xr_tk, xt_tk, xt_tk+ct_tk, xr_tk+cr_tk, xr_tk],
                [sign*yr_tk, sign*yt_tk, sign*yt_tk, sign*yr_tk, sign*yr_tk],
                color=C_TANK, lw=LW_CS, linestyle='--')

    # --- Flap ---
    if flap_type is not None:
        for sign in (+1, -1):
            ax.plot([xr_f, xt_f, xt_f+ct_f, xr_f+cr_f, xr_f],
                    [sign*yr_f, sign*yt_f, sign*yt_f, sign*yr_f, sign*yr_f],
                    color=C_FLAP, lw=LW_CS)

    # --- Slat ---
    if slat_type is not None:
        for sign in (+1, -1):
            ax.plot([xr_s, xt_s, xt_s+ct_s, xr_s+cr_s, xr_s],
                    [sign*yr_s, sign*yt_s, sign*yt_s, sign*yr_s, sign*yr_s],
                    color=C_SLAT, lw=LW_CS)

    # --- Aileron ---
    for sign in (+1, -1):
        ax.plot([xr_a, xt_a, xt_a+ct_a, xr_a+cr_a, xr_a],
                [sign*yr_a, sign*yt_a, sign*yt_a, sign*yr_a, sign*yr_a],
                color=C_AIL, lw=LW_CS, linestyle='-.')

    # --- Elevator ---
    for sign in (+1, -1):
        ax.plot([xr_e, xt_e, xt_e+ct_e, xr_e+cr_e, xr_e],
                [sign*yr_e, sign*yt_e, sign*yt_e, sign*yr_e, sign*yr_e],
                color=C_ELEV, lw=LW_CS)

    # --- Landing gear (top view: circles at ground projection) ---
    if x_nlg is not None:
        ax.add_patch(mpatches.Circle((x_mlg,  y_mlg), d_lg/2, color=C_LG, fill=True, alpha=0.5))
        ax.add_patch(mpatches.Circle((x_mlg, -y_mlg), d_lg/2, color=C_LG, fill=True, alpha=0.5))
        ax.add_patch(mpatches.Circle((x_nlg,  0),     d_lg/2, color=C_LG, fill=True, alpha=0.5))

    # --- CG / NP markers ---
    if xcg_fwd is not None:
        ax.plot(xcg_fwd, ym_w, 'ko', ms=4, zorder=5)
    if xcg_aft is not None:
        ax.plot(xcg_aft, ym_w, 'ko', ms=4, zorder=5)
    if xnp is not None:
        ax.plot(xnp, ym_w, 'kx', ms=6, zorder=5)

    ax.set_xlabel('x [m]', fontsize=8)
    ax.set_ylabel('y [m]', fontsize=8)
    ax.set_title('Vista Superior', fontsize=10, fontweight='bold')

    # ==================================================================
    # SIDE VIEW  (x horizontal → right, z vertical → up)
    # ==================================================================
    ax = ax_side

    # --- Fuselage side outline ---
    ax.fill_between(xf,  fh, -fh, alpha=0.08, color=C_FUS)
    ax.plot(xf,  fh, color=C_FUS, lw=LW_FUS)
    ax.plot(xf, -fh, color=C_FUS, lw=LW_FUS)

    # --- Wing (side = root chord silhouette) ---
    ax.plot([xr_w, xt_w, xt_w+ct_w, xr_w+cr_w, xr_w],
            [zr_w, zt_w, zt_w,       zr_w,       zr_w],
            color=C_WING, lw=LW_SURF)
    # Thickness band at root
    ax.fill_between([xr_w, xr_w+cr_w],
                    [zr_w - tcr_w*cr_w/2, zr_w - tcr_w*cr_w/2],
                    [zr_w + tcr_w*cr_w/2, zr_w + tcr_w*cr_w/2],
                    alpha=0.15, color=C_WING)

    # Winglet side projection
    if has_winglet:
        ttw = 0.21
        ax.plot([xt_w, xt_w+(1-ttw)*ct_w, xt_w+ct_w, xt_w+ct_w, xt_w],
                [zt_w, zt_w+ct_w,           zt_w+ct_w,  zt_w,      zt_w],
                color=C_WING, lw=LW_SURF)

    # --- Horizontal tail ---
    ax.plot([xr_h, xt_h, xt_h+ct_h, xr_h+cr_h, xr_h],
            [zr_h, zt_h, zt_h,       zr_h,       zr_h],
            color=C_HT, lw=LW_SURF)

    # --- Vertical tail ---
    ax.plot([xr_v, xt_v, xt_v+ct_v, xr_v+cr_v, xr_v],
            [zr_v, zt_v, zt_v,       zr_v,       zr_v],
            color=C_VT, lw=LW_SURF)

    # --- Rudder ---
    ax.plot([xr_v2, xt_v2, xt_v2+ct_v2, xr_v2+cr_v2, xr_v2],
            [zr_v2, zt_v2, zt_v2,         zr_v2,        zr_v2],
            color=C_RUD, lw=LW_CS)

    # --- Nacelle (side: ellipse center at z_n) ---
    ax.add_patch(mpatches.Ellipse((x_n + L_n/2, z_n),
                                   L_n, D_n,
                                   angle=0, fill=False,
                                   edgecolor=C_NAC, lw=LW_SURF))

    # --- Fuel tank (side: root band) ---
    ax.plot([xr_tk, xr_tk+cr_tk], [zr_tk, zr_tk], color=C_TANK, lw=LW_CS, linestyle='--')

    # --- Flap side ---
    if flap_type is not None:
        ax.plot([xr_f, xr_f+cr_f], [zr_f, zr_f], color=C_FLAP, lw=LW_CS)

    # --- Slat side ---
    if slat_type is not None:
        ax.plot([xr_s, xr_s+cr_s], [zr_s, zr_s], color=C_SLAT, lw=LW_CS)

    # --- Aileron side ---
    ax.plot([xr_a, xr_a+cr_a], [zr_a, zr_a], color=C_AIL, lw=LW_CS, linestyle='-.')

    # --- Elevator ---
    ax.plot([xr_e, xr_e+cr_e], [zr_e, zr_e], color=C_ELEV, lw=LW_CS)

    # --- Landing gear (side: vertical lines) ---
    if x_nlg is not None:
        ax.plot([x_mlg, x_mlg], [z_lg, z_lg + d_lg], color=C_LG, lw=2.0)
        ax.plot([x_nlg, x_nlg], [z_lg, z_lg + d_lg], color=C_LG, lw=2.0)
        # Tailstrike reference line
        ax.plot([x_mlg, x_tailstrike],
                [z_lg,  z_tailstrike],
                color=C_REF, lw=LW_AUX, linestyle='--')

    # --- CG / NP ---
    if xcg_fwd is not None:
        ax.plot(xcg_fwd, zm_w, 'ko', ms=4, zorder=5, label='CG fwd/aft')
    if xcg_aft is not None:
        ax.plot(xcg_aft, zm_w, 'ko', ms=4, zorder=5)
    if xnp is not None:
        ax.plot(xnp, zm_w, 'kx', ms=6, zorder=5, label='NP')

    ax.set_xlabel('x [m]', fontsize=8)
    ax.set_ylabel('z [m]', fontsize=8)
    ax.set_title('Vista Lateral', fontsize=10, fontweight='bold')

    # ==================================================================
    # FRONT VIEW  (y horizontal → right = port side, z vertical → up)
    # ==================================================================
    ax = ax_front

    # --- Fuselage (front: ellipse cross-section at widest point) ---
    ax.add_patch(mpatches.Ellipse((0, 0), D_f, D_f,
                                   fill=False, edgecolor=C_FUS, lw=LW_FUS))

    # --- Wing (front: dihedral projection) ---
    #  root at (0, zr_w), tip at (±yt_w, zt_w)
    ax.plot([ 0,    yt_w,  yt_w,    0],
            [zr_w, zt_w,  zt_w,   zr_w],
            color=C_WING, lw=LW_SURF)
    ax.plot([ 0,   -yt_w, -yt_w,    0],
            [zr_w, zt_w,  zt_w,   zr_w],
            color=C_WING, lw=LW_SURF)
    # Thickness band at root
    ax.plot([0, 0], [zr_w - tcr_w*cr_w/2, zr_w + tcr_w*cr_w/2],
            color=C_WING, lw=2)

    # Winglet
    if has_winglet:
        for sign in (+1, -1):
            ax.plot([sign*yt_w, sign*yt_w],
                    [zt_w, zt_w + ct_w],
                    color=C_WING, lw=LW_SURF)

    # --- Horizontal tail ---
    ax.plot([ 0,    yt_h,  yt_h,    0],
            [zr_h, zt_h,  zt_h,   zr_h],
            color=C_HT, lw=LW_SURF)
    ax.plot([ 0,   -yt_h, -yt_h,    0],
            [zr_h, zt_h,  zt_h,   zr_h],
            color=C_HT, lw=LW_SURF)

    # --- Vertical tail ---
    ax.plot([0, 0], [zr_v, zt_v], color=C_VT, lw=LW_SURF + 1)

    # --- Nacelles ---
    for sign in (+1, -1):
        ax.add_patch(mpatches.Ellipse((sign*y_n, z_n), D_n, D_n,
                                       fill=False, edgecolor=C_NAC, lw=LW_SURF))

    # --- Landing gear (front: circles) ---
    if x_nlg is not None:
        ax.add_patch(mpatches.Circle(( y_mlg, z_lg), d_lg/2, color=C_LG, fill=True, alpha=0.5))
        ax.add_patch(mpatches.Circle((-y_mlg, z_lg), d_lg/2, color=C_LG, fill=True, alpha=0.5))
        ax.add_patch(mpatches.Circle((0,      z_lg), d_lg/2, color=C_LG, fill=True, alpha=0.5))
        # LG struts
        ax.plot([ y_mlg,  y_mlg], [zr_w, z_lg], color=C_LG, lw=1.5)
        ax.plot([-y_mlg, -y_mlg], [zr_w, z_lg], color=C_LG, lw=1.5)
        ax.plot([0,       0],     [0,    z_lg], color=C_LG, lw=1.5)

    ax.set_xlabel('y [m]', fontsize=8)
    ax.set_ylabel('z [m]', fontsize=8)
    ax.set_title('Vista Frontal', fontsize=10, fontweight='bold')

    # ==================================================================
    # Legend panel
    # ==================================================================
    ax_leg.axis('off')

    legend_elements = [
        Line2D([0],[0], color=C_WING,  lw=2,       label='Asa'),
        Line2D([0],[0], color=C_HT,    lw=2,       label='Empenagem Horizontal'),
        Line2D([0],[0], color=C_VT,    lw=2,       label='Empenagem Vertical'),
        Line2D([0],[0], color=C_NAC,   lw=2,       label='Nacele'),
        Line2D([0],[0], color=C_TANK,  lw=2, ls='--', label='Tanque de Combustível'),
        Line2D([0],[0], color=C_FLAP,  lw=2,       label='Flap'),
        Line2D([0],[0], color=C_SLAT,  lw=2,       label='Slat'),
        Line2D([0],[0], color=C_AIL,   lw=2, ls='-.', label='Aileron'),
        Line2D([0],[0], color=C_ELEV,  lw=2,       label='Profundor'),
        Line2D([0],[0], color=C_RUD,   lw=2,       label='Leme'),
        Line2D([0],[0], color=C_LG,    lw=2,       label='Trem de Pouso'),
        Line2D([0],[0], color=C_REF,   lw=1, ls='--', label='Linhas de referência'),
    ]
    if xcg_fwd is not None or xcg_aft is not None:
        legend_elements.append(Line2D([0],[0], marker='o', color='k', lw=0, ms=5, label='CG (avanç./recuado)'))
    if xnp is not None:
        legend_elements.append(Line2D([0],[0], marker='x', color='k', lw=0, ms=7, label='Ponto Neutro'))

    ax_leg.legend(handles=legend_elements, loc='center',
                  fontsize=9, frameon=True, framealpha=0.9,
                  title='Legenda', title_fontsize=10)

    # ==================================================================
    # Apply equal aspect after drawing (autoscale done)
    # ==================================================================
    for ax in (ax_top, ax_side, ax_front):
        ax.autoscale_view()
        ax.set_aspect('equal', adjustable='datalim')

    fig.suptitle('Vistas Ortogonais — Geometria da Aeronave',
                 fontsize=13, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(figname, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.show()
    return fig
